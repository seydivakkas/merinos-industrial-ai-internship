# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Merinos Doküman Üretici: Test ve Benchmark Amaçlı Gerçekçi PDF, Word ve Markdown Belgeleri
"""

import os
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def create_simple_pdf(filepath: str, pages_data: list):
    """
    Standart PDF 1.4 spesifikasyonuna uygun, pypdf tarafından
    kusursuz okunabilen çok sayfalı geçerli bir PDF üretir.
    """
    objects = []
    # obj 1: Catalog
    # obj 2: Pages
    
    # We will build objects dynamically
    page_objs = []
    content_objs = []
    font_obj_idx = 0
    
    # We'll construct standard raw PDF
    # First catalog and pages
    pdf_parts = []
    offsets = []
    
    pdf_header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    
    # We can write objects:
    # 1: Catalog -> Pages 2
    # 2: Pages -> Kids [3, 5, ...]
    # For each page:
    #   Page obj: Parent 2, Contents, Resources
    #   Content stream obj
    
    num_pages = len(pages_data)
    # Object indices:
    # 1: Catalog
    # 2: Pages
    # For i in 0..num_pages-1:
    #   Page i: 3 + 2*i
    #   Content i: 4 + 2*i
    # Font obj: 3 + 2*num_pages
    
    font_idx = 3 + 2 * num_pages
    kids_refs = " ".join([f"{3 + 2*i} 0 R" for i in range(num_pages)])
    
    obj_dict = {}
    obj_dict[1] = f"<< /Type /Catalog /Pages 2 0 R >>".encode("latin1")
    obj_dict[2] = f"<< /Type /Pages /Kids [{kids_refs}] /Count {num_pages} >>".encode("latin1")
    
    for i, (p_title, lines) in enumerate(pages_data):
        page_idx = 3 + 2 * i
        content_idx = 4 + 2 * i
        
        # Build stream text
        stream_cmds = ["BT", f"/F1 12 Tf", "50 750 Td"]
        stream_cmds.append(f"({p_title}) Tj")
        stream_cmds.append("0 -20 Td")
        for line in lines:
            # Escape parenthesis
            safe_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            # Replace non-ascii with closest ascii for basic Type1 font
            ascii_line = (safe_line
                          .replace("ç", "c").replace("Ç", "C")
                          .replace("ğ", "g").replace("Ğ", "G")
                          .replace("ı", "i").replace("İ", "I")
                          .replace("ö", "o").replace("Ö", "O")
                          .replace("ş", "s").replace("Ş", "S")
                          .replace("ü", "u").replace("Ü", "U"))
            stream_cmds.append(f"({ascii_line}) Tj")
            stream_cmds.append("0 -15 Td")
        stream_cmds.append("ET")
        stream_data = "\n".join(stream_cmds).encode("latin1")
        
        obj_dict[page_idx] = f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents {content_idx} 0 R /Resources << /Font << /F1 {font_idx} 0 R >> >> >>".encode("latin1")
        obj_dict[content_idx] = f"<< /Length {len(stream_data)} >>\nstream\n".encode("latin1") + stream_data + b"\nendstream"
        
    obj_dict[font_idx] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    
    # Assemble PDF with cross reference table
    out = bytearray(pdf_header)
    offsets = {}
    
    for obj_num in range(1, font_idx + 1):
        offsets[obj_num] = len(out)
        out.extend(f"{obj_num} 0 obj\n".encode("latin1"))
        out.extend(obj_dict[obj_num])
        out.extend(b"\nendobj\n")
        
    xref_offset = len(out)
    out.extend(f"xref\n0 {font_idx + 1}\n".encode("latin1"))
    out.extend(b"0000000000 65535 f \n")
    for obj_num in range(1, font_idx + 1):
        out.extend(f"{offsets[obj_num]:010d} 00000 n \n".encode("latin1"))
        
    out.extend(f"trailer\n<< /Size {font_idx + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin1"))
    
    with open(filepath, "wb") as f:
        f.write(out)


def create_simple_docx(filepath: str, paragraphs: list):
    """Standart ECMA-376 Word (.docx) dosyasını yerel zipfile ile üretir."""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    body_items = []
    for p in paragraphs:
        # Escape XML chars
        safe_p = p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        body_items.append(f"<w:p><w:r><w:t>{safe_p}</w:t></w:r></w:p>")

    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {"".join(body_items)}
  </w:body>
</w:document>"""

    with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", doc_xml)


