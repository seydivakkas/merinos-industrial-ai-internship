# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Merinos Gün 32 Jupyter Notebook Üreteci
Şekil 64 ile %100 birebir hizalı başlık, hücre yapısı ve analiz içeriği
"""

import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def build_day32_notebook():
    nb = {
        "cells": [],
        "metadata": {
            "language_info": {
                "name": "python",
                "version": "3.11.6"
            },
            "kernelspec": {
                "display_name": "Python 3.11.6",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    def add_md(content: str):
        nb["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in content.split("\n")]
        })

    def add_code(code: str, outputs: list = None):
        nb["cells"].append({
            "cell_type": "code",
            "metadata": {},
            "execution_count": None,
            "outputs": outputs or [],
            "source": [line + "\n" for line in code.split("\n")]
        })

    # 1. BAŞLIK VE LİSANS
    add_md("""# GÜN 32: Hibrit Arama (Hybrid Search) Ağırlıklandırması ve IR Başarım Değerlendirmesi
## Staj Defteri: Yaprak 63 & 64 | Merinos Halı Sanayi A.Ş. — Endüstriyel Yapay Zekâ Stajı

---

> ### **ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR**
> **Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)**  
> Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim amaçlı olarak paylaşılmıştır.  
> Yazarın açık yazılı izni olmaksızın kopyalanamaz, çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

---

### Günün Hedefleri ve Endüstriyel Motivasyon
1. **Leksikal (BM25) ve Vektörel (Dense) Arama Birleştirmesi**: Leksikal aramanın kesin kod/rakam yakalama üstünlüğü ile vektörel aramanın kavramsal anlamsal kavrayışını tek bir skorda veya sıralamada füzyonlamak.
2. **Min-Max Lineer Birleştirme (Score Fusion)**: Skor ölçek uyuşmazlığını ortadan kaldırmak için $[0, 1]$ aralığına normalizasyon ve $\\alpha$ ağırlık parametresi optimizasyonu.
3. **Reciprocal Rank Fusion (RRF $k=60$)**: Puanlama ölçeklerinden ve kalibrasyon sorunlarından bağımsız, rank-tabanlı matematiksel füzyonun endüstriyel standartta uygulanması.
4. **Bilgi Getirme (Information Retrieval - IR) Metrikleri**: Hit@K, Mean Reciprocal Rank (MRR), Precision@K, Recall@K ve NDCG@K metrikleriyle 4 sistemin (BM25, Dense, Linear_0.5, RRF_k60) 15 adet doğrulanmış fabrika altın test sorgusu üzerinden objektif karşılaştırılması.
5. **Dörtlü Hata Taksonomisi (Error Taxonomy)**: KEYWORD_MISMATCH, CODE_DRIFT, CHUNK_BOUNDARY ve OUT_OF_DOMAIN kök neden analizi.
""")

    # 2. TEORİK MATEMATİK
    add_md("""---
## 1. Matematiksel Temeller ve Formülasyonlar

### 1.1. Min-Max Normalizasyonu ve Lineer Skor Füzyonu
BM25 skorları $[0, \\infty)$ aralığında sınırsız iken Cosine Benzerliği $[-1, 1]$ aralığındadır. Bu iki farklı ölçeği doğrudan toplamak bir motorun diğerini ezmesine yol açar:

$$\\hat{S}(d) = \\frac{S(d) - \\min_{d' \\in D} S(d')}{\\max_{d' \\in D} S(d') - \\min_{d' \\in D} S(d')}$$

Normalize edilmiş skorlar $\\alpha \\in [0, 1]$ parametresiyle birleştirilir:

$$S_{\\text{linear}}(d) = \\alpha \\cdot \\hat{S}_{\\text{BM25}}(d) + (1 - \\alpha) \\cdot \\hat{S}_{\\text{Dense}}(d)$$

### 1.2. Reciprocal Rank Fusion (RRF $k=60$)
Skor normalizasyonunun dağılım bozulmalarına hassas olduğu senaryolarda rank-tabanlı RRF kullanılır (Cormack et al., SIGIR 2009):

$$RRF(d) = \\sum_{m \\in M} \\frac{1}{k + r_m(d)}$$
""")

    # 3. KOD HÜCRESİ: ÇEVRE HAZIRLIĞI VE IMPORTLAR
    add_code("""# Gerekli kütüphanelerin içe aktarılması
import sys
import json
from pathlib import Path

