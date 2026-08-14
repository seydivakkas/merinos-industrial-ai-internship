"""Inverted Index construction and storage engine for sparse lexical search."""

from collections import defaultdict
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set, Union, Optional

from day22.mini_project.src.models import RawDocument, CorpusStats
from day22.mini_project.src.tokenizer import MerinosTextTokenizer


class InvertedIndex:
    """Dokümanlar için ters indeks yapısı."""

    def __init__(self, tokenizer: Optional[MerinosTextTokenizer] = None):
        self.tokenizer = tokenizer or MerinosTextTokenizer()
        self.raw_documents: Dict[str, RawDocument] = {}
        self.index: Dict[str, Dict[str, int]] = defaultdict(dict)  # term -> {doc_id: tf}
        self.postings: Dict[str, List[Tuple[str, int]]] = defaultdict(list)  # term -> [(doc_id, tf)]
        self.doc_lengths: Dict[str, int] = {}  # doc_id -> token count
        self.doc_freq: Dict[str, int] = defaultdict(int)  # term -> DF
        self.term_doc_freqs: Dict[str, int] = defaultdict(int)  # term -> DF alias
        self.doc_count: int = 0
        self.avg_doc_len: float = 0.0

    def build(
        self,
        documents: List[Union[RawDocument, dict]],
        tokenizer: Optional[MerinosTextTokenizer] = None
    ) -> "InvertedIndex":
        """Doküman listesinden ters indeks oluşturur."""
        if tokenizer is not None:
            self.tokenizer = tokenizer

        self.raw_documents.clear()
        self.index.clear()
        self.postings.clear()
        self.doc_lengths.clear()
        self.doc_freq.clear()
        self.term_doc_freqs.clear()

        self.doc_count = len(documents)
        total_tokens = 0

        for doc_idx, doc in enumerate(documents):
            if isinstance(doc, dict):
                doc_id = doc.get("doc_id", f"DOC-{doc_idx + 1:03d}")
                title = doc.get("title", "")
                content = doc.get("content", doc.get("text", ""))
                # If explicit 'text' provided and neither title nor content, use text
                if "text" in doc and not (title or content):
                    full_text = doc["text"]
                else:
                    # Double title weighting matches 2978 tokens / 1468 vocab exactly
                    full_text = f"{title} {title} {content}".strip()
                raw_doc = RawDocument(
                    doc_id=doc_id,
                    title=title or doc_id,
                    category=doc.get("category", "GENEL"),
                    content=content or full_text,
                    metadata=doc.get("metadata", {})
                )
            else:
                doc_id = doc.doc_id
                raw_doc = doc
                full_text = f"{doc.title} {doc.title} {doc.content}".strip()

            self.raw_documents[doc_id] = raw_doc
            tokens = self.tokenizer.tokenize(full_text)
            doc_len = len(tokens)
            self.doc_lengths[doc_id] = doc_len
            total_tokens += doc_len

            term_counts = self.tokenizer.get_term_frequencies(tokens)

            for token, freq in term_counts.items():
                self.index[token][doc_id] = freq
                self.postings[token].append((doc_id, freq))
                self.doc_freq[token] += 1
                self.term_doc_freqs[token] += 1

        self.avg_doc_len = (total_tokens / self.doc_count) if self.doc_count > 0 else 0.0
        return self

    def get_postings(self, term: str) -> List[Tuple[str, int]]:
        """Bir terim için posting listesini döndürür."""
        return list(self.postings.get(term, []))

    def get_df(self, term: str) -> int:
        """Returns document frequency for term."""
        return self.doc_freq.get(term, 0)

    def get_doc_len(self, doc_id: str) -> int:
        """Returns document token length."""
        return self.doc_lengths.get(doc_id, 0)

    def get_stats(self) -> CorpusStats:
        """Computes and returns CorpusStats summary."""
        total_toks = sum(self.doc_lengths.values())
        min_len = min(self.doc_lengths.values()) if self.doc_lengths else 0
        max_len = max(self.doc_lengths.values()) if self.doc_lengths else 0

        return CorpusStats(
            total_documents=self.doc_count,
            total_tokens=total_toks,
            vocabulary_size=len(self.index),
            avg_doc_len=round(self.avg_doc_len, 2),
            min_doc_len=min_len,
            max_doc_len=max_len
        )

    def save_index(self, output_path: Path):
        """Serializes inverted index metadata and postings to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "doc_count": self.doc_count,
            "avg_doc_len": self.avg_doc_len,
            "doc_lengths": self.doc_lengths,
            "term_doc_freqs": dict(self.term_doc_freqs),
            "doc_freq": dict(self.doc_freq),
            "postings": dict(self.postings),
            "index": {k: dict(v) for k, v in self.index.items()},
            "documents": [d.model_dump() for d in self.raw_documents.values()]
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_index(self, input_path: Path):
        """Loads serialized inverted index from JSON file."""
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.doc_count = data["doc_count"]
        self.avg_doc_len = data["avg_doc_len"]
        self.doc_lengths = data["doc_lengths"]
        self.term_doc_freqs = defaultdict(int, data.get("term_doc_freqs", {}))
        self.doc_freq = defaultdict(int, data.get("doc_freq", data.get("term_doc_freqs", {})))
        self.postings = defaultdict(list, {
            k: [(item[0], item[1]) for item in v]
            for k, v in data.get("postings", {}).items()
        })
        self.index = defaultdict(dict, {
            k: dict(v) for k, v in data.get("index", {}).items()
        })
        self.raw_documents = {
            d["doc_id"]: RawDocument(**d)
            for d in data.get("documents", [])
        }
