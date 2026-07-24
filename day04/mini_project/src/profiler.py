"""
Merinos Industrial AI Internship - Day 04
profiler.py: Automated Data Profiler and HTML Dashboard Generator
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


class AutomatedDataProfiler:
    """Computes comprehensive statistical profiles for tabular datasets and generates visual reports."""

    @staticmethod
    def profile(df: pd.DataFrame) -> Dict[str, Any]:
        total_rows = len(df)
        total_cols = len(df.columns)
        memory_usage_bytes = int(df.memory_usage(deep=True).sum())
        
        duplicate_rows = int(df.duplicated().sum())
        duplicate_percent = round((duplicate_rows / total_rows) * 100, 2) if total_rows > 0 else 0.0

        total_cells = total_rows * total_cols
        total_missing = int(df.isna().sum().sum())
        overall_missing_pct = round((total_missing / total_cells) * 100, 2) if total_cells > 0 else 0.0

        columns_profile: Dict[str, Any] = {}

        for col in df.columns:
            series = df[col]
            missing_count = int(series.isna().sum())
            missing_pct = round((missing_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
            non_null_count = total_rows - missing_count
            unique_count = int(series.nunique(dropna=True))
            unique_pct = round((unique_count / total_rows) * 100, 2) if total_rows > 0 else 0.0

            is_numeric = pd.api.types.is_numeric_dtype(series)

            col_meta: Dict[str, Any] = {
                "name": str(col),
                "dtype": str(series.dtype),
                "is_numeric": bool(is_numeric),
                "non_null_count": non_null_count,
                "missing_count": missing_count,
                "missing_percent": missing_pct,
                "unique_count": unique_count,
                "unique_percent": unique_pct,
            }

            if is_numeric and non_null_count > 0:
                valid_num = series.dropna().astype(float)
                col_meta["mean"] = round(float(valid_num.mean()), 3)
                col_meta["std"] = round(float(valid_num.std()), 3) if len(valid_num) > 1 else 0.0
                col_meta["min"] = round(float(valid_num.min()), 3)
                col_meta["q25"] = round(float(valid_num.quantile(0.25)), 3)
                col_meta["median"] = round(float(valid_num.median()), 3)
                col_meta["q75"] = round(float(valid_num.quantile(0.75)), 3)
                col_meta["max"] = round(float(valid_num.max()), 3)
                col_meta["skewness"] = round(float(valid_num.skew()), 3) if len(valid_num) > 2 else 0.0
                zeros = int((valid_num == 0).sum())
                col_meta["zeros_count"] = zeros
                col_meta["zeros_percent"] = round((zeros / total_rows) * 100, 2)
            else:
                str_series = series.dropna().astype(str)
                if len(str_series) > 0:
                    val_counts = str_series.value_counts(normalize=True).head(5)
                    top_values = [
                        {"value": str(idx), "percentage": round(float(val) * 100, 1)}
                        for idx, val in val_counts.items()
                    ]
                    lengths = str_series.str.len()
                    col_meta["top_values"] = top_values
                    col_meta["min_length"] = int(lengths.min())
                    col_meta["max_length"] = int(lengths.max())
                    col_meta["mean_length"] = round(float(lengths.mean()), 1)
                else:
                    col_meta["top_values"] = []
                    col_meta["min_length"] = 0
                    col_meta["max_length"] = 0
                    col_meta["mean_length"] = 0.0

            columns_profile[col] = col_meta

        return {
            "dataset_summary": {
                "total_rows": total_rows,
                "total_columns": total_cols,
                "memory_bytes": memory_usage_bytes,
                "memory_kb": round(memory_usage_bytes / 1024, 2),
                "duplicate_rows": duplicate_rows,
                "duplicate_percent": duplicate_percent,
                "total_cells": total_cells,
                "total_missing_cells": total_missing,
                "overall_missing_percent": overall_missing_pct,
            },
            "columns": columns_profile,
        }

    @staticmethod
    def generate_html_report(profile_data: Dict[str, Any], validation_result: Optional[Dict[str, Any]] = None) -> str:
        """Generates a standalone, modern single-page HTML report embedding profile stats & validation results."""
        summary = profile_data.get("dataset_summary", {})
        columns = profile_data.get("columns", {})

        val_stats = validation_result.get("statistics", {}) if validation_result else {}
        val_success_pct = val_stats.get("success_percent", 100.0)
        val_total = val_stats.get("evaluated_expectations", 0)
        val_passed = val_stats.get("successful_expectations", 0)
        val_failed = val_stats.get("unsuccessful_expectations", 0)

        # Build column rows
        col_rows = []
        for col_name, c in columns.items():
            dtype_badge = f'<span class="badge badge-info">{c["dtype"]}</span>'
            missing_bar = f'''
                <div class="progress-bar-wrap">
                    <div class="progress-bar-fill" style="width: {min(c["missing_percent"], 100)}%;"></div>
                    <span class="progress-text">{c["missing_count"]} ({c["missing_percent"]}%)</span>
                </div>
            '''
            
            if c.get("is_numeric"):
                stats_desc = f'Min: {c.get("min")} | Med: {c.get("median")} | Max: {c.get("max")} (Ort: {c.get("mean")})'
            else:
                top_v = ", ".join([f'{tv["value"]} ({tv["percentage"]}%)' for tv in c.get("top_values", [])[:3]])
                stats_desc = f'Top: {top_v}' if top_v else '-'

            col_rows.append(f"""
                <tr>
                    <td><strong>{col_name}</strong></td>
                    <td>{dtype_badge}</td>
                    <td>{c["unique_count"]} ({c["unique_percent"]}%)</td>
                    <td>{missing_bar}</td>
                    <td class="stats-cell">{stats_desc}</td>
                </tr>
            """)

        # Build validation expectation rows
        exp_rows = []
        if validation_result and "results" in validation_result:
            for exp in validation_result["results"]:
                exp_type = exp.get("expectation_type", "")
                status = exp.get("success", False)
                status_badge = '<span class="badge badge-pass">GEÇTİ (PASS)</span>' if status else '<span class="badge badge-fail">BAŞARISIZ (FAIL)</span>'
                kwargs_str = ", ".join([f"{k}={v}" for k, v in exp.get("kwargs", {}).items()])
                res_dict = exp.get("result", {})
                message = res_dict.get("message", "-")
                if not status and "partial_unexpected_list" in res_dict and res_dict["partial_unexpected_list"]:
                    message += f" Örnekler: {res_dict['partial_unexpected_list'][:3]}"

                exp_rows.append(f"""
                    <tr class="{'row-fail' if not status else ''}">
                        <td><code>{exp_type}</code></td>
                        <td><small>{kwargs_str}</small></td>
                        <td>{status_badge}</td>
                        <td><small>{message}</small></td>
                    </tr>
                """)
        else:
            exp_rows.append('<tr><td colspan="4" class="text-center">Doğrulama paketi çalıştırılmadı.</td></tr>')

        html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Merinos Endüstriyel Veri Kalitesi & Profil Paneli</title>
    <style>
        :root {{
            --bg-main: #0b0f19;
            --bg-card: #151d30;
            --bg-card-hover: #1c263f;
            --border-color: #24304f;
            --text-primary: #f1f5f9;
            --text-muted: #94a3b8;
            --accent-cyan: #06b6d4;
            --accent-emerald: #10b981;
            --accent-rose: #f43f5e;
            --accent-amber: #f59e0b;
            --accent-indigo: #6366f1;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }}
        body {{
            background-color: var(--bg-main);
            color: var(--text-primary);
            padding: 32px 24px;
            line-height: 1.5;
        }}
        .container {{
            max-width: 1300px;
            margin: 0 auto;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
            margin-bottom: 28px;
        }}
        .header-title h1 {{
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.5px;
            color: #fff;
        }}
        .header-title p {{
            color: var(--text-muted);
            font-size: 14px;
            margin-top: 4px;
        }}
        .brand-badge {{
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            color: #fff;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .grid-kpi {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        }}
        .kpi-label {{
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        .kpi-value {{
            font-size: 28px;
            font-weight: 800;
            margin: 8px 0;
            color: #fff;
        }}
        .kpi-sub {{
            font-size: 12px;
            color: var(--text-muted);
        }}
        .section-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 32px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        th {{
            text-align: left;
            padding: 12px 14px;
            background: #101626;
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border-color);
        }}
        td {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--border-color);
            color: #cbd5e1;
        }}
        tr:hover td {{
            background-color: var(--bg-card-hover);
        }}
        .row-fail td {{
            background: rgba(244, 63, 94, 0.08);
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
        }}
        .badge-info {{ background: #1e293b; color: #38bdf8; }}
        .badge-pass {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .badge-fail {{ background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }}
        .progress-bar-wrap {{
            position: relative;
            background: #202b46;
            height: 18px;
            border-radius: 9999px;
            overflow: hidden;
            min-width: 140px;
        }}
        .progress-bar-fill {{
            position: absolute;
            top: 0; left: 0; bottom: 0;
            background: var(--accent-rose);
            border-radius: 9999px;
        }}
        .progress-text {{
            position: relative;
            z-index: 2;
            font-size: 10px;
            font-weight: 600;
            line-height: 18px;
            padding-left: 8px;
            color: #fff;
        }}
        .stats-cell {{
            font-family: monospace;
            font-size: 12px;
            color: #93c5fd;
        }}
        code {{
            background: #0f172a;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: "Courier New", Courier, monospace;
            color: #e2e8f0;
        }}
        footer {{
            text-align: center;
            color: var(--text-muted);
            font-size: 12px;
            margin-top: 40px;
            border-top: 1px solid var(--border-color);
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-title">
                <h1>Merinos Endüstriyel Veri Kalitesi & Profil Paneli</h1>
                <p>Otomatik Şema Doğrulama, İstatistiksel Dağılım ve Anomali Tespit Raporu</p>
            </div>
            <div class="brand-badge">Day 04 — MLOps Data Quality</div>
        </header>

        <div class="grid-kpi">
            <div class="kpi-card">
                <span class="kpi-label">Toplam Satır (Rows)</span>
                <span class="kpi-value">{summary.get("total_rows", 0):,}</span>
                <span class="kpi-sub">{summary.get("total_columns", 0)} Sütun | {summary.get("memory_kb", 0)} KB Bellek</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">Kalite Kural Başarımı</span>
                <span class="kpi-value" style="color: {'#34d399' if val_success_pct >= 90 else '#fb7185'};">%{val_success_pct}</span>
                <span class="kpi-sub">{val_passed}/{val_total} Başarılı Kural</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">Eksik Veri Oranı</span>
                <span class="kpi-value" style="color: {'#34d399' if summary.get("overall_missing_percent", 0) == 0 else '#fb7185'};">%{summary.get("overall_missing_percent", 0)}</span>
                <span class="kpi-sub">{summary.get("total_missing_cells", 0)} Eksik Hücre</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">Mükerrer (Duplicate) Satır</span>
                <span class="kpi-value">{summary.get("duplicate_rows", 0)}</span>
                <span class="kpi-sub">Oran: %{summary.get("duplicate_percent", 0.0)}</span>
            </div>
        </div>

        <div class="section-card">
            <div class="section-title">
                <span>📋 Expectation Suite Doğrulama Sonuçları</span>
                <span style="font-size: 13px; font-weight: normal; color: var(--text-muted);">Paket: <code>{validation_result.get("suite_name", "N/A") if validation_result else "-"}</code></span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 25%;">Beklenti Kuralı</th>
                        <th style="width: 30%;">Parametreler</th>
                        <th style="width: 15%;">Durum</th>
                        <th style="width: 30%;">Sonuç / Hata Açıklaması</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(exp_rows)}
                </tbody>
            </table>
        </div>

        <div class="section-card">
            <div class="section-title">
                <span>📊 Sütun Bazlı İstatistiksel Profil</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 18%;">Sütun Adı</th>
                        <th style="width: 10%;">Veri Tipi</th>
                        <th style="width: 14%;">Tekil Değerler</th>
                        <th style="width: 22%;">Eksiklik Dağılımı</th>
                        <th style="width: 36%;">İstatistiksel Özet / Sık Değerler</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(col_rows)}
                </tbody>
            </table>
        </div>

        <footer>
            Merinos Endüstriyel Yapay Zeka Staj Portföyü — Day 04: Otomatik Veri Kalitesi Doğrulama ve Profilleme Hattı &copy; 2026 Seydi Eryılmaz
        </footer>
    </div>
</body>
</html>
        """
        return html
