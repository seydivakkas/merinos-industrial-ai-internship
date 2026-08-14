"""TF-IDF vector space lexical retrieval engine with cosine similarity scoring."""

import math
from typing import Dict, List, Tuple
from day22.mini_project.src.inverted_index import InvertedIndex
from day22.mini_project.src.models import SearchResultItem, RawDocument
from day22.mini_project.src.tokenizer import MerinosTextTokenizer


class TFIDFRetrievalEngine:
    """Vector Space Model (VSM) using sublinear TF-IDF weighting and L2 cosine normalization."""

    def __init__(
        self,
        index: InvertedIndex = None,
        tokenizer: MerinosTextTokenizer = None,
        sublinear_tf: bool = True,
        inverted_index: InvertedIndex = None
    ):
        self.index = index or inverted_index
        self.tokenizer = tokenizer or getattr(self.index, "tokenizer", MerinosTextTokenizer())
        self.sublinear_tf = sublinear_tf
        self.doc_l2_norms: Dict[str, float] = {}
        if self.index:
            self._compute_doc_norms()

    def index_corpus(self):
        """Precomputes L2 document norms across the corpus."""
        if self.index:
            self._compute_doc_norms()

    def _compute_idf(self, df: int) -> float:
        """Calculates smoothed inverse document frequency."""
        # IDF(t) = ln((1 + N) / (1 + df(t))) + 1
        n = self.index.doc_count
        return math.log((1.0 + n) / (1.0 + df)) + 1.0

    def _compute_tf(self, freq: int) -> float:
        """Calculates term frequency, optionally applying sublinear logarithmic scaling."""
        if freq <= 0:
            return 0.0
        if self.sublinear_tf:
            return 1.0 + math.log(freq)
        return float(freq)

    def _compute_doc_norms(self):
        """Precomputes L2 Euclidean norms for all documents in the index."""
        doc_sq_sums: Dict[str, float] = {doc_id: 0.0 for doc_id in self.index.raw_documents}

        for term, postings in self.index.postings.items():
            df = self.index.get_df(term)
            idf = self._compute_idf(df)
            for doc_id, tf_count in postings:
                tf_weight = self._compute_tf(tf_count)
                weight = tf_weight * idf
                doc_sq_sums[doc_id] += weight * weight

        for doc_id, sq_sum in doc_sq_sums.items():
            self.doc_l2_norms[doc_id] = math.sqrt(sq_sum) if sq_sum > 0 else 1.0

    def search(self, query: str, top_k: int = 5, snippet_max_len: int = 160) -> List[SearchResultItem]:
        """Scores documents against query using cosine similarity and returns top-K results."""
        query_tokens = self.tokenizer.tokenize(query)
        if not query_tokens:
            return []

        query_tf = self.tokenizer.get_term_frequencies(query_tokens)
        query_weights: Dict[str, float] = {}
        query_sq_sum = 0.0

        for term, count in query_tf.items():
            df = self.index.get_df(term)
            if df > 0:
                idf = self._compute_idf(df)
                q_tf = self._compute_tf(count)
                w_q = q_tf * idf
                query_weights[term] = w_q
                query_sq_sum += w_q * w_q

        query_norm = math.sqrt(query_sq_sum) if query_sq_sum > 0 else 1.0

        # Accumulate dot products
        scores: Dict[str, float] = {}
        for term, w_q in query_weights.items():
            postings = self.index.get_postings(term)
            df = self.index.get_df(term)
            idf = self._compute_idf(df)

            for doc_id, doc_tf_count in postings:
                w_d = self._compute_tf(doc_tf_count) * idf
                scores[doc_id] = scores.get(doc_id, 0.0) + (w_q * w_d)

        # Normalize by document L2 norm and query L2 norm (Cosine Similarity)
        cosine_scores: List[Tuple[str, float]] = []
        for doc_id, dot_prod in scores.items():
            doc_norm = self.doc_l2_norms.get(doc_id, 1.0)
            denom = query_norm * doc_norm
            cos_sim = (dot_prod / denom) if denom > 0 else 0.0
            cosine_scores.append((doc_id, cos_sim))

        cosine_scores.sort(key=lambda x: x[1], reverse=True)
        top_results = cosine_scores[:top_k]

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
