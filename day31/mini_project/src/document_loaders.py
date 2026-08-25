# -*- coding: utf-8 -*-
"""
ÖZEL LİSANS — TÜM HAKLAR SAKLIDIR

Telif Hakkı (c) 2026 Seydi Eryılmaz (@seydivakkas)
Bu yazılım ve ilgili tüm dosyalar ("Yazılım") yalnızca görüntüleme ve eğitim
amaçlı olarak paylaşılmıştır. Yazarın açık yazılı izni olmaksızın kopyalanamaz,
çoğaltılamaz, dağıtılamaz veya ticari/ticari olmayan projelerde kullanılamaz.

Merinos Industrial AI Internship - Day 31
Document Loaders: PDF, Word .docx, Markdown & Text Loaders
Şekil 61: LangChain Document Loader arayüzü ve yerel gömülü ayrıştırma mimarisi
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import os
import hashlib
import zipfile
import xml.etree.ElementTree as ET

# Şekil 61: langchain_community document loaders entegrasyonu (varsa kullanılır, yoksa yerel adaptör sağlanır)
try:
    from langchain_community.document_loaders import (
        PyPDFLoader,
        Docx2txtLoader,
        TextLoader as LangChainTextLoader,
    )
except ImportError:
    # Yerel hafif loader sarmalayıcıları (langchain_community kurulu değilse kesintisiz çalışması için)
    class _FallbackDoc:
        def __init__(self, page_content: str, metadata: dict):
            self.page_content = page_content
            self.metadata = metadata

    class PyPDFLoader:
        def __init__(self, file_path: str):
            self.file_path = file_path

        def load(self):
            import pypdf
            reader = pypdf.PdfReader(self.file_path)
            docs = []
            for idx, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                docs.append(_FallbackDoc(page_content=text, metadata={"page": idx, "source": self.file_path}))
            return docs

    class Docx2txtLoader:
        def __init__(self, file_path: str):
            self.file_path = file_path

        def load(self):
            title, pages = DocxLoader._parse_docx(self.file_path)
            docs = []
            for p_num, p_text in pages:
                docs.append(_FallbackDoc(page_content=p_text, metadata={"page": p_num, "source": self.file_path}))
            return docs

    class LangChainTextLoader:
        def __init__(self, file_path: str, encoding: str = "utf-8"):
            self.file_path = file_path
            self.encoding = encoding

        def load(self):
            with open(self.file_path, "r", encoding=self.encoding, errors="replace") as f:
                content = f.read()
            return [_FallbackDoc(page_content=content, metadata={"source": self.file_path, "page": 1})]

from day31.mini_project.src.models import RawDocument
from day31.mini_project.src.text_cleaner import TextCleaner


W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def calculate_file_hash(filepath: str) -> str:
    """Bir dosyanın SHA-256 özetini (hash) hesaplar."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class PDFLoader:
    """
    PDF dosyalarını okuyan yükleyici.
    Şekil 61: Hem LangChain Document sözlüğü döndüren `load(file_path)` metodunu
    hem de geriye dönük uyumlu `(title, pages)` demetini destekler.
    """

    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def load(self, file_path: Optional[str] = None) -> Any:
        # 1. Instance çağrısı: loader = PDFLoader(); loader.load(file_path) -> Şekil 61 standardı
        if isinstance(self, PDFLoader):
            target_path = file_path or self.file_path
            if not target_path:
                raise ValueError("file_path belirtilmelidir.")
            loader = PyPDFLoader(target_path)
            documents = loader.load()
            return [
                {
                    "page_content": doc.page_content,
                    "metadata": {
                        "source": target_path,
                        "page": getattr(doc, "metadata", {}).get("page", 0),
                        "type": "pdf",
                    },
                }
                for doc in documents
            ]
        else:
            # 2. Statik çağrı: PDFLoader.load(filepath) -> Test ve UnifiedLoader standardı
            actual_path = self if isinstance(self, (str, Path)) else file_path
            return PDFLoader._parse_pdf(str(actual_path))

    @staticmethod
    def _parse_pdf(filepath: str) -> Tuple[str, List[Tuple[int, str]]]:
        try:
            import pypdf
        except ImportError:
            raise ImportError("pypdf kütüphanesi bulunamadı! Lütfen 'pip install pypdf' çalıştırın.")

        reader = pypdf.PdfReader(filepath)
        pages: List[Tuple[int, str]] = []
        doc_title = Path(filepath).stem.replace("_", " ").title()

        if reader.metadata and reader.metadata.title:
            meta_title = str(reader.metadata.title).strip()
            if meta_title:
                doc_title = meta_title

        for idx, page in enumerate(reader.pages, start=1):
            raw_text = page.extract_text() or ""
            cleaned_text = TextCleaner.clean(raw_text)
            if cleaned_text:
                pages.append((idx, cleaned_text))

        if pages and pages[0][1]:
            first_line = pages[0][1].split("\n")[0].strip()
            has_meta_title = bool(reader.metadata and getattr(reader.metadata, "title", None))
            if len(first_line) < 100 and not has_meta_title:
                doc_title = first_line

        return doc_title, pages


