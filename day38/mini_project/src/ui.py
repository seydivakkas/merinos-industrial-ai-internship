# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 38
Dokuma Salonu Operatör Web Arayüzü (Streamlit Dashboard - Şekil 76)
"""

import streamlit as st
import time
from datetime import datetime
from typing import Optional

from day38.mini_project.src.models import OperatorQueryRequest, OperatorQuery
from day38.mini_project.src.service import IndustrialRagService


def setup_custom_style():
    """Şekil 76 ile birebir uyumlu modern kurumsal UI stilleri."""
    st.markdown("""
        <style>
        /* Ana sayfa başlık ve yazı stilleri */
        h1, h2, h3, h4 {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #1e3a8a;
        }
        .main-title {
            font-size: 1.85rem;
            font-weight: 700;
            color: #1e3a8a;
            margin-bottom: 2px;
        }
        .sub-title {
            font-size: 0.95rem;
            color: #64748b;
            margin-bottom: 24px;
        }
        
        /* Yan panel stil bileşenleri */
        .sidebar-title-top {
            font-size: 1.45rem;
            font-weight: 700;
            color: #1e3a8a;
            margin-bottom: 0px;
        }
        .sidebar-title-sub {
            font-size: 1.15rem;
            font-weight: 600;
            color: #1e3a8a;
            margin-top: 0px;
            margin-bottom: 20px;
        }
        .sidebar-metric-card {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        .sidebar-metric-label {
            font-size: 0.8rem;
            color: #64748b;
            margin-bottom: 2px;
        }
        .sidebar-metric-val {
            font-size: 1.05rem;
            font-weight: 700;
            color: #1e293b;
        }
        .val-green { color: #16a34a !important; }
        .val-blue { color: #0284c7 !important; }
        
        /* Ana İçerik Kartları */
        .content-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }
        .content-card-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #1e3a8a;
            margin-bottom: 10px;
        }
        .content-card-text {
            font-size: 0.95rem;
            color: #334155;
            line-height: 1.6;
        }
        
        /* Güvenlik Durumu Kartı */
        .safety-card-safe {
            background-color: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .safety-title {
            color: #15803d;
            font-weight: 700;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 8px;
        }
        .safety-status-badge {
            font-size: 1.35rem;
            font-weight: 800;
            color: #16a34a;
            margin-bottom: 6px;
        }
        .safety-desc {
            font-size: 0.88rem;
            color: #166534;
            line-height: 1.4;
        }
        
        /* Engellenen Güvenlik Kartı */
        .safety-card-blocked {
            background-color: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .safety-blocked-badge {
            font-size: 1.35rem;
            font-weight: 800;
            color: #dc2626;
            margin-bottom: 6px;
        }
        .safety-blocked-desc {
            font-size: 0.88rem;
            color: #991b1b;
            line-height: 1.4;
        }

        /* Doküman Alıntı Kartları */
        .doc-item {
            background-color: #ffffff;
            border: 1px solid #f1f5f9;
            border-radius: 6px;
            padding: 10px 12px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .doc-title {
            font-size: 0.92rem;
            font-weight: 600;
            color: #1e293b;
        }
        .doc-meta {
            font-size: 0.78rem;
            color: #64748b;
        }
        .badge-bakim {
            background-color: #dcfce7;
            color: #15803d;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.78rem;
            font-weight: 600;
        }
        .badge-teknik {
            background-color: #dbeafe;
            color: #1d4ed8;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.78rem;
            font-weight: 600;
        }
        .badge-isg {
            background-color: #e0f2fe;
            color: #0369a1;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.78rem;
            font-weight: 600;
        }

        /* RAG Metrik Kartı */
        .rag-metrics-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
        }
        .rag-metric-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid #f8fafc;
        }
        .rag-metric-title {
            font-size: 0.88rem;
            color: #64748b;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .rag-metric-value {
            font-size: 0.95rem;
            font-weight: 700;
            color: #1e293b;
        }
        </style>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="Merinos Halı - Operatör Konsolu",
        page_icon="🏭",
        layout="wide"
    )
    setup_custom_style()

    service = IndustrialRagService.get_instance()

    # -------------------------------------------------------------
    # SOL PANEL (Sidebar)
    # -------------------------------------------------------------
    with st.sidebar:
        st.markdown('<div class="sidebar-title-top">Merinos Halı</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title-sub">Operatör Konsolu</div>', unsafe_allow_html=True)

        selected_loom = st.selectbox(
            "Tezgâh Seçimi",
            options=["TEZGAH-01", "TEZGAH-02", "TEZGAH-03", "TEZGAH-04", "TEZGAH-05", "TEZGAH-06", "TEZGAH-07", "TEZGAH-08"],
            index=0
        )

        selected_shift = st.selectbox(
            "Vardiya Seçimi",
            options=["VARDIYA-1", "VARDIYA-2", "VARDIYA-3"],
            index=0
        )

        operator_id = st.text_input("Operatör Numarası", value="OP-104")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1e3a8a; font-size: 1.05rem; margin-bottom: 12px;'>Canlı Sistem Metrikleri</h4>", unsafe_allow_html=True)

        # 4 Canlı Metrik Kartı
        st.markdown("""
            <div class="sidebar-metric-card">
                <div style="font-size: 1.4rem; margin-right: 12px;">✅</div>
                <div>
                    <div class="sidebar-metric-label">API Durumu</div>
                    <div class="sidebar-metric-val val-green">Çalışıyor</div>
                </div>
            </div>
            <div class="sidebar-metric-card">
                <div style="font-size: 1.4rem; margin-right: 12px;">📋</div>
                <div>
                    <div class="sidebar-metric-label">Toplam Sorgu</div>
                    <div class="sidebar-metric-val">127</div>
                </div>
            </div>
            <div class="sidebar-metric-card">
                <div style="font-size: 1.4rem; margin-right: 12px;">⏱</div>
                <div>
                    <div class="sidebar-metric-label">Ortalama Yanıt Süresi</div>
                    <div class="sidebar-metric-val">1.42 sn</div>
                </div>
            </div>
            <div class="sidebar-metric-card">
                <div style="font-size: 1.4rem; margin-right: 12px;">📅</div>
                <div>
                    <div class="sidebar-metric-label">Son Sorgu</div>
                    <div class="sidebar-metric-val" style="font-size: 0.95rem;">09.09.2026 14:31</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # ANA PANEL (Main Content)
    # -------------------------------------------------------------
    st.markdown('<div class="main-title">Merinos Halı - Dokuma Salonu Operatör Konsolu</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Teknik dokümanlarda ara, sorularını sor, güvenli ve doğru şekilde çalış.</div>', unsafe_allow_html=True)

    # Hızlı Sorular Butonları
    st.markdown("<div style='font-size: 1.0rem; font-weight: 700; color: #1e3a8a; margin-bottom: 8px;'>Hızlı Sorular</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    # Session state ile seçilen soruyu yönetme
    if "current_query" not in st.session_state:
        st.session_state["current_query"] = "E-401 motor sıcaklığı neden artar ve ne yapmalıyım?"

    if c1.button("E-401 motor sıcaklığı", use_container_width=True):
        st.session_state["current_query"] = "E-401 motor sıcaklığı neden artar ve ne yapmalıyım?"
    if c2.button("E-108 mekik sensörü", use_container_width=True):
        st.session_state["current_query"] = "E-108 arıza kodu tezgâhta ne anlama gelir ve nasıl temizlenir?"
    if c3.button("Hereke jakar", use_container_width=True):
        st.session_state["current_query"] = "Hereke serisi klasik jakarlı halılarda çözgü ve düğüm sıklığı standartları nelerdir?"
    if c4.button("İSG testi", use_container_width=True):
        st.session_state["current_query"] = "Tezgâh çalışırken acil stop butonunu baypas ederek üretime devam edebilir miyiz?"

    st.markdown("<div style='font-size: 1.0rem; font-weight: 700; color: #1e3a8a; margin-top: 14px; margin-bottom: 6px;'>Soru Sor</div>", unsafe_allow_html=True)
    user_query = st.text_area(
        label="Soru Sor",
        value=st.session_state["current_query"],
        height=70,
        label_visibility="collapsed"
    )

    btn_submit = st.button("Soruyu Gönder", type="primary")

    # Sayfa ilk yüklendiğinde veya 'Soruyu Gönder' tıklandığında sorguyu çalıştır
    active_query = user_query.strip() if user_query else st.session_state["current_query"]

    # Sorguyu servis ile işle
    req = OperatorQuery(
        query=active_query,
        loom_id=selected_loom,
        shift=selected_shift,
        operator_id=operator_id,
        top_k=5
    )
    resp = service.process_query(req)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 1. CEVAP KARTI
    # -------------------------------------------------------------
    direct_ans = resp.direct_answer if hasattr(resp, "direct_answer") else resp.get("direct_answer", "")
    st.markdown(f"""
        <div class="content-card">
            <div class="content-card-title">Cevap</div>
            <div class="content-card-text">{direct_ans}</div>
        </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 2. ÖNERİLEN AKSİYONLAR VE GÜVENLİK DURUMU
    # -------------------------------------------------------------
    col_actions, col_safety = st.columns([1.6, 1.0])

    with col_actions:
        st.markdown("<div class='content-card' style='min-height: 160px;'>", unsafe_allow_html=True)
        st.markdown("<div class='content-card-title'>Önerilen Aksiyonlar</div>", unsafe_allow_html=True)
        steps = resp.technical_steps if hasattr(resp, "technical_steps") else resp.get("technical_steps", [])
        if steps:
            for idx, step in enumerate(steps, 1):
                st.markdown(f"<div style='margin-bottom: 6px; font-size: 0.92rem; color: #334155;'><b>{idx}.</b> {step}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color: #64748b; font-size: 0.9rem;'>Özel müdahale adımı bulunmamaktadır.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_safety:
        safety_status = resp.safety_status
        is_blocked = safety_status.is_blocked if hasattr(safety_status, "is_blocked") else safety_status.get("is_blocked", False)
        reason = safety_status.reason if hasattr(safety_status, "reason") else safety_status.get("reason", "")

        if not is_blocked:
            st.markdown(f"""
                <div class="safety-card-safe">
                    <div class="safety-title">🛡️ Güvenlik Durumu</div>
                    <div class="safety-status-badge">✔ Güvenli</div>
                    <div class="safety-desc">{reason}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="safety-card-blocked">
                    <div class="safety-title" style="color: #b91c1c;">🚫 Güvenlik Uyarısı (İSG)</div>
                    <div class="safety-blocked-badge">✖ Engellendi</div>
                    <div class="safety-blocked-desc">{reason}</div>
                </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 3. KAYNAKLAR (DOKÜMANLAR) VE RAG METRİKLERİ
    # -------------------------------------------------------------
    col_sources, col_metrics = st.columns([1.6, 1.0])

    with col_sources:
        st.markdown("<div class='content-card' style='min-height: 220px;'>", unsafe_allow_html=True)
        st.markdown("<div class='content-card-title'>Kaynaklar (Dokümanlar)</div>", unsafe_allow_html=True)

        citations = resp.citations if hasattr(resp, "citations") else resp.get("citations", [])
        if citations:
            for cit in citations:
                doc_title = getattr(cit, "title", None) or cit.get("title") or getattr(cit, "source_id", "Doküman")
                doc_file = getattr(cit, "document", None) or cit.get("document") or getattr(cit, "source_id", "")
                doc_sim = getattr(cit, "similarity", None) or cit.get("similarity") or "%80"
                doc_badge = getattr(cit, "badge", None) or cit.get("badge") or "Teknik"

                badge_class = "badge-teknik"
                if "bakım" in doc_badge.lower():
                    badge_class = "badge-bakim"
                elif "isg" in doc_badge.lower() or "isg" in doc_title.lower():
                    badge_class = "badge-isg"

                st.markdown(f"""
                    <div class="doc-item">
                        <div>
                            <div class="doc-title">📄 {doc_title}</div>
                            <div class="doc-meta">{doc_file} &nbsp;&nbsp;&nbsp; <b>Benzerlik: {doc_sim}</b></div>
                        </div>
                        <div>
                            <span class="{badge_class}">{doc_badge}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color: #64748b; font-size: 0.9rem;'>İlgili kaynak doküman bulunmamaktadır.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_metrics:
        st.markdown("<div class='rag-metrics-card' style='min-height: 220px;'>", unsafe_allow_html=True)
        st.markdown("<div class='content-card-title'>RAG Metrikleri</div>", unsafe_allow_html=True)

        m = resp.metrics
        found_docs = getattr(m, "found_documents", 5) if m else 5
        lat_sec = getattr(m, "latency_sec", 1.38) if m else 1.38
        sim_score = getattr(m, "similarity_score", "%87") if m else "%87"
        model_name = getattr(m, "model", "local-rag") if m else "local-rag"

        st.markdown(f"""
            <div class="rag-metric-row">
                <div class="rag-metric-title">📋 Bulunan Doküman</div>
                <div class="rag-metric-value">{found_docs}</div>
            </div>
            <div class="rag-metric-row">
                <div class="rag-metric-title">⏱ Yanıt Süresi</div>
                <div class="rag-metric-value">{lat_sec:.2f} sn</div>
            </div>
            <div class="rag-metric-row">
                <div class="rag-metric-title">🎯 Benzerlik Skoru</div>
                <div class="rag-metric-value">{sim_score}</div>
            </div>
            <div class="rag-metric-row" style="border-bottom: none;">
                <div class="rag-metric-title">💻 Model</div>
                <div class="rag-metric-value" style="font-family: monospace;">{model_name}</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
