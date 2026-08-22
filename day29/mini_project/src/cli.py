"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR
Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)

Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Kopyalanamaz, çoğaltılamaz, dağıtılamaz.

Merinos Halı Sanayi ve Ticaret A.Ş. — Endüstriyel Yapay Zekâ Stajı
Day 29: Çok Boyutlu Görsel Analiz Komut Satırı Arayüzü (CLI)
Staj Defteri Yaprak 57 ve 58 Müfredatı
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Windows konsolunda UTF-8 karakter desteğini garantiye al
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import cv2
import numpy as np

from day29.mini_project.src.master_analyzer import MasterCarpetAnalyzer
from day29.mini_project.src.color_analyzer import ColorPaletteAnalyzer
from day29.mini_project.src.symmetry_analyzer import StructuralSymmetryAnalyzer
from day29.mini_project.src.seam_analyzer import SeamContinuityAnalyzer
from day29.mini_project.src.embedding_retriever import CNNEmbeddingRetriever


def read_image_utf8(path: Path) -> np.ndarray:
    """Windows Türkçe karakterli dosya yollarında cv2.imread çökmesini önleyen ikili okuyucu."""
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if bgr is not None:
            return bgr
    except Exception:
        pass
    return cv2.imread(str(path))


def write_image_utf8(path: Path, img_bgr: np.ndarray) -> bool:
    """Windows Türkçe karakterli dosya yollarında cv2.imwrite çökmesini önleyen yazıcı."""
    success, encoded = cv2.imencode(".png", img_bgr)
    if success:
        with open(path, "wb") as f:
            f.write(encoded.tobytes())
        return True
    return False


def get_default_sample_image() -> Path:
    """Eğer kullanıcı görsel vermezse Day 28 çıktılarındaki veya test sentetik görselini kullanır."""
    workspace_root = Path(__file__).resolve().parent.parent.parent.parent
    day28_img = workspace_root / "day28" / "mini_project" / "outputs" / "seed_variations" / "BRF-CLS-01_seed_42.png"
    if day28_img.exists():
        return day28_img
    # Day 30 outputs fallback
    day30_img = workspace_root / "day30" / "mini_project" / "outputs" / "BRF-WEB-01_generated_carpet.png"
    if day30_img.exists():
        return day30_img
    # Sentetik üret ve kaydet
    fallback_path = workspace_root / "day29" / "mini_project" / "outputs" / "sample_carpet.png"
    fallback_path.parent.mkdir(parents=True, exist_ok=True)
    canvas = np.full((384, 256, 3), (139, 30, 30), dtype=np.uint8)  # Kırmızı zemin
    cv2.circle(canvas, (128, 192), 70, (245, 239, 235), -1)       # Krem göbek
    cv2.circle(canvas, (128, 192), 40, (212, 175, 55), 4)         # Altın varak halka
    write_image_utf8(fallback_path, cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR))
    return fallback_path


