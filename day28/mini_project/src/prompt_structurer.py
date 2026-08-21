from typing import Dict, List, Optional
from day28.mini_project.src.models import (
    PromptAssemblyResult,
    StructuredDesignBrief,
)


class PromptStructurer:
    """
    Halı tasarım bilgilerini belirli bir sırada
    düzenleyerek SDXL için optimize edilmiş
    prompt metni oluşturur.
    """

    ORDERED_FIELDS = [
        "style",
        "motif",
        "color",
        "composition",
        "border",
        "symmetry",
    ]

    DEFAULT_NEGATIVE = (
        "low quality, distorted borders, blurry, pixelated, asymmetrical medallion, "
        "dull colors, broken yarn, misaligned pattern, text, signature, watermark"
    )

    def __init__(self, config: Dict | None = None, negative_prompt: str = ""):
        self.config = config or {}
        self.negative_prompt = negative_prompt or self.DEFAULT_NEGATIVE

    def assemble(self, attributes: Dict[str, str] | StructuredDesignBrief) -> str | PromptAssemblyResult:
        """
        Verilen tasarım özelliklerine göre
        sıralı bir prompt metni oluşturur.
        """
        if isinstance(attributes, dict):
            parts: List[str] = []
            for field in self.ORDERED_FIELDS:
                value = attributes.get(field, "").strip()
                if value:
                    parts.append(f"{field}: {value}")
            return ", ".join(parts)

        # StructuredDesignBrief instance
        brief = attributes
        segments: List[str] = []
        field_order: List[str] = []
        omitted: List[str] = []

        field_labels = {
            "style": brief.style,
            "motif": brief.motif,
            "color": brief.color,
            "composition": brief.composition,
            "border": brief.border,
            "symmetry": brief.symmetry,
        }

        for field_name in self.ORDERED_FIELDS:
            val = field_labels.get(field_name)
            if val and val.strip():
                segments.append(f"{val.strip()}")
                field_order.append(field_name)
            else:
                omitted.append(field_name)

        base_quality_suffix = "Merinos woven carpet textile pattern, fine weaving structure, rich yarn texture, high resolution"
        assembled_text = ", ".join(segments) + f", {base_quality_suffix}."

        return PromptAssemblyResult(
            assembled_prompt=assembled_text,
            negative_prompt=self.negative_prompt,
            field_order=field_order,
            omitted_fields=omitted,
            brief_id=brief.brief_id,
        )

    def mutate_single_field(
        self,
        brief: StructuredDesignBrief,
        field_to_change: str,
        new_value: str
    ) -> StructuredDesignBrief:
        """
        Staj Defteri Yaprak 56: Seed ve diğer tüm alanları sabit tutarak
        yalnızca tek bir alanı değiştirir (Single-Variable Controlled Comparison).
        """
        if field_to_change not in self.ORDERED_FIELDS:
            raise ValueError(
                f"Geçersiz alan adı: '{field_to_change}'. Geçerli alanlar: {self.ORDERED_FIELDS}"
            )

        if not new_value or not new_value.strip():
            raise ValueError(f"'{field_to_change}' alanı boş bir değerle değiştirilemez.")

        data = brief.model_dump()
        data[field_to_change] = new_value.strip()
        data["brief_id"] = f"{brief.brief_id}_MUT_{field_to_change.upper()}"
        data["title"] = f"{brief.title} (Değiştirilen: {field_to_change})"

        return StructuredDesignBrief(**data)
