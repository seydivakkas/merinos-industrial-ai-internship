"""
day03/mini_project/src/pipeline.py
Çok kaynaklı veri işleme, birleştirme (merge), normalizasyon ve kalite raporlama boru hattı.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# Ensure project root is in sys.path
_repo_root = Path(__file__).resolve().parents[3]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from day05.mini_project.src.normalizer import DataNormalizer
from day05.mini_project.src.parsers import CsvDataSourceParser, JsonDataSourceParser

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class DataIngestionPipeline:
    """
    Üretim logları CSV'si ile katalog JSON beslemelerini birleştiren,
    temizleyen, doğrulayan ve kalite raporu üreten ETL hattı.
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (
            Path(__file__).resolve().parent.parent / "configs" / "etl_pipeline_config.json"
        )
        self.config = self._load_config()
        self.normalizer = DataNormalizer()

    def _load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        return {}

    def run(
        self,
        csv_path: Path,
        json_path: Path,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Boru hattını baştan sona çalıştırır."""
        logger.info(f"Boru hattı başlatıldı. CSV: {csv_path.name}, JSON: {json_path.name}")

        # 1. Parse CSV
        csv_parser = CsvDataSourceParser(
            source_path=csv_path,
            required_columns=["product_id", "raw_width", "raw_length"]
        )
        csv_records = csv_parser.parse()

        # 2. Parse JSON
        json_parser = JsonDataSourceParser(source_path=json_path)
        json_records = json_parser.parse()

        logger.info(f"Ayrıştırılan kayıtlar: CSV={len(csv_records)}, JSON={len(json_records)}")

        # 3. İki kaynağı Pandas DataFrame üzerinde product_id ile birleştirme (Full Outer Join)
        df_csv = pd.DataFrame(csv_records)
        df_json = pd.DataFrame(json_records)

        # Standart ID sütunu oluşturma
        if not df_json.empty and "product_code" in df_json.columns and "product_id" not in df_json.columns:
            df_json["product_id"] = df_json["product_code"]

        if df_csv.empty and df_json.empty:
            merged_df = pd.DataFrame()
        elif df_csv.empty:
            merged_df = df_json
        elif df_json.empty:
            merged_df = df_csv
        else:
            merged_df = pd.merge(df_csv, df_json, on="product_id", how="outer", suffixes=("_csv", "_json"))

        logger.info(f"Birleştirilen toplam kayıt sayısı: {len(merged_df)}")

        # 4. Normalizasyon ve Doğrulama
        valid_products = []
        quarantine_records = []
        error_breakdown: Dict[str, int] = {}

        # Parsers'dan gelen ham hataları karantinaya ekle
        quarantine_records.extend(csv_parser.stats.quarantine_records)
        quarantine_records.extend(json_parser.stats.quarantine_records)

        for _, row in merged_df.iterrows():
            record_dict = row.dropna().to_dict()
            product, err = self.normalizer.process_record(record_dict)

            if product:
                valid_products.append(product)
            else:
                quarantine_records.append(err)
                err_type = err.get("error_type", "UnknownError")
                error_breakdown[err_type] = error_breakdown.get(err_type, 0) + 1

        total_inputs = len(csv_records) + len(json_records)
        valid_count = len(valid_products)
        quarantine_count = len(quarantine_records)
        validity_rate = round((valid_count / max(len(merged_df), 1)) * 100, 2)

        quality_report = {
            "pipeline_name": self.config.get("pipeline_name", "merinos_multisource_pipeline"),
            "total_csv_records": len(csv_records),
            "total_json_records": len(json_records),
            "merged_unique_records": len(merged_df),
            "valid_products_count": valid_count,
            "quarantine_records_count": quarantine_count,
            "data_quality_score_pct": validity_rate,
            "error_breakdown": error_breakdown,
            "status": "SUCCESS" if valid_count > 0 else "FAILED"
        }

        # 5. Çıktıları Kaydetme
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

            # Geçerli ürünler JSON
            products_json_path = output_dir / "normalized_products.json"
            products_data = [p.model_dump() for p in valid_products]
            products_json_path.write_text(
                json.dumps(products_data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            # Karantina JSON
            quarantine_path = output_dir / "quarantine_records.json"
            quarantine_path.write_text(
                json.dumps(quarantine_records, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8"
            )

            # Kalite Raporu JSON
            report_path = output_dir / "data_quality_report.json"
            report_path.write_text(
                json.dumps(quality_report, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            logger.info(f"Çıktılar kaydedildi: {output_dir}")

        return quality_report


def main():
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "fixtures" / "raw_production_logs.csv"
    json_path = base_dir / "fixtures" / "raw_catalog_feed.json"
    output_dir = base_dir / "outputs"

    pipeline = DataIngestionPipeline()
    report = pipeline.run(csv_path=csv_path, json_path=json_path, output_dir=output_dir)
    print("Boru Hattı Kalite Raporu:")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
