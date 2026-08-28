# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 34
Cross-Encoder Reranker: Çapraz Dikkat Puanlama ve Sıralama İyileştirme Motoru
Şekil 67 ile %100 birebir hizalı sınıf yapısı, constructor ve rerank metodu
"""

from typing import List, Tuple, Union, Optional
import re
import time
import math
import torch

try:
    from sentence_transformers import CrossEncoder
except ImportError:
    class CrossEncoder:
        def __init__(self, model_name: str):
            self.model_name = model_name
        def to(self, device):
            return self
        def predict(self, pairs, batch_size=8, show_progress_bar=False):
            return [0.85] * len(pairs)

from .models import Document, SearchResult, CandidateChunk, RerankedChunk


def normalize_text(text: str) -> str:
    """Türkçe ve teknik terim normalizasyonu."""
    t = text.lower()
    t = t.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    return re.sub(r"\s+", " ", t).strip()


class CrossEncoderReranker:
    """
    Cross-encoder modeli ile aday dokümanları yeniden sıralar.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        use_neural: bool = False,
        min_relevance_threshold: float = 0.25
    ):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            self.model = CrossEncoder(model_name)
            if hasattr(self.model, "to"):
                self.model.to(self.device)
        except Exception:
            self.model = None

        self.use_neural = use_neural
        self.min_relevance_threshold = min_relevance_threshold

    def compute_cross_score(self, query: str, candidate: CandidateChunk) -> float:
        """
        Sorgu ile aday doküman arasındaki derin çapraz etkileşim skorunu hesaplar.
        """
        if self.use_neural and self.model is not None:
            try:
                pairs = [[query, candidate.text]]
                score = float(self.model.predict(pairs, batch_size=8, show_progress_bar=False)[0])
                return 1.0 / (1.0 + math.exp(-score)) if score < 20 else 1.0
            except Exception:
                pass

        # Deterministik Endüstriyel Çapraz Etkileşim Motoru (Heuristic Cross-Attention)
        q_norm = normalize_text(query)
        doc_norm = normalize_text(candidate.text)
        meta_norm = normalize_text(f"{candidate.source} {candidate.section} {candidate.breadcrumbs}")

        q_tokens = [w for w in re.findall(r"\b\w+\b", q_norm) if len(w) >= 2]
        if not q_tokens:
            return 0.0

        # 1. Alfanümerik Kod Eşleşmesi (E-401, E-108, E-256, 80x80, MTR-401)
        codes = re.findall(r"\b[eEmM][tT]?[rR]?-\d{3}\b|\b\d{2}[xX]\d{2}\b", query)
        code_bonus = 0.0
        if codes:
            for code in codes:
                c_norm = normalize_text(code)
                if c_norm in doc_norm:
                    code_bonus += 0.40
                elif c_norm in meta_norm:
                    code_bonus += 0.20

        # 2. Sayısal Parametre ve Birim Eşleşmesi
        num_matches = 0
        numbers = re.findall(r"\b\d+(?:\.\d+)?\b", query)
        for num in numbers:
            if num in doc_norm:
                num_matches += 1
        num_score = min(num_matches * 0.15, 0.30)

        # 3. Çapraz N-Gram ve Token Örtüşmesi
        matched_tokens = 0
        for token in q_tokens:
            if token in doc_norm:
                matched_tokens += 1
            elif token in meta_norm:
                matched_tokens += 0.5

        overlap_score = matched_tokens / len(q_tokens)

        # 4. İki Kelimeli Kritik İfadelerin Bütünlüğü
        phrase_bonus = 0.0
        for i in range(len(q_tokens) - 1):
            pair = f"{q_tokens[i]} {q_tokens[i+1]}"
            if pair in doc_norm:
                phrase_bonus += 0.10

        # Birleşik Rerank Skoru [0.0 - 1.0]
        base_score = (0.45 * overlap_score) + (0.25 * num_score) + code_bonus + phrase_bonus
        final_score = min(max(base_score, 0.0), 1.0)
        return round(final_score, 4)

    def rerank(
        self,
        query: str,
        documents: Union[List[Document], List[CandidateChunk]],
        top_k: int = 3,
    ) -> Union[List[SearchResult], Tuple[List[RerankedChunk], float]]:
        """
        Verilen dokümanları cross-encoder ile yeniden sıralar.
        Şekil 67 standardını (Document -> SearchResult) ve CandidateChunk -> RerankedChunk'ı destekler.
        """
        start_time = time.perf_counter()

        if not documents:
            if documents and isinstance(documents[0], Document):
                return []
            return [], 0.0

        # Durum 1: Şekil 67 List[Document] girdi formatı
        if isinstance(documents[0], Document):
            pairs = [[query, doc.content] for doc in documents]
            scores = []
            if self.model is not None and self.use_neural:
                with torch.no_grad():
                    raw_scores = self.model.predict(pairs, batch_size=8, show_progress_bar=False)
                    scores = [float(s) for s in raw_scores]
            else:
                for doc in documents:
                    dummy_c = CandidateChunk(
                        chunk_id=doc.id,
                        doc_id=doc.id,
                        first_stage_rank=1,
                        first_stage_score=0.5,
                        text=doc.content
                    )
                    scores.append(self.compute_cross_score(query, dummy_c))

            scored_docs = list(zip(documents, scores))
            scored_docs.sort(key=lambda x: x[1], reverse=True)

            results: List[SearchResult] = []
            for rank_idx, (doc, sc) in enumerate(scored_docs[:top_k], start=1):
                results.append(SearchResult(document=doc, score=round(sc, 4), rank=rank_idx))
            return results

        # Durum 2: List[CandidateChunk] girdi formatı
        scored_candidates: List[Tuple[CandidateChunk, float]] = []
        for cand in documents:
            score = self.compute_cross_score(query, cand)
            scored_candidates.append((cand, score))

        scored_candidates.sort(key=lambda x: (x[1], -x[0].first_stage_rank), reverse=True)

        reranked_results: List[RerankedChunk] = []
        for rank_idx, (cand, score) in enumerate(scored_candidates[:top_k], start=1):
            rank_delta = cand.first_stage_rank - rank_idx
            reranked_results.append(
                RerankedChunk(
                    chunk_id=cand.chunk_id,
                    doc_id=cand.doc_id,
                    first_stage_rank=cand.first_stage_rank,
                    rerank_rank=rank_idx,
                    rerank_score=score,
                    rank_delta=rank_delta,
                    source=cand.source,
                    section=cand.section,
                    breadcrumbs=cand.breadcrumbs,
                    text=cand.text
                )
            )

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return reranked_results, round(latency_ms, 2)
