"""Unit tests for Day 04 Data Contracts."""

import pytest
from pydantic import ValidationError
from day04.mini_project.src.data_contracts import CarpetSpecificationContract, LoomTelemetryContract


def test_carpet_contract_valid():
    contract = CarpetSpecificationContract(
        product_id="CRP-01",
        title="Merinos Classic Navy",
        collection="Heritage",
        width_cm=160.0,
        length_cm=230.0,
        pile_height_mm=12.0,
        palette_hex=["#001F3F", "#FFFFFF", "#AAAAAA"],
    )
    assert contract.product_id == "CRP-01"
    assert contract.palette_hex[0] == "#001F3F"


def test_carpet_contract_aspect_ratio_exceeded():
    with pytest.raises(ValidationError):
        # 100 cm width by 800 cm length -> 8:1 ratio exceeds 6:1
        CarpetSpecificationContract(
            product_id="CRP-02",
            title="Too Long Runner",
            collection="Runner",
            width_cm=100.0,
            length_cm=800.0,
            pile_height_mm=10.0,
            palette_hex=["#123456"],
        )


def test_loom_telemetry_contract():
    telemetry = LoomTelemetryContract(
        loom_id="LOOM-01",
        motor_temperature_c=78.5,
        pneumatic_pressure_bar=14.2,
        warp_tension_cn=350.0,
        rpm=850,
    )
    assert telemetry.loom_id == "LOOM-01"
    assert telemetry.motor_temperature_c == 78.5
