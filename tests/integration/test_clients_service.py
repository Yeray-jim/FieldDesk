"""Integration tests for :class:`ClientService`."""

from __future__ import annotations

import pytest

from app.database import Database
from app.schemas import ClientCreate, ClientUpdate
from app.services import ClientService
from app.services.base_service import BaseService
from app.utils.exceptions import ConflictError, NotFoundError

from tests.conftest import Workflow


@pytest.mark.integration
def test_create_and_fetch_client(database: Database) -> None:
    service = ClientService(database)

    created = service.create_client(ClientCreate(name="Acme", company="Acme S.A."))

    assert created.id is not None
    assert service.count_clients() == 1
    assert service.get_client(created.id).name == "Acme"
    assert [client.name for client in service.list_clients()] == ["Acme"]


@pytest.mark.integration
def test_update_changes_only_provided_fields(database: Database) -> None:
    service = ClientService(database)
    client = service.create_client(ClientCreate(name="Acme", phone="555-0101"))

    updated = service.update_client(client.id, ClientUpdate(phone="555-9999"))

    assert updated.name == "Acme"
    assert updated.phone == "555-9999"


@pytest.mark.integration
def test_update_missing_client_raises(database: Database) -> None:
    service = ClientService(database)

    with pytest.raises(NotFoundError):
        service.update_client(999, ClientUpdate(name="Nuevo"))


@pytest.mark.integration
def test_delete_client_without_relations(database: Database) -> None:
    service = ClientService(database)
    client = service.create_client(ClientCreate(name="Efímero"))

    service.delete_client(client.id)

    assert service.count_clients() == 0


@pytest.mark.integration
def test_delete_client_with_relations_is_blocked(workflow: Workflow) -> None:
    with pytest.raises(ConflictError) as error:
        workflow.clients.delete_client(workflow.client_id)

    assert "ubicación" in str(error.value)
    assert "servicio" in str(error.value)


@pytest.mark.integration
def test_search_clients(database: Database) -> None:
    service = ClientService(database)
    service.create_client(ClientCreate(name="Alpha"))
    service.create_client(ClientCreate(name="Beta", company="Alphabet Inc."))

    found = {client.name for client in service.search_clients("alph")}

    assert found == {"Alpha", "Beta"}


@pytest.mark.integration
def test_relation_label_singular_and_plural() -> None:
    assert BaseService._relation_label(1, "equipo", "equipos") == "1 equipo"
    assert BaseService._relation_label(2, "equipo", "equipos") == "2 equipos"
