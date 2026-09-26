"""
Test Curriculum Alignment across all 40 Days.
Verifies that all 40 day directories, READMEs, standalone notebooks,
and mini_projects are present, properly named, and aligned with ROADMAP.md.
"""

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

OFFICIAL_DAYS = {
    1: "firma_ve_calisma_ortami",
    2: "veri_turleri_ve_modelleme",
    3: "problem_tanimi_ve_baseline",
    4: "python_ortami_ve_veri_sozlesmesi",
    5: "pandas_ve_veri_kalitesi",
    6: "numpy_vektorel_hesaplama",
    7: "uzaklik_ve_benzerlik",
    8: "kesifsel_veri_analizi",
    9: "opencv_temelleri",
    10: "renk_uzaylari_ve_farki",
    11: "kmeans_baskin_renk",
    12: "perspektif_ve_homografi",
    13: "morfoloji_ve_kenar",
    14: "klasik_segmentasyon",
    15: "gorsel_ozellik_entegrasyonu",
    16: "binary_classification",
    17: "multiclass_defect_classification",
    18: "decision_trees_and_random_forest",
    19: "gradient_boosting",
    20: "support_vector_machines",
    21: "unsupervised_learning",
    22: "sparse_retrieval",
    23: "dense_retrieval",
    24: "hybrid_retrieval",
    25: "document_chunking",
    26: "vector_database",
    27: "rag_retrieval_evaluation",
    28: "controlled_image_generation",
    29: "image_analysis_metrics",
    30: "integrated_generation_analysis",
    31: "document_prep_and_retrieval",
    32: "hybrid_retrieval_and_evaluation",
    33: "rag_and_attributed_generation",
    34: "reranking_and_cross_encoder",
    35: "query_transformation_and_hyde",
    36: "generation_prompting_and_citations",
    37: "evaluation_and_guardrails",
    38: "industrial_rag_api_and_ui",
    39: "model_compression_and_edge_deployment",
    40: "industrial_ai_platform_final"
}

def test_master_staj_defteri_exists():
    """Official 80-page staj defteri must exist and remain untouched."""
    defter_path = REPO_ROOT / "Merinos_40_Gun_80_Yaprak_Genislestirilmis_Staj_Defteri.md"
    assert defter_path.exists(), "Master staj defteri missing!"
    content = defter_path.read_text(encoding="utf-8")
    assert "**YAPRAK NO:** 1" in content
    assert "**YAPRAK NO:** 80" in content
    assert "## GÜN 40" in content

def test_roadmap_exists_and_covers_40_days():
    """ROADMAP.md must exist and list all 40 days."""
    roadmap_path = REPO_ROOT / "ROADMAP.md"
    assert roadmap_path.exists(), "ROADMAP.md missing!"
    content = roadmap_path.read_text(encoding="utf-8")
    for d in range(1, 41):
        assert f"Day {d:02d}:" in content, f"Day {d:02d} missing in ROADMAP.md"

@pytest.mark.parametrize("day_num", range(1, 41))
def test_day_directory_structure(day_num):
    """Each day from 01 to 40 must have day folder, README, notebook and mini_project."""
    day_folder = REPO_ROOT / f"day{day_num:02d}"
    assert day_folder.exists(), f"Directory {day_folder.name} missing!"

    # 1. Day README
    readme = day_folder / "README.md"
    assert readme.exists(), f"README.md missing in {day_folder.name}"

    # 2. Notebook
    notebooks = list(day_folder.glob("*.ipynb"))
    assert len(notebooks) >= 1, f"No .ipynb notebook found in {day_folder.name}"

    # 3. Mini Project structure
    mini_project = day_folder / "mini_project"
    assert mini_project.exists(), f"mini_project/ missing in {day_folder.name}"
    assert (mini_project / "src").exists(), f"mini_project/src missing in {day_folder.name}"
    assert (mini_project / "tests").exists(), f"mini_project/tests missing in {day_folder.name}"
