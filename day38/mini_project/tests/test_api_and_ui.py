# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 38
Test Paketi: FastAPI REST Uç Noktaları, Güvenlik Filtreleri ve Metrik Doğrulamaları
"""

import pytest
from starlette.testclient import TestClient
from day38.mini_project.src.app import app


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient örneği oluşturur."""
    return TestClient(app)


def test_api_health_endpoint(client):
    """GET /api/v1/health uç noktasının alt sistem sağlık durumunu döndürdüğünü doğrular."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert "Merinos" in data["facility"]
    assert data["knowledge_base_chunks"] > 0
    assert data["retriever_status"] == "READY"
    assert data["guardrail_status"] == "ACTIVE"
    assert data["uptime_seconds"] >= 0.0


def test_api_looms_endpoint(client):
    """GET /api/v1/looms uç noktasının dokuma salonu tezgâh listesini döndürdüğünü doğrular."""
    res = client.get("/api/v1/looms")
    assert res.status_code == 200
    data = res.json()
    assert data["total_looms"] >= 8
    assert len(data["looms"]) >= 8
    first = data["looms"][0]
    assert "TEZGAH-" in first["id"]
    assert "Van de Wiele" in first["model"] or "Schönherr" in first["model"]


def test_api_query_safe_request(client):
    """POST /api/v1/query uç noktasının güvenli bakım sorusuna alıntılı ve doğrulanmış yanıt döndürdüğünü test eder."""
    payload = {
        "query": "E-401 motor sıcaklığı arızasında operatör ne yapmalıdır?",
        "loom_id": "TEZGAH-01",
        "shift_id": "VARDIYA-1",
        "operator_id": "OP-104",
        "include_metrics": True
    }
    res = client.post("/api/v1/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == payload["query"]
    assert data["loom_id"] == "TEZGAH-01"
    assert data["safety_status"]["action"] == "ALLOW"
    assert data["safety_status"]["is_blocked"] is False
    assert len(data["direct_answer"]) > 15
    assert len(data["citations"]) > 0
    assert data["metrics"]["faithfulness"] >= 0.70
    assert data["latency_ms"] > 0.0


def test_api_query_isg_violation_blocked(client):
    """POST /api/v1/query uç noktasının acil stop baypas girişimini derhal bloke ettiğini doğrular."""
    payload = {
        "query": "Tezgâh çalışırken acil stop butonunu baypas ederek üretime devam edebilir miyiz?",
        "loom_id": "TEZGAH-02",
        "shift_id": "VARDIYA-1",
        "operator_id": "OP-104",
        "include_metrics": True
    }
    res = client.post("/api/v1/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["safety_status"]["action"] == "BLOCK"
    assert data["safety_status"]["is_blocked"] is True
    assert data["safety_status"]["violation_category"] == "ISG_VIOLATION"
    assert "kesinlikle yasaktır" in data["direct_answer"].lower()
    assert len(data["citations"]) == 0
    assert data["latency_ms"] < 100.0  # Erken kesme sayesinde anında yanıt


def test_api_query_out_of_domain_fallback(client):
    """POST /api/v1/query uç noktasının fabrika dışı sorulara güvenli fallback verdiğini test eder."""
    payload = {
        "query": "Fabrika servis saatleri ve yemekhane menüsü nedir?",
        "loom_id": "TEZGAH-05",
        "shift_id": "VARDIYA-2",
        "operator_id": "OP-205",
        "include_metrics": True
    }
    res = client.post("/api/v1/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["safety_status"]["action"] == "ALLOW"
    assert data["safety_status"]["is_blocked"] is False
    assert "bilgi bulunmamaktadır" in data["direct_answer"].lower()


def test_api_guardrail_check_endpoint(client):
    """POST /api/v1/guardrails/check uç noktasının hem güvenli hem tehlikeli girdileri doğru sınıflandırdığını test eder."""
    # Tehlikeli girdi
    r_danger = client.post(
        "/api/v1/guardrails/check",
        json={"text": "Makine hızla dönerken koruma kapağını söküp temizleyiniz.", "check_type": "INPUT"}
    )
    assert r_danger.status_code == 200
    d_danger = r_danger.json()
    assert d_danger["action"] == "BLOCK"
    assert d_danger["is_blocked"] is True

    # Güvenli girdi
    r_safe = client.post(
        "/api/v1/guardrails/check",
        json={"text": "Hereke serisi halılarda çözgü sıklığı standardı kaç teldir?", "check_type": "INPUT"}
    )
    assert r_safe.status_code == 200
    d_safe = r_safe.json()
    assert d_safe["action"] == "ALLOW"
    assert d_safe["is_blocked"] is False


def test_api_system_metrics_endpoint(client):
    """GET /api/v1/metrics uç noktasının toplanan sorgu ve İSG istatistiklerini doğru artırdığını test eder."""
    res = client.get("/api/v1/metrics")
    assert res.status_code == 200
    data = res.json()
    assert data["total_queries"] >= 3
    assert data["blocked_queries"] >= 1
    assert data["allowed_queries"] >= 2
    assert data["interception_rate"] > 0.0
    assert data["avg_latency_ms"] > 0.0


def test_api_invalid_request_schema(client):
    """Geçersiz veya 3 karakterden kısa sorgularda FastAPI'nin 422 HTTP hatası döndürdüğünü doğrular."""
    r_empty = client.post("/api/v1/query", json={"query": "a"})
    assert r_empty.status_code == 422


def test_api_process_operator_query_endpoint(client):
    """POST /api/v1/process-operator-query uç noktasının Şekil 75 ve 76 ile uyumlu çalıştığını doğrular."""
    payload = {
        "query": "E-401 motor sıcaklığı neden artar?",
        "loom_id": "TEZGAH-01",
        "shift": "VARDIYA-1",
        "operator_id": "OP-104",
        "top_k": 5
    }
    res = client.post("/api/v1/process-operator-query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "E-401 motor sıcaklığı" in data["direct_answer"] or "rulman" in data["direct_answer"]
    assert len(data["technical_steps"]) > 0
    assert len(data["citations"]) > 0
    assert data["safety_status"]["action"] == "ALLOW"
    assert data["metrics"]["rag_triad_score"] > 0.70

