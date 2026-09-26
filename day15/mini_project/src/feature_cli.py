"""
Merinos Halı Sanayi ve Ticaret A.Ş. — Day 14
Geleneksel Öznitelik Çıkarımı ve Jakarlı Halı Desen Sınıflandırma CLI Aracı

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Özel Lisans — Tüm Hakları Saklıdır.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Tuple
import cv2
import numpy as np

from .benchmark import FeatureBenchmarkEngine
from .color_histogram import ColorHistogramEngine
from .feature_fusion import CarpetPatternClassifierAndMatcher
from .generator import CarpetPatternFixtureGenerator, _safe_imread, _safe_imwrite
from .glcm_engine import GLCMFeatureEngine
from .keypoint_engine import KeypointFeatureEngine
from .models import (
    KeypointDescriptorType,
    PatternClass,
)


def cmd_generate_fixtures(args: argparse.Namespace):
    """Sentetik halı fikstürlerini üretir."""
    output_dir = Path(args.output_dir)
    gen = CarpetPatternFixtureGenerator(seed=42)
    paths = gen.generate_all_fixtures(output_dir)

    print(f"[OK] {len(paths)} adet sentetik halı fikstürü başarıyla üretildi:")
    for cls_name, p in paths.items():
        print(f"  - {cls_name:<22} -> {p.resolve()}")


def cmd_extract(args: argparse.Namespace):
    """Görüntüden öznitelikleri çıkarır ve özetler."""
    img_path = Path(args.image)
    image = _safe_imread(img_path)
    if image is None:
        print(f"[HATA] Görsel okunamadı: {img_path}")
        return

    kp_engine = KeypointFeatureEngine()
    glcm_engine = GLCMFeatureEngine()
    color_engine = ColorHistogramEngine()
    matcher = CarpetPatternClassifierAndMatcher()

    method = KeypointDescriptorType(args.keypoint_type)
    if method == KeypointDescriptorType.SIFT:
        kpts, _, kp_stats = kp_engine.extract_sift(image)
    else:
        kpts, _, kp_stats = kp_engine.extract_orb(image)

    glcm_feats = glcm_engine.extract_features(image)
    _, color_feats = color_engine.compute_histogram(image)
    fused_model = matcher.build_feature_vector(image, image_name=img_path.name, keypoint_type=method)

    print("\n" + "=" * 55)
    print(f"ÖZNİTELİK ÇIKARIM ÖZETİ: {img_path.name}")
    print("=" * 55)
    print(f"[1] Anahtar Nokta ({method.value}):")
    print(f"  - Tespit Edilen Nokta Sayısı: {kp_stats.count}")
    print(f"  - Ortalama Tepki (Response):   {kp_stats.mean_response}")
    print(f"  - Açı Entropisi (Rotasyon):   {kp_stats.angle_entropy}")
    print(f"[2] GLCM Haralick Doku:")
    print(f"  - Kontrast:      {glcm_feats.contrast}")
    print(f"  - Homojenlik:    {glcm_feats.homogeneity}")
    print(f"  - Enerji (ASM):  {glcm_feats.energy}")
    print(f"  - Korelasyon:    {glcm_feats.correlation}")
    print(f"  - Doku Entropi:  {glcm_feats.entropy}")
    print(f"[3] 3D Renk Histogramı (HSV):")
    print(f"  - Toplam Bin:    {color_feats.dimension}")
    print(f"  - Renk Entropisi:{color_feats.entropy}")
    print(f"  - Zirve Bin %:   %{color_feats.peak_bin_value * 100:.2f}")
    print(f"[4] Birleştirilmiş (Fused) Vektör Boyutu: {fused_model.total_dimension}")
    print("=" * 55 + "\n")

    if args.output_json:
        out_p = Path(args.output_json)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            f.write(fused_model.model_dump_json(indent=2))
        print(f"[+] Öznitelik vektörü JSON kaydedildi: {out_p.resolve()}")


def cmd_match(args: argparse.Namespace):
    """İki halı görseli arasındaki anahtar nokta eşleşmelerini analiz eder."""
    p1 = Path(args.image1)
    p2 = Path(args.image2)
    img1 = _safe_imread(p1)
    img2 = _safe_imread(p2)

    if img1 is None or img2 is None:
        print("[HATA] Görsellerden biri veya her ikisi okunamadı.")
        return

    kp_engine = KeypointFeatureEngine()
    method = KeypointDescriptorType(args.method)

    if method == KeypointDescriptorType.SIFT:
        kpts1, desc1, _ = kp_engine.extract_sift(img1)
        kpts2, desc2, _ = kp_engine.extract_sift(img2)
    else:
        kpts1, desc1, _ = kp_engine.extract_orb(img1)
        kpts2, desc2, _ = kp_engine.extract_orb(img2)

    good_matches = kp_engine.match_features(desc1, desc2, method=method)
    H, inlier_ratio = kp_engine.compute_homography_inliers(kpts1, kpts2, good_matches)

    print("\n" + "=" * 50)
    print("ANAHTAR NOKTA EŞLEŞTİRME ANALİZİ")
    print("=" * 50)
    print(f"  - Metod:                {method.value}")
    print(f"  - Görsel 1 Nokta:       {len(kpts1)}")
    print(f"  - Görsel 2 Nokta:       {len(kpts2)}")
    print(f"  - İyi Eşleşme (Lowe):   {len(good_matches)}")
    print(f"  - RANSAC Inlier Oranı:  %{inlier_ratio * 100:.1f}")
    print(f"  - Geometri Uyumlu (H):  {'EVET' if H is not None else 'HAYIR'}")
    print("=" * 50 + "\n")

    if args.output_vis:
        vis_p = Path(args.output_vis)
        vis = kp_engine.draw_matches(img1, kpts1, img2, kpts2, good_matches)
        _safe_imwrite(vis_p, vis)
        print(f"[+] Eşleşme görseli kaydedildi: {vis_p.resolve()}")


def cmd_classify(args: argparse.Namespace):
    """Sorgu halısını katalogda arar ve desen sınıfını tahmin eder."""
    q_path = Path(args.query)
    query_img = _safe_imread(q_path)
    if query_img is None:
        print(f"[HATA] Sorgu görseli okunamadı: {q_path}")
        return

    cat_dir = Path(args.catalog_dir)
    if not cat_dir.exists():
        print(f"[*] Katalog dizini bulunamadı, sentetik fikstürler üretiliyor: {cat_dir}")
        CarpetPatternFixtureGenerator(seed=42).generate_all_fixtures(cat_dir)

    # Katalog görsellerini yükle
    catalog_items: Dict[str, Tuple[np.ndarray, PatternClass]] = {}
    class_mapping = {
        "medallion": PatternClass.MEDALLION_CLASSIC,
        "geometric": PatternClass.GEOMETRIC_MODERN,
        "floral": PatternClass.FLORAL_TRADITIONAL,
        "vintage": PatternClass.VINTAGE_DISTRESSED,
    }

    for f in cat_dir.glob("*.png"):
        img = _safe_imread(f)
        if img is not None:
            name_lower = f.stem.lower()
            p_class = PatternClass.MEDALLION_CLASSIC
            for key, cls_val in class_mapping.items():
                if key in name_lower:
                    p_class = cls_val
                    break
            catalog_items[f.stem] = (img, p_class)

    matcher = CarpetPatternClassifierAndMatcher()
    matcher.index_catalog(catalog_items, keypoint_type=KeypointDescriptorType.ORB)

    # Top-K Benzerlik ve Sınıflandırma
    top_matches = matcher.find_top_k_similar(query_img, query_name=q_path.stem, k=args.top_k)
    best_class, confidence = matcher.classify_pattern(query_img, k=args.top_k)

    print("\n" + "=" * 60)
    print(f"HALI DESEN SINIFLANDIRMA VE RETRIEVAL SONUCU: {q_path.name}")
    print("=" * 60)
    print(f"  -> TAHMİN EDİLEN SINIF:  {best_class.value}")
    print(f"  -> GÜVEN SKORU:          %{confidence:.1f}")
    print("-" * 60)
    print(f"{'Sıra':<5} | {'Katalog Halısı':<25} | {'Sınıf':<20} | {'Benzerlik'}")
    print("-" * 60)
    for i, res in enumerate(top_matches, start=1):
        print(f"{i:<5} | {res.catalog_name:<25} | {res.predicted_class.value:<20} | %{res.similarity_score:.1f}")
    print("=" * 60 + "\n")


def cmd_benchmark(args: argparse.Namespace):
    """Öznitelik çıkarımı ve görsel arama kıyaslama testini yürütür."""
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    engine = FeatureBenchmarkEngine()
    report, catalog_images = engine.run_benchmark(iterations=10)

    print("\n" + "=" * 65)
    print("Merinos Halı — Day 14 Geleneksel Öznitelik Benchmark Raporu")
    print("=" * 65)
    print(f"{'Öznitelik Modülü':<22} | {'Süre (ms)':<12} | {'Throughput':<15}")
    print("-" * 65)
    print(f"{'ORB Anahtar Nokta':<22} | {report.orb_latency_ms:<12.3f} | {report.orb_fps:.1f} FPS")
    print(f"{'SIFT Anahtar Nokta':<22} | {report.sift_latency_ms:<12.3f} | {report.sift_fps:.1f} FPS")
    print(f"{'GLCM Haralick Doku':<22} | {report.glcm_latency_ms:<12.3f} | {report.glcm_fps:.1f} FPS")
    print(f"{'Katalog Arama (Top-K)':<22} | {report.retrieval_latency_ms:<12.3f} | -")
    print("-" * 65)
    print(f"4 Sınıflı Desen Doğruluğu: %{report.classification_accuracy:.1f}")
    print("=" * 65)

    # JSON ve Panel Kaydet
    json_path = out_dir / "retrieval_benchmark.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))
    print(f"[+] Benchmark JSON kaydedildi: {json_path.resolve()}")

    panel = engine.create_feature_summary_panel(catalog_images)
    panel_path = out_dir / "feature_summary_panel.png"
    _safe_imwrite(panel_path, panel)
    print(f"[+] Öznitelik paneli kaydedildi: {panel_path.resolve()}")

    # Özet Markdown
    md_path = out_dir / "feature_summary.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Day 14 Öznitelik Çıkarımı ve Desen Sınıflandırma Özeti\n\n")
        f.write(f"- **ORB Hızı:** {report.orb_latency_ms:.2f} ms ({report.orb_fps:.0f} FPS)\n")
        f.write(f"- **SIFT Hızı:** {report.sift_latency_ms:.2f} ms ({report.sift_fps:.0f} FPS)\n")
        f.write(f"- **GLCM Hızı:** {report.glcm_latency_ms:.2f} ms ({report.glcm_fps:.0f} FPS)\n")
        f.write(f"- **Sınıflandırma Başarısı:** %{report.classification_accuracy:.1f}\n")
    print(f"[+] Özet Markdown kaydedildi: {md_path.resolve()}\n")


def main():
    parser = argparse.ArgumentParser(description="Merinos Halı — Day 14 Geleneksel Öznitelik Çıkarımı CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. generate-fixtures
    p_gen = subparsers.add_parser("generate-fixtures", help="Sentetik halı desen fikstürlerini üretir")
    p_gen.add_argument("--output-dir", default="day14/mini_project/fixtures/synthetic_carpets")

    # 2. extract
    p_ext = subparsers.add_parser("extract", help="Halı görselinden öznitelikleri çıkarır")
    p_ext.add_argument("--image", required=True, help="Halı görsel yolu")
    p_ext.add_argument("--keypoint-type", default="ORB", choices=["ORB", "SIFT"])
    p_ext.add_argument("--output-json", help="Öznitelik JSON çıktı yolu")

    # 3. match
    p_match = subparsers.add_parser("match", help="İki halı arasında anahtar nokta eşleştirmesi yapar")
    p_match.add_argument("--image1", required=True, help="Birinci halı görsel yolu")
    p_match.add_argument("--image2", required=True, help="İkinci halı görsel yolu")
    p_match.add_argument("--method", default="ORB", choices=["ORB", "SIFT"])
    p_match.add_argument("--output-vis", help="Eşleşme paneli görsel çıktı yolu")

    # 4. classify
    p_clf = subparsers.add_parser("classify", help="Sorgu halısını katalogda arar ve sınıflandırır")
    p_clf.add_argument("--query", required=True, help="Sorgu görsel yolu")
    p_clf.add_argument("--catalog-dir", default="day14/mini_project/fixtures/synthetic_carpets")
    p_clf.add_argument("--top-k", type=int, default=3)

    # 5. benchmark
    p_bm = subparsers.add_parser("benchmark", help="Hız ve sınıflandırma benchmark testini çalıştırır")
    p_bm.add_argument("--output-dir", default="day14/mini_project/outputs")

    args = parser.parse_args()

    dispatch = {
        "generate-fixtures": cmd_generate_fixtures,
        "extract": cmd_extract,
        "match": cmd_match,
        "classify": cmd_classify,
        "benchmark": cmd_benchmark,
    }

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