class DocxLoader:
    """
    Word (.docx) belgelerini okuyan yükleyici.
    Standart kütüphane (zipfile + xml.etree) ve Docx2txtLoader arayüzünü destekler.
    """

    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def load(self, file_path: Optional[str] = None) -> Any:
        if isinstance(self, DocxLoader):
            target_path = file_path or self.file_path
            if not target_path:
                raise ValueError("file_path belirtilmelidir.")
            title, pages = self._parse_docx(target_path)
            return [
                {
                    "page_content": p_text,
                    "metadata": {
                        "source": target_path,
                        "page": p_num,
                        "type": "docx",
                    },
                }
                for p_num, p_text in pages
            ]
        else:
            actual_path = self if isinstance(self, (str, Path)) else file_path
            return DocxLoader._parse_docx(str(actual_path))

    @staticmethod
    def _parse_docx(filepath: str) -> Tuple[str, List[Tuple[int, str]]]:
        if not zipfile.is_zipfile(filepath):
            raise ValueError(f"Geçersiz docx dosyası: {filepath}")

        with zipfile.ZipFile(filepath, "r") as zf:
            if "word/document.xml" not in zf.namelist():
                raise ValueError("DOCX arşivi içinde word/document.xml bulunamadı!")
            xml_content = zf.read("word/document.xml")

        root = ET.fromstring(xml_content)
        body = root.find(f"{W_NS}body")
        if body is None:
            return Path(filepath).stem, []

        paragraphs: List[str] = []
        doc_title = Path(filepath).stem.replace("_", " ").title()

        for child in body:
            tag = child.tag
            if tag == f"{W_NS}p":
                texts = [node.text for node in child.iter(f"{W_NS}t") if node.text]
                p_text = "".join(texts).strip()
                if p_text:
                    paragraphs.append(p_text)
            elif tag == f"{W_NS}tbl":
                for row in child.iter(f"{W_NS}tr"):
                    cell_texts = []
                    for cell in row.iter(f"{W_NS}tc"):
                        c_text = "".join(node.text for node in cell.iter(f"{W_NS}t") if node.text).strip()
                        cell_texts.append(c_text)
                    if cell_texts and any(cell_texts):
                        paragraphs.append(" | ".join(cell_texts))

        if paragraphs:
            if len(paragraphs[0]) < 120:
                doc_title = paragraphs[0]

        full_doc_text = "\n\n".join(paragraphs)
        cleaned_text = TextCleaner.clean(full_doc_text)

        pages: List[Tuple[int, str]] = []
        chars_per_page = 1800
        if len(cleaned_text) <= chars_per_page:
            pages.append((1, cleaned_text))
        else:
            cur_pos = 0
            page_no = 1
            while cur_pos < len(cleaned_text):
                end_pos = min(cur_pos + chars_per_page, len(cleaned_text))
                if end_pos < len(cleaned_text):
                    next_nl = cleaned_text.find("\n\n", end_pos)
                    if next_nl != -1 and (next_nl - end_pos) < 300:
                        end_pos = next_nl
                page_text = cleaned_text[cur_pos:end_pos].strip()
                if page_text:
                    pages.append((page_no, page_text))
                    page_no += 1
                cur_pos = end_pos

        return doc_title, pages


