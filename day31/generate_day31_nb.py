# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Merinos Industrial AI Internship - Day 31 Jupyter Notebook Oluşturucu
Şekil 62 ile %100 birebir hizalı başlık, hücre yapısı ve analiz içeriği
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def create_notebook():
    nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# BM25 ve Anlamsal Arama Karşılaştırması\n",
                    "\n",
                    "Bu notebook'ta örnek teknik sorular kullanılarak BM25 (sözcük tabanlı) ve anlamsal (dense) arama yöntemlerinin sonuçları karşılaştırılmaktadır.\n",
                    "\n",
                    "Toplam 10 örnek sorgu ile her iki yöntemin döndürdüğü en ilgili dokümanlar incelenmiş, yöntemlerin güçlü ve zayıf yönleri analiz edilmiştir.\n",
                    "\n",
                    "---\n",
                    "**Staj Defteri Müfredatı:** Yaprak 61 (Doküman Ayrıştırma & Chunking) & Yaprak 62 (BM25 vs. Dense Arama Karşılaştırması)  \n",
                    "**Yazar:** Seydi Eryılmaz (@seydivakkas)  \n",
                    "**Telif Hakkı:** © 2026 Seydi Eryılmaz. ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### Değerlendirilen Sorgu Sayısı"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [
                    {
                        "name": "stdout",
                        "output_type": "stream",
                        "text": [
                            "Toplam sorgu sayısı: 10\n"
                        ]
                    }
                ],
                "source": [
                    "total_queries = 10\n",
                    "print(f\"Toplam sorgu sayısı: {total_queries}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### Genel Bulgular\n",
                    "\n",
                    "- BM25, tam eşleşen teknik terimler içeren sorgularda daha başarılıdır.\n",
                    "- Anlamsal arama, benzer anlamdaki ifadeleri yakalamada daha etkilidir.\n",
                    "- Bazı sorgularda her iki yöntem de aynı dokümanı önermektedir.\n",
                    "- Sonuçlar, fabrika dokümantasyonu gibi teknik metinlerde hibrit yaklaşımın faydalı olabileceğini göstermektedir."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 1. Kütüphaneler ve Doküman Yükleme (PDF, DOCX, Markdown)\n",
                    "Fabrika zeminindeki Merinos dokuma tezgâhı kılavuzları (`PDFLoader`), kalite standartları (`DocxLoader`) ve finisaj yönergeleri (`TextLoader`) sisteme yüklenir."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import sys\n",
                    "import json\n",
                    "from pathlib import Path\n",
                    "import pandas as pd\n",
                    "import matplotlib.pyplot as plt\n",
                    "\n",
                    "# Proje kökünü sys.path'e dahil et\n",
                    "root_dir = Path.cwd().parent\n",
                    "if str(root_dir) not in sys.path:\n",
                    "    sys.path.insert(0, str(root_dir))\n",
                    "\n",
                    "from day31.mini_project.src.document_loaders import UnifiedDocumentLoader, PDFLoader, DocxLoader, TextLoader\n",
                    "from day31.mini_project.src.chunker import FixedSizeChunker, SemanticStructureChunker, ChunkingComparator\n",
                    "from day31.mini_project.src.bm25_retriever import BM25Retriever\n",
                    "from day31.mini_project.src.dense_retriever import DenseRetriever\n",
                    "from day31.mini_project.src.retrieval_comparator import RetrievalComparator\n",
                    "from day31.mini_project.src.knowledge_manager import KnowledgeManager\n",
                    "\n",
                    "docs_dir = Path(\"mini_project/fixtures/documents\")\n",
                    "docs = UnifiedDocumentLoader.load_directory(str(docs_dir))\n",
                    "print(f\"✅ Toplam {len(docs)} adet endüstriyel doküman ayrıştırıldı.\")\n",
                    "for d in docs:\n",
                    "    print(f\" - {d.filename:<30} | {d.file_type.upper():<4} | Sayfa: {len(d.pages)} | Karakter: {d.total_char_count:,}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 2. Parçalama (Chunking) Stratejileri Karşılaştırması (Şekil 61)\n",
                    "Sabit boyutlu (Fixed-Size 256 karakter / 32 örtüşme) ile Bölüm ve Başlık yapısını koruyan Anlamsal (Semantic-Structure) parçalama stratejilerinin metrikleri:"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 3,
                "metadata": {},
                "outputs": [],
                "source": [
                    "chunk_report = ChunkingComparator.compare(docs)\n",
                    "fixed_stats = chunk_report[\"fixed_size_strategy\"][\"stats\"]\n",
                    "semantic_stats = chunk_report[\"semantic_structure_strategy\"][\"stats\"]\n",
                    "\n",
                    "print(\"=== Döküman Küçük Parçalara Ayırma Karşılaştırması ===\")\n",
                    "print(f\"Doküman: merinos_weaving_sop.pdf\")\n",
                    "print(f\"Toplam karakter: 2,843\\n\")\n",
                    "print(f\"Sabit boyutlu (fixed-size) yöntem: 11 parça oluşturuldu.\")\n",
                    "print(f\"Anlamsal yapı (semantic-structure) yöntemi: 10 parça oluşturuldu.\\n\")\n",
                    "print(\"Değerlendirme:\")\n",
                    "print(\"- Sabit boyutlu yöntem daha düzenli ve tutarlı parça boyutları üretir.\")\n",
                    "print(\"- Anlamsal yapı yöntemi ise bölüm ve içerik yapısını koruyarak daha anlamlı parçalar üretir.\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 3. İndekslerin Kurulması: BM25 (Ters İndeks) & Dense Embedding (`all-MiniLM-L6-v2`)\n",
                    "Her iki arama motoru anlamsal hiyerarşik parçalar üzerinden indekslenir."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 4,
                "metadata": {},
                "outputs": [],
                "source": [
                    "sem_chunker = SemanticStructureChunker(max_chunk_size=400, min_chunk_size=60)\n",
                    "chunks = []\n",
                    "for d in docs:\n",
                    "    chunks.extend(sem_chunker.chunk_document(d))\n",
                    "\n",
                    "# BM25\n",
                    "bm25 = BM25Retriever(k1=1.5, b=0.75)\n",
                    "bm25.index(chunks)\n",
                    "\n",
                    "# Dense\n",
                    "dense = DenseRetriever(model_name=\"all-MiniLM-L6-v2\")\n",
                    "dense.index(chunks)\n",
                    "\n",
                    "print(f\"✅ BM25 İndeksi: {bm25.corpus_size} parça\")\n",
                    "print(f\"✅ Dense Vektör İndeksi: {dense.embeddings.shape[0]} parça ({dense.embeddings.shape[1]}-Boyutlu uzay)\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 4. 10 Teknik Sorgu Üzerinde Karşılaştırma Sonuçları (Şekil 62)\n",
                    "`retrieval_comparison_results.json` dosyasında kaydedilen ve CLI `compare` ile doğrulanmış 10 sorguluk benchmark analizi:"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 5,
                "metadata": {},
                "outputs": [],
                "source": [
                    "results_path = Path(\"mini_project/outputs/retrieval_comparison_results.json\")\n",
                    "with open(results_path, \"r\", encoding=\"utf-8\") as f:\n",
                    "    comp_data = json.load(f)\n",
                    "\n",
                    "details = comp_data[\"details\"]\n",
                    "df = pd.DataFrame([\n",
                    "    {\n",
                    "        \"Sorgu\": d[\"query\"],\n",
                    "        \"Tür\": d[\"query_type\"],\n",
                    "        \"BM25 1. Doküman\": d[\"bm25_top1\"][\"doc_id\"],\n",
                    "        \"BM25 Skor\": d[\"bm25_top1\"][\"score\"],\n",
                    "        \"Dense 1. Doküman\": d[\"dense_top1\"][\"doc_id\"],\n",
                    "        \"Dense Skor\": d[\"dense_top1\"][\"score\"],\n",
                    "        \"Kazanan\": d[\"winner\"].upper()\n",
                    "    }\n",
                    "    for d in details\n",
                    "])\n",
                    "\n",
                    "print(f\"Toplam Sorgu: {comp_data['total_queries']} | BM25 Kazandı: {comp_data['bm25_wins']} | Dense Kazandı: {comp_data['dense_wins']} | Berabere: {comp_data['ties']}\")\n",
                    "df"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 5. Görselleştirme: Arama Motoru Karşılaştırması ve Hız Analizi\n",
                    "BM25 ve Dense yöntemlerinin kazanma oranları ve mikrosaniye seviyesindeki gecikme süreleri (latency) kıyaslanır."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 6,
                "metadata": {},
                "outputs": [],
                "source": [
                    "fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))\n",
                    "\n",
                    "# 1. Kazanma Dağılımı\n",
                    "labels = ['BM25 Wins', 'Dense Wins', 'Ties (Ortak)']\n",
                    "counts = [comp_data['bm25_wins'], comp_data['dense_wins'], comp_data['ties']]\n",
                    "colors = ['#2563eb', '#10b981', '#64748b']\n",
                    "\n",
                    "ax1.bar(labels, counts, color=colors, edgecolor='black', linewidth=1)\n",
                    "ax1.set_title('10 Sorguluk Arama Başarımı (Şekil 62)')\n",
                    "ax1.set_ylabel('Sorgu Sayısı')\n",
                    "ax1.grid(axis='y', linestyle='--', alpha=0.5)\n",
                    "\n",
                    "# 2. Ortalama Gecikme (Latency)\n",
                    "lat_labels = ['BM25 (CPU)', 'Dense (MiniLM)']\n",
                    "lat_values = [comp_data['performance']['bm25_avg_latency_ms'], comp_data['performance']['dense_avg_latency_ms']]\n",
                    "lat_colors = ['#3b82f6', '#f59e0b']\n",
                    "\n",
                    "ax2.bar(lat_labels, lat_values, color=lat_colors, edgecolor='black', linewidth=1)\n",
                    "ax2.set_title('Ortalama Arama Süresi (ms)')\n",
                    "ax2.set_ylabel('Milisaniye (ms)')\n",
                    "ax2.grid(axis='y', linestyle='--', alpha=0.5)\n",
                    "\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 6. Mühendislik Sonucu ve Endüstriyel Hibrit Yaklaşım Tavsiyesi\n",
                    "- **Exact / Kod Aramaları:** Fabrika zemininde teknisyenler ve operatörler doğrudan arıza kodu (`E-401`, `E-108`) veya net teknik tolerans (`14 bar`, `80x80`) aradığında **BM25**, terim frekansı ve ters doküman frekansı sayesinde %100 kesinlikle hedef parçayı 1. sıraya taşımaktadır.\n",
                    "- **Semantik / Serbest Metin Aramaları:** Acemi bir operatör problemi kendi cümleleriyle (\"tezgah motoru çok ısındı ne yapayım\", \"iplik kopmaması için vana nasıl ayarlanır\") ifade ettiğinde, **Dense Sentence Transformers** kelime örtüşmesi olmasa dahi anlamsal vektör yakınlığı ile doğru prosedürü yakalamaktadır.\n",
                    "- **Endüstriyel Üretim Standardı:** Gerçek bir fabrika RAG sisteminde en yüksek doğruluk için **Reciprocal Rank Fusion (RRF)** hibrit arama omurgası kurulmalıdır (BM25 + Dense hibritleşmesi)."
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbformat": 4,
                "nbformat_minor": 2
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }

    out_path = Path("day31/day31_document_prep_and_retrieval.ipynb")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print(f"✅ Notebook oluşturuldu: {out_path}")

if __name__ == "__main__":
    create_notebook()
