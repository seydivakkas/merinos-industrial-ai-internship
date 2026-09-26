"""
day03/mini_project/src/parsers.py
Heterojen endüstriyel veri kaynakları için hata toleranslı ayrıştırıcılar (parsers).
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ParserStats:
    """Ayrıştırıcı çalışma istatistikleri."""
    source_path: str
    total_raw_records: int = 0
    valid_records_count: int = 0
    malformed_records_count: int = 0
    quarantine_records: List[Dict[str, Any]] = field(default_factory=list)


class BaseDataSourceParser(ABC):
    """Tüm endüstriyel veri kaynakları için temel soyut sınıf."""

    def __init__(self, source_path: Union[str, Path]):
        self.source_path = Path(source_path)
        self.stats = ParserStats(source_path=str(self.source_path))

    @abstractmethod
    def parse(self) -> List[Dict[str, Any]]:
        """Kaynağı ayrıştırıp ham sözlükler listesi döndürür."""
        pass


class CsvDataSourceParser(BaseDataSourceParser):
    """
    Üretim logları ve tezgah verileri için CSV ayrıştırıcı.
    Eksik ve bozuk satırları sessizce atmak yerine karantinaya alır.
    """

    def __init__(
        self,
        source_path: Union[str, Path],
        required_columns: Optional[List[str]] = None,
        delimiter: str = ",",
        encoding: str = "utf-8"
    ):
        super().__init__(source_path)
        self.required_columns = required_columns or []
        self.delimiter = delimiter
        self.encoding = encoding

    def parse(self) -> List[Dict[str, Any]]:
        if not self.source_path.exists():
            raise FileNotFoundError(f"CSV kaynak dosyası bulunamadı: {self.source_path}")

        try:
            df = pd.read_csv(
                self.source_path,
                sep=self.delimiter,
                encoding=self.encoding,
                skipinitialspace=True
            )
        except Exception as e:
            logger.error(f"CSV okuma hatası: {e}")
            self.stats.malformed_records_count += 1
            self.stats.quarantine_records.append({
                "source": str(self.source_path),
                "error": str(e),
                "raw_data": None
            })
            return []

        self.stats.total_raw_records = len(df)
        valid_records: List[Dict[str, Any]] = []

        # Zorunlu sütun kontrolü
        missing_cols = set(self.required_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"CSV dosyasında zorunlu sütunlar eksik: {missing_cols}")

        for index, row in df.iterrows():
            record = row.to_dict()
            # NaN temizliği (None ile değiştirme)
            clean_record = {
                k: (None if pd.isna(v) else v)
                for k, v in record.items()
            }

            # Temel boş satır veya primary key yokluğu kontrolü
            pk_col = self.required_columns[0] if self.required_columns else None
            if pk_col and clean_record.get(pk_col) is None:
                self.stats.malformed_records_count += 1
                self.stats.quarantine_records.append({
                    "row_index": index,
                    "error": f"Birincil anahtar '{pk_col}' boş (null/NaN).",
                    "raw_data": clean_record
                })
                continue

            valid_records.append(clean_record)
            self.stats.valid_records_count += 1

        return valid_records


class JsonDataSourceParser(BaseDataSourceParser):
    """
    Desen katalogları ve tasarım şartnameleri için JSON/NDJSON ayrıştırıcı.
    """

    def __init__(self, source_path: Union[str, Path]):
        super().__init__(source_path)

    def parse(self) -> List[Dict[str, Any]]:
        if not self.source_path.exists():
            raise FileNotFoundError(f"JSON kaynak dosyası bulunamadı: {self.source_path}")

        try:
            content = self.source_path.read_text(encoding="utf-8").strip()
            if not content:
                return []

            if content.startswith("[") and content.endswith("]"):
                data = json.loads(content)
                if not isinstance(data, list):
                    data = [data]
            else:
                # Satır satır NDJSON denemesi
                data = []
                for line in content.splitlines():
                    line = line.strip()
                    if line:
                        data.append(json.loads(line))

        except Exception as e:
            logger.error(f"JSON okuma/parse hatası: {e}")
            self.stats.malformed_records_count += 1
            self.stats.quarantine_records.append({
                "source": str(self.source_path),
                "error": str(e),
                "raw_data": None
            })
            return []

        self.stats.total_raw_records = len(data)
        valid_records: List[Dict[str, Any]] = []

        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                self.stats.malformed_records_count += 1
                self.stats.quarantine_records.append({
                    "record_index": idx,
                    "error": "Kayıt bir sözlük (JSON object) değil.",
                    "raw_data": item
                })
                continue

            valid_records.append(item)
            self.stats.valid_records_count += 1

        return valid_records
