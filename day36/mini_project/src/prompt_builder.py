from typing import List, Dict, Any

class PromptBuilder:
    """Retrieved context ve operatör sorusu kullanarak
    yapısal çıktı üretimi için prompt hazırlar."""

    def __init__(self, template: str = None, config_path: str = None):
        self.template = template or self._default_template()

    def build_prompt(self, operator_query: str,
                     retrieved_context: List[Dict[str, Any]],
                     task_instructions: str = None) -> str:
        """Operatör sorusu ve retrieved dokümanlardan
        üretim promptu oluşturur."""
        context_text = self._format_context(retrieved_context)
        template = self.template or self._default_template()
        prompt = template.format(
            operator_query=operator_query,
            retrieved_context=context_text,
            task_instructions=task_instructions or ""
        )
        return prompt

    def _default_template(self) -> str:
        """Varsayılan Merinos endüstriyel prompt şablonu."""
        return (
            "### SİSTEM ROLÜ VE KATI KURALLAR:\n"
            "Sen Merinos Halı Sanayi A.Ş. Baş Teknik Bakım Uzmanısın. Gaziantep fabrikasındaki "
            "dokuma tezgâhları, buharlı fikse hatları ve kalite kontrol süreçlerinde operatörlere rehberlik edersin.\n\n"
            "KATI YÖNERGELER:\n"
            "1. Yalnızca <retrieved_context> etiketleri içinde verilen teknik parçalardaki bilgilere dayanarak yanıt ver.\n"
            "2. Genel bilginden veya eğitim hafızandan ASLA tahmin veya varsayım ekleme.\n"
            "3. Eğer operatörün sorusunun cevabı bağlamda açıkça bulunmuyorsa doğrudan şu mesajı ver: \"Merinos teknik dokümantasyonunda bu konuya ilişkin bilgi bulunmamaktadır.\"\n"
            "4. Yanıtında geçen her teknik kuralı ve parametreyi [DOC_..._c00X] formatında kaynak göster.\n"
            "5. Acil durdurma, aşırı ısınma veya mekanik sıkışma gibi durumlar varsa GÜVENLİK UYARISI ekle.\n\n"
            "<retrieved_context>\n"
            "{retrieved_context}\n"
            "</retrieved_context>\n\n"
            "<operator_query>\n"
            "{operator_query}\n"
            "</operator_query>\n\n"
            "{task_instructions}\n"
            "Lütfen yukarıdaki bağlama dayanarak operatör için yapılandırılmış teknik yanıtı üret."
        )

    def _format_context(self, retrieved_context: List[Any]) -> str:
        """Getirilen parçaları sıralı XML bloklarına dönüştürür."""
        blocks = []
        for idx, c in enumerate(retrieved_context, start=1):
            if isinstance(c, dict):
                cid = c.get("chunk_id", c.get("id", f"doc_{idx}"))
                source = c.get("source", c.get("source_id", "Bilinmiyor"))
                section = c.get("section", "Genel")
                text = str(c.get("text", "")).strip()
            else:
                cid = getattr(c, "chunk_id", f"doc_{idx}")
                source = getattr(c, "source", getattr(c, "source_id", "Bilinmiyor"))
                section = getattr(c, "section", "Genel")
                text = getattr(c, "text", str(c)).strip()
            block = (
                f'<doc id="{cid}" rank="{idx}" source="{source}" section="{section}">\n'
                f"{text}\n"
                f"</doc>"
            )
            blocks.append(block)
        return "\n\n".join(blocks)

    def format_context_blocks(self, chunks: List[Any]) -> str:
        """Geriye dönük uyumluluk için blok dönüştürme takma adı."""
        return self._format_context(chunks)