# Proje kök dizinini ekle
root_dir = Path.cwd().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from day31.mini_project.src.knowledge_manager import KnowledgeManager
from day32.mini_project.src.models import GoldenQuery
from day32.mini_project.src.hybrid_retriever import HybridRetriever, min_max_normalize, compute_rrf_score
from day32.mini_project.src.retrieval_evaluator import RetrievalEvaluator
from day32.mini_project.src.error_analyzer import ErrorAnalyzer
from day32.mini_project.src.cli import load_golden_queries

print("✅ Gün 32 modülleri başarıyla yüklendi!")
""")

    # 4. FABRİKA KORPUSU VE CHUNKLARIN YÜKLENMESİ
    add_md("""---
## 2. Merinos Fabrika Korpusunun ve Parçalarının (Chunks) Yüklenmesi
Gün 31'de indekslenen endüstriyel SOP ve kılavuz belgeleri (`merinos_weaving_sop.pdf`, `merinos_quality_standards.docx`, `merinos_finishing_manual.md`) `KnowledgeManager` üzerinden senkronize edilir.
""")

    add_code("""docs_path = Path("mini_project/fixtures/documents")
if not docs_path.exists():
    docs_path = Path("../day31/mini_project/fixtures/documents")

km = KnowledgeManager(documents_dir=str(docs_path))
km.sync()

print(f"📄 İndekslenen Ham Doküman Sayısı: {len(km.raw_documents)}")
print(f"🧩 Oluşturulan Chunk Sayısı: {len(km.chunks)}\\n")

print(f"{'Chunk ID':<35} | {'Doküman':<30} | {'Bölüm':<25}")
print("-" * 95)
for c in km.chunks:
    print(f"{c.chunk_id:<35} | {c.doc_id:<30} | {c.section:<25}")
""")

    # 5. ALTIN KIYASLAMA VERİ SETİNİN İNCELENMESİ
    add_md("""---
## 3. Altın Kıyaslama Veri Seti (Golden Benchmark Dataset)
15 adet doğrulanmış sorgu 4 kategoriye ayrılmıştır:
1. `EXACT_CODE`: Alfanümerik arıza kodları (E-401, E-108), kritik basınç eşikleri (14 bar).
2. `SEMANTIC_SYMPTOM`: Doğal dil operatör semptomları ve bakım prosedürleri.
3. `HYBRID_COMPLEX`: Hem teknik kod hem açıklayıcı semptom içeren karmaşık sorgular.
4. `OUT_OF_DOMAIN`: Fabrika SOP korpusu dışı negatif kontrol sorguları.
""")

    add_code("""golden_path = Path("mini_project/fixtures/golden_benchmark_dataset.json")
queries = load_golden_queries(str(golden_path))

print(f"🎯 Yüklenen Altın Test Sorgusu Sayısı: {len(queries)}\\n")
print(f"{'ID':<18} | {'Kategori':<18} | {'Hedef Chunk':<30} | {'Sorgu Metni'}")
print("-" * 110)
for q in queries:
    target = q.target_chunk_id or "YOK (Negatif Kontrol)"
    print(f"{q.id:<18} | {q.category:<18} | {target:<30} | {q.query[:40]}...")
""")

    # 6. ŞEKİL 64: GÖRSELLEŞTİRME VE ANALİZ GRAFİĞİ (4 PANEL)
    add_md("""---
## 4. Hibrit Retrieval Değerlendirme Grafikleri (Şekil 64)
BM25, Dense, Linear_0.5 ve RRF_k60 sistemlerinin Hit@1, MRR ve NDCG@5 metrikleri, lineer alpha duyarlılık analizi, soru kategorilerine göre başarım ve hata taksonomisi dağılımı:
""")

    add_code("""from IPython.display import Image
Image(filename='mini_project/outputs/hybrid_retrieval_evaluation.png')
""")

    # 7. ŞEKİL 64 İLE BİREBİR: 5. BENCHMARK RAPORUNU İNCELE
    add_md("""---
# 5. Benchmark raporunu incele
Altın kıyaslama veri seti üzerinden elde edilen konsolide metrikler ve sistem başarım karşılaştırması:
""")

    add_code("""report_path = Path("mini_project/outputs/benchmark_report.json")
