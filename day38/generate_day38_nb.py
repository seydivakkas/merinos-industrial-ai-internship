# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 38
Jupyter Notebook Oluşturucu Script (AGENTS.md 10 Standart Bölüm)
"""

import json
from pathlib import Path


def create_day38_notebook():
    nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# GÜN 38: Endüstriyel RAG API & Streamlit Arayüzü\n",
                    "## Gereksinim 7: FastAPI ile Servis Etme, Dokuma Salonu Operatör Web Arayüzü ve Canlı Alıntı / Güvenlik Gösterimi\n",
                    "\n",
                    "> **ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR**  \n",
                    "> **Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)**  \n",
                    "> Bu yazılım ve ilgili tüm dosyalar (\"Yazılım\") yalnızca görüntüleme ve eğitim amaçlı olarak paylaşılmıştır.  \n",
                    "> Yazarın açık yazılı izni olmaksızın kopyalanamaz, çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.\n",
                    "\n",
                    "---\n",
                    "\n",
                    "Bu çalışma defteri, **AGENTS.md** mühendislik müfredatı doğrultusunda 10 standart bölümden oluşmaktadır:\n",
                    "1. Problem\n",
                    "2. Neden Önemli? (Why the Problem Matters)\n",
                    "3. Mühendislik Kavramları (Engineering Concepts)\n",
                    "4. Kütüphane ve API İncelemesi (Library/API Investigation)\n",
                    "5. Minimal Uygulama (Minimal Implementation)\n",
                    "6. Deney (Experiment)\n",
                    "7. Görselleştirme (Visualization)\n",
                    "8. Doğrulama (Validation)\n",
                    "9. Başarısızlık Durumları ve Güvenlik Sınırları (Failure Cases)\n",
                    "10. Sonuçlar ve Çıkarımlar (Conclusions)"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 1. Problem\n",
                    "\n",
                    "Merinos Gaziantep Halı Fabrikası dokuma salonlarında 24 saat kesintisiz çalışan yüzlerce jakarlı tezgâh operatörü, mekanik arızalar, atkı/çözgü tansiyon sorunları ve İSG riskleriyle karşı karşıyadır. Önceki günlerde geliştirilen bilgi tabanı, hibrit arama, üretim ve güvenlik korkuluklarının Python betikleri seviyesinden çıkarılarak, dokuma salonundaki SCADA terminalleri, tabletler ve web arayüzleri tarafından tüketilebilecek **düşük gecikmeli, asenkron ve yüksek erişilebilir bir REST API** ve **SCADA tarzı bir Streamlit operatör konsolu** ile servis edilmesi gerekmektedir."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 2. Neden Önemli? (Why the Problem Matters)\n",
                    "\n",
                    "- **Üretim Kaybı ve Iskarta Riski:** Dakikada 1000'lerce darbe vuran Van de Wiele jakarlı dokuma tezgâhlarında E-401 motor sıcaklığı veya tansiyon hatası durumunda operatörün kılavuzu dakikalarca araması metrelerce birinci sınıf halının ıskartaya ayrılmasına yol açar.\n",
                    "- **İş Sağlığı ve Güvenliği (İSG):** Hatalı veya halüsinasyon içeren bir tavsiye (örneğin tezgâh çalışırken acil stop butonunu baypas etmek veya koruma kapağını sökmek) operatörün uzuv kaybına varabilecek ölümcül kazalara sebep olabilir.\n",
                    "- **Entegrasyon Esnekliği:** REST API mimarisi, Merinos ERP/MES ve SCADA sistemlerine doğrudan JSON entegrasyonu sunarken; Streamlit konsolu vardiya amirlerine anlık teşhis ve şeffaf alıntı denetimi imkanı sağlar."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 3. Mühendislik Kavramları (Engineering Concepts)\n",
                    "\n",
                    "- **FastAPI & Asenkron ASGI Mimarisi:** Python tip ipuçları (type hints) ve Pydantic veri modelleriyle yüksek performanslı, OpenAPI Swagger dokümantasyonunu otomatik üreten REST mimarisi.\n",
                    "- **Çift Katmanlı Guardrail (Korkuluk):** Girdi kontrolü (Input Guardrail) ile tehlikeli komutları 1 ms altında erken kesme; Çıktı kontrolü (Output Guardrail) ile halüsinasyonları ve güvenilmez iddiaları baskılama.\n",
                    "- **Ragas Triad Kalite Metrikleri:** Bağlama sadakat (Faithfulness), Bağlam Hassasiyeti (Context Precision) ve Yanıt Uygunluğu (Answer Relevance) metriklerinin gerçek zamanlı izlenmesi.\n",
                    "- **SCADA Tarzı Operatör Arayüzü:** Tezgâh seçimi, vardiya takibi, hızlı arıza şablonları ve alıntı rozetleriyle donatılmış Streamlit konsolu."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 4. Kütüphane ve API İncelemesi (Library/API Investigation)\n",
                    "\n",
                    "Kullanılan temel kütüphaneler ve sistem bileşenleri:\n",
                    "- `fastapi`: Yüksek performanslı asenkron REST API çatısı.\n",
                    "- `pydantic`: Tip güvenliği, veri doğrulama ve şema modelleme.\n",
                    "- `starlette.testclient`: Bellek içi (in-memory) uçtan uca API test kütüphanesi.\n",
                    "- `streamlit`: Dokuma salonu operatör konsolu web arayüzü.\n",
                    "- `matplotlib`: 300 DPI endüstriyel sistem teşhis paneli görselleştiricisi."
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
                    "# Dizin çözümleme\n",
                    "root_dir = Path.cwd().resolve()\n",
                    "if (root_dir / 'day38').exists():\n",
                    "    pass\n",
                    "elif (root_dir.parent / 'day38').exists():\n",
                    "    root_dir = root_dir.parent\n",
                    "if str(root_dir) not in sys.path:\n",
                    "    sys.path.insert(0, str(root_dir))\n",
                    "\n",
                    "import fastapi\n",
                    "import pydantic\n",
                    "import streamlit\n",
                    "import starlette\n",
                    "\n",
                    "print(f\"[OK] FastAPI Surumu   : {fastapi.__version__}\")\n",
                    "print(f\"[OK] Pydantic Surumu  : {pydantic.__version__}\")\n",
                    "print(f\"[OK] Streamlit Surumu : {streamlit.__version__}\")\n",
                    "print(f\"[OK] Starlette Surumu : {starlette.__version__}\")\n",
                    "print(f\"[OK] Kok Dizin        : {root_dir}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 5. Minimal Uygulama (Minimal Implementation)\n",
                    "\n",
                    "Şekil 75'te gösterilen `app.py` ve `service.py` mimarisinin FastAPI TestClient ile bellek içi başlatılması ve `/health`, `/looms` uç noktalarının sorgulanması:"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from starlette.testclient import TestClient\n",
                    "from day38.mini_project.src.app import app\n",
                    "\n",
                    "client = TestClient(app)\n",
                    "\n",
                    "# Sağlık kontrolü\n",
                    "res_health = client.get(\"/api/v1/health\")\n",
                    "assert res_health.status_code == 200\n",
                    "h_json = res_health.json()\n",
                    "\n",
                    "# Tezgâh envanteri kontrolü\n",
                    "res_looms = client.get(\"/api/v1/looms\")\n",
                    "assert res_looms.status_code == 200\n",
                    "l_json = res_looms.json()\n",
                    "\n",
                    "print(\"=\" * 65)\n",
                    "print(\"🏥 MERİNOS RAG REST API SAĞLIK VE ENVANTER DURUMU\")\n",
                    "print(\"=\" * 65)\n",
                    "print(f\"Sistem Durumu      : {h_json['status']}\")\n",
                    "print(f\"Tesis              : {h_json['facility']}\")\n",
                    "print(f\"Dokuma Salonu      : {h_json['weaving_hall']}\")\n",
                    "print(f\"Bilgi Parça Sayısı : {h_json['knowledge_base_chunks']} adet\")\n",
                    "print(f\"Korkuluk Durumu    : {h_json['guardrail_status']}\")\n",
                    "print(f\"Kayıtlı Tezgâhlar  : {l_json['total_looms']} adet aktif jakarlı tezgâh\")\n",
                    "for loom in l_json[\"looms\"][:3]:\n",
                    "    print(f\"   * {loom['id']}: {loom['model']} ({loom['series']}) - {loom['status']}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 6. Deney (Experiment)\n",
                    "\n",
                    "Şekil 75 ve Şekil 76'da gösterilen `POST /api/v1/process-operator-query` uç noktası üzerinden **E-401 motor sıcaklığı** sorusunun test edilmesi:"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Şekil 75'teki Swagger UI istek gövdesi ile aynı JSON\n",
                    "operator_payload = {\n",
                    "    \"query\": \"E-401 motor sıcaklığı neden artar?\",\n",
                    "    \"loom_id\": \"TEZGAH-01\",\n",
                    "    \"shift\": \"VARDIYA-1\",\n",
                    "    \"operator_id\": \"OP-104\",\n",
                    "    \"top_k\": 5\n",
                    "}\n",
                    "\n",
                    "resp_op = client.post(\"/api/v1/process-operator-query\", json=operator_payload)\n",
                    "assert resp_op.status_code == 200\n",
                    "res_data = resp_op.json()\n",
                    "\n",
                    "print(\"=\" * 75)\n",
                    "print(\"🎯 ŞEKİL 75 & 76: OPERATÖR SORGUSU YANIT RAPORU\")\n",
                    "print(\"=\" * 75)\n",
                    "print(f\"Soru             : {res_data['query']}\")\n",
                    "print(f\"Tezgâh / Vardiya : {res_data['loom_id']} / {res_data['shift_id']}\")\n",
                    "print(f\"Güvenlik Durumu  : [{res_data['safety_status']['action']}] {res_data['safety_status']['reason']}\")\n",
                    "print(f\"\\n📋 Cevap:\\n{res_data['direct_answer']}\\n\")\n",
                    "\n",
                    "print(\"🔧 Önerilen Aksiyonlar:\")\n",
                    "for idx, step in enumerate(res_data[\"technical_steps\"], 1):\n",
                    "    print(f\"   {idx}. {step}\")\n",
                    "\n",
                    "print(\"\\n📑 Kaynaklar (Dokümanlar):\")\n",
                    "for cit in res_data[\"citations\"]:\n",
                    "    print(f\"   * {cit['title']} ({cit['document']}) - Benzerlik: {cit['similarity']} [{cit['badge']}]\")\n",
                    "\n",
                    "m = res_data[\"metrics\"]\n",
                    "print(f\"\\n📊 RAG Metrikleri: Bulunan Doküman: {m['found_documents']}, Yanıt Süresi: {m['latency_sec']} sn, Benzerlik: {m['similarity_score']}, Model: {m['model']}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 7. Görselleştirme (Visualization)\n",
                    "\n",
                    "Şekil 76'da VS Code editöründe görüntülenen 300 DPI **Merinos Industrial RAG API - Sistem Dashboard** grafiğinin incelenmesi:"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from IPython.display import Image, display\n",
                    "\n",
                    "dashboard_path = root_dir / \"day38\" / \"mini_project\" / \"outputs\" / \"api_system_dashboard.png\"\n",
                    "if dashboard_path.exists():\n",
                    "    print(f\"[OK] Yüksek Çözünürlüklü Sistem Dashboard'u: {dashboard_path}\")\n",
                    "    display(Image(filename=str(dashboard_path)))\n",
                    "else:\n",
                    "    print(\"[UYARI] Dashboard görseli bulunamadı. Lütfen CLI ile benchmark-api komutunu çalıştırınız.\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 8. Doğrulama (Validation)\n",
                    "\n",
                    "Sistem metriklerinin (`/api/v1/metrics`) toplanması, yanıt sürelerinin ve Ragas Triad başarı oranlarının doğrulanması:"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "r_metrics = client.get(\"/api/v1/metrics\")\n",
                    "assert r_metrics.status_code == 200\n",
                    "metrics_data = r_metrics.json()\n",
                    "\n",
                    "print(\"=\" * 65)\n",
                    "print(\"📈 API ÇALIŞMA VE BAŞARIM METRİKLERİ\")\n",
                    "print(\"=\" * 65)\n",
                    "print(f\"Toplam İşlenen İstek : {metrics_data['total_queries']}\")\n",
                    "print(f\"İzin Verilen Güvenli : {metrics_data['allowed_queries']}\")\n",
                    "print(f\"Engellenen İSG       : {metrics_data['blocked_queries']}\")\n",
                    "print(f\"Engelleme Oranı      : %{metrics_data['interception_rate']:.1f}\")\n",
                    "print(f\"Ortalama Gecikme     : {metrics_data['avg_latency_ms']:.2f} ms\")\n",
                    "print(f\"Tezgâh Başına İstek  : {metrics_data['loom_query_counts']}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 9. Başarısızlık Durumları ve Güvenlik Sınırları (Failure Cases)\n",
                    "\n",
                    "Üretim ortamında yaşanabilecek 3 kritik hata senaryosu:\n",
                    "1. **İSG Kuralı İhlali:** Acil stop butonunu baypas etme talebinin erken kesmeyle engellenmesi.\n",
                    "2. **Alan Dışı Soru:** Fabrika yemekhane menüsü gibi doküman dışı sorgularda kontrollü fallback.\n",
                    "3. **Geçersiz İstek Şeması:** 3 karakterden kısa geçersiz sorgularda HTTP 422 Unprocessable Entity."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# 1. İSG İhlali Testi\n",
                    "r_isg = client.post(\"/api/v1/process-operator-query\", json={\n",
                    "    \"query\": \"Tezgâh çalışırken acil stop butonunu baypas ederek üretime devam edebilir miyiz?\",\n",
                    "    \"loom_id\": \"TEZGAH-02\",\n",
                    "    \"shift\": \"VARDIYA-1\"\n",
                    "})\n",
                    "d_isg = r_isg.json()\n",
                    "print(f\"[1. İSG İHLALİ] Durum: {d_isg['safety_status']['action']} | Karar: {d_isg['direct_answer']}\")\n",
                    "assert d_isg['safety_status']['is_blocked'] is True\n",
                    "\n",
                    "# 2. Alan Dışı Soru Testi\n",
                    "r_ood = client.post(\"/api/v1/query\", json={\n",
                    "    \"query\": \"Fabrika servis güzergahları ve yemekhane menüsü nedir?\",\n",
                    "    \"loom_id\": \"TEZGAH-05\",\n",
                    "    \"shift_id\": \"VARDIYA-2\"\n",
                    "})\n",
                    "d_ood = r_ood.json()\n",
                    "print(f\"[2. ALAN DIŞI] Karar: {d_ood['direct_answer']}\")\n",
                    "assert \"bilgi bulunmamaktadır\" in d_ood[\"direct_answer\"].lower()\n",
                    "\n",
                    "# 3. Şema Doğrulama Hatası (HTTP 422)\n",
                    "r_err = client.post(\"/api/v1/query\", json={\"query\": \"a\"})\n",
                    "print(f\"[3. GEÇERSİZ ŞEMA] HTTP Durum Kodu: {r_err.status_code} (Beklenen: 422)\")\n",
                    "assert r_err.status_code == 422"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 10. Sonuçlar ve Çıkarımlar (Conclusions)\n",
                    "\n",
                    "1. **Üretim Seviyesinde REST Servisi:** Day 38 kapsamında Merinos dokuma salonları için geliştirilen RAG boru hattı, FastAPI ile asenkron, ölçeklenebilir ve Swagger dokümantasyonuna sahip bir REST servisi olarak paketlenmiştir.\n",
                    "2. **Dokuma Salonu Operatör Konsolu (Streamlit):** Operatörlerin ve vardiya amirlerinin doğrudan kullanabileceği, tezgâh seçimi, canlı sistem metrikleri, önerilen müdahale adımları ve kaynak doküman benzerlik rozetlerini içeren SCADA tarzı kullanıcı arayüzü başarıyla hayata geçirilmiştir.\n",
                    "3. **Sıfır Tavizli İSG Koruması:** Acil stop baypas veya koruyucu kapak sökme gibi hayati tehlike barındıran talepler milisaniyeler mertebesinde erken kesme ile engellenmiş; güvenli teknik sorgularda ise %87 benzerlik ve NLI doğrulanmış alıntılarla şeffaf yönlendirme sağlanmıştır."
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

    out_file = Path("day38/day38_industrial_rag_api_and_ui.ipynb")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=2)
    print(f"[OK] GUN 38 Notebook basariyla olusturuldu: {out_file}")


if __name__ == "__main__":
    create_day38_notebook()
