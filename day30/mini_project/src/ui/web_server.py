# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 30
FastAPI Web Server for Integrated Carpet Design & Visual Analysis Cockpit.
Staj Defteri Yaprak 60 Uyarınca Basit ve Anlaşılır Web Arayüzü Sunucusu.
"""

from __future__ import annotations
import base64
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import cv2
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import numpy as np

from day30.mini_project.src.models import (
    CarpetDesignInput,
    IntegratedPipelineOutput,
    PromptAssemblyResult,
    SymmetryMode,
    TechnicalLimitationsReport,
)
from day30.mini_project.src.pipeline import IntegratedCarpetPipeline, DEFAULT_LIMITATIONS
from day30.mini_project.src.visualizer import CarpetPipelineVisualizer

logger = logging.getLogger("MerinosDay30WebServer")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UI_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = BASE_DIR / "mini_project" / "fixtures"
OUTPUTS_DIR = BASE_DIR / "mini_project" / "outputs"

app = FastAPI(
    title="Merinos Endüstriyel Yapay Zekâ — Tümleşik Halı Tasarım & Görsel Analiz Kokpiti",
    description="Staj Defteri Yaprak 59 ve 60 müfredatına dayalı halı desen üretimi, çok boyutlu görsel analiz ve benzerlik arama servisi.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline_instance = IntegratedCarpetPipeline(output_dir=str(OUTPUTS_DIR))
visualizer_instance = CarpetPipelineVisualizer(dpi=150)


def _image_to_base64(img_path_or_rgb: Any) -> str:
    """Görüntüyü Web UI için base64 data URI formatına dönüştürür."""
    try:
        if isinstance(img_path_or_rgb, (str, Path)):
            path = Path(img_path_or_rgb)
            if path.exists():
                with open(path, "rb") as f:
                    data = f.read()
                return f"data:image/png;base64,{base64.b64encode(data).decode('utf-8')}"
        elif isinstance(img_path_or_rgb, np.ndarray):
            bgr = cv2.cvtColor(img_path_or_rgb, cv2.COLOR_RGB2BGR)
            success, buffer = cv2.imencode(".png", bgr)
            if success:
                return f"data:image/png;base64,{base64.b64encode(buffer).decode('utf-8')}"
    except Exception as e:
        logger.warning(f"Base64 dönüşüm hatası: {e}")
    return ""


# ------------------------------------------------------------------------------
# STATİK DOSYALAR VE ANA SAYFA
# ------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Ana kokpit HTML sayfasını sunar (Yaprak 60 Basit Arayüz)."""
    index_file = UI_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>Merinos Halı Tasarım Kokpiti (Day 30) - index.html bulunamadı</h1>", status_code=404)


@app.get("/style.css")
async def serve_css():
    css_file = UI_DIR / "style.css"
    if css_file.exists():
        return FileResponse(css_file, media_type="text/css")
    return Response(status_code=404)


@app.get("/app.js")
async def serve_js():
    js_file = UI_DIR / "app.js"
    if js_file.exists():
        return FileResponse(js_file, media_type="application/javascript")
    return Response(status_code=404)


from fastapi.staticfiles import StaticFiles
assets_dir = UI_DIR / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


# ------------------------------------------------------------------------------
# API UÇ NOKTALARI
# ------------------------------------------------------------------------------
@app.get("/api/health")
async def health_check():
    """Sistem sağlık kontrolü."""
    return {
        "status": "HEALTHY",
        "day": 30,
        "phase": "Phase 5 - Capstone (Day 28 Üretim + Day 29 Görsel Analiz)",
        "title": "Tümleşik Halı Tasarım & Çok Boyutlu Görsel Analiz Hattı",
        "internship": "Merinos Halı Sanayi ve Ticaret A.Ş. (Gaziantep 4. OSB)"
    }


@app.get("/api/pipeline/briefs")
async def get_sample_briefs():
    """Örnek tasarım briflerini döndürür."""
    briefs_file = FIXTURES_DIR / "sample_design_briefs.json"
    if briefs_file.exists():
        with open(briefs_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@app.get("/api/pipeline/yarns")
async def get_yarn_palette():
    """Merinos 16'lı kurumsal iplik bobin renk paletini döndürür."""
    palette_file = FIXTURES_DIR / "merinos_yarn_palette.json"
    if palette_file.exists():
        with open(palette_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@app.get("/api/pipeline/catalog")
async def get_reference_catalog():
    """CNN embedding referans halı kataloğunu döndürür."""
    catalog_file = FIXTURES_DIR / "reference_carpet_catalog.json"
    if catalog_file.exists():
        with open(catalog_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@app.get("/api/pipeline/limitations")
async def get_technical_limitations():
    """Staj Defteri Yaprak 60'ta belirtilen 4 temel teknik çalışma sınırını döndürür."""
    return DEFAULT_LIMITATIONS.model_dump()


@app.post("/api/pipeline/assemble-prompt")
@app.post("/api/pipeline/synthesize-prompt")
async def assemble_prompt(brief_data: Dict[str, Any]):
    """
    Day 28 Prompt Structurer ile kullanıcı girdisini sabit sırayla birleştirir.
    Zorunlu alan doğrulamasını yapar (Yaprak 59 & 60).
    """
    try:
        brief = CarpetDesignInput(**brief_data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Brif doğrulama hatası: {str(e)}")

    res = pipeline_instance.assemble_prompt(brief)
    return res.model_dump()


@app.post("/api/pipeline/run")
async def run_pipeline(brief_data: Dict[str, Any]):
    """
    Staj Defteri Yaprak 59 ve 60 Tümleşik Boru Hattını uçtan uca çalıştırır.
    Sonuçta üretilen görsel ve teşhis paneli base64 olarak döner.
    """
    try:
        brief = CarpetDesignInput(**brief_data)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Zorunlu alanlar eksik veya geçersiz (Yaprak 60 Boş Alan Hatası): {str(e)}"
        )

    output: IntegratedPipelineOutput = pipeline_instance.run(brief)

    # Master görsel teşhis panelini oluştur
    panel_path = OUTPUTS_DIR / f"{brief.brief_id}_panel.png"
    visualizer_instance.create_master_diagnostic_panel(
        output_data=output,
        save_path=panel_path
    )

    out_dict = output.model_dump()

    # Base64 görselleri enjekte et
    if output.generated_image_path and Path(output.generated_image_path).exists():
        out_dict["carpet_image_base64"] = _image_to_base64(output.generated_image_path)
    else:
        out_dict["carpet_image_base64"] = ""

    if panel_path.exists():
        out_dict["diagnostic_panel_base64"] = _image_to_base64(panel_path)
    else:
        out_dict["diagnostic_panel_base64"] = ""

    return out_dict


@app.post("/api/pipeline/empty-catalog-test")
async def test_empty_catalog(brief_data: Dict[str, Any]):
    """
    Yaprak 60 Testi: Referans kataloğun boş olduğu durumdaki fallback davranışını simüle eder.
    """
    try:
        brief = CarpetDesignInput(**brief_data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Brif geçersiz: {str(e)}")

    output = pipeline_instance.run(brief, empty_catalog_test=True)

    return {
        "status": "FALLBACK_VERIFIED",
        "similar_items_count": len(output.similar_carpets),
        "similar_items": output.similar_carpets,
        "message": "Referans katalog boş olduğu için sistem çökmeden zarif fallback sağlandı (Staj Defteri Yaprak 60)."
    }
