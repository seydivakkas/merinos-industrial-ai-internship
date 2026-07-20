"""
Merinos Industrial AI Internship - Day 28 (Phase 4 Capstone)
FastAPI Production Microservice for Industrial RAG & Quality Gate

Author: Seydi Eryılmaz (@seydivakkas)
Copyright (c) 2026 Seydi Eryılmaz. All Rights Reserved.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException

from day28.mini_project.src.models import (
    QueryRequest,
    GenerationResponse,
    GateCheckResult,
    SystemStats,
    DocumentItem
)
from day28.mini_project.src.document_indexer import DocumentIndexer
from day28.mini_project.src.hybrid_retriever import HybridRetriever
from day28.mini_project.src.generator_llm import GroundedGenerator
from day28.mini_project.src.deployment_gate import DeploymentGate

app = FastAPI(
    title="Merinos Phase 4 Capstone: Industrial RAG Service",
    description="Gaziantep 4. OSB Tesisleri Uçtan Uca Hibrit Getirme ve Kalite Kapısı Mikroservisi",
    version="1.0.0"
)

# Global Tekil Durum (Singleton Context)
_INDEXER: DocumentIndexer = None
_RETRIEVER: HybridRetriever = None
_GENERATOR: GroundedGenerator = None
_GATE: DeploymentGate = None


def get_pipeline():
    """Gerektiğinde hattı başlatır ve dokümanları indeksler."""
    global _INDEXER, _RETRIEVER, _GENERATOR, _GATE
    if _INDEXER is None:
        base_dir = Path(__file__).resolve().parent.parent
        corpus_path = base_dir / "fixtures" / "merinos_factory_corpus.json"
        with open(corpus_path, "r", encoding="utf-8") as f:
            raw_docs = json.load(f)
        docs = [DocumentItem(**d) for d in raw_docs]

        _INDEXER = DocumentIndexer(collection_name="merinos_capstone_kb")
        _INDEXER.build_indexes(docs)

        _RETRIEVER = HybridRetriever(_INDEXER, rrf_k=60, sparse_weight=0.4, dense_weight=0.6)
        _GENERATOR = GroundedGenerator()
        _GATE = DeploymentGate(_RETRIEVER, _GENERATOR)

    return _INDEXER, _RETRIEVER, _GENERATOR, _GATE


@app.get("/api/v1/health")
def health_check() -> Dict[str, Any]:
    """Mikroservis sağlık ve sürüm kontrolü."""
    return {
        "status": "healthy",
        "service": "merinos-industrial-rag",
        "phase": "Phase 4 Capstone",
        "version": "1.0.0"
    }


@app.get("/api/v1/stats", response_model=SystemStats)
def get_system_stats() -> SystemStats:
    """İndekslenen korpus ve vektör istatistiklerini döner."""
    indexer, _, _, _ = get_pipeline()
    departments = sorted(list({ch.department for ch in indexer.chunks}))
    machines = sorted(list({ch.machine for ch in indexer.chunks}))

    return SystemStats(
        corpus_document_count=len({ch.doc_id for ch in indexer.chunks}),
        total_chunks=len(indexer.chunks),
        bm25_vocab_size=len(indexer.bm25_index.doc_freqs),
        qdrant_vector_count=len(indexer.chunks),
        quantization_type="INT8",
        departments=departments,
        machines=machines
    )


@app.post("/api/v1/query", response_model=GenerationResponse)
def query_rag(request: QueryRequest) -> GenerationResponse:
    """Uçtan uca RAG sorgulaması ve alıntı destekli cevap üretimi."""
    _, retriever, generator, _ = get_pipeline()
    try:
        candidates, latencies = retriever.retrieve(request)
        response = generator.generate(request, candidates, latencies)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG sorgulama hatası: {str(e)}")


@app.post("/api/v1/gate-check", response_model=GateCheckResult)
def run_deployment_gate_check() -> GateCheckResult:
    """Tüm doğrulama sorgularını koşturarak otomatik canlıya geçiş onayını denetler."""
    _, _, _, gate = get_pipeline()
    base_dir = Path(__file__).resolve().parent.parent
    queries_path = base_dir / "fixtures" / "capstone_queries.json"
    with open(queries_path, "r", encoding="utf-8") as f:
        queries = json.load(f)

    result = gate.run_gate_audit(queries)
    return result
