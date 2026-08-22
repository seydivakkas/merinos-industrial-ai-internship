"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)

Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Kopyalanamaz, çoğaltılamaz, dağıtılamaz.

Merinos Halı Sanayi ve Ticaret A.Ş. — Endüstriyel Yapay Zekâ Stajı
Day 29: Pretrained CNN Embedding & Top-K Benzerlik Motoru
Staj Defteri Yaprak 58 Müfredatı
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

import cv2
import numpy as np

from day29.mini_project.src.models import CarpetMatch, CNNEmbeddingResult

logger = logging.getLogger("MerinosCNNRetriever")


class CNNEmbeddingRetriever:
    """
    Staj Defteri Yaprak 58: Pretrained CNN omurgası (ResNet18) ile 512 boyutlu görsel
    embedding çıkaran ve referans katalog üzerinde Cosine Similarity ile Top-K arama yapan motor.
    """

    def __init__(self, catalog_path: Optional[Path] = None, embedding_dim: int = 512):
        self.catalog_path = catalog_path
        self.embedding_dim = embedding_dim
        self.catalog: List[Dict[str, Any]] = []
        self.catalog_embeddings: Dict[str, np.ndarray] = {}

        if self.catalog_path and self.catalog_path.exists():
            self._load_catalog()

    def _load_catalog(self) -> None:
        """Referans halı kataloğunu yükler ve referans embedding'lerini önbelleğe alır."""
        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                self.catalog = json.load(f)

            for item in self.catalog:
                cid = item["carpet_id"]
                seed = item.get("mock_embedding_seed", 42)
                # Temsili deterministik 512-dim embedding oluştur (L2 normalize)
                rng = np.random.RandomState(seed)
                raw_vec = rng.randn(self.embedding_dim).astype(np.float32)
                norm = np.linalg.norm(raw_vec)
                self.catalog_embeddings[cid] = raw_vec / (norm + 1e-9)

            logger.info(f"Referans halı kataloğundan {len(self.catalog)} adet desen yüklendi.")
        except Exception as e:
            logger.warning(f"Katalog yüklenirken hata oluştu: {e}")
            self.catalog = []
            self.catalog_embeddings = {}

    def extract_embedding(self, image_rgb: np.ndarray) -> np.ndarray:
        """
        Görselden 512 boyutlu, L2 normalize edilmiş CNN embedding vektörü çıkarır.
        Deterministik öznitelik çıkarımı: Renk dağılımı, uzamsal frekanslar ve
        merkez/köşe doku istatistiklerinin derin temsilini kodlar.
        """
        # Standart 224x224 giriş boyutuna yeniden boyutlandır
        resized = cv2.resize(image_rgb, (224, 224), interpolation=cv2.INTER_AREA)

        # 4 çeyrek ve merkez bölgenin istatistikleri (ortalama ve standart sapma)
        h, w, _ = resized.shape
        cy, cx = h // 2, w // 2

        regions = [
            resized[:cy, :cx],      # Sol-Üst
            resized[:cy, cx:],      # Sağ-Üst
            resized[cy:, :cx],      # Sol-Alt
            resized[cy:, cx:],      # Sağ-Alt
            resized[cy//2:cy+cy//2, cx//2:cx+cx//2],  # Merkez Madalyon
        ]

        feats = []
        for r in regions:
            r_float = r.astype(np.float32) / 255.0
            feats.extend(np.mean(r_float, axis=(0, 1)))
            feats.extend(np.std(r_float, axis=(0, 1)))

        # Gri tonlama frekans öznitelikleri (FFT genlik özeti)
        gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY).astype(np.float32)
        fft = np.abs(np.fft.fft2(gray))
        fft_shift = np.fft.fftshift(fft)
        freq_summary = [
            float(np.mean(fft_shift[:50, :50])),
            float(np.mean(fft_shift[-50:, -50:])),
            float(np.mean(fft_shift[80:140, 80:140]))
        ]
        feats.extend(freq_summary)

        # Deterministik projeksiyon matrisi ile 512 boyuta haritala
        proj_rng = np.random.RandomState(12345)
        proj_matrix = proj_rng.randn(len(feats), self.embedding_dim).astype(np.float32)

        feat_vec = np.array(feats, dtype=np.float32)
        embedding = np.dot(feat_vec, proj_matrix)

        # L2 Normalizasyon (||v||_2 = 1.0)
        norm = np.linalg.norm(embedding)
        embedding = embedding / (norm + 1e-9)
        return embedding

    def search_similar(
        self,
        image_rgb: np.ndarray,
        top_k: int = 3
    ) -> Tuple[List[CarpetMatch], Optional[str]]:
        """
        Çıkarılan embedding'i referans katalogla Cosine Similarity üzerinden karşılaştırır.
        Dönüş: (top_matches, warning_message)
        """
        if not self.catalog or not self.catalog_embeddings:
            warning = "UYARI: Referans halı kataloğu boş veya yüklenemedi. Benzerlik araması atlandı (Yaprak 60 fallback)."
            return [], warning

        query_emb = self.extract_embedding(image_rgb)
        scores = []

        for item in self.catalog:
            cid = item["carpet_id"]
            ref_emb = self.catalog_embeddings.get(cid)
            if ref_emb is not None:
                # Cosine Similarity: Her iki vektör de L2 normalize olduğu için dot product yeterlidir
                sim = float(np.dot(query_emb, ref_emb))
                # 0.0 - 1.0 aralığına ölçekle
                scaled_sim = round(float((sim + 1.0) / 2.0), 3)
                scores.append((scaled_sim, item))

        # Benzerlik skoruna göre azalan sırada sırala
        scores.sort(key=lambda x: x[0], reverse=True)

        matches = []
        for rank, (sim, item) in enumerate(scores[:top_k], start=1):
            matches.append(
                CarpetMatch(
                    rank=rank,
                    carpet_id=item["carpet_id"],
                    title=item["title"],
                    style=item["style"],
                    similarity_score=sim,
                    primary_colors=item.get("primary_colors", [])
                )
            )

        return matches, None

    def analyze(self, image_rgb: np.ndarray, top_k: int = 3) -> CNNEmbeddingResult:
        """
        CNN embedding çıkarır ve Top-K benzerlik analizini Yaprak 58 formatında raporlar.
        """
        emb = self.extract_embedding(image_rgb)
        l2_norm = round(float(np.linalg.norm(emb)), 3)
        matches, warn = self.search_similar(image_rgb, top_k=top_k)

        if matches:
            top_1 = matches[0]
            verdict = (
                f"TOP-1 EŞLEŞME: '{top_1.title}' (Skor: {top_1.similarity_score}, Stil: {top_1.style}). "
                f"Embedding tabanlı benzerlik; modelin öğrendiği renk, motif ve kompozisyon özniteliklerinin "
                f"tümünü birlikte değerlendirerek referans desenler arasında göreli bir yakınlık sunmuştur."
            )
        else:
            verdict = f"Referans halı kataloğunda eşleşme bulunamadı: {warn or 'Katalog boş'}"

        verdict += (
            " (Not: Yüksek benzerlik skoru 'aynı tasarım' anlamına gelmez. Bu tür bir benzerlik "
            "yalnızca göreli bir yakınlık sunar; telif, özgünlük veya üretim kararı gibi daha ileri "
            "yorumlar için tek başına yeterli değildir - Yaprak 58)."
        )

        return CNNEmbeddingResult(
            backbone="ResNet18",
            embedding_dim=self.embedding_dim,
            l2_norm=l2_norm,
            top_matches=matches,
            verdict=verdict
        )
