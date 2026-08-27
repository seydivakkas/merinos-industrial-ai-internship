# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 33
Citation Verifier: Kaynak Sadakati (Faithfulness) ve Halüsinasyon Doğrulama Motoru
"""

import re
from typing import List, Dict, Tuple, Optional
from day33.mini_project.src.models import (
    RAGContext,
    Claim,
    ClaimVerification,
    SourceChunk
)

DEFAULT_STOP_WORDS_TR = {
    "ve", "veya", "ile", "için", "bir", "bu", "şu", "o", "gibi", "kadar",
    "olan", "olarak", "ise", "daha", "en", "çok", "bazı", "tüm", "her",
    "da", "de", "ta", "te", "ki", "mi", "mu", "mü", "mı", "nın", "nin",
    "nun", "nün", "ye", "ya", "den", "dan", "ten", "tan"
}


def normalize_tr(text: str) -> str:
    """Türkçe karakterleri ve ASCII varyantlarını tek tip karşılaştırma için normalize eder."""
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    return text.translate(tr_map).lower()


def extract_technical_keywords(text: str, stop_words: Optional[set] = None) -> List[str]:
    """
    Cümleden noktalama ve bağlaçları temizleyerek
    karşılaştırmaya esas teknik kelimeleri, sayısal eşikleri ve kodları ayıklar.
    """
    stops = stop_words or DEFAULT_STOP_WORDS_TR
    norm_stops = {normalize_tr(s) for s in stops}
    cleaned = normalize_tr(text.replace("’", "'").replace("`", ""))
    # Alfanümerik terimler, kodlar (e-401) ve sayılar
    tokens = re.findall(r"[a-z0-9]+(?:[-/.][a-z0-9]+)*", cleaned)
    return [t for t in tokens if len(t) >= 2 and t not in norm_stops]


def split_into_claims(answer: str) -> List[Claim]:
    """
    Üretilen cevabı mantıksal iddia veya cümlelere böler,
    her cümlede geçen [S1], [S2] gibi atıf etiketlerini haritalar.
    """
    raw_lines = re.split(r"(?<=[.!?])\s+|\n+", answer.strip())
    claims: List[Claim] = []
    claim_counter = 1

    for line in raw_lines:
        s = line.strip()
        if not s or len(s) < 5:
            continue

        # [S1], [S2] etiketlerini bul
        citations = re.findall(r"\[([A-Za-z]\d+)\]", s)
        norm_citations = [c.upper() for c in citations]

        claims.append(Claim(
            claim_id=claim_counter,
            text=s,
            cited_source_ids=norm_citations,
            is_cited=len(norm_citations) > 0
        ))
        claim_counter += 1

    return claims


class CitationVerifier:
    """
    RAG çıktısındaki iddiaları ve atıfları kaynak parçalarla karşılaştırarak
    Faithfulness (Kaynak Sadakati) ve Hallucination (Uydurma Bilgi) denetimi yapar.
    """

    def __init__(self, faithfulness_threshold: float = 0.70):
        self.faithfulness_threshold = faithfulness_threshold

    def verify_claims(
        self,
        claims: List[Claim],
        context: RAGContext
    ) -> Tuple[List[ClaimVerification], float, float, float, bool]:
        """
        Tüm iddiaları doğrular.
        Dönüş: (Doğrulama kayıtları, Ortalama Faithfulness, Citation Precision, Citation Recall, Hallucination Var mı?)
        """
        if not claims:
            return [], 1.0, 1.0, 1.0, False

        source_map: Dict[str, SourceChunk] = {s.source_id.upper(): s for s in context.sources}
        verifications: List[ClaimVerification] = []

        total_citations = 0
        supported_citations = 0
        total_claims = len(claims)
        supported_claims = 0
        faithfulness_scores: List[float] = []
        any_hallucination = False

        for c in claims:
            # 1. Atıf Yoksa
            if not c.is_cited:
                verifications.append(ClaimVerification(
                    claim=c,
                    status="MISSING_CITATION",
                    faithfulness_score=0.0,
                    matched_keywords=[],
                    missing_keywords=extract_technical_keywords(c.text),
                    explanation="Cümlede hiçbir kaynak atfı ([S1], [S2] vb.) bulunmamaktadır."
                ))
                faithfulness_scores.append(0.0)
                continue

            # 2. Atıf Varsa, her bir atıf için kontrol et
            claim_cits = c.cited_source_ids
            total_citations += len(claim_cits)

            # İddianın anahtar kelimeleri (atıf etiketleri hariç)
            clean_text = re.sub(r"\[[A-Za-z]\d+\]", "", c.text)
            claim_keywords = extract_technical_keywords(clean_text)

            if not claim_keywords:
                # İddia teknik içerik taşımıyorsa
                verifications.append(ClaimVerification(
                    claim=c,
                    status="SUPPORTED",
                    faithfulness_score=1.0,
                    matched_keywords=[],
                    missing_keywords=[],
                    explanation="İfade teknik iddia içermeyen genel ifadedir."
                ))
                supported_citations += len(claim_cits)
                supported_claims += 1
                faithfulness_scores.append(1.0)
                continue

            # Birden fazla kaynak gösterilmişse en yüksek örtüşmeyi al
            best_faith = 0.0
            best_matched = []
            best_missing = claim_keywords
            has_invalid_sid = False
            invalid_sid_name = ""

            for sid in claim_cits:
                if sid not in source_map:
                    has_invalid_sid = True
                    invalid_sid_name = sid
                    any_hallucination = True
                    break

                src_chunk = source_map[sid]
                src_text_clean = normalize_tr(src_chunk.text)

                matched = [k for k in claim_keywords if k in src_text_clean]
                missing = [k for k in claim_keywords if k not in src_text_clean]

                faith = len(matched) / len(claim_keywords)
                if faith >= best_faith:
                    best_faith = faith
                    best_matched = matched
                    best_missing = missing

            if has_invalid_sid:
                best_status = "INVALID_SOURCE_ID"
                best_expl = f"Atıfta bulunulan '{invalid_sid_name}' kaynak kimliği sunulan context içinde mevcut değildir."
                any_hallucination = True
            elif best_faith >= self.faithfulness_threshold:
                best_status = "SUPPORTED"
                best_expl = f"İddia %{best_faith*100:.1f} oranında kaynakla örtüşmekte ve doğrulanmaktadır."
                supported_citations += len(claim_cits)
                supported_claims += 1
            else:
                best_status = "HALLUCINATION"
                best_expl = (
                    f"İddia kaynakla yalnızca %{best_faith*100:.1f} oranında örtüşmektedir. "
                    f"Eksik/Uydurma Terimler: {', '.join(best_missing[:5])}"
                )
                any_hallucination = True

            faithfulness_scores.append(round(best_faith, 4))
            verifications.append(ClaimVerification(
                claim=c,
                status=best_status,
                faithfulness_score=round(best_faith, 4),
                matched_keywords=best_matched,
                missing_keywords=best_missing,
                explanation=best_expl
            ))

        mean_faith = round(sum(faithfulness_scores) / len(faithfulness_scores), 4) if faithfulness_scores else 1.0
        cit_prec = round(supported_citations / total_citations, 4) if total_citations > 0 else 1.0
        cit_rec = round(supported_claims / total_claims, 4) if total_claims > 0 else 1.0

        return verifications, mean_faith, cit_prec, cit_rec, any_hallucination