if report_path.exists():
    with open(report_path, "r", encoding="utf-8") as f:
        report_data = json.load(f)
    
    print("=" * 82)
    print(f"{'Sistem':<15} | {'Hit@1':<8} | {'Hit@3':<8} | {'Hit@5':<8} | {'MRR':<8} | {'NDCG@5':<8}")
    print("-" * 82)
    for sname, rep in report_data.get("systems", {}).items():
        m = rep["overall_metrics"]
        h1 = m["hit_at_k"].get("1", 0.0)
        h3 = m["hit_at_k"].get("3", 0.0)
        h5 = m["hit_at_k"].get("5", 0.0)
        mrr = m["mrr"]
        ndcg5 = m["ndcg_at_k"].get("5", 0.0)
        print(f"{sname:<15} | {h1:<8.4f} | {h3:<8.4f} | {h5:<8.4f} | {mrr:<8.4f} | {ndcg5:<8.4f}")
    print("=" * 82)
    print(f"\\n🏆 En Yüksek MRR  : {report_data.get('best_system_mrr')}")
    print(f"🎯 En Yüksek Hit@1: {report_data.get('best_system_hit1')}")
    print(f"⚖️ Optimum Alpha  : {report_data.get('best_alpha')}")
""")

    # 8. HATA TAKSONOMİSİ VE TEŞHİS ANALİZİ
    add_md("""---
## 6. Hata Taksonomisi ve Teşhis Analizi
Her sistemin hangi kategorilerde hata yaptığı analiz edilir:
- **KEYWORD_MISMATCH**: Doğal dil semptomlarının BM25 sözlüğünde bulunamaması.
- **CODE_DRIFT**: Alfanümerik teknik kodların Dense vektör uzayında kaybolması.
- **CHUNK_BOUNDARY**: Parça sınırları nedeniyle bağlamın bölünmesi.
- **OUT_OF_DOMAIN**: Korpus dışı sorgularda filtreleme ihtiyacı.
""")

    add_code("""hybrid = HybridRetriever(
    bm25=km.bm25,
    dense=km.dense,
    chunks=km.chunks,
    default_k_rrf=60,
    default_alpha=0.5
)
evaluator = RetrievalEvaluator(hybrid, k_values=[1, 3, 5])
reports = evaluator.evaluate_all_standard_systems(queries)
analyzer = ErrorAnalyzer()
failure_stats = analyzer.compare_system_failures(reports, queries)

print(f"{'Sistem':<15} | {'Keyword Mismatch':<18} | {'Code Drift':<12} | {'Boundary':<10} | {'Out of Domain':<14}")
print("-" * 75)
for sname, counts in failure_stats.items():
    print(f"{sname:<15} | {counts['KEYWORD_MISMATCH']:<18} | {counts['CODE_DRIFT']:<12} | {counts['CHUNK_BOUNDARY']:<10} | {counts['OUT_OF_DOMAIN']:<14}")
print("-" * 75)
""")

    # 9. SONUÇ VE STAJ ÇIKARIMLARI
    add_md("""---
## 7. Staj Değerlendirmesi ve Mühendislik Çıkarımları
1. **Tek Başına Arama Motorlarının Zafiyeti**:
   - Salt BM25, doğal dilde semptom anlatan operatör sorgularında (%14.3 oranında) 1. sırayı kaçırmıştır (`KEYWORD_MISMATCH`).
   - Salt Dense, teknik parça kodlarında (`E-401`, `14 bar`) semantik genelleme nedeniyle (%35.7 oranında) 1. sırayı kaçırmıştır (`CODE_DRIFT`).
2. **Hibrit Füzyonun Kusursuz Gücü**:
   - Min-Max normalizasyonlu **Lineer Hibrit Arama ($\\alpha = 0.5$)**, tüm geçerli altın sorgularda **Hit@1 = 1.0000** ve **MRR = 1.0000** ile kusursuz başarı sergilemiştir.
   - **RRF ($k=60$)**, skor kalibrasyonuna gerek kalmaksızın %87.14 MRR seviyesinde son derece dirençli bir alternatif sunmuştur.
3. **Üretim Dağıtımı Önerisi**:
   - Fabrika içi dokuma tezgâhı bakım asistanında birincil motor olarak **Linear Hibrit ($\\alpha=0.4 - 0.5$)** veya **RRF ($k=60$)** devreye alınmalı; negatif sorgular için bir cosine similarity threshold gate eklenmelidir.
""")

    out_file = Path("day32/day32_hybrid_retrieval_and_evaluation.ipynb")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=2)

    print(f"✅ Notebook başarıyla üretildi: {out_file}")


if __name__ == "__main__":
    build_day32_notebook()
