"""
Merinos Industrial AI Internship - Day 04
pipeline.py: End-to-End Data Quality Pipeline Orchestrator
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
import json
import pandas as pd

from day04.mini_project.src.suite import ExpectationSuite, SuiteValidator, ValidationResult
from day04.mini_project.src.profiler import AutomatedDataProfiler


class DataQualityPipeline:
    """Orchestrates automated dataset ingestion, statistical profiling, and suite validation."""

    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        output_dir: Optional[Union[str, Path]] = None,
    ):
        base_dir = Path(__file__).resolve().parent.parent
        self.config_path = Path(config_path) if config_path else base_dir / "configs" / "expectation_suite_config.json"
        self.output_dir = Path(output_dir) if output_dir else base_dir / "outputs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.suite = ExpectationSuite.from_json(self.config_path)

    def load_data(self, input_path: Union[str, Path]) -> pd.DataFrame:
        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")

        if path.suffix.lower() == ".csv":
            return pd.read_csv(path)
        elif path.suffix.lower() == ".json":
            return pd.read_json(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}. Expected .csv or .json")

    def run(self, input_path: Union[str, Path]) -> Dict[str, Any]:
        df = self.load_data(input_path)
        total_rows = len(df)

        # 1. Automated Profiling
        profile_data = AutomatedDataProfiler.profile(df)

        # 2. Expectation Suite Validation
        val_result = SuiteValidator.validate(df, self.suite)
        val_dict = val_result.to_dict()

        # 3. Anomaly Isolation: Collect all failing row indices
        anomalous_indices: Set[int] = set()
        for exp in val_result.results:
            if not exp.success:
                unexpected_idx = exp.result.get("unexpected_index_list", [])
                anomalous_indices.update(unexpected_idx)

        anomalous_df = df.loc[sorted(list(anomalous_indices))] if anomalous_indices else pd.DataFrame(columns=df.columns)

        # 4. Composite Quality Score
        success_pct = val_result.statistics.get("success_percent", 0.0)
        summary = profile_data.get("dataset_summary", {})
        missing_pct = summary.get("overall_missing_percent", 0.0)
        dup_pct = summary.get("duplicate_percent", 0.0)

        # Formula: Success rate penalized by missingness and duplicates
        composite_score = round(max(0.0, (success_pct * (1.0 - (missing_pct / 100.0)) * (1.0 - (dup_pct / 100.0)))), 2)

        pipeline_summary = {
            "dataset_path": str(input_path),
            "total_records": total_rows,
            "anomalous_records_count": len(anomalous_df),
            "clean_records_count": total_rows - len(anomalous_df),
            "composite_quality_score": composite_score,
            "validation_success": val_result.success,
            "statistics": val_result.statistics,
        }

        # 5. Persist artifacts
        # Validation report
        val_report_path = self.output_dir / "validation_report.json"
        with open(val_report_path, "w", encoding="utf-8") as f:
            json.dump({**pipeline_summary, "validation_details": val_dict}, f, indent=2, ensure_ascii=False)

        # Data profile
        profile_path = self.output_dir / "data_profile.json"
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)

        # Interactive HTML Dashboard
        html_content = AutomatedDataProfiler.generate_html_report(profile_data, val_dict)
        html_path = self.output_dir / "data_quality_dashboard.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Anomalous records CSV
        anom_path = self.output_dir / "anomalous_records.csv"
        anomalous_df.to_csv(anom_path, index=False)

        return {
            "summary": pipeline_summary,
            "validation_report_path": str(val_report_path),
            "data_profile_path": str(profile_path),
            "dashboard_html_path": str(html_path),
            "anomalous_records_path": str(anom_path),
        }


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    clean_csv = base_dir / "fixtures" / "clean_production_data.csv"
    pipeline = DataQualityPipeline()
    res = pipeline.run(clean_csv)
    print("=" * 60)
    print("Merinos Day 04: Data Quality Pipeline Execution Complete")
    print(f"Dataset: {res['summary']['dataset_path']}")
    print(f"Records: {res['summary']['total_records']} (Anomalies: {res['summary']['anomalous_records_count']})")
    print(f"Validation Success: {res['summary']['validation_success']}")
    print(f"Composite Quality Score: %{res['summary']['composite_quality_score']}")
    print(f"Dashboard: {res['dashboard_html_path']}")
    print("=" * 60)
