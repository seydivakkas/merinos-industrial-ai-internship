"""
Merinos Industrial AI Internship - Day 27
Atomic Claim & Proposition Extractor for RAG Evaluation

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

import re
from typing import List


class ClaimExtractor:
    """Metinleri atomik teknik iddialara (atomic propositions/claims) ayrıştıran motor."""

    def __init__(self, min_words: int = 3):
        self.min_words = min_words
        # Cümle sonu noktalama işaretleri ve satır sonları
        self.sentence_end_pattern = re.compile(r"(?<=[.?!;\n])\s+")
        # Sadece virgüllü veya noktalı virgüllü açık yan tümce bağlaçları
        self.clause_splitter = re.compile(
            r"(?:;\s*|,\s*(?:ancak|fakat|öte yandan|ayrıca)\s+)",
            re.IGNORECASE
        )

    def extract_claims(self, text: str) -> List[str]:
        """Verilen metni temizleyip atomik iddialara (claims) böler."""
        if not text or not text.strip():
            return []

        cleaned_text = re.sub(r"\s+", " ", text.strip())
        # 1. Cümle bazlı bölme
        raw_sentences = self.sentence_end_pattern.split(cleaned_text)
        
        claims: List[str] = []
        for sent in raw_sentences:
            sent = sent.strip()
            if not sent:
                continue

            # Konuşma girişlerini ve gereksiz dolguları temizle
            sent = re.sub(r"^(merhaba|özetle|sonuç olarak|sorunuza göre|teknik olarak)[,:]?\s*", "", sent, flags=re.IGNORECASE)

            # 2. Eğer cümle çok uzunsa (>18 kelime), virgüllü bağlaçlarla yan tümcelere ayır
            if len(sent.split()) > 18:
                clauses = self.clause_splitter.split(sent)
            else:
                clauses = [sent]

            for clause in clauses:
                clause = clause.strip(" ,.;:-_")
                words = clause.split()
                if len(words) >= self.min_words:
                    claims.append(clause)

        # Eğer hiç iddia çıkarılamadıysa fakat metin varsa, cümlenin kendisini döndür
        if not claims and len(cleaned_text.split()) >= 2:
            claims.append(cleaned_text.strip(" ,.;:-_"))

        return claims
