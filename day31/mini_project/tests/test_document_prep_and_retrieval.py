# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 31
Test Suite: Doküman Yükleyiciler (PDF/DOCX), Chunking, BM25 vs. Dense ve Auto-Sync
"""

import pytest
import os
import shutil
import tempfile
from pathlib import Path

from day31.mini_project.src.models import RawDocument, ChunkRecord
from day31.mini_project.src.text_cleaner import TextCleaner
from day31.mini_project.src.document_loaders import (
    PDFLoader,
    DocxLoader,
    TextLoader,
    UnifiedDocumentLoader,
    calculate_file_hash,
)
from day31.mini_project.src.chunker import (
    FixedSizeChunker,
    SemanticStructureChunker,
    ChunkingComparator,
)
from day31.mini_project.src.bm25_retriever import BM25Retriever, tokenize_technical
from day31.mini_project.src.dense_retriever import DenseRetriever
from day31.mini_project.src.retrieval_comparator import RetrievalComparator
from day31.mini_project.src.knowledge_manager import KnowledgeManager


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
DOCS_DIR = FIXTURES_DIR / "documents"


# =====================================================================
# 1. METİN TEMİZLEYİCİ TESTLERİ
# =====================================================================
class TestTextCleaner:
    def test_clean_hyphenation_and_blank_lines(self):
        raw = "Bu halı dokuma-\n   ları Hereke tipi-\n  dir.\n\n\n\nSon paragraf."
        cleaned = TextCleaner.clean(raw)
        assert "dokumaları" in cleaned
        assert "tipidir" in cleaned
        assert "\n\n\n" not in cleaned

    def test_extract_sections(self):
        text = """# 1. Tarak Ayarları
Bu bölüm tarak sıklığı hakkındadır.

## 2. Arıza Kodları
E-401 motor arızasıdır."""
        sections = TextCleaner.extract_sections(text)
        assert len(sections) >= 2
        titles = [s[0] for s in sections]
        assert any("Tarak Ayarları" in t for t in titles)
        assert any("Arıza Kodları" in t for t in titles)


# =====================================================================
# 2. DOKÜMAN YÜKLEYİCİ TESTLERİ (PDF, DOCX, TEXT)
# =====================================================================
class TestDocumentLoaders:
    def test_pdf_loader(self):
        pdf_path = DOCS_DIR / "merinos_weaving_sop.pdf"
        assert pdf_path.exists(), "Test PDF dosyası fixtures/documents içinde bulunmalı!"

        title, pages = PDFLoader.load(str(pdf_path))
        assert len(pages) >= 2, "PDF en az 2 sayfa olmalı!"
        assert pages[0][0] == 1
        assert pages[1][0] == 2
        # İçerik kontrolü
        full_text = " ".join(p[1] for p in pages)
        assert "28 teldir" in full_text
        assert "E-401" in full_text

    def test_docx_loader(self):
        docx_path = DOCS_DIR / "merinos_quality_standards.docx"
        assert docx_path.exists(), "Test DOCX dosyası fixtures/documents içinde bulunmalı!"

        title, pages = DocxLoader.load(str(docx_path))
        assert len(pages) >= 1
        full_text = " ".join(p[1] for p in pages)
        assert "14 bar" in full_text
        assert "vana 3" in full_text

    def test_unified_loader_directory(self):
        docs = UnifiedDocumentLoader.load_directory(str(DOCS_DIR))
        assert len(docs) >= 3, "PDF, DOCX ve MD olmak üzere en az 3 doküman yüklenmeli!"

        extensions = {d.file_type for d in docs}
        assert "pdf" in extensions
        assert "docx" in extensions
        assert "md" in extensions

        for d in docs:
            assert d.doc_id.startswith("DOC_")
            assert len(d.file_hash) == 64  # SHA-256
            assert d.total_char_count > 50


# =====================================================================
# 3. CHUNKING VE OVERLAP TESTLERİ (YAPRAK 61)
# =====================================================================
class TestChunkingStrategies:
    def test_fixed_size_chunker_overlap(self):
        doc = RawDocument(
            doc_id="DOC_TEST",
            filename="test.txt",
            file_type="txt",
            file_hash="dummy",
            title="Test Kılavuzu",
            pages=[(1, "Hereke serisi dokuma tezgahında tarak sıklığı cm başına 28 teldir. " * 15)]
        )
        chunker = FixedSizeChunker(chunk_size=200, chunk_overlap=50)
        chunks = chunker.chunk_document(doc)

        assert len(chunks) >= 3
        # Örtüşme (overlap) kontrolü: 1. parçanın son 40 karakteri 2. parçanın başında geçmeli
        for i in range(len(chunks) - 1):
            tail_snippet = chunks[i].text[-40:].strip()
            # Örtüşen kelimeler sonraki chunk'ta yer almalı
            tokens = tail_snippet.split()
            assert any(t in chunks[i + 1].text for t in tokens if len(t) > 4)

    def test_semantic_structure_chunker(self):
        doc = RawDocument(
            doc_id="DOC_SEM_TEST",
            filename="sem_test.md",
            file_type="md",
            file_hash="dummy",
            title="Semantik Test",
            pages=[(1, """# 1. Giriş
Bu sistem endüstriyel halı üretimi içindir.

