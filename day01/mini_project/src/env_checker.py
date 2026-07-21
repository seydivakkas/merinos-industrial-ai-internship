"""
day01/mini_project/src/env_checker.py
Endüstriyel Yapay Zeka geliştirme ortamı denetleyicisi ve donanım raporlayıcısı.
"""

from __future__ import annotations

import importlib.metadata
import json
import logging
import platform
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("EnvironmentChecker")


@dataclass
class HardwareReport:
    """Sistem donanımı ve hızlandırıcı durumu."""
    cuda_available: bool
    device_count: int
    device_name: Optional[str] = None
    cuda_version: Optional[str] = None
    total_memory_gb: Optional[float] = None


@dataclass
class PackageStatus:
    """Paket yükleme ve sürüm durumu."""
    name: str
    installed: bool
    version: Optional[str] = None
    required: bool = True


@dataclass
class EnvironmentReport:
    """Toplanan tüm ortam bilgilerini içeren yapısal rapor."""
    python_version: str
    python_executable: str
    os_name: str
    os_release: str
    architecture: str
    hardware: HardwareReport
    packages: List[PackageStatus] = field(default_factory=list)
    is_compliant: bool = False
    validation_messages: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class EnvironmentChecker:
    """
    Python çalışma ortamını, donanım kaynaklarını ve bağımlılıkları doğrular.
    """

    def __init__(self, spec_path: Optional[Path] = None):
        self.spec_path = spec_path
        self.spec = self._load_spec()

    def _load_spec(self) -> Dict[str, Any]:
        """Konfigürasyon dosyasını yükler, yoksa varsayılanları döner."""
        if self.spec_path and self.spec_path.exists():
            try:
                with open(self.spec_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Spesifikasyon dosyası okunamadı: {e}. Varsayılanlar kullanılıyor.")
        
        return {
            "min_python_version": [3, 11],
            "required_packages": ["numpy", "pydantic", "pytest"],
            "optional_packages": ["torch", "torchvision", "fastapi"]
        }

    def check_python_version(self) -> Tuple[bool, str]:
        """Python sürümünü denetler."""
        min_v = tuple(self.spec.get("min_python_version", [3, 11]))
        current_v = sys.version_info[:2]
        is_ok = current_v >= min_v
        msg = f"Python {current_v[0]}.{current_v[1]} tespit edildi (Beklenen asgari: {min_v[0]}.{min_v[1]})."
        return is_ok, msg

    def check_hardware(self) -> HardwareReport:
        """CUDA ve hızlandırıcı donanımını denetler."""
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            device_count = torch.cuda.device_count() if cuda_available else 0
            device_name = torch.cuda.get_device_name(0) if cuda_available and device_count > 0 else None
            cuda_v = torch.version.cuda if cuda_available else None
            mem_gb = None
            if cuda_available and device_count > 0:
                mem_gb = round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 2)
            
            return HardwareReport(
                cuda_available=cuda_available,
                device_count=device_count,
                device_name=device_name,
                cuda_version=cuda_v,
                total_memory_gb=mem_gb
            )
        except ImportError:
            logger.info("PyTorch yüklü değil; CUDA kontrolleri atlandı.")
            return HardwareReport(cuda_available=False, device_count=0)

    def check_package(self, package_name: str, required: bool = True) -> PackageStatus:
        """Tek bir paketin kurulu olup olmadığını ve sürümünü denetler."""
        try:
            ver = importlib.metadata.version(package_name)
            return PackageStatus(name=package_name, installed=True, version=ver, required=required)
        except importlib.metadata.PackageNotFoundError:
            return PackageStatus(name=package_name, installed=False, version=None, required=required)

    def run_full_check(self) -> EnvironmentReport:
        """Tüm kontrolleri icra eder ve EnvironmentReport nesnesi üretir."""
        logger.info("Ortam denetimi başlatılıyor...")
        py_ok, py_msg = self.check_python_version()
        hw = self.check_hardware()

        packages: List[PackageStatus] = []
        messages: List[str] = [py_msg]

        # Gerekli paketler
        all_required_ok = True
        for pkg in self.spec.get("required_packages", []):
            st = self.check_package(pkg, required=True)
            packages.append(st)
            if not st.installed:
                all_required_ok = False
                messages.append(f"Eksik zorunlu paket: {pkg}")
            else:
                messages.append(f"Kurulu zorunlu paket: {pkg} ({st.version})")

        # Opsiyonel paketler
        for pkg in self.spec.get("optional_packages", []):
            st = self.check_package(pkg, required=False)
            packages.append(st)
            if st.installed:
                messages.append(f"Kurulu opsiyonel paket: {pkg} ({st.version})")

        is_compliant = py_ok and all_required_ok

        report = EnvironmentReport(
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            python_executable=sys.executable,
            os_name=platform.system(),
            os_release=platform.release(),
            architecture=platform.machine(),
            hardware=hw,
            packages=packages,
            is_compliant=is_compliant,
            validation_messages=messages
        )

        logger.info(f"Ortam denetimi tamamlandı. Uyumluluk durumu: {is_compliant}")
        return report

    def save_report(self, report: EnvironmentReport, output_path: Path) -> Path:
        """Raporu belirtilen yola JSON olarak kaydeder."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report.to_json())
        logger.info(f"Ortam raporu kaydedildi: {output_path}")
        return output_path


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    spec_file = base_dir / "configs" / "env_spec.json"
    output_file = base_dir / "outputs" / "env_report.json"

    checker = EnvironmentChecker(spec_path=spec_file)
    rep = checker.run_full_check()
    checker.save_report(rep, output_file)
    print(rep.to_json())
