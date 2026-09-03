# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 39
ONNX İhracat Motoru: Bi-Encoder ve Cross-Encoder Modellerini PyTorch'tan ONNX'e Derleme
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import onnx
from typing import Tuple, Dict, Any, Optional
from pathlib import Path


class BiEncoderModule(nn.Module):
    """Bi-encoder model for document and query encoding."""

    def __init__(
        self,
        model: Optional[nn.Module] = None,
        device: str = "cpu",
        input_dim: int = 384,
        hidden_dim: int = 256,
        output_dim: int = 384
    ):
        super().__init__()
        self.model = model
        self.device = device
        # Tezgâh başı IPC çıkarımı için optimize edilmiş projeksiyon katmanları
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.activation = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)
        self.layer_norm = nn.LayerNorm(output_dim)

    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        if self.model is not None and attention_mask is not None:
            return self.model(input_ids=input_ids, attention_mask=attention_mask)
        x = input_ids
        h = self.activation(self.fc1(x))
        out = self.layer_norm(x + self.fc2(h))
        # L2 Normalization (Cosine similarity için birim vektör)
        norm = torch.norm(out, p=2, dim=-1, keepdim=True).clamp(min=1e-12)
        return out / norm

    # Pooling for sentence embeddings
    def encode(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        outputs = self.forward(input_ids, attention_mask)
        if hasattr(outputs, "last_hidden_state"):
            return outputs.last_hidden_state[:, 0, :]
        return outputs


class CrossEncoderModule(nn.Module):
    """Cross-encoder model for pairwise text matching."""

    def __init__(
        self,
        model: Optional[nn.Module] = None,
        device: str = "cpu",
        input_dim: int = 768,
        hidden_dim: int = 256,
        output_dim: int = 1
    ):
        super().__init__()
        self.model = model
        self.device = device
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.activation1 = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, 64)
        self.activation2 = nn.ReLU()
        self.fc3 = nn.Linear(64, output_dim)
        self.sigmoid = nn.Sigmoid()

    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        if self.model is not None and attention_mask is not None:
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            return outputs.logits
        x = input_ids
        q = x[:, :384]
        d = x[:, 384:]
        cos_sim = torch.sum(q * d, dim=-1, keepdim=True)
        h = self.activation1(self.fc1(x))
        h = self.activation2(self.fc2(h))
        logits = self.fc3(h) + 4.0 * cos_sim
        return self.sigmoid(logits)


class OnnxExporter:
    """Export models to ONNX format."""

    def __init__(self, output_dir: str = "outputs", opset_version: int = 17):
        self.output_dir = output_dir
        self.opset_version = opset_version

    def export_bi_encoder(
        self,
        output_path: Optional[str] = None,
        input_dim: int = 384,
        hidden_dim: int = 256,
        output_dim: int = 384,
        model: Optional[nn.Module] = None
    ) -> str:
        """Bi-Encoder modelini ONNX FP32 formatına derler."""
        if output_path is None:
            output_path = os.path.join(self.output_dir, "bi_encoder_fp32.onnx")
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        if model is None:
            model = BiEncoderModule(input_dim=input_dim, hidden_dim=hidden_dim, output_dim=output_dim)
        model.eval()

        dummy_input = torch.randn(1, input_dim, dtype=torch.float32)

        torch.onnx.export(
            model,
            (dummy_input,),
            output_path,
            input_names=["input_features"],
            output_names=["embeddings"],
            dynamic_axes={
                "input_features": {0: "batch_size"},
                "embeddings": {0: "batch_size"}
            },
            opset_version=self.opset_version,
            dynamo=False
        )

        # ONNX Graf Doğrulaması
        onnx_model = onnx.load(output_path)
        onnx.checker.check_model(onnx_model)
        return output_path

    def export_cross_encoder(
        self,
        output_path: Optional[str] = None,
        input_dim: int = 768,
        hidden_dim: int = 256,
        model: Optional[nn.Module] = None
    ) -> str:
        """Cross-Encoder modelini ONNX FP32 formatına derler."""
        if output_path is None:
            output_path = os.path.join(self.output_dir, "cross_encoder_fp32.onnx")
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        if model is None:
            model = CrossEncoderModule(input_dim=input_dim, hidden_dim=hidden_dim)
        model.eval()

        dummy_input = torch.randn(1, input_dim, dtype=torch.float32)

        torch.onnx.export(
            model,
            (dummy_input,),
            output_path,
            input_names=["pair_features"],
            output_names=["relevance_score"],
            dynamic_axes={
                "pair_features": {0: "batch_size"},
                "relevance_score": {0: "batch_size"}
            },
            opset_version=self.opset_version,
            dynamo=False
        )

        # ONNX Graf Doğrulaması
        onnx_model = onnx.load(output_path)
        onnx.checker.check_model(onnx_model)
        return output_path