## 2. Motor Bakımı
Motor fanları haftalık temizlenmelidir. Aksi halde aşırı ısınma meydana gelir.""")]
        )
        chunker = SemanticStructureChunker(max_chunk_size=300, min_chunk_size=50)
        chunks = chunker.chunk_document(doc)

        assert len(chunks) >= 2
        sections = [c.section for c in chunks]
        assert any("Giriş" in s for s in sections)
        assert any("Motor Bakımı" in s for s in sections)
        assert all("Semantik Test" in c.breadcrumbs for c in chunks)

    def test_chunking_comparator(self):
        docs = UnifiedDocumentLoader.load_directory(str(DOCS_DIR))
        comp_report = ChunkingComparator.compare(docs)

        assert "fixed_size_strategy" in comp_report
        assert "semantic_structure_strategy" in comp_report
        assert comp_report["total_documents_processed"] >= 3
        assert comp_report["fixed_size_strategy"]["stats"]["count"] > 0
        assert comp_report["semantic_structure_strategy"]["stats"]["count"] > 0


# =====================================================================
# 4. BM25 VE DENSE ARAMA MOTORLARI TESTLERİ (YAPRAK 62)
# =====================================================================
class TestRetrievalEngines:
    @pytest.fixture(scope="class")
    def indexed_chunks(self):
        docs = UnifiedDocumentLoader.load_directory(str(DOCS_DIR))
        chunker = SemanticStructureChunker(max_chunk_size=400, min_chunk_size=60)
        chunks = []
        for d in docs:
            chunks.extend(chunker.chunk_document(d))
        return chunks

    def test_bm25_exact_keyword_search(self, indexed_chunks):
        bm25 = BM25Retriever(k1=1.5, b=0.75)
        bm25.index(indexed_chunks)

        # 1. E-401 arıza kodu sorgusu
        res = bm25.search("E-401 arıza kodu", top_k=3, query_type="exact")
        assert len(res.items) > 0
        assert res.items[0].doc_id == "DOC_MERINOS_WEAVING_SOP"
        assert "E-401" in res.items[0].text_snippet

        # 2. 14 bar tansiyon sorgusu
        res2 = bm25.search("14 bar tansiyon", top_k=3, query_type="exact")
        assert len(res2.items) > 0
        assert res2.items[0].doc_id == "DOC_MERINOS_QUALITY_STANDARDS"

    def test_dense_semantic_search(self, indexed_chunks):
        dense = DenseRetriever(model_name="all-MiniLM-L6-v2")
        dense.index(indexed_chunks)

        # Semantik sorgu: kelimeler farklı olsa dahi kavramsal olarak bulmalı
        query = "tezgahta aşırı ısınma meydana gelirse motor için ne yapılmalı"
        res = dense.search(query, top_k=3, query_type="semantic")

        assert len(res.items) > 0
        # En az bir weaving SOP parçası ilk 3'te olmalı
        top_doc_ids = [item.doc_id for item in res.items]
        assert "DOC_MERINOS_WEAVING_SOP" in top_doc_ids

    def test_retrieval_comparator(self, indexed_chunks):
        bm25 = BM25Retriever()
        bm25.index(indexed_chunks)
        dense = DenseRetriever()
        dense.index(indexed_chunks)

        comparator = RetrievalComparator(bm25, dense)
        c_res = comparator.compare_single_query(
            query="E-401 arıza kodu",
            query_type="exact",
            expected_doc_id="DOC_MERINOS_WEAVING_SOP"
        )
        assert c_res.bm25_top1_id != "YOK"
        assert c_res.dense_top1_id != "YOK"
        assert c_res.winner_method in ["bm25", "dense", "tie"]


# =====================================================================
# 5. KNOWLEDGE MANAGER VE AUTO-SYNC TESTİ (KULLANICI TALEBİ)
# =====================================================================
class TestKnowledgeManagerAutoSync:
    def test_auto_sync_lifecycle(self, tmp_path):
        # Geçici doküman dizini ve manifesto
        test_docs_dir = tmp_path / "documents"
        test_docs_dir.mkdir()
        test_manifest = tmp_path / "manifest.json"

        # 1. Başlangıçta 1 adet metin dosyası koy
        doc1 = test_docs_dir / "doc1.txt"
        doc1.write_text("Merinos Halı dokuma tarağı 28 teldir.", encoding="utf-8")

        mgr = KnowledgeManager(
            documents_dir=str(test_docs_dir),
            manifest_path=str(test_manifest),
            chunk_strategy="fixed"
        )

        # İlk senkronizasyon
        sync_res1 = mgr.sync()
        assert sync_res1["status"] == "synced"
        assert sync_res1["total_documents"] == 1
        assert sync_res1["total_chunks"] >= 1

        # 2. Değişiklik yokken tekrar sync çağrısı
        sync_res2 = mgr.sync()
        assert sync_res2["status"] == "unchanged"

        # 3. YENİ BELGE EKLEME (Kullanıcının tek PDF/Word ekleme senaryosu)
        doc2 = test_docs_dir / "doc2.txt"
        doc2.write_text("İplik tansiyonu 14 bar altına düşerse vana kapatılır.", encoding="utf-8")

        sync_res3 = mgr.sync()
        assert sync_res3["status"] == "synced"
        assert "doc2.txt" in sync_res3["changes"]["new"]
        assert sync_res3["total_documents"] == 2

        # Yeni eklenen belge anında aranabilir olmalı
        search_res = mgr.search("14 bar", method="bm25")
        assert len(search_res.items) > 0
        assert "14 bar" in search_res.items[0].text_snippet