def main():
    parser = argparse.ArgumentParser(
        description="Merinos Halı Sanayi A.Ş. — Üretilen Görsellerin Analizi CLI (Day 29 / Yaprak 57-58)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. analyze-color
    p_color = subparsers.add_parser("analyze-color", help="K-Means Renk Paleti ve CIELAB Delta E analizi (Yaprak 57)")
    p_color.add_argument("--image", type=str, default=None, help="Görsel dosya yolu")
    p_color.add_argument("--clusters", type=int, default=5, help="K-Means küme sayısı (varsayılan: 5)")
    p_color.add_argument("--palette", type=str, default="PAL-OSMANLI-01", help="Hedef Merinos palet ID'si")

    # 2. analyze-symmetry
    p_sym = subparsers.add_parser("analyze-symmetry", help="Yatay/Dikey ayna simetrisi ve tekrar analizi (Yaprak 57)")
    p_sym.add_argument("--image", type=str, default=None, help="Görsel dosya yolu")

    # 3. analyze-seam
    p_seam = subparsers.add_parser("analyze-seam", help="Kenar ve dikiş sürekliliği analizi (Yaprak 58)")
    p_seam.add_argument("--image", type=str, default=None, help="Görsel dosya yolu")

    # 4. find-similar
    p_sim = subparsers.add_parser("find-similar", help="CNN Embedding ile Top-K benzer halı arama (Yaprak 58)")
    p_sim.add_argument("--image", type=str, default=None, help="Görsel dosya yolu")
    p_sim.add_argument("--top-k", type=int, default=3, help="Getirilecek en benzer halı sayısı (varsayılan: 3)")

    # 5. full-analysis
    p_full = subparsers.add_parser("full-analysis", help="Tüm analizleri uçtan uca çalıştırır ve 300 DPI panel üretir")
    p_full.add_argument("--image", type=str, default=None, help="Görsel dosya yolu")
    p_full.add_argument("--palette", type=str, default="PAL-OSMANLI-01", help="Hedef Merinos palet ID'si")
    p_full.add_argument("--top-k", type=int, default=3, help="Top-K benzerlik")

    args = parser.parse_args()

    # Görsel yolunu çöz
    img_path = Path(args.image) if args.image else get_default_sample_image()
    if not img_path.exists():
        print(f"HATA: Görsel dosyası bulunamadı: {img_path}", file=sys.stderr)
        sys.exit(1)

    bgr = read_image_utf8(img_path)
    if bgr is None:
        print(f"HATA: Görsel okunamadı: {img_path}", file=sys.stderr)
        sys.exit(1)
    image_rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    base_dir = Path(__file__).resolve().parent.parent
    fixtures_dir = base_dir / "fixtures"

    if args.command == "analyze-color":
        analyzer = ColorPaletteAnalyzer(target_palettes_path=fixtures_dir / "merinos_target_palettes.json")
        res = analyzer.analyze(image_rgb, num_clusters=args.clusters, target_palette_id=args.palette)
        print("=" * 65)
        print("🎨 K-MEANS RENK PALETİ VE CIELAB DELTA E* ANALİZİ (Yaprak 57)")
        print("=" * 65)
        print(f"İncelenen Görsel   : {img_path.name}")
        print(f"K-Means Küme Sayısı : {res.num_clusters}")
        print(f"Hedef Palet        : {res.target_palette_name}")
        print(f"Ortalama ΔE*       : {res.mean_delta_e}")
        print(f"En Yakın ΔE*       : {res.min_delta_e}")
        print("\nBaskın Renkler:")
        for c in res.dominant_colors:
            print(f"  • {c.hex_code} ({c.rgb}): %{c.percentage:5.1f} | LAB: {c.lab} | En Yakın: {c.nearest_yarn_name} (ΔE: {c.delta_e_to_target})")
        print(f"\nMühendislik Yorumu:\n{res.verdict}")

    elif args.command == "analyze-symmetry":
        analyzer = StructuralSymmetryAnalyzer()
        res = analyzer.analyze(image_rgb)
        print("=" * 65)
        print("🏛️ SİMETRİ VE TEKRAR YAPISI İNCELEMESİ (Yaprak 57)")
        print("=" * 65)
        print(f"İncelenen Görsel        : {img_path.name}")
        print(f"Yatay (Sol-Sağ) Simetri : %{res.horizontal_symmetry * 100:.1f}")
        print(f"Dikey (Üst-Alt) Simetri : %{res.vertical_symmetry * 100:.1f}")
        print(f"4-Çeyrek Saray Simetri  : %{res.four_way_symmetry * 100:.1f}")
        print(f"Periyodik Tekrar Skoru  : %{res.repeat_autocorrelation_score * 100:.1f}")
        print(f"\nMühendislik Yorumu:\n{res.verdict}")

    elif args.command == "analyze-seam":
        analyzer = SeamContinuityAnalyzer()
        res = analyzer.analyze(image_rgb)
        print("=" * 65)
        print("🧵 KENAR VE DİKİŞ SÜREKLİLİĞİ ANALİZİ (Yaprak 58)")
        print("=" * 65)
        print(f"İncelenen Görsel        : {img_path.name}")
        print(f"Sol-Sağ Kenar MSE       : {res.left_right_mse:.2f}")
        print(f"Üst-Alt Kenar MSE       : {res.top_bottom_mse:.2f}")
        print(f"Dikiş Süreklilik Skoru  : %{res.continuity_score * 100:.1f}")
        print(f"Belirgin Kopukluk Var mı: {'EVET' if res.has_seam_discontinuity else 'HAYIR'}")
        print(f"\nMühendislik Yorumu:\n{res.verdict}")

    elif args.command == "find-similar":
        retriever = CNNEmbeddingRetriever(catalog_path=fixtures_dir / "reference_carpet_catalog.json")
        res = retriever.analyze(image_rgb, top_k=args.top_k)
        print("=" * 65)
        print("🔍 PRETRAINED CNN EMBEDDING & TOP-K BENZERLİK ARAMASI (Yaprak 58)")
        print("=" * 65)
        print(f"İncelenen Görsel   : {img_path.name}")
        print(f"Kullanılan Omurga  : {res.backbone}")
        print(f"Embedding Boyutu   : {res.embedding_dim}")
        print(f"L2 Vektör Normu    : {res.l2_norm}")
        print("\nEn Çok Benzeyen Referans Halılar (Top-K):")
        for m in res.top_matches:
            print(f"  #{m.rank} [{m.similarity_score:.3f}] {m.title} ({m.style}) - Renkler: {', '.join(m.primary_colors)}")
        print(f"\nMühendislik Yorumu:\n{res.verdict}")

    elif args.command == "full-analysis":
        master = MasterCarpetAnalyzer()
        report = master.analyze(
            img_path,
            target_palette_id=args.palette,
            top_k=args.top_k,
            generate_panel=True
        )
        print("=" * 65)
        print("📊 TÜMLEŞİK GÖRSEL ANALİZ TAMAMLANDI (Yaprak 57 & 58)")
        print("=" * 65)
        print(f"Rapor ID         : {report.report_id}")
        print(f"Görsel Dosyası   : {report.image_path}")
        print(f"İşlem Süresi     : {report.execution_time_sec} saniye")
        print(f"300 DPI Teşhis   : {report.diagnostic_panel_path}")
        print(f"\n1. Renk Analizi  : Hedef={report.color_analysis.target_palette_name} | Ort. ΔE*={report.color_analysis.mean_delta_e}")
        print(f"2. Simetri       : Yatay=%{report.symmetry_analysis.horizontal_symmetry*100:.1f} | Dikey=%{report.symmetry_analysis.vertical_symmetry*100:.1f}")
        print(f"3. Dikiş/Kenar   : Süreklilik=%{report.seam_continuity.continuity_score*100:.1f} | Kopukluk={'VAR' if report.seam_continuity.has_seam_discontinuity else 'YOK'}")
        top1 = report.cnn_embedding.top_matches[0] if report.cnn_embedding.top_matches else None
        print(f"4. CNN Benzerlik : Top-1={top1.title if top1 else 'Yok'} (Skor: {top1.similarity_score if top1 else 0.0})")
        print(f"\nSentez Değerlendirmesi:\n{report.synthesis_verdict}")
        print("\nTeknik Sınırlar (Yaprak 58 & 60):")
        for lim in report.technical_limitations:
            print(f"  • {lim}")


if __name__ == "__main__":
    main()
