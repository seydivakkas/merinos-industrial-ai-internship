import re
from typing import List, Dict, Any, Tuple, Optional

from day25.mini_project.src.models import DocumentItem, ChunkItem

class MarkdownAwareChunker:
    """
    Markdown yapısını (başlıklar, bölümler, listeler) dikkate alarak
    dokümanı anlamlı parçalara böler.
    """

    HEADER_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)

    def __init__(self, max_chunk_size: int = 400, *args, **kwargs):
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = kwargs.get("chunk_overlap", 50)

    def _extract_sections(self, text: str) -> List[Tuple[str, str, int]]:
        """
        Markdown başlıklarını tespit ederek bölümleri çıkarır.
        """
        sections = []
        current_level = 0
        current_title = "Giriş"
        current_content = []
        current_start = 0
        for match in self.HEADER_PATTERN.finditer(text):
            level = len(match.group(1))
            title = match.group(2).strip()
            start_idx = match.start()
            chunk_body = text[current_start:start_idx].strip()
            if chunk_body:
                current_content.append(chunk_body)
            if current_content:
                section_text = "\n".join(current_content).strip()
                sections.append((current_title, section_text, current_level))
                current_content = []
            current_title = title
            current_level = level
            current_start = match.end()

        tail = text[current_start:].strip()
        if tail:
            sections.append((current_title, tail, current_level))

        return sections

    def _sub_split(self, text: str) -> List[str]:
        """Bölüm metni max_chunk_size'tan büyükse paragraflara göre böler."""
        if len(text) <= self.max_chunk_size:
            return [text]

        paragraphs = text.split("\n\n")
        sub_chunks: List[str] = []
        curr: List[str] = []
        curr_len = 0

        for p in paragraphs:
            p_len = len(p)
            if curr_len + p_len + 2 > self.max_chunk_size and curr:
                sub_chunks.append("\n\n".join(curr).strip())
                curr = [p]
                curr_len = p_len
            else:
                curr.append(p)
                curr_len += p_len + 2

        if curr:
            sub_chunks.append("\n\n".join(curr).strip())

        final = []
        for sc in sub_chunks:
            if len(sc) > self.max_chunk_size:
                # Satır satır böl
                lines = sc.split("\n")
                l_acc = []
                l_len = 0
                for l in lines:
                    if l_len + len(l) + 1 > self.max_chunk_size and l_acc:
                        final.append("\n".join(l_acc).strip())
                        l_acc = [l]
                        l_len = len(l)
                    else:
                        l_acc.append(l)
                        l_len += len(l) + 1
                if l_acc:
                    final.append("\n".join(l_acc).strip())
            else:
                final.append(sc)

        return [c for c in final if c]

    def chunk_document(self, doc: Any) -> Any:
        """Markdown dokümanını başlık hiyerarşisine ve boyut sınırına göre parçalar."""
        if hasattr(doc, "content"):
            text = doc.content.strip()
            doc_id = getattr(doc, "doc_id", "unknown")
            title = getattr(doc, "title", doc_id)
            category = getattr(doc, "category", "DOKUMA_TEZGAHI_BAKIM")
            metadata = dict(getattr(doc, "metadata", {}))
            is_model = True
        else:
            text = doc.get("content", "").strip()
            doc_id = doc.get("id", doc.get("doc_id", "unknown"))
            title = doc.get("title", doc_id)
            category = doc.get("category", "DOKUMA_TEZGAHI_BAKIM")
            metadata = dict(doc.get("metadata", {}))
            is_model = False

        if not text:
            return []

        raw_sections = self._extract_sections(text)
        if not raw_sections:
            raw_sections = [("Giriş", text, 0)]

        # Başlık hiyerarşisi oluşturma
        breadcrumbs_stack: Dict[int, str] = {0: title}
        chunks_data: List[Tuple[str, List[str]]] = []

        for sec_title, sec_content, sec_level in raw_sections:
            if not sec_content.strip():
                continue
            # Seviyeye göre yığını güncelle
            levels_to_pop = [lvl for lvl in breadcrumbs_stack if lvl >= sec_level and lvl > 0]
            for lvl in levels_to_pop:
                del breadcrumbs_stack[lvl]
            if sec_level > 0:
                breadcrumbs_stack[sec_level] = sec_title

            active_headers = [breadcrumbs_stack[lvl] for lvl in sorted(breadcrumbs_stack.keys())]

            sub_pieces = self._sub_split(sec_content)
            for piece in sub_pieces:
                chunks_data.append((piece, list(active_headers)))

        total_chunks = len(chunks_data)
        if is_model or isinstance(doc, DocumentItem):
            items: List[ChunkItem] = []
            search_pos = 0
            for idx, (c_text, headers) in enumerate(chunks_data, start=1):
                first_line = c_text.split("\n")[0].strip()
                pos = text.find(first_line, search_pos)
                if pos != -1:
                    c_start = pos
                    c_end = pos + len(c_text)
                    search_pos = max(0, c_end - 50)
                else:
                    c_start = 0
                    c_end = len(c_text)

                chunk_meta = dict(metadata)
                chunk_meta["breadcrumbs"] = " > ".join(headers) if headers else title
                chunk_meta["section_depth"] = len(headers)

                items.append(
                    ChunkItem(
                        chunk_id=f"{doc_id}_chunk_{idx:03d}",
                        doc_id=doc_id,
                        title=title,
                        category=category,
                        content=c_text,
                        strategy="markdown_aware",
                        chunk_index=idx,
                        total_chunks_in_doc=total_chunks,
                        char_start=c_start,
                        char_end=c_end,
                        char_length=len(c_text),
                        token_count=len(c_text.split()),
                        section_headers=headers,
                        metadata=chunk_meta
                    )
                )
            return items

        return [
            {
                "chunk_id": f"{doc_id}_chunk_{idx:03d}",
                "doc_id": doc_id,
                "text": c_text,
                "headers": headers,
                "breadcrumbs": " > ".join(headers) if headers else title
            }
            for idx, (c_text, headers) in enumerate(chunks_data, start=1)
        ]
