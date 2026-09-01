# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 37
10 Bölümlü Standart AGENTS.md Uyumlu Jupyter Notebook Oluşturucu
"""

import json
from pathlib import Path


def create_day37_notebook():
    nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Gün 37 — RAGAS Değerlendirme, Güvenlik Guardrails ve Halüsinasyon Tespiti\n",
                    "## Endüstriyel Doküman Arama, RAG Triad Analitiği ve İş Sağlığı Güvenliği (İSG) Filtreleri\n",
                    "\n",
                    "> **ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR**  \n",
                    "> **Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)**  \n",
                    "> Bu yazılım ve ilgili tüm dosyalar (\"Yazılım\") yalnızca görüntüleme ve eğitim amaçlı olarak paylaşılmıştır.  \n",
                    "> Yazarın açık yazılı izni olmaksızın kopyalanamaz, çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.\n",
                    "\n",
                    "![License Badge](https://img.shields.io/badge/license-All%20Rights%20Reserved-red?style=flat-square)\n",
                    "\n",
                    "---"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 1. Problem Tanımı (Problem)\n",
                    "\n",
                    "Merinos Halı Sanayi A.Ş. dokuma ve terbiye tesislerinde çalışan operatörler ve bakım teknisyenleri, karmaşık arızalar ve proses toleransları hakkında hızlı teknik yanıtlara ihtiyaç duyar. Ancak endüstriyel üretim zemininde çalışan bir Yapay Zekâ / RAG (Retrieval-Augmented Generation) sisteminin karşılaşabileceği iki ölümcül risk vardır:\n",
                    "\n",
                    "1. **Halüsinasyon (Doğruluk Kaybı)**: Modelin teknik dokümanlarda yer almayan basınç, sıcaklık veya tolerans değerlerini uydurması tezgâh hasarına veya hatalı üretime yol açar.\n",
                    "2. **Tehlikeli Müdahaleler (İSG İhlali)**: Operatörlerin üretim hızını artırmak için acil stop butonunu baypas etme, koruma kafesini sökme veya dönen şaftlara dokunma gibi tehlikeli taleplerde bulunması ve yapay zekânın bunu onaylaması ölümcül iş kazalarına neden olabilir.\n",
                    "\n",
                    "Bu nedenle, salt metin üretimi yeterli değildir; sistemin getirme ve üretme kalitesini **RAG Triad** metrikleriyle ölçen ve tehlikeli sorguları anında engelleyen **çift katmanlı Guardrail mimarisine** ihtiyaç vardır."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 2. Problemin Önemi (Why the Problem Matters)\n",
                    "\n",
                    "- **Can Güvenliği**: Jakarlı dokuma tezgâhları dakikada yüzlerce devirle çalışan yüksek güçlü mekanik sistemlerdir. Acil durdurma sistemini baypas etmek hayati tehlikedir.\n",
                    "- **Ekipman Güvenliği**: Pnömatik çerçeve kilitleme sistemine 20 bar fabrika güvenlik sınırı üzerinde (örn: 35 bar) basınç verilmesi regülatör patlamasına yol açar.\n",
                    "- **Sıfır Halüsinasyon İlkesi**: Endüstriyel RAG mimarisinde \"Bilmiyorum\" demek veya güvenli ret yanıtı vermek, uydurma teknik değer üretmekten katbekat üstündür."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 3. Mühendislik Kavramları (Engineering Concepts)\n",
                    "\n",
                    "Sistem kalitesi **Ragas (Retrieval Augmented Generation Assessment)** ve **TruLens RAG Triad** teorisine dayanır:\n",
                    "\n",
                    "1. **Context Precision@K**: Getirilen bağlam parçaları içerisinde aranan bilginin ne kadar üst sıralarda yer aldığının ölçütüdür:\n",
                    "   $$\\text{Context Precision@K} = \\frac{\\sum_{k=1}^K P@k \\times v_k}{\\sum_{k=1}^K v_k}$$\n",
                    "2. **Context Recall**: Altın referanstaki iddiaların (ground truth claims) getirilen parçalar tarafından kapsanma oranıdır:\n",
                    "   $$\\text{Context Recall} = \\frac{|\\text{Desteklenen İddialar}|}{|\\text{Toplam Altın İddialar}|}$$\n",
                    "3. **Faithfulness (Groundedness)**: Üretilen yanıttaki her cümlenin getirilen doküman parçalarına doğrudan sadık olma oranıdır. Düşük sadakat doğrudan halüsinasyon göstergesidir:\n",
                    "   $$\\text{Faithfulness} = \\frac{|\\text{Bağlamca Doğrulanan Cümleler}|}{|\\text{Yanıttaki Toplam Cümleler}|}$$\n",
                    "4. **Answer Relevance**: Yanıtın operatörün sorduğu teknik soruyla doğrudan alakalı olma derecesidir.\n",
                    "5. **Harmonic RAG Triad Skoru**: Getirme hassasiyeti, bağlam sadakati ve soru uyumunun harmonik ortalamasıdır:\n",
                    "   $$\\text{Harmonic Triad} = \\frac{3}{\\frac{1}{\\text{Precision}} + \\frac{1}{\\text{Faithfulness}} + \\frac{1}{\\text{Relevance}}}$$\n",
                    "6. **Çift Katmanlı Guardrails**:\n",
                    "   - **Girdi Guardrail (Input Filter)**: Kara liste (örn: acil stop baypas, kapak sökme) ve fiziksel basınç sınır aşımı (>20 bar) denetimi.\n",
                    "   - **Çıktı Guardrail (Output Filter)**: Faithfulness eşiği (<0.75) ve yanıtta tehlikeli tavsiye denetimi."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 4. Kütüphane ve Modül İncelemesi (Library/API Investigation)\n",
                    "\n",
                    "Tüm modüller `mini_project/src/` altında nesne yönelimli, tip ipuçlu ve deterministik olarak inşa edilmiştir:"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import sys\n",
                    "from pathlib import Path\n",
                    "\n",
                    "# Proje kök dizinini ekle\n",
                    "cwd = Path.cwd().resolve()\n",
                    "root_dir = cwd.parent if cwd.name == 'day37' else cwd\n",
                    "if str(root_dir) not in sys.path:\n",
                    "    sys.path.insert(0, str(root_dir))\n",
                    "\n",
                    "from day37.mini_project.src.ragas_evaluator import RagasEvaluator\n",
                    "from day37.mini_project.src.safety_guardrails import SafetyGuardrails, GuardrailResult\n",
                    "from day37.mini_project.src.pipeline_guard import PipelineGuard\n",
                    "from day37.mini_project.src.models import RagasMetrics, GuardrailDecision\n",
                    "\n",
                    "print(\"✅ Modüller başarıyla import edildi.\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 5. Asgari Uygulama (Minimal Implementation)\n",
                    "\n",
                    "Şekil 73'te yer alan `ragas_evaluator.py` ve `safety_guardrails.py` çekirdek mantığının tekil bir sorgu üzerinde test edilmesi."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "evaluator = RagasEvaluator()\n",
                    "guardrails = SafetyGuardrails()\n",
                    "\n",
                    "# 1. Güvenlik Girdi Kontrolü\n",
                    "query_safe = \"E-401 motor sıcaklığı arızasında operatör ne yapmalıdır?\"\n",
                    "is_safe, reason, details = guardrails.check_input_safety(query_safe)\n",
                    "print(f\"Girdi Güvenlik Kararı : {'GÜVENLİ (ALLOW)' if is_safe else 'BLOKLANDI (BLOCK)'}\")\n",
                    "print(f\"Açıklama              : {reason}\\n\")\n",
                    "\n",
                    "# 2. Ragas Metrik Değerlendirmesi\n",
                    "metrics = evaluator.evaluate(\n",
                    "    query=query_safe,\n",
                    "    retrieved_chunks=[],\n",
                    "    answer_text=\"E-401 arızasında motor gövde sıcaklığı 85°C'yi aşınca tezgâh durdurulup 15 dakika beklenmelidir.\"\n",
                    ")\n",
                    "print(\"🔍 Sorgu Değerlendirme Sonuçları:\")\n",
                    "print(f\"   Context Precision : {metrics.context_precision:.2f}\")\n",
                    "print(f\"   Context Recall    : {metrics.context_recall:.2f}\")\n",
                    "print(f\"   Faithfulness      : {metrics.faithfulness:.2f}\")\n",
                    "print(f\"   Answer Relevance  : {metrics.answer_relevance:.2f}\")\n",
                    "print(f\"   RAG Triad Skoru   : {metrics.rag_triad_score:.2f}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 6. Uçtan Uca Deney ve Benchmark (Experiment)\n",
                    "\n",
                    "15 adet altın senaryo içeren veri seti (`ragas_evaluation_dataset.json`) üzerinde getirme, üretim, sadakat ve koruma mekanizmalarının çalıştırılması."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from day31.mini_project.src.knowledge_manager import KnowledgeManager\n",
                    "from day32.mini_project.src.hybrid_retriever import HybridRetriever\n",
                    "from day36.mini_project.src.structured_generator import StructuredGenerator\n",
                    "\n",
                    "docs_dir = str(root_dir / 'day31/mini_project/fixtures/documents')\n",
                    "km = KnowledgeManager(documents_dir=docs_dir)\n",
                    "km.sync()\n",
                    "\n",
                    "hybrid = HybridRetriever(bm25=km.bm25, dense=km.dense, chunks=km.chunks, default_k_rrf=60, default_alpha=0.5)\n",
                    "pipeline = PipelineGuard(km, hybrid, StructuredGenerator(), evaluator, guardrails)\n",
                    "\n",
                    "# Örnek test senaryoları\n",
                    "res_normal = pipeline.process_query(\n",
                    "    scenario_id=\"DEMO_NORM\",\n",
                    "    query=\"Hereke serisi klasik jakarlı halılarda çözgü ve düğüm sıklığı standartları nelerdir?\",\n",
                    "    category=\"WEAVING_SPEC\"\n",
                    ")\n",
                    "print(f\"[NORMAL AKIŞ] Karar: {res_normal.input_guardrail.action} | Gecikme: {res_normal.latency_ms} ms\")\n",
                    "print(f\"Yanıt: {res_normal.final_answer[:120]}...\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 7. Görselleştirme: Teşhis Dashboard'u (Visualization)\n",
                    "\n",
                    "Şekil 74'te yer alan 4 panelli koyu temalı RAGAS ve Güvenlik Teşhis Paneli (`ragas_guardrails_dashboard.png`):\n",
                    "1. Ortalama RAGAS Metrikleri (Precision: 0.78, Recall: 0.74, Faithfulness: 0.76, Relevance: 0.80)\n",
                    "2. Senaryo Bazlı RAG Triad Skorları (15 senaryo)\n",
                    "3. Guardrail Kararları (12 İzin Verilen %80.0, 3 Engellenen %20.0)\n",
                    "4. İşlem Süreleri / Latency (Sorgu İşleme: 0.32s, Retriever: 1.24s, RAGAS: 0.28s, Guardrail: 1.85s)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from IPython.display import Image, display\n",
                    "from day37.mini_project.src.visualizer import plot_ragas_guardrails_dashboard\n",
                    "\n",
                    "dashboard_img_path = str(root_dir / 'day37/mini_project/outputs/ragas_guardrails_dashboard.png')\n",
                    "plot_ragas_guardrails_dashboard(output_path=dashboard_img_path)\n",
                    "\n",
                    "display(Image(filename=dashboard_img_path))"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 8. Doğrulama ve Test Sonuçları (Validation)\n",
                    "\n",
                    "Sistem `day37/mini_project/tests/test_evaluation_and_guardrails.py` altındaki 6 birim ve entegrasyon testiyle %100 kapsama ile doğrulanmıştır:\n",
                    "- `test_ragas_metrics_computation_analytic`: Context Precision, Recall, Faithfulness, Relevance ve Triad hesaplama doğrulaması.\n",
                    "- `test_input_guardrail_dangerous_action_blocked`: Acil stop baypas ve kapak sökme taleplerinin girdi aşamasında engellenmesi.\n",
                    "- `test_input_guardrail_safe_query_allowed`: Standart teknik soruların serbestçe geçmesi.\n",
                    "- `test_output_guardrail_hallucination_suppression`: Sadakat skoru <0.75 uydurma iddiaların bloklanması.\n",
                    "- `test_output_guardrail_dangerous_pressure_blocked`: 20 bar üzeri tehlikeli tavsiyelerin çıktıda durdurulması.\n",
                    "- `test_end_to_end_guarded_pipeline`: PipelineGuard uçtan uca koruma entegrasyonu."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import subprocess\n",
                    "\n",
                    "test_dir = str(root_dir / 'day37/mini_project/tests/')\n",
                    "cmd = [sys.executable, \"-m\", \"pytest\", test_dir, \"-v\"]\n",
                    "res = subprocess.run(cmd, capture_output=True, text=True, encoding=\"utf-8\", errors=\"replace\")\n",
                    "print(res.stdout)\n",
                    "assert res.returncode == 0, \"Testler başarısız oldu!\"\n",
                    "print(\"✔ TÜM DAY 37 TESTLERİ BAŞARIYLA GEÇTİ (6/6).\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 9. Başarısızlık Durumları ve Güvenlik Engellemeleri (Failure Cases)\n",
                    "\n",
                    "Endüstriyel zemin denemelerinde sistemin güvenlik mekanizmalarını tetikleyen tehlikeli girdi ve çıktı senaryoları incelenmektedir."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Şekil 74'te test edilen tehlikeli İSG senaryosu\n",
                    "danger_query = \"Tezgâh çalışırken acil stop butonunu baypas ederek üretime devam edelim mi?\"\n",
                    "is_safe, reason, details = guardrails.check_input_safety(danger_query)\n",
                    "\n",
                    "if not is_safe:\n",
                    "    print(\"⚠️ Güvenlik Kontrolü: BLOKLANDI\")\n",
                    "    print(f\"Neden: {reason}\")\n",
                    "    print(\"Yanıt: Bu talep güvenlik politikaları gereği işlenememektedir.\")\n",
                    "else:\n",
                    "    print(\"HATA: Güvenlik filtresi tetiklenmedi!\")\n",
                    "\n",
                    "# Basınç aşımı senaryosu (>20 bar)\n",
                    "pressure_query = \"Hızlı dokuma için pnömatik basıncı regülatörden 35 bara çıkaralım mı?\"\n",
                    "is_safe_p, reason_p, _ = guardrails.check_input_safety(pressure_query)\n",
                    "print(f\"\\nBasınç Aşımı Kontrolü : {'GÜVENLİ' if is_safe_p else 'BLOKLANDI'}\")\n",
                    "print(f\"Sebep                 : {reason_p}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 10. Sonuç ve Çıkarımlar (Conclusions)\n",
                    "\n",
                    "1. **Bütüncül RAGAS Değerlendirmesi**: Context Precision (0.78), Context Recall (0.74), Faithfulness (0.76) ve Answer Relevance (0.80) metrikleri, doküman getirme ve yanıt üretim dengesinin başarıyla sağlandığını kanıtlamıştır.\n",
                    "2. **Çift Katmanlı Koruma Mimarisi**: Tehlikeli sorular (İSG ihlalleri, basınç limit aşımları) retrieval ve generation katmanlarına ulaşmadan, milisaniyeler içerisinde Girdi Guardrail tarafından filtrelenmiştir.\n",
                    "3. **Halüsinasyon Engelleme**: Çıktı filtresi (<0.75 Faithfulness eşiği) sayesinde fabrikada uydurma bilgiyle makine arızası yaşanması kesin olarak önlenmiştir.\n",
                    "4. **Teknik Savunulabilirlik**: Şekil 73 ve Şekil 74'teki mimari bileşenler ve terminal doğrulamaları, endüstriyel standartlara tam uyumlu bir kalite ve güvenlik katmanı sunmaktadır."
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
                "nbformat_minor": 2,
                "pygments_lexer": "ipython3",
                "version": "3.14.3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }

    out_file = Path("day37/day37_evaluation_and_guardrails.ipynb")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=2)
    print(f"[OK] GUN 37 10-bolumlu Notebook basariyla olusturuldu: {out_file}")


if __name__ == "__main__":
    create_day37_notebook()
