"""
day01/mini_project/tests/test_env_checker.py
EnvironmentChecker ve RepositoryBootstrap birim testleri.
"""

import json
from pathlib import Path
import pytest

from day04.mini_project.src.env_checker import EnvironmentChecker, HardwareReport
from day04.mini_project.src.repo_bootstrap import RepositoryBootstrap


@pytest.fixture
def repo_root():
    # merinos-industrial-ai-internship kök dizini
    return Path(__file__).resolve().parent.parent.parent.parent


@pytest.fixture
def spec_path():
    return Path(__file__).resolve().parent.parent / "configs" / "env_spec.json"


def test_python_version_check(spec_path):
    checker = EnvironmentChecker(spec_path=spec_path)
    is_ok, msg = checker.check_python_version()
    assert isinstance(is_ok, bool)
    assert "Python" in msg


def test_hardware_check(spec_path):
    checker = EnvironmentChecker(spec_path=spec_path)
    hw = checker.check_hardware()
    assert isinstance(hw, HardwareReport)
    assert isinstance(hw.cuda_available, bool)
    assert isinstance(hw.device_count, int)


def test_package_check_installed_and_missing(spec_path):
    checker = EnvironmentChecker(spec_path=spec_path)
    
    # Kesinlikle kurulu olan bir paket (örneğin pytest)
    st_installed = checker.check_package("pytest", required=True)
    assert st_installed.installed is True
    assert st_installed.version is not None

    # Asla var olmayan bir paket
    st_missing = checker.check_package("non_existent_package_xyz_999", required=True)
    assert st_missing.installed is False
    assert st_missing.version is None


def test_full_check_and_report_serialization(spec_path, tmp_path):
    checker = EnvironmentChecker(spec_path=spec_path)
    report = checker.run_full_check()

    assert report.python_version is not None
    assert report.os_name is not None
    assert len(report.packages) > 0

    json_str = report.to_json()
    parsed = json.loads(json_str)
    assert "python_version" in parsed
    assert "hardware" in parsed

    out_file = tmp_path / "test_report.json"
    checker.save_report(report, out_file)
    assert out_file.exists()


def test_repository_bootstrap_validation(repo_root, spec_path):
    bootstrap = RepositoryBootstrap(repo_root=repo_root, spec_path=spec_path)
    result = bootstrap.validate_structure()

    assert result.repo_root == str(repo_root)
    assert "README.md" in result.existing_files
    assert "AGENTS.md" in result.existing_files
    assert "LICENSE" in result.existing_files
    assert "day01" in result.existing_dirs
    assert result.is_valid is True
