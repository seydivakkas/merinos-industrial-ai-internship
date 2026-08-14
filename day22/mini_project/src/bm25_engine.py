"""Probabilistic Okapi BM25 lexical ranking engine with length normalization."""

import math
from typing import Dict, List, Tuple
from day22.mini_project.src.inverted_index import InvertedIndex
from day22.mini_project.src.models import SearchResultItem, RawDocument
from day22.mini_project.src.tokenizer import MerinosTextTokenizer


class OkapiBM25Engine:
    """Okapi BM25 probabilistic retrieval engine with tunable k1 and b parameters."""

    def __init__(
        self,
        index: InvertedIndex = None,
        tokenizer: MerinosTextTokenizer = None,
        k1: float = 1.5,
        b: float = 0.75,
        epsilon: float = 0.25,
        inverted_index: InvertedIndex = None
    ):
        self.index = index or inverted_index
        self.tokenizer = tokenizer or getattr(self.index, "tokenizer", MerinosTextTokenizer())
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon
        self.idf_cache: Dict[str, float] = {}
        if self.index:
            self._precompute_idf()

    def index_corpus(self):
        """Precomputes BM25 IDF for all vocabulary terms."""
        if self.index:
            self._precompute_idf()

    def _precompute_idf(self):
        """Precomputes BM25 IDF for all vocabulary terms."""
        n = self.index.doc_count
        for term, df in self.index.term_doc_freqs.items():
            # Robertson-Spärck Jones IDF with +1 floor to guarantee non-negative values
            # IDF = ln((N - df + 0.5) / (df + 0.5) + 1)
            idf = math.log(((n - df + 0.5) / (df + 0.5)) + 1.0)
            self.idf_cache[term] = max(idf, self.epsilon)

    def get_term_idf(self, term: str) -> float:
        """Returns cached IDF score for term, or computes floor IDF for unseen term."""
        if term in self.idf_cache:
            return self.idf_cache[term]
        df = self.index.get_df(term)
        if df == 0:
            return 0.0
        n = self.index.doc_count
        idf = math.log(((n - df + 0.5) / (df + 0.5)) + 1.0)
        return max(idf, self.epsilon)

    def score_term_document(self, term: str, tf: int, doc_len: int) -> float:
        """Calculates single term-document BM25 score component."""
        if tf <= 0:
            return 0.0

        idf = self.get_term_idf(term)
        avgdl = self.index.avg_doc_len if self.index.avg_doc_len > 0 else 1.0
        len_norm = 1.0 - self.b + self.b * (doc_len / avgdl)
        tf_component = (tf * (self.k1 + 1.0)) / (tf + self.k1 * len_norm)

        return idf * tf_component

    def search(self, query: str, top_k: int = 5, snippet_max_len: int = 160) -> List[SearchResultItem]:
        """Calculates cumulative BM25 score across query terms and returns ranked Top-K items."""
        query_tokens = self.tokenizer.tokenize(query)
        if not query_tokens:
            return []

        doc_scores: Dict[str, float] = {}

        for term in set(query_tokens):
            idf = self.get_term_idf(term)
            if idf <= 0.0:
                continue

            postings = self.index.get_postings(term)
            avgdl = self.index.avg_doc_len if self.index.avg_doc_len > 0 else 1.0

            for doc_id, tf in postings:
                doc_len = self.index.get_doc_len(doc_id)
                len_norm = 1.0 - self.b + self.b * (doc_len / avgdl)
                tf_score = (tf * (self.k1 + 1.0)) / (tf + self.k1 * len_norm)

                doc_scores[doc_id] = doc_scores.get(doc_id, 0.0) + (idf * tf_score)

        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        top_results = sorted_docs[:top_k]

        results: List[SearchResultItem] = []
        for rank, (doc_id, score) in enumerate(top_results, 1):
            doc = self.index.raw_documents[doc_id]
            snippet = self._extract_snippet(doc.content, query_tokens, max_len=snippet_max_len)
            results.append(
                SearchResultItem(
                    doc_id=doc_id,
                    title=doc.title,
                    category=doc.category,
                    score=round(score, 4),
                    rank=rank,
                    snippet=snippet
                )
            )

        return results

    def _extract_snippet(self, text: str, query_tokens: List[str], max_len: int = 160) -> str:
        """Extracts contextual snippet containing the earliest matched query token."""
        lower_text = text.lower()
        earliest_idx = len(text)

        for t in query_tokens:
            idx = lower_text.find(t.lower())
            if 0 <= idx < earliest_idx:
                earliest_idx = idx

        if earliest_idx == len(text):
            return text[:max_len] + ("..." if len(text) > max_len else "")

        start = max(0, earliest_idx - 40)
        end = min(len(text), start + max_len)
        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        return snippet
