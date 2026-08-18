"""
Merinos Industrial AI Internship - Day 25
Unified Merinos Document Chunking Engine

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from day25.mini_project.src.models import DocumentItem, ChunkItem
from day25.mini_project.src.fixed_chunker import FixedSizeChunker
from day25.mini_project.src.recursive_chunker import RecursiveCharacterChunker
from day25.mini_project.src.semantic_chunker import SemanticChunker
from day25.mini_project.src.markdown_chunker import MarkdownAwareChunker


class MerinosChunkEngine:
    """
    Tüm parçalama stratejilerini (Fixed-Size, Recursive, Semantic, Markdown-Aware)
    tek çatı altında yöneten, konfigürasyon odaklı birleşik metin parçalama motoru.
    """

    AVAILABLE_STRATEGIES = ["fixed_size", "recursive", "semantic", "markdown_aware"]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self._init_chunkers()

    @classmethod
    def from_config_file(cls, config_path: str | Path) -> "MerinosChunkEngine":
        """JSON konfigürasyon dosyasından motoru başlatır."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Konfigürasyon dosyası bulunamadı: {config_path}")
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return cls(cfg)

    def _default_config(self) -> Dict[str, Any]:
        """Varsayılan konfigürasyon sözlüğü."""
        return {
            "strategies": {
                "fixed_size": {"chunk_size": 350, "chunk_overlap": 70, "separator": " "},
                "recursive": {"chunk_size": 350, "chunk_overlap": 70, "separators": ["\n\n", "\n", ". ", " ", ""]},
                "semantic": {
                    "model_name": "all-MiniLM-L6-v2",
                    "similarity_threshold_percentile": 85.0,
                    "min_chunk_size": 120,
                    "max_chunk_size": 600
                },
                "markdown_aware": {
                    "headers_to_split_on": [["#", "H1"], ["##", "H2"], ["###", "H3"]],
                    "max_chunk_size": 450,
                    "chunk_overlap": 50
                }
            }
        }

    def _init_chunkers(self) -> None:
        """Tüm alt parçalama motorlarını konfigürasyona göre hazırlar."""
        strat_cfg = self.config.get("strategies", {})

        # 1. Fixed-Size
        f_cfg = strat_cfg.get("fixed_size", {})
        self.fixed_chunker = FixedSizeChunker(
            chunk_size=f_cfg.get("chunk_size", 350),
            chunk_overlap=f_cfg.get("chunk_overlap", 70),
            separator=f_cfg.get("separator", " ")
        )

        # 2. Recursive
        r_cfg = strat_cfg.get("recursive", {})
        self.recursive_chunker = RecursiveCharacterChunker(
            chunk_size=r_cfg.get("chunk_size", 350),
            chunk_overlap=r_cfg.get("chunk_overlap", 70),
            separators=r_cfg.get("separators", ["\n\n", "\n", ". ", " ", ""])
        )

        # 3. Semantic
        s_cfg = strat_cfg.get("semantic", {})
        self.semantic_chunker = SemanticChunker(
            model_name=s_cfg.get("model_name", "all-MiniLM-L6-v2"),
            similarity_threshold_percentile=s_cfg.get("similarity_threshold_percentile", 85.0),
            min_chunk_size=s_cfg.get("min_chunk_size", 120),
            max_chunk_size=s_cfg.get("max_chunk_size", 600)
        )

        # 4. Markdown-Aware
        m_cfg = strat_cfg.get("markdown_aware", {})
        self.markdown_chunker = MarkdownAwareChunker(
            max_chunk_size=m_cfg.get("max_chunk_size", 400)
        )

        self._chunkers_map = {
            "fixed_size": self.fixed_chunker,
            "recursive": self.recursive_chunker,
            "semantic": self.semantic_chunker,
            "markdown_aware": self.markdown_chunker
        }

    def chunk_document(self, doc: DocumentItem, strategy: str) -> List[ChunkItem]:
        """Belirtilen strateji ile tek bir dokümanı parçalar."""
        if strategy not in self._chunkers_map:
            raise ValueError(
                f"Bilinmeyen strateji: '{strategy}'. Geçerli seçenekler: {self.AVAILABLE_STRATEGIES}"
            )
        chunker = self._chunkers_map[strategy]
        return chunker.chunk_document(doc)

    def chunk_corpus(self, corpus: List[DocumentItem], strategy: str) -> List[ChunkItem]:
        """Belirtilen strateji ile tüm doküman koleksiyonunu parçalar."""
        if strategy not in self._chunkers_map:
            raise ValueError(
                f"Bilinmeyen strateji: '{strategy}'. Geçerli seçenekler: {self.AVAILABLE_STRATEGIES}"
            )
        all_chunks: List[ChunkItem] = []
        for doc in corpus:
            doc_chunks = self.chunk_document(doc, strategy)
            all_chunks.extend(doc_chunks)
        return all_chunks

    def chunk_all_strategies(self, corpus: List[DocumentItem]) -> Dict[str, List[ChunkItem]]:
        """Tüm koleksiyonu 4 stratejinin her biriyle parçalar ve sözlük olarak döner."""
        results: Dict[str, List[ChunkItem]] = {}
        for strat in self.AVAILABLE_STRATEGIES:
            results[strat] = self.chunk_corpus(corpus, strat)
        return results
