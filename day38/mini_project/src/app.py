# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 38
FastAPI Endüstriyel REST Servis Uygulaması (Şekil 75 ve Şekil 76)
"""

from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .service import IndustrialRagService
from day38.mini_project.src.models import (
    OperatorQuery,
    OperatorQueryRequest,
    OperatorQueryResponse,
    GuardrailCheckRequest,
    GuardrailStatusDto,
    HealthResponse,
    SystemMetricsResponse,
    LoomListResponse
)


app = FastAPI(
    title="Merinos Industrial RAG API",
    description="Teknik doküman arama ve cevap hazırlama sistemi",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS Middleware Ekleme
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = IndustrialRagService.get_instance()


def get_rag_service() -> IndustrialRagService:
    """FastAPI bağımlılık enjeksiyonu için servis sağlayıcı."""
    return rag_service


@app.get("/", tags=["Genel"])
def root() -> Dict[str, Any]:
    """Kök karşılama ve servis genel bilgisi."""
    return {
        "service": "Merinos Industrial RAG API",
        "version": "1.0.0",
        "description": "Teknik doküman arama ve cevap hazırlama sistemi",
        "facility": "Merinos Halı Sanayi A.Ş. - Gaziantep 4. OSB",
        "status": "OPERATIONAL",
        "docs_url": "/api/v1/docs"
    }


@app.post(
    "/api/v1/process-operator-query",
    tags=["default"],
    summary="Teknik dokümanlarda arama yapar ve operatör sorusuna cevap hazırlar."
)
async def process_operator_query(request: OperatorQuery):
    """
    Şekil 75 Uyumlu Uç Nokta:
    Teknik dokümanlarda arama yapar ve operatör sorusuna cevap hazırlar.
    """
    try:
        result = rag_service.process_query(
            query=request.query,
            loom_id=request.loom_id,
            shift=request.shift,
            operator_id=request.operator_id,
            top_k=request.top_k
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/v1/query",
    response_model=OperatorQueryResponse,
    status_code=status.HTTP_200_OK,
    tags=["Operatör Asistanı"]
)
def process_operator_query_v1(
    req: OperatorQueryRequest,
    service: IndustrialRagService = Depends(get_rag_service)
) -> OperatorQueryResponse:
    """
    Dokuma salonu operatörünün teknik sorusunu veya arıza semptomunu işler:
    1. Girdi İSG Korkuluğu Denetimi (Input Guardrail)
    2. Hibrit Arama (BM25 + Dense Vektör)
    3. Yapılandırılmış Yanıt Üretimi ve Katı Alıntı Doğrulama
    4. Ragas Triad Metrik Analizi
    5. Çıktı Güvenlik ve Halüsinasyon Baskılama Korkuluğu (Output Guardrail)
    """
    try:
        response = service.process_query(req)
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sorgu işlenirken endüstriyel sunucu hatası oluştu: {str(exc)}"
        )


@app.get("/api/v1/health", response_model=HealthResponse, tags=["İzleme & Teşhis"])
def get_health(service: IndustrialRagService = Depends(get_rag_service)) -> HealthResponse:
    """API ve bilgi tabanı alt sistemlerinin canlılık/sağlık durumunu döner."""
    return service.get_health()


@app.get("/api/v1/metrics", response_model=SystemMetricsResponse, tags=["İzleme & Teşhis"])
def get_metrics(service: IndustrialRagService = Depends(get_rag_service)) -> SystemMetricsResponse:
    """Toplam sorgu, İSG engelleme oranları ve ortalama yanıt sürelerini döner."""
    return service.get_metrics()


@app.get("/api/v1/looms", response_model=LoomListResponse, tags=["Fabrika Envanteri"])
def get_looms(service: IndustrialRagService = Depends(get_rag_service)) -> LoomListResponse:
    """Dokuma salonundaki aktif Van de Wiele ve Schönherr tezgâhlarını listeler."""
    return service.get_looms()


@app.post("/api/v1/guardrails/check", response_model=GuardrailStatusDto, tags=["Güvenlik & İSG"])
def check_guardrail(
    req: GuardrailCheckRequest,
    service: IndustrialRagService = Depends(get_rag_service)
) -> GuardrailStatusDto:
    """
    Sorguyu arama veya modele göndermeden önce hızlı İSG ve tehlike kontrolünden geçirir.
    Acil durdurma baypas veya koruma kapağı sökme gibi ihlallerde erken uyarı verir.
    """
    return service.check_guardrail(text=req.text, check_type=req.check_type)
