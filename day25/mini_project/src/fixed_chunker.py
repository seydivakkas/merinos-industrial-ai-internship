from typing import List, Dict, Any, Optional
import re
from day25.mini_project.src.models import DocumentItem, ChunkItem

class FixedSizeChunker:
    """
    Sabit karakter boyutuna göre doküman parçalayan basit ama
    etkili bir chunking stratejisi.
    """

    def __init__(self, chunk_size: int = 350, chunk_overlap: int = 70, separator: str = " ", **kwargs):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator

    @property
    def chunk_size(self) -> int:
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, val: int) -> None:
        if val <= 0:
            raise ValueError("chunk_size pozitif bir tam sayı olmalıdır.")
        self._chunk_size = val

    @property
    def chunk_overlap(self) -> int:
        return self._chunk_overlap

    @chunk_overlap.setter
    def chunk_overlap(self, val: int) -> None:
        if hasattr(self, "_chunk_size") and val >= self._chunk_size:
            raise ValueError("chunk_overlap, chunk_size değerinden küçük olmalıdır.")
        self._chunk_overlap = val

    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Verilen dokümanı sabit boyutlu parçalara böler.
        """
        text = document.get("content", "")
        doc_id = document.get("id", "unknown")
        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            chunk = {
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "text": chunk_text.strip(),
                "char_start": start,
                "char_end": end,
            }
            if chunk["text"]:
                chunks.append(chunk)
            if end >= len(text):
                break
            start += (self.chunk_size - self.chunk_overlap)
            chunk_id += 1

        if isinstance(document, DocumentItem) or hasattr(document, "category"):
            total = len(chunks)
            title = getattr(document, "title", doc_id)
            cat = getattr(document, "category", "DOKUMA_TEZGAHI_BAKIM")
            meta = getattr(document, "metadata", {})
            return [
                ChunkItem(
                    chunk_id=f"{doc_id}_chunk_{idx:03d}",
                    doc_id=doc_id,
                    title=title,
                    category=cat,
                    content=c["text"],
                    strategy="fixed_size",
                    chunk_index=idx,
                    total_chunks_in_doc=total,
                    char_start=c["char_start"],
                    char_end=c["char_end"],
                    char_length=len(c["text"]),
                    token_count=len(c["text"].split()),
                    section_headers=[title],
                    metadata=meta
                )
                for idx, c in enumerate(chunks, start=1)
            ]

        return chunks
