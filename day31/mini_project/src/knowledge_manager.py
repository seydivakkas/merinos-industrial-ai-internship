# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 31
Knowledge Manager: Dinamik PDF/Word Senkronizasyonu, Otomatik Güncelleme (Auto-Sync) ve İndeks Orkestrasyonu
"""

import json
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from day31.mini_project.src.models import RawDocument, ChunkRecord, IndexManifest
from day31.mini_project.src.document_loaders import UnifiedDocumentLoader, calculate_file_hash
from day31.mini_project.src.chunker import FixedSizeChunker, SemanticStructureChunker
from day31.mini_project.src.bm25_retriever import BM25Retriever
from day31.mini_project.src.dense_retriever import DenseRetriever
from day31.mini_project.src.retrieval_comparator import RetrievalComparator


class KnowledgeManager:
    """
    Belgeler dizinini izleyen, tek bir PDF/Word değişikliğinde sistemi
    otomatik güncelleyen ve retrieval motorlarını yöneten ana orkestratör.
    """

    def __init__(
        self,
        documents_dir: str,
        manifest_path: Optional[str] = None,
        chunk_strategy: str = "semantic",
        fixed_chunk_size: int = 256,
        fixed_chunk_overlap: int = 50,
        semantic_max_chunk_size: int = 450,
        semantic_min_chunk_size: int = 80,
        bm25_k1: float = 1.5,
        bm25_b: float = 0.75,
        dense_model_name: str = "all-MiniLM-L6-v2"
    ):
        self.documents_dir = Path(documents_dir)
        self.manifest_path = Path(manifest_path) if manifest_path else self.documents_dir.parent / "outputs" / "index_manifest.json"
        self.chunk_strategy = chunk_strategy

        # Parçalayıcılar
        self.fixed_chunker = FixedSizeChunker(chunk_size=fixed_chunk_size, chunk_overlap=fixed_chunk_overlap)
        self.semantic_chunker = SemanticStructureChunker(max_chunk_size=semantic_max_chunk_size, min_chunk_size=semantic_min_chunk_size)

        # Retrieval motorları
        self.bm25 = BM25Retriever(k1=bm25_k1, b=bm25_b)
        self.dense = DenseRetriever(model_name=dense_model_name)
        self.comparator = RetrievalComparator(self.bm25, self.dense)

        # Durum
        self.raw_documents: List[RawDocument] = []
        self.chunks: List[ChunkRecord] = []
        self.manifest: Optional[IndexManifest] = None

        self._load_manifest()

    def _load_manifest(self) -> None:
        """Kayıtlı manifestoyu yükler."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.manifest = IndexManifest(**data)
            except Exception:
                self.manifest = None

    def _save_manifest(self) -> None:
        """Mevcut dizin durumunu manifestoya kaydeder."""
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        doc_meta: Dict[str, Dict[str, Any]] = {}

        for doc in self.raw_documents:
            doc_chunks = [c for c in self.chunks if c.doc_id == doc.doc_id]
            doc_meta[doc.filename] = {
                "doc_id": doc.doc_id,
                "file_hash": doc.file_hash,
                "file_type": doc.file_type,
                "chunk_count": len(doc_chunks),
                "page_count": len(doc.pages),
                "total_char_count": doc.total_char_count,
            }

        self.manifest = IndexManifest(
            indexed_at=datetime.datetime.now().isoformat(),
            total_documents=len(self.raw_documents),
            total_chunks=len(self.chunks),
            documents=doc_meta
        )

        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.manifest.model_dump(), f, indent=2, ensure_ascii=False)

    def check_changes(self) -> Dict[str, List[str]]:
        """
        Dizindeki dosyaların SHA-256 hash'lerini mevcut manifesto ile kıyaslar.
        Dönüş: {'new': [...], 'modified': [...], 'deleted': [...], 'unchanged': [...]}
        """
        changes: Dict[str, List[str]] = {
            "new": [],
            "modified": [],
            "deleted": [],
            "unchanged": []
        }

        if not self.documents_dir.exists():
            return changes

        # Mevcut fiziksel dosyaları tara
        current_files: Dict[str, str] = {}
        for f in self.documents_dir.iterdir():
            if f.is_file() and f.suffix.lower() in UnifiedDocumentLoader.SUPPORTED_EXTENSIONS:
                current_files[f.name] = calculate_file_hash(str(f))

        old_docs = self.manifest.documents if self.manifest else {}

        # Yeni ve değişenleri bul
        for fname, fhash in current_files.items():
            if fname not in old_docs:
                changes["new"].append(fname)
            elif old_docs[fname]["file_hash"] != fhash:
                changes["modified"].append(fname)
            else:
                changes["unchanged"].append(fname)

        # Silinenleri bul
        for fname in old_docs:
            if fname not in current_files:
                changes["deleted"].append(fname)

        return changes

    def sync(self, force: bool = False) -> Dict[str, Any]:
        """
        Tek bir PDF/DOCX eklendiğinde veya değiştiğinde sistemi senkronize eder.
        Değişiklik varsa tüm belgeleri yeniden yükleyip parçalar ve indeksleri günceller.
        """
        changes = self.check_changes()
        has_changes = bool(changes["new"] or changes["modified"] or changes["deleted"])

        if not has_changes and not force and self.chunks:
            return {
                "status": "unchanged",
                "message": "Tüm belgeler güncel; indeksleme gerekmedi.",
                "changes": changes,
                "total_documents": len(self.raw_documents),
                "total_chunks": len(self.chunks)
            }

        # 1. Belgeleri yeniden yükle
        self.raw_documents = UnifiedDocumentLoader.load_directory(str(self.documents_dir))

        # 2. Chunking uygula
        all_chunks: List[ChunkRecord] = []
        for doc in self.raw_documents:
            if self.chunk_strategy == "fixed":
                all_chunks.extend(self.fixed_chunker.chunk_document(doc))
            else:
                all_chunks.extend(self.semantic_chunker.chunk_document(doc))

        self.chunks = all_chunks

        # 3. BM25 indeksle
        self.bm25.index(self.chunks)

        # 4. Dense vektör indeksle
        self.dense.index(self.chunks)

        # 5. Manifestoyu kaydet
        self._save_manifest()

        return {
            "status": "synced",
            "message": f"Bilgi tabanı senkronize edildi ({len(changes['new'])} yeni, {len(changes['modified'])} değiştirildi, {len(changes['deleted'])} silindi).",
            "changes": changes,
            "total_documents": len(self.raw_documents),
            "total_chunks": len(self.chunks),
            "chunk_strategy": self.chunk_strategy
        }

    def search(self, query: str, top_k: int = 5, method: str = "bm25", query_type: str = "exact"):
        """Seçilen arama yöntemiyle (bm25 veya dense) arama yapar."""
        if method == "dense":
            return self.dense.search(query, top_k=top_k, query_type=query_type)
        return self.bm25.search(query, top_k=top_k, query_type=query_type)

    def compare_query(self, query: str, query_type: str = "exact", expected_doc_id: Optional[str] = None):
        """Sorgu üzerinde BM25 vs. Dense karşılaştırması yapar."""
        return self.comparator.compare_single_query(query, query_type=query_type, expected_doc_id=expected_doc_id)
