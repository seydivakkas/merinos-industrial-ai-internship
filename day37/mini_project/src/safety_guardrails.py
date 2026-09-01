# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 37
Safety Guardrails: İSG İhlali, Tehlikeli Tavsiye ve Halüsinasyon Önleme Güvenlik Korkulukları
"""

import re
import json
from pathlib import Path
from typing import Dict, Tuple, Any, Optional, List
from day37.mini_project.src.models import GuardrailDecision


class GuardrailResult(tuple):
    """
    Hem 3-elemanlı Tuple (is_safe, reason, details) olarak açılabilen,
    hem de pydantic GuardrailDecision özelliklerini (.action, .reason, vb.) destekleyen hibrit sınıf.
    """
    def __new__(cls, is_safe: bool, reason: str, details: Optional[Dict[str, Any]] = None):
        d = details or {}
        return super(GuardrailResult, cls).__new__(cls, (is_safe, reason, d))

    @property
    def is_safe(self) -> bool:
        return self[0]

    @property
    def reason(self) -> str:
        return self[1]

    @property
    def details(self) -> Dict[str, Any]:
        return self[2]

    @property
    def action(self) -> str:
        return "ALLOW" if self[0] else "BLOCK"

    @property
    def violation_category(self) -> Optional[str]:
        if self[0]:
            return None
        t = self[2].get("type")
        if t == "blacklist":
            return "ISG_VIOLATION"
        elif t == "pressure_limit":
            src = self[2].get("source", "query")
            return "PARAMETER_OUT_OF_BOUNDS" if src == "query" else "DANGEROUS_ADVICE"
        elif t == "hallucination":
            return "HALLUCINATION"
        return "ISG_VIOLATION"

    @property
    def sanitized_content(self) -> Optional[str]:
        if self[0]:
            return None
        t = self[2].get("type")
        if t == "blacklist":
            return (
                "İŞ SAĞLIĞI VE GÜVENLİĞİ (İSG) İHLALİ: Makine çalışırken koruma kapaklarını sökmek, "
                "dönen mekanizmalara dokunmak veya acil durdurma sistemlerini baypas etmek kesinlikle yasaktır ve hayati tehlike taşır."
            )
        elif t == "pressure_limit":
            val = self[2].get("value", 20.0)
            src = self[2].get("source", "query")
            if src == "output":
                return f"GÜVENLİK İPTALİ: Model {val:.0f} bar basınç önermiştir ancak fabrika güvenlik limiti 20 bar'dır."
            return f"PARAMETRE İHLALİ: Pnömatik sistem maksimum 20 bar sınırına sahiptir. {val:.0f} bar basınç regülatör patlamasına yol açar."
        elif t == "hallucination":
            return "GÜVENLİK FİLTRESİ: Üretilen yanıtın bağlama sadakat oranı düşüktür. Halüsinasyon riskine karşı yanıt bloke edilmiştir."
        return "Bu talep güvenlik politikaları gereği işlenememektedir."

    def to_decision(self) -> GuardrailDecision:
        return GuardrailDecision(
            action=self.action,
            reason=self.reason,
            violation_category=self.violation_category,
            sanitized_content=self.sanitized_content
        )


class SafetyGuardrails:
    """Kullanıcı girdilerini güvenlik açısından kontrol eden sınıf."""

    def __init__(self, config_path: Optional[str] = None):
        # Tehlikeli ifadeler (kara liste)
        self.blacklist_phrases = [
            "acil stop butonunu baypas",
            "acil stop'u iptal et",
            "koruma sensörünü devre dışı bırak",
            "emniyet fotoselini iptal et",
            "güvenlik kilidini devre dışı bırak",
            "emniyet sistemini atla",
            "koruma kapağını sök",
            "dönen şafta elini sok",
            "hareket halindeyken dokun",
            "sensörü körlet",
            "kilit mekanizmasını kır",
            "sigortayı telle bağla"
        ]
        self.pressure_limit_bar = 20.0

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    actions = cfg.get("safety_guardrails", {}).get("input_blacklisted_actions")
                    if actions:
                        for a in actions:
                            if a not in self.blacklist_phrases:
                                self.blacklist_phrases.append(a)
                    max_p = cfg.get("safety_guardrails", {}).get("physical_parameter_limits", {}).get("max_pressure_bar")
                    if max_p is not None:
                        self.pressure_limit_bar = float(max_p)
            except Exception:
                pass

    def check_input_safety(self, query: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Kullanıcı girdisini güvenlik kurallarına göre kontrol eder."""
        q = query.lower()

        # 1) Kara liste kontrolü
        for phrase in self.blacklist_phrases:
            if phrase in q:
                return GuardrailResult(
                    False,
                    f"Güvenlik riski: '{phrase}' ifadesi tespit edildi.",
                    {"type": "blacklist", "matched_phrase": phrase, "source": "query"}
                )

        # 2) Basınç sınırı kontrolü (20.0 bar)
        bar_pattern = r"(\d+(?:\.\d+)?)\s*bar"
        match = re.search(bar_pattern, q)
        if match:
            pressure = float(match.group(1))
            if pressure > self.pressure_limit_bar:
                return GuardrailResult(
                    False,
                    f"Güvenlik riski: {pressure} bar sınırı aşıldı.",
                    {"type": "pressure_limit", "value": pressure, "source": "query"}
                )

        return GuardrailResult(True, "Güvenli girdi", {})

    def check_output_safety(
        self,
        answer_text: str,
        retrieved_chunks: Optional[List[Any]] = None,
        faithfulness: Optional[float] = None
    ) -> GuardrailResult:
        """Üretilen çıktıyı bağlam sadakati ve güvenlik parametreleri açısından denetler."""
        # 1) Halüsinasyon Eşiği Kontrolü
        if faithfulness is not None and faithfulness < 0.75:
            if "bilgi bulunmamaktadır" not in answer_text.lower() and "kesinlikle yasaktır" not in answer_text.lower():
                return GuardrailResult(
                    False,
                    f"Halüsinasyon Riski: Faithfulness ({faithfulness:.2f}) < Eşik (0.75)",
                    {"type": "hallucination", "faithfulness": faithfulness}
                )

        # 2) Yanıtta Kural Dışı Basınç Tavsiyesi Kontrolü
        bar_pattern = r"(\d+(?:\.\d+)?)\s*bar"
        match = re.search(bar_pattern, answer_text.lower())
        if match:
            pressure = float(match.group(1))
            if pressure > self.pressure_limit_bar:
                return GuardrailResult(
                    False,
                    f"Güvenlik riski: {pressure} bar sınırı aşıldı.",
                    {"type": "pressure_limit", "value": pressure, "source": "output"}
                )

        return GuardrailResult(True, "Güvenli çıktı", {})
