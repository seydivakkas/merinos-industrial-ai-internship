# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 33
Error Classifier: Retrieval Hatası vs. Generation Hatası vs. Hallucination Ayrıştırma Motoru
"""

from typing import Dict, Any, Optional
from day33.mini_project.src.models import RAGResponse, RAGEvalItem


class RAGErrorClassifier:
    """
    RAG akışındaki başarısızlıkları kök nedenine göre ayrıştırır:
    - SUCCESS: Retrieval doğru, Generation sadık ve atıflar eksiksiz.
    - RETRIEVAL_FAILURE: Hedef parça context'e giremedi (Retrieval kusuru).
    - GENERATION_HALLUCINATION: Doğru parça context'te vardı fakat model uydurdu (LLM kusuru).
    - CORRECT_ABSTENTION: Korpus dışı sorguda dürüstçe 'bilgi yok' denildi.
    - FAILED_ABSTENTION: Korpus dışı sorguda uydurma cevap üretildi.
    """

    def __init__(self, faithfulness_threshold: float = 0.70):
        self.faithfulness_threshold = faithfulness_threshold

    def classify_result(
        self,
        query_id: str,
        query: str,
        category: str,
        expected_behavior: str,
        target_chunk_id: Optional[str],
        rag_response: RAGResponse
    ) -> RAGEvalItem:
        """Sorgu çıktısını değerlendirip hata kategorisini belirler."""
        # Context içinde hedef parça var mı?
        retrieved_chunk_ids = [s.chunk_id for s in rag_response.context.sources]
        retrieval_hit = False
        target_rank = None

        if target_chunk_id:
            for r_idx, cid in enumerate(retrieved_chunk_ids, start=1):
                if cid == target_chunk_id:
                    retrieval_hit = True
                    target_rank = r_idx
                    break

        actual_behavior = "REFUSAL" if rag_response.is_refusal else "ANSWER_GENERATED"
        generation_faithful = (rag_response.overall_faithfulness >= self.faithfulness_threshold) and not rag_response.hallucination_detected

        # 1. Korpus Dışı (Negative Control) Senaryosu
        if category == "OUT_OF_DOMAIN" or expected_behavior == "REFUSAL":
            if rag_response.is_refusal:
                error_type = "CORRECT_ABSTENTION"
            else:
                error_type = "FAILED_ABSTENTION"

        # 2. Retrieval Başarısızlığı
        elif not retrieval_hit:
            error_type = "RETRIEVAL_FAILURE"

        # 3. Retrieval Başarılı Fakat Model Halüsinasyon Üretti
        elif rag_response.hallucination_detected or not generation_faithful:
            error_type = "GENERATION_HALLUCINATION"

        # 4. Tam Başarı
        else:
            error_type = "SUCCESS"

        return RAGEvalItem(
            query_id=query_id,
            query=query,
            category=category,
            expected_behavior=expected_behavior,
            actual_behavior=actual_behavior,
            retrieval_hit=retrieval_hit,
            retrieval_target_rank=target_rank,
            generation_faithful=generation_faithful,
            hallucination_detected=rag_response.hallucination_detected,
            error_type=error_type,
            rag_response=rag_response
        )
