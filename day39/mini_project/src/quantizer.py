# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 39
Model Kuantizasyon Motoru: Post-Training Dynamic Quantization (PTQ - INT8)
"""

import torch
import os
import shutil
import tempfile
import numpy as np
from typing import Dict, Tuple, Optional, Any
from pathlib import Path
from onnxruntime.quantization import quantize_dynamic, QuantType

from day39.mini_project.src.models import ModelSizeReport


class ModelQuantizer:
    """Model quantization utilities for edge deployment."""

    def __init__(
        self,
        model=None,
        output_dir: str = "outputs",
        weight_type: QuantType = QuantType.QInt8,
        per_channel: bool = True
    ):
        self.model = model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.weight_type = weight_type
        self.per_channel = per_channel

    def quantize_to_int8(self, onnx_path: str, output_path: Optional[str] = None) -> ModelSizeReport:
        """Quantize ONNX model to INT8 format."""
        if output_path is None:
            model_stem = Path(onnx_path).stem
            output_path = str(self.output_dir / f"{model_stem}_int8.onnx")

        if getattr(self, "verbose", False):
            print(f"Quantizing {onnx_path} to INT8...")
        from onnxruntime.quantization import (
            quantize_dynamic,
            QuantType
        )

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        try:
            quantize_dynamic(
                model_input=onnx_path,
                model_output=output_path,
                weight_type=QuantType.QInt8
            )
        except Exception:
            # Windows ASCII olmayan karakter içeren yollarda yedek güvenli geçici dizin kullanımı
            with tempfile.TemporaryDirectory() as td:
                tmp_in = os.path.join(td, "model_fp32.onnx")
                tmp_out = os.path.join(td, "model_int8.onnx")
                shutil.copyfile(onnx_path, tmp_in)
                quantize_dynamic(
                    model_input=tmp_in,
                    model_output=tmp_out,
                    weight_type=QuantType.QInt8,
                    per_channel=self.per_channel,
                    reduce_range=False
                )
                shutil.copyfile(tmp_out, output_path)

        orig_size = os.path.getsize(onnx_path)
        quant_size = os.path.getsize(output_path)

        orig_mb = round(orig_size / (1024 * 1024), 3)
        quant_mb = round(quant_size / (1024 * 1024), 3)

        reduction_pct = round((1.0 - (quant_size / orig_size)) * 100.0, 2)
        compression_ratio = round(orig_size / max(quant_size, 1), 2)

        return ModelSizeReport(
            original_bytes=orig_size,
            original_mb=orig_mb,
            quantized_bytes=quant_size,
            quantized_mb=quant_mb,
            reduction_percentage=reduction_pct,
            compression_ratio=compression_ratio
        )

    @staticmethod
    def manual_quantize_int8(
        tensor: np.ndarray,
        symmetric: bool = True
    ) -> Tuple[np.ndarray, float, int]:
        """Eğitim ve matematiksel doğrulama için analitik INT8 kuantizasyon fonksiyonu.
        
        Döndürür: (kuantize_tensör, scale S, zero_point Z)
        """
        tensor_float = tensor.astype(np.float32)
        if symmetric:
            max_val = np.max(np.abs(tensor_float))
            scale = float(max_val / 127.0) if max_val > 1e-12 else 1.0
            zero_point = 0
            q = np.clip(np.round(tensor_float / scale), -128, 127).astype(np.int8)
        else:
            min_val = np.min(tensor_float)
            max_val = np.max(tensor_float)
            range_val = max_val - min_val
            scale = float(range_val / 255.0) if range_val > 1e-12 else 1.0
            zero_point = int(np.clip(np.round(-min_val / scale) - 128, -128, 127))
            q = np.clip(np.round(tensor_float / scale) + zero_point, -128, 127).astype(np.int8)

        return q, scale, zero_point

    @staticmethod
    def manual_dequantize_int8(
        q_tensor: np.ndarray,
        scale: float,
        zero_point: int
    ) -> np.ndarray:
        """Kuantize tensörü gerçel sayılar uzayına de-kuantize eder."""
        return scale * (q_tensor.astype(np.float32) - float(zero_point))
