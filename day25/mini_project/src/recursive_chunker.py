"""
Merinos Industrial AI Internship - Day 25
Recursive Character Text Chunker

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Optional
from day25.mini_project.src.models import DocumentItem, ChunkItem


class RecursiveCharacterChunker:
    """
    Hiyerarşik ayırıcılar (\\n\\n, \\n, . , boşluk) kullanarak metni
    paragraf ve cümle bütünlüğünü bozmadan özyinelemeli parçalayan motor.
    """

    def __init__(
        self,
        chunk_size: int = 350,
        chunk_overlap: int = 70,
        separators: Optional[List[str]] = None
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size pozitif bir tam sayı olmalıdır.")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap, chunk_size değerinden küçük olmalıdır.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Metni verilen ayırıcı hiyerarşisine göre parçalar."""
        final_chunks: List[str] = []
        separator = separators[-1]
        new_separators = []

        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break

        splits = text.split(separator) if separator != "" else list(text)

        good_splits: List[str] = []
        for s in splits:
            if separator != "" and s:
                piece = s
            else:
                piece = s

            if len(piece) < self.chunk_size:
                good_splits.append(piece)
            else:
                if new_separators:
                    other_splits = self._split_text(piece, new_separators)
                    good_splits.extend(other_splits)
                else:
                    good_splits.append(piece)

        # Küçük parçaları chunk_size ve chunk_overlap dikkate alarak birleştir
        merged_chunks = self._merge_splits(good_splits, separator)
        return merged_chunks

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        """Ayrılmış küçük parçaları overlap ile birleştirir."""
        merged: List[str] = []
        current_doc: List[str] = []
        current_len = 0

        for piece in splits:
            piece_len = len(piece)
            sep_len = len(separator) if current_doc else 0

            if current_len + piece_len + sep_len > self.chunk_size:
                if current_doc:
                    chunk_text = separator.join(current_doc).strip()
                    if chunk_text:
                        merged.append(chunk_text)

                    # Overlap koruma: Geriye doğru parçaları tut
                    while current_doc and current_len > self.chunk_overlap:
                        removed = current_doc.pop(0)
                        current_len -= len(removed) + len(separator)

                current_doc.append(piece)
                current_len = sum(len(p) for p in current_doc) + len(separator) * (len(current_doc) - 1)
            else:
                current_doc.append(piece)
                current_len += piece_len + sep_len

        if current_doc:
            last_text = separator.join(current_doc).strip()
            if last_text:
                merged.append(last_text)

        return merged

    def chunk_document(self, doc: DocumentItem) -> List[ChunkItem]:
        """Dokümanı özyinelemeli olarak parçalar ve ChunkItem listesi üretir."""
        text = doc.content.strip()
        if not text:
            return []

        raw_chunks = self._split_text(text, self.separators)
        if not raw_chunks:
            return []

        total_chunks = len(raw_chunks)
        items: List[ChunkItem] = []
        search_start = 0

        for idx, chunk_text in enumerate(raw_chunks, start=1):
            # Karakter sınırlarını bul
            found_pos = text.find(chunk_text, search_start)
            if found_pos != -1:
                char_start = found_pos
                char_end = found_pos + len(chunk_text)
                # Overlap durumunda search_start geride kalabilir
                search_start = max(0, char_end - self.chunk_overlap)
            else:
                char_start = 0
                char_end = len(chunk_text)

            items.append(
                ChunkItem(
                    chunk_id=f"{doc.doc_id}_chunk_{idx:03d}",
                    doc_id=doc.doc_id,
                    title=doc.title,
                    category=doc.category,
                    content=chunk_text,
                    strategy="recursive",
                    chunk_index=idx,
                    total_chunks_in_doc=total_chunks,
                    char_start=char_start,
                    char_end=char_end,
                    char_length=len(chunk_text),
                    token_count=len(chunk_text.split()),
                    section_headers=[doc.title],
                    metadata=doc.metadata
                )
            )

        return items
