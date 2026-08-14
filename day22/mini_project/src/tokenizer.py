"""Industrial Turkish and technical text tokenizer for Sparse Retrieval."""

import re
from typing import Dict, List, Set


class MerinosTextTokenizer:
    """Merinos teknik dokümanları için Türkçe odaklı tokenizer."""

    TURKISH_LOWER_MAP = {
        ord("I"): "ı",
        ord("İ"): "i",
        ord("Ğ"): "ğ",
        ord("Ü"): "ü",
        ord("Ş"): "ş",
        ord("Ö"): "ö",
        ord("Ç"): "ç"
    }

    def __init__(
        self,
        stopwords: Set[str] = None,
        min_token_len: int = 2,
        lowercase: bool = True,
        remove_punct: bool = True,
        remove_punctuation: bool = None,
        remove_stopwords: bool = None,
        use_bigrams: bool = False
    ):
        self.stopwords = set(stopwords) if stopwords else set()
        if remove_stopwords is False:
            self.stopwords = set()
        self.min_token_len = min_token_len
        self.lowercase = lowercase
        self.remove_punct = remove_punctuation if remove_punctuation is not None else remove_punct
        self.use_bigrams = use_bigrams

    def turkish_lower(self, text: str) -> str:
        """Türkçe karakterlere duyarlı küçük harfe çevirme."""
        if not text:
            return ""
        return text.translate(self.TURKISH_LOWER_MAP).lower()

    def tokenize(self, text: str) -> List[str]:
        """Metni tokenlara ayırır."""
        if not text:
            return []

        if self.lowercase:
            text = self.turkish_lower(text)

        if self.remove_punct:
            text = re.sub(r"[^\w\s\-\/]", " ", text, flags=re.UNICODE)
            text = text.replace("-", " ").replace("/", " ")

        raw_tokens = text.split()
        tokens: List[str] = []
        for t in raw_tokens:
            t = t.strip()
            if len(t) >= self.min_token_len and t not in self.stopwords:
                tokens.append(t)

        if not self.use_bigrams:
            return tokens

        bigrams = [
            f"{tokens[i]}_{tokens[i+1]}"
            for i in range(len(tokens) - 1)
        ]
        return tokens + bigrams

    def get_term_frequencies(self, tokens: List[str]) -> Dict[str, int]:
        """Counts frequency of each token in tokenized list."""
        freqs: Dict[str, int] = {}
        for t in tokens:
            freqs[t] = freqs.get(t, 0) + 1
        return freqs


# Standart ve geriye dönük uyumluluk takma adı
TurkishTokenizer = MerinosTextTokenizer
