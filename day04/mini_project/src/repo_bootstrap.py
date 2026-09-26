"""
day01/mini_project/src/repo_bootstrap.py
Repository yapısı ve dizin hiyerarşisi doğrulama ve ilklendirme motoru.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("RepositoryBootstrap")


@dataclass
class BootstrapResult:
    """Repo yapısı doğrulama sonucu."""
    repo_root: str
    existing_dirs: List[str] = field(default_factory=list)
    missing_dirs: List[str] = field(default_factory=list)
    existing_files: List[str] = field(default_factory=list)
    missing_files: List[str] = field(default_factory=list)
    is_valid: bool = False


class RepositoryBootstrap:
    """
    Proje dosya ve dizin sözleşmesinin eksiksiz olduğunu doğrular.
    """

    def __init__(self, repo_root: Path, spec_path: Optional[Path] = None):
        self.repo_root = repo_root
        self.spec_path = spec_path
        self.spec = self._load_spec()

    def _load_spec(self) -> Dict:
        if self.spec_path and self.spec_path.exists():
            try:
                with open(self.spec_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "required_repo_directories": ["shared", "tests", "docs", "day01"],
            "required_root_files": ["README.md", "AGENTS.md", "LICENSE", ".gitignore"]
        }

    def validate_structure(self) -> BootstrapResult:
        """Kök depodaki zorunlu dosya ve klasörleri denetler."""
        req_dirs = self.spec.get("required_repo_directories", [])
        req_files = self.spec.get("required_root_files", [])

        existing_dirs = []
        missing_dirs = []
        for d in req_dirs:
            target = self.repo_root / d
            if target.is_dir():
                existing_dirs.append(d)
            else:
                missing_dirs.append(d)

        existing_files = []
        missing_files = []
        for f in req_files:
            target = self.repo_root / f
            if target.is_file():
                existing_files.append(f)
            else:
                missing_files.append(f)

        is_valid = (len(missing_dirs) == 0 and len(missing_files) == 0)

        return BootstrapResult(
            repo_root=str(self.repo_root),
            existing_dirs=existing_dirs,
            missing_dirs=missing_dirs,
            existing_files=existing_files,
            missing_files=missing_files,
            is_valid=is_valid
        )

    def ensure_directories(self) -> List[str]:
        """Eksik zorunlu dizinleri oluşturur."""
        created = []
        for d in self.spec.get("required_repo_directories", []):
            target = self.repo_root / d
            if not target.exists():
                target.mkdir(parents=True, exist_ok=True)
                created.append(d)
                logger.info(f"Oluşturulan dizin: {d}")
        return created
