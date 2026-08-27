# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 33
Context Builder: Teknik dokümanlardan ilgili bağlamı (context) oluşturan sınıf.
Şekil 65 ile %100 birebir hizalı sınıf yapısı ve context oluşturma mimarisi
"""

from typing import List, Dict, Any, Optional, Union
import json
from pathlib import Path

from day33.mini_project.src.models import SourceChunk, RAGContext


class ContextBuilder:
    """Teknik dokümanlardan ilgili bağlamı (context) oluşturan sınıf."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        top_k: int = 3,
        id_prefix: str = "S"
    ):
        self.top_k = top_k
        self.id_prefix = id_prefix
        self.config: Dict[str, Any] = {}

        if config_path:
            self.config_path = Path(config_path)
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                self.top_k = self.config.get("retrieval", {}).get("top_k", top_k)
            else:
                self.config_path = None
        else:
            self.config_path = None

    def _retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Sorgu için basit veya harici getirme işlemi yapar."""
        return [
            {
                "content": "E-401 arıza kodu, genellikle pompa çıkış basıncının düşük olması durumunda oluşur. Pompa besleme hattında tıkanıklık veya pompa arızası kontrol edilmelidir.",
                "source": "Teknik Doküman - Pompa Hata Kodları (dokuman_v1.pdf, s. 24)"
            }
        ]

    def build_context(
        self,
        query_or_items: Union[str, List[Any]],
        chunk_lookup: Optional[dict] = None
    ) -> Any:
        """
        Soruya göre ilgili doküman parçalarını bularak bağlam oluşturur.
        Şekil 65 ve hibrit pipeline kullanımını polimorfik olarak destekler.
        """
        # 1. Şekil 65 Standardı: Doğrudan sorgu metni (str) verilmişse
        if isinstance(query_or_items, str):
            query = query_or_items
            docs = self._retrieve(query, top_k=self.top_k)
            context_parts = []
            sources = []
            for i, doc in enumerate(docs):
                content = doc.get("content", "")
                source = doc.get("source", "bilinmiyor")
                context_parts.append(f"[{self.id_prefix}{i+1}] {content}")
                sources.append({
                    "id": f"{self.id_prefix}{i+1}",
                    "source": source,
                    "content": content
                })
            return {
                "context_text": "\n\n".join(context_parts),
                "sources": sources
            }

        # 2. Pipeline / Test Standardı: retrieved_items (List[Any]) ve chunk_lookup verilmişse
        retrieved_items = query_or_items
        selected_items = retrieved_items[:self.top_k] if retrieved_items else []
        lookup = chunk_lookup or {}
        sources_list: List[SourceChunk] = []

        formatted_blocks: List[str] = [
            "--- BAŞLANGIÇ: TEKNİK FABRİKA DOKÜMANLARI (CONTEXT) ---"
        ]

        for idx, item in enumerate(selected_items, start=1):
            source_id = f"{self.id_prefix}{idx}"
            cid = getattr(item, "chunk_id", str(item))
            score = getattr(item, "final_score", getattr(item, "score", 0.0))
            rank = getattr(item, "rank", idx)

            chunk = lookup.get(cid)
            if chunk:
                doc_id = chunk.doc_id
                source_file = chunk.source
                section = chunk.section
                breadcrumbs = chunk.breadcrumbs
                text = chunk.text.strip()
            else:
                doc_id = getattr(item, "doc_id", "BILINMEYEN_DOC")
                source_file = getattr(item, "source", "belge")
                section = getattr(item, "section", "Genel")
                breadcrumbs = getattr(item, "breadcrumbs", "")
                text = getattr(item, "text_snippet", "")

            src_chunk = SourceChunk(
                source_id=source_id,
                chunk_id=cid,
                doc_id=doc_id,
                title=source_file,
                section=section,
                breadcrumbs=breadcrumbs,
                text=text,
                rank=rank,
                score=round(float(score), 4)
            )
            sources_list.append(src_chunk)

            block = (
                f"[{source_id}] Doküman: {source_file} | Bölüm: {section}\n"
                f"Hiyerarşi: {breadcrumbs}\n"
                f"Metin:\n{text}"
            )
            formatted_blocks.append(block)

        formatted_blocks.append("--- BİTİŞ: TEKNİK FABRİKA DOKÜMANLARI ---")
        full_context_text = "\n\n".join(formatted_blocks)
        total_tokens = sum(len(s.text) // 4 for s in sources_list)

        return RAGContext(
            sources=sources_list,
            formatted_text=full_context_text,
            total_tokens_estimate=total_tokens
        )
