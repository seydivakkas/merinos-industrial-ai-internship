# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 31
Chunker: Sabit Boyutlu (Kayan Pencere) ve Anlamsal/Bölüm Bazlı Parçalama Stratejileri
Şekil 61: Sabit boyutlu parça (Fixed-Size) ve anlamsal yapı (Semantic-Structure) karşılaştırması
"""

import math
import re
from typing import List, Dict, Any, Union

from day31.mini_project.src.models import RawDocument, ChunkRecord
from day31.mini_project.src.text_cleaner import TextCleaner


class FixedSizeChunker:
    """
    Sabit boyutlu metin parçalama yöntemi.
    Belirtilen karakter sayısına göre metni parçalar.
    Şekil 61: Hem sözlük (Dict[str, Any]) hem de ham doküman (RawDocument) girdilerini destekler.
    """

    def __init__(self, chunk_size: int = 256, chunk_overlap: int = 32):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap, chunk_size'dan küçük olmalıdır!")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: Union[Dict[str, Any], RawDocument]) -> Union[List[Dict[str, Any]], List[ChunkRecord]]:
        """Verilen dokümanı sabit boyutlu parçalara ayırır."""
        # 1. Şekil 61 Standardı: Sözlük (Dict[str, Any]) girdisi
        if isinstance(document, dict):
            text = document.get("page_content", "")
            metadata = document.get("metadata", {})
            chunks: List[Dict[str, Any]] = []
            start = 0
            text_length = len(text)
            while start < text_length:
                end = min(start + self.chunk_size, text_length)
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunk = {
                        "text": chunk_text,
                        "metadata": {
                            **metadata,
                            "chunk_index": len(chunks),
                            "char_start": start,
                            "char_end": end,
                        },
                    }
                    chunks.append(chunk)
                if end >= text_length:
                    break
                start += self.chunk_size - self.chunk_overlap
            return chunks

        # 2. Pipeline / Test Standardı: RawDocument girdisi
        doc: RawDocument = document
        chunks_rec: List[ChunkRecord] = []
        step = self.chunk_size - self.chunk_overlap
        chunk_counter = 1

        for page_num, page_text in doc.pages:
            cleaned = TextCleaner.clean(page_text)
            if not cleaned:
                continue

            if len(cleaned) <= self.chunk_size:
                cid = f"{doc.doc_id}_c{chunk_counter:03d}"
                breadcrumbs = f"{doc.title} > Sayfa {page_num}"
                chunks_rec.append(ChunkRecord(
                    chunk_id=cid,
                    doc_id=doc.doc_id,
                    title=doc.title,
                    source=doc.filename,
                    page_number=page_num,
                    section="Genel",
                    breadcrumbs=breadcrumbs,
                    text=cleaned,
                    char_count=len(cleaned),
                    token_estimate=max(1, len(cleaned) // 4),
                    chunk_strategy="fixed"
                ))
                chunk_counter += 1
                continue

            start_idx = 0
            while start_idx < len(cleaned):
                end_idx = min(start_idx + self.chunk_size, len(cleaned))
                chunk_text = cleaned[start_idx:end_idx].strip()

                if chunk_text:
                    cid = f"{doc.doc_id}_c{chunk_counter:03d}"
                    breadcrumbs = f"{doc.title} > Sayfa {page_num} > [Karakter {start_idx}-{end_idx}]"
                    chunks_rec.append(ChunkRecord(
                        chunk_id=cid,
                        doc_id=doc.doc_id,
                        title=doc.title,
                        source=doc.filename,
                        page_number=page_num,
                        section=f"Sayfa {page_num}",
                        breadcrumbs=breadcrumbs,
                        text=chunk_text,
                        char_count=len(chunk_text),
                        token_estimate=max(1, len(chunk_text) // 4),
                        chunk_strategy="fixed"
                    ))
                    chunk_counter += 1

                if end_idx >= len(cleaned):
                    break
                start_idx += step

        return chunks_rec


class SemanticStructureChunker:
    """
    Başlık ve Paragraf Yapısını Koruyan Bölümleme (Semantic Chunking).
    Yaprak 61: Metnin anlamsal bütünlüğünü ve hiyerarşik bağlamını koruyan yaklaşım.
    """

    def __init__(self, max_chunk_size: int = 450, min_chunk_size: int = 80):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size

    def chunk_document(self, doc: RawDocument) -> List[ChunkRecord]:
        chunks: List[ChunkRecord] = []
        chunk_counter = 1

        for page_num, page_text in doc.pages:
            cleaned = TextCleaner.clean(page_text)
            if not cleaned:
                continue

            sections = TextCleaner.extract_sections(cleaned)

            for sec_title, sec_body in sections:
                paragraphs = [p.strip() for p in sec_body.split("\n\n") if p.strip()]

                buffer = ""
                for p in paragraphs:
                    if len(p) > self.max_chunk_size:
                        if buffer:
                            cid = f"{doc.doc_id}_c{chunk_counter:03d}"
                            breadcrumbs = f"{doc.title} > Sayfa {page_num} > {sec_title}"
                            chunks.append(ChunkRecord(
                                chunk_id=cid,
                                doc_id=doc.doc_id,
                                title=doc.title,
                                source=doc.filename,
                                page_number=page_num,
                                section=sec_title,
                                breadcrumbs=breadcrumbs,
                                text=buffer.strip(),
                                char_count=len(buffer.strip()),
                                token_estimate=max(1, len(buffer.strip()) // 4),
                                chunk_strategy="semantic"
                            ))
                            chunk_counter += 1
                            buffer = ""

                        sentences = p.replace(". ", ".\n").split("\n")
                        s_buffer = ""
                        for s in sentences:
                            if len(s_buffer) + len(s) + 1 <= self.max_chunk_size:
                                s_buffer = f"{s_buffer} {s}".strip()
                            else:
                                if s_buffer:
                                    cid = f"{doc.doc_id}_c{chunk_counter:03d}"
                                    breadcrumbs = f"{doc.title} > Sayfa {page_num} > {sec_title}"
                                    chunks.append(ChunkRecord(
                                        chunk_id=cid,
                                        doc_id=doc.doc_id,
                                        title=doc.title,
                                        source=doc.filename,
                                        page_number=page_num,
                                        section=sec_title,
                                        breadcrumbs=breadcrumbs,
                                        text=s_buffer,
                                        char_count=len(s_buffer),
                                        token_estimate=max(1, len(s_buffer) // 4),
                                        chunk_strategy="semantic"
                                    ))
                                    chunk_counter += 1
                                s_buffer = s
                        if s_buffer:
                            buffer = s_buffer

                    elif len(buffer) + len(p) + 2 <= self.max_chunk_size:
                        buffer = f"{buffer}\n\n{p}".strip() if buffer else p
                    else:
                        cid = f"{doc.doc_id}_c{chunk_counter:03d}"
                        breadcrumbs = f"{doc.title} > Sayfa {page_num} > {sec_title}"
                        chunks.append(ChunkRecord(
                            chunk_id=cid,
                            doc_id=doc.doc_id,
                            title=doc.title,
                            source=doc.filename,
                            page_number=page_num,
                            section=sec_title,
                            breadcrumbs=breadcrumbs,
                            text=buffer,
                            char_count=len(buffer),
                            token_estimate=max(1, len(buffer) // 4),
                            chunk_strategy="semantic"
                        ))
                        chunk_counter += 1
                        buffer = p

                if buffer:
                    cid = f"{doc.doc_id}_c{chunk_counter:03d}"
                    breadcrumbs = f"{doc.title} > Sayfa {page_num} > {sec_title}"
                    chunks.append(ChunkRecord(
                        chunk_id=cid,
                        doc_id=doc.doc_id,
                        title=doc.title,
                        source=doc.filename,
                        page_number=page_num,
                        section=sec_title,
                        breadcrumbs=breadcrumbs,
                        text=buffer,
                        char_count=len(buffer),
                        token_estimate=max(1, len(buffer) // 4),
                        chunk_strategy="semantic"
                    ))
                    chunk_counter += 1

        return chunks


class ChunkingComparator:
    """İki parçalama stratejisinin istatistiksel karşılaştırma motoru."""

    @staticmethod
    def compare(docs: List[RawDocument]) -> Dict[str, Any]:
        fixed_chunker = FixedSizeChunker(chunk_size=256, chunk_overlap=32)
        semantic_chunker = SemanticStructureChunker(max_chunk_size=450, min_chunk_size=80)

        fixed_chunks: List[ChunkRecord] = []
        semantic_chunks: List[ChunkRecord] = []

        for d in docs:
            fixed_chunks.extend(fixed_chunker.chunk_document(d))
            semantic_chunks.extend(semantic_chunker.chunk_document(d))

        def calc_stats(chunks: List[ChunkRecord]):
            if not chunks:
                return {"count": 0, "avg_len": 0, "min_len": 0, "max_len": 0, "std_dev": 0}
            lens = [c.char_count for c in chunks]
            avg = sum(lens) / len(lens)
            variance = sum((x - avg) ** 2 for x in lens) / len(lens)
            return {
                "count": len(chunks),
                "avg_char_length": round(avg, 1),
                "min_char_length": min(lens),
                "max_char_length": max(lens),
                "std_dev": round(math.sqrt(variance), 1),
                "total_tokens_est": sum(c.token_estimate for c in chunks)
            }

        fixed_stats = calc_stats(fixed_chunks)
        semantic_stats = calc_stats(semantic_chunks)

        return {
            "total_documents_processed": len(docs),
            "fixed_size_strategy": {
                "config": {"chunk_size": 256, "chunk_overlap": 32},
                "stats": fixed_stats
            },
            "semantic_structure_strategy": {
                "config": {"max_chunk_size": 450, "min_chunk_size": 80},
                "stats": semantic_stats
            },
            "engineering_insight": (
                "Sabit boyutlu parçalama (Fixed-Size) düzenli pencere uzunluğu ve overlap sayesinde "
                "sınır kayıplarını minimize eder; ancak cümleleri bölebilir. Anlamsal parçalama (Semantic) "
                "başlık ve paragraf bütünlüğünü korur; standart sapması daha yüksek fakat bağlam sadakati daha güçlüdür."
            )
        }