class TextLoader:
    """Markdown (.md) ve Düz Metin (.txt) dosyalarını ayrıştıran yükleyici."""

    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def load(self, file_path: Optional[str] = None) -> Any:
        if isinstance(self, TextLoader):
            target_path = file_path or self.file_path
            if not target_path:
                raise ValueError("file_path belirtilmelidir.")
            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            cleaned = TextCleaner.clean(content)
            return [
                {
                    "page_content": cleaned,
                    "metadata": {
                        "source": target_path,
                        "page": 1,
                        "type": Path(target_path).suffix.replace(".", ""),
                    },
                }
            ]
        else:
            actual_path = self if isinstance(self, (str, Path)) else file_path
            return TextLoader._parse_text(str(actual_path))

    @staticmethod
    def _parse_text(filepath: str) -> Tuple[str, List[Tuple[int, str]]]:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            raw_text = f.read()

        cleaned = TextCleaner.clean(raw_text)
        doc_title = Path(filepath).stem.replace("_", " ").title()

        lines = cleaned.split("\n")
        for line in lines:
            s_line = line.strip()
            if s_line.startswith("# ") and len(s_line) < 120:
                doc_title = s_line.replace("# ", "").strip()
                break

        return doc_title, [(1, cleaned)]


class UnifiedDocumentLoader:
    """
    Dosya türünü (PDF, DOCX, MD, TXT) otomatik algılayıp
    standart RawDocument veri nesnesine dönüştüren ana orkestratör.
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".md", ".txt"}

    @classmethod
    def load_file(cls, filepath: str) -> RawDocument:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {filepath}")

        ext = path.suffix.lower()
        if ext not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Desteklenmeyen dosya türü: '{ext}'. Desteklenenler: {cls.SUPPORTED_EXTENSIONS}")

        file_hash = calculate_file_hash(filepath)
        doc_id = f"DOC_{path.stem.upper()}"

        if ext == ".pdf":
            title, pages = PDFLoader.load(filepath)
        elif ext == ".docx":
            title, pages = DocxLoader.load(filepath)
        else:
            title, pages = TextLoader.load(filepath)

        total_chars = sum(len(p[1]) for p in pages)

        metadata = {
            "source_path": str(path.absolute()),
            "extension": ext,
            "page_count": len(pages),
            "file_size_bytes": path.stat().st_size,
        }

        return RawDocument(
            doc_id=doc_id,
            filename=path.name,
            file_type=ext.replace(".", ""),
            file_hash=file_hash,
            title=title,
            pages=pages,
            metadata=metadata,
            total_char_count=total_chars
        )

    @classmethod
    def load_directory(cls, directory_path: str) -> List[RawDocument]:
        """Belirtilen dizindeki tüm desteklenen belgeleri tarar ve yükler."""
        p = Path(directory_path)
        if not p.exists() or not p.is_dir():
            return []

        documents: List[RawDocument] = []
        for file in sorted(p.iterdir()):
            if file.is_file() and file.suffix.lower() in cls.SUPPORTED_EXTENSIONS:
                try:
                    doc = cls.load_file(str(file))
                    documents.append(doc)
                except Exception as e:
                    print(f"Uyarı: '{file.name}' yüklenirken hata oluştu: {e}")

        return documents