def generate_all_sample_fixtures():
    base_dir = Path(__file__).resolve().parent / "documents"
    base_dir.mkdir(parents=True, exist_ok=True)

    # 1. PDF: Merinos Dokuma Tezgah Ayarları ve Arıza Kılavuzu (2 Sayfa)
    pdf_path = base_dir / "merinos_weaving_sop.pdf"
    p1_lines = [
        "1. Bolum: Tarak ve Atki Sikligi Standartlari",
        "Hereke serisi klasik jakarli halilarda cozgude tarak sikligi cm basina 28 teldir.",
        "Atki sikligi ise 80x80 dugum yapisina gore ayarlanir.",
        "Tarak boslugu 0.45 mm toleransi asarsa jakar guveleri arasinda desen kaymasi olusur.",
        "Bu durumda tezgah otomatik olarak sarı ikaz lambasini yakar ve yavas moda gecer."
    ]
    p2_lines = [
        "2. Bolum: Ariza Kodlari ve Acil Durdurma",
        "E-401 Ariza Kodu: Ana tahrik motoru asinmasi veya asiri isinmasi durumunda verilir.",
        "E-401 goruldugunde operator derhal kirmizi acil durdurma butonuna basmali ve motor fanini temizlemelidir.",
        "E-108 Ariza Kodu: Mekik iplik rezerv sensoru bos kaldi hatasidir.",
        "E-256 Ariza Kodu: Cozgu cerceve kilit mekanizmasi basinci 6 bar altina dustugunde olusur."
    ]
    create_simple_pdf(str(pdf_path), [("Sayfa 1: Merinos Weaving SOP", p1_lines), ("Sayfa 2: Ariza Kodlari", p2_lines)])
    print(f"✅ PDF Üretildi: {pdf_path}")

    # 2. DOCX: Merinos Kalite ve İplik Standartları Kılavuzu
    docx_path = base_dir / "merinos_quality_standards.docx"
    docx_paras = [
        "Merinos Halı Kalite Güvence ve İplik Mukavemet Standartları",
        "BÖLÜM 1: İplik Mukavemet ve Tansiyon Basıncı",
        "Dokuma sırasında akrilik ve polipropilen ipliklerin gerginlik tansiyonu 14 bar altına düşmemelidir.",
        "Tansiyon 14 bar altına düştüğünde çözgü tellerinde anlık kopuş meydana gelir ve tezgah durur.",
        "Operatör manometre üzerinden vana 3'ü sıkarak basıncı 16 bar seviyesine dengelemelidir.",
        "BÖLÜM 2: Nem ve Sıcaklık Toleransı",
        "Dokuma salonu ortam nemi yüzde 65 ile 70 bağıl nem aralığında sabit tutulmalıdır.",
        "Ortam sıcaklığı 22 santigrat dereceyi aştığında iplik statik elektrik yüklenir ve atkı besleme hatası verir."
    ]
    create_simple_docx(str(docx_path), docx_paras)
    print(f"✅ DOCX Üretildi: {docx_path}")

    # 3. MD: Merinos Finisaj ve Buharlı Fikse Kılavuzu
    md_path = base_dir / "merinos_finishing_manual.md"
    md_content = """# Merinos Halı Finisaj, Yıkama ve Hav Sabitleme Kılavuzu

## 1. Buharlı Fikse ve Renk Sabitleme
Dokuma tezgahından çıkan ham halı, hav ipliklerinin kıvrım stabilitesini kazanması için finisaj tüneline girer.
Finisaj tünelinde 60 derece sıcaklıkta doymuş buharlı fikse işlemi uygulanır.
Bu işlem liflerin kristal yapısını kilitler ve CIELAB renk parlaklığını yüzde 12 artırır.

## 2. Hav Traşlama (Shearing) ve Kenar Overlok
Buhar fiksesi sonrası halı yüzeyindeki düzensiz hav yükseklikleri döner bıçaklı traşlama makinesinde 9.5 mm standardına getirilir.
Kenar overlok dikişinde poliamid takviyeli 3 katlı iplik kullanılır.
Kenar dikiş çekme mukavemeti en az 45 Newton olmalıdır.
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"✅ MD Üretildi: {md_path}")


if __name__ == "__main__":
    generate_all_sample_fixtures()
