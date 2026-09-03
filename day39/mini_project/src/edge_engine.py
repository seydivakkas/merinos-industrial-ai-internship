# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 39
Edge Çıkarım Motoru: ONNX Runtime (ORT) C++ CPU Yürütme ve Thread Havuzu Yönetimi
"""

import os
import time
import numpy as np
from typing import Dict, Any, List, Optional
import onnxruntime as ort


class EdgeInferenceEngine:
    """Endüstriyel Edge PC üzerinde Düşük Gecikmeli C++ Çıkarım Motoru."""

    def __init__(
        self,
        model_path: str,
        num_threads: int = 2,
        enable_optimizations: bool = True
    ):
        self.model_path = model_path
        self.num_threads = num_threads
        self.enable_optimizations = enable_optimizations
        self.session: Optional[ort.InferenceSession] = None
        self._init_session()

    def _init_session(self):
        """ONNX Runtime oturumunu endüstriyel IPC ayarlarına göre yapılandırır."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model dosyasi bulunamadi: {self.model_path}")

        opts = ort.SessionOptions()
        # Tezgâh yanı fansız IPC için thread yapılandırması
        opts.intra_op_num_threads = self.num_threads
        opts.inter_op_num_threads = 1
        opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

        if self.enable_optimizations:
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        # CPU Execution Provider
        self.session = ort.InferenceSession(
            self.model_path,
            sess_options=opts,
            providers=["CPUExecutionProvider"]
        )

        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]

    def warmup(self, num_iterations: int = 5):
        """CPU önbelleğini ve tensör tablolarını ısıtarak kuyruk gecikmesini (P99) dengeler."""
        if self.session is None:
            return

        input_meta = self.session.get_inputs()[0]
        shape = [dim if isinstance(dim, int) and dim > 0 else 1 for dim in input_meta.shape]
        if len(shape) == 0:
            shape = [1, 384]
        dummy_data = np.random.randn(*shape).astype(np.float32)

        for _ in range(num_iterations):
            self.run({self.input_names[0]: dummy_data})

    def run(self, input_feed: Dict[str, np.ndarray]) -> List[np.ndarray]:
        """Tek veya çoklu tensör için C++ çekirdeğinde çıkarım çalıştırır."""
        if self.session is None:
            raise RuntimeError("InferenceSession baslatilamadi.")
        return self.session.run(self.output_names, input_feed)

    def encode(self, features: np.ndarray) -> np.ndarray:
        """Bi-Encoder için girdi özelliklerini 384-D gömme vektörüne dönüştürür."""
        if features.ndim == 1:
            features = np.expand_dims(features, axis=0)
        feed = {self.input_names[0]: features.astype(np.float32)}
        outputs = self.run(feed)
        return outputs[0]

    def score(self, pair_features: np.ndarray) -> np.ndarray:
        """Cross-Encoder için (soru, doküman) çiftinin alaka skorunu hesaplar."""
        if pair_features.ndim == 1:
            pair_features = np.expand_dims(pair_features, axis=0)
        feed = {self.input_names[0]: pair_features.astype(np.float32)}
        outputs = self.run(feed)
        return outputs[0].flatten()
