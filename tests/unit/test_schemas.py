"""Unit tests for the Pydantic input schemas."""

from __future__ import annotations

from datetime import date, time
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas import (
    ClientCreate,
    EquipmentCreate,
    MaterialCreate,
    ServiceMaterialCreate,
    VisitCreate,
)


@pytest.mark.unit
def test_client_accepts_valid_email() -> None:
    client = ClientCreate(name="Acme", email="contacto@acme.com")
    assert client.email == "contacto@acme.com"


@pytest.mark.unit
def test_client_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(name="Acme", email="no-es-un-email")


@pytest.mark.unit
def test_client_allows_missing_email() -> None:
    for value in (None, "", "   "):
        client = ClientCreate(name="Acme", email=value)
        assert client.email is None


@pytest.mark.unit
def test_client_trims_and_requires_name() -> None:
    client = ClientCreate(name="  Acme  ")
    assert client.name == "Acme"

    with pytest.raises(ValidationError):
        ClientCreate(name="   ")


@pytest.mark.unit
def test_schemas_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(name="Acme", unknown="value")


@pytest.mark.unit
def test_equipment_rejects_warranty_before_installation() -> None:
    with pytest.raises(ValidationError):
        EquipmentCreate(
            location_id=1,
            name="Bomba",
            type="Hidráulica",
            installation_date=date(2026, 1, 10),
            warranty_expiration=date(2026, 1, 1),
        )


@pytest.mark.unit
def test_visit_rejects_end_before_start() -> None:
    with pytest.raises(ValidationError):
        VisitCreate(
            service_id=1,
            visit_date=date(2026, 1, 10),
            start_time=time(10, 0),
            end_time=time(9, 0),
        )


@pytest.mark.unit
def test_service_material_requires_positive_quantity() -> None:
    with pytest.raises(ValidationError):
        ServiceMaterialCreate(
            service_id=1,
            material_id=1,
            quantity=Decimal("0"),
        )


@pytest.mark.unit
def test_material_requires_name() -> None:
    with pytest.raises(ValidationError):
        MaterialCreate(name="")
