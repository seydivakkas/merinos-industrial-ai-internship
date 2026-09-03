# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 39
Tezgâh Başı Yerel Arama Boru Hattı: ONNX INT8 Tabanlı İki Aşamalı (Bi-Encoder + Cross-Encoder) Arama
"""

import os
import time
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional

from day39.mini_project.src.edge_engine import EdgeInferenceEngine
from day39.mini_project.src.models import EdgeQueryResult


class EdgeRagPipeline:
    """Merinos Dokuma Salonu Tezgâh Başı (Edge IPC) Yerel Arama Hattı."""

    DEFAULT_CORPUS = [
        {
            "doc_id": "DOC-VDW-001",
            "section": "Motor Termik Arızaları",
            "text": "E-401 arıza kodu Van de Wiele jakarlı dokuma tezgâhlarında ana tahrik motorunun 85 derece termik sınırını aştığını gösterir. Tezgâh acilen durdurulmalı, motor fan ızgaraları temizlenmeli ve sıcaklık 65 derece altına inene kadar yeniden başlatılmamalıdır."
        },
        {
            "doc_id": "DOC-VDW-002",
            "section": "Pnömatik İplik Tansiyonu",
            "text": "İplik tansiyon basıncı 14 ila 16 bar arasında tutulmalıdır. Basınç 14 bar altına düşerse atkı kopması meydana gelir; regülatör vana 3 saat yönünde çevrilerek 15 bar seviyesine ayarlanmalıdır. 20 bar fabrika pnömatik güvenlik üst sınırıdır."
        },
        {
            "doc_id": "DOC-TEX-003",
            "section": "Finisaj Buharlı Fikse",
            "text": "Akrilik ve yün halı terbiyesinde buharlı fikse tüneli 135 derecede doymuş buhar ile 60 saniye boyunca uygulanmalıdır. Sıcaklık 140 dereceyi aşarsa elyaf deformasyonu ve sararma meydana gelir."
        },
        {
            "doc_id": "DOC-SCH-004",
            "section": "Mekik Optik Sensörü",
            "text": "E-108 arıza kodu Schönherr dokuma tezgâhında atkı taşıyıcı mekik sensörünün optik kirlenmesini belirtir. Mercek basınçlı hava ve izopropil alkol ile temizlenmelidir."
        },
        {
            "doc_id": "DOC-SPEC-005",
            "section": "Hereke Serisi Dokuma Şartnamesi",
            "text": "Hereke serisi jakarlı halı üretiminde çözgü sıklığı 28 tel/cm, düğüm sıklığı ise 80x80 düğüm/dm2 olarak sabitlenmelidir. Tolerans sınırı artı eksi yüzde ikidir."
        }
    ]

    def __init__(
        self,
        bi_encoder_model_path: str,
        cross_encoder_model_path: str,
        corpus: Optional[List[Dict[str, str]]] = None,
        num_threads: int = 2
    ):
        self.bi_encoder_path = bi_encoder_model_path
        self.cross_encoder_path = cross_encoder_model_path
        self.corpus = corpus if corpus is not None else self.DEFAULT_CORPUS
        self.num_threads = num_threads

        # Motorları Başlat
        self.bi_engine = EdgeInferenceEngine(bi_encoder_model_path, num_threads=num_threads)
        self.cross_engine = EdgeInferenceEngine(cross_encoder_model_path, num_threads=num_threads)

        # Doküman Vektör İndeksini Hazırla
        self.doc_embeddings: Optional[np.ndarray] = None
        self._build_index()

    def _hash_text_to_feature(self, text: str, dim: int = 384) -> np.ndarray:
        """Deterministik metin öznitelik vektörü üretir (unigram + bigram sha256)."""
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().replace("-", " ").replace(",", " ").split()
        for idx, word in enumerate(words):
            h1 = int(hashlib.sha256(word.encode("utf-8")).hexdigest()[:8], 16)
            pos1 = h1 % dim
            vec[pos1] += 2.0 / (idx + 1.0)
            if idx > 0:
                bigram = f"{words[idx-1]}_{word}"
                h2 = int(hashlib.sha256(bigram.encode("utf-8")).hexdigest()[:8], 16)
                pos2 = h2 % dim
                vec[pos2] += 3.0 / (idx + 1.0)
        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec /= norm
        return vec

    def _build_index(self):
        """Kılavuz dokümanlarının Bi-Encoder vektörlerini hesaplar."""
        embeddings = []
        for item in self.corpus:
            feat = self._hash_text_to_feature(item["text"], dim=384)
            emb = self.bi_engine.encode(feat)[0]
            embeddings.append(emb)
        self.doc_embeddings = np.array(embeddings, dtype=np.float32)

    def search_and_rerank(
        self,
        query: str,
        loom_id: str = "TEZGAH-01",
        top_k: int = 4,
        top_n: int = 2
    ) -> EdgeQueryResult:
        """Tezgâh başı iki aşamalı (Bi-Encoder Retrieval + Cross-Encoder Rerank) yerel arama."""
        t_start = time.perf_counter()

        # 1. Aşama: Bi-Encoder Arama
        q_feat = self._hash_text_to_feature(query, dim=384)
        q_emb = self.bi_engine.encode(q_feat)[0]

        # Cosine Similarity
        scores = np.dot(self.doc_embeddings, q_emb)
        top_indices = np.argsort(scores)[::-1][:top_k]

        candidates = [self.corpus[i] for i in top_indices]

        # 2. Aşama: Cross-Encoder Reranking
        pair_features = []
        for cand in candidates:
            c_feat = self._hash_text_to_feature(cand["text"], dim=384)
            combined = np.concatenate([q_feat, c_feat])
            pair_features.append(combined)

        pair_array = np.array(pair_features, dtype=np.float32)
        rerank_scores = self.cross_engine.score(pair_array)

        # Skorlara göre yeniden sırala
        ranked_order = np.argsort(rerank_scores)[::-1][:top_n]

        final_doc_ids = [candidates[idx]["doc_id"] for idx in ranked_order]
        final_scores = [round(float(rerank_scores[idx]), 4) for idx in ranked_order]

        elapsed_ms = round((time.perf_counter() - t_start) * 1000.0, 2)

        return EdgeQueryResult(
            query=query,
            loom_id=loom_id,
            retrieved_doc_ids=final_doc_ids,
            scores=final_scores,
            execution_time_ms=elapsed_ms,
            engine_used="ONNX_INT8_EDGE"
        )
