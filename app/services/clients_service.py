"""Business operations for clients."""

from __future__ import annotations

from app.database.models import Client
from app.schemas.client_schema import ClientCreate, ClientUpdate
from app.services.base_service import BaseService
from app.utils.exceptions import ConflictError, NotFoundError


class ClientService(BaseService):
    """Provides business operations related to clients."""

    def create_client(self, data: ClientCreate) -> Client:
        """Create a new client.

        Args:
            data: Validated client information.

        Returns:
            The newly created client.
        """
        with self._repositories() as repositories:
            client = Client(**data.model_dump())
            return repositories.clients.add(client)

    def get_client(self, client_id: int) -> Client | None:
        """Return a client by id, or ``None`` when it does not exist."""
        with self._repositories() as repositories:
            return repositories.clients.get(client_id)

    def get_client_or_raise(self, client_id: int) -> Client:
        """Return a client by id or raise :class:`NotFoundError`."""
        with self._repositories() as repositories:
            client = repositories.clients.get(client_id)
            if client is None:
                raise NotFoundError(f"No existe el cliente con id {client_id}.")
            return client

    def list_clients(self) -> list[Client]:
        """Return every client sorted by name."""
        with self._repositories() as repositories:
            return repositories.clients.list_ordered()

    def search_clients(self, term: str) -> list[Client]:
        """Return clients matching the given search term."""
        with self._repositories() as repositories:
            return repositories.clients.search(term)

    def count_clients(self) -> int:
        """Return the total number of clients."""
        with self._repositories() as repositories:
            return repositories.clients.count()

    def update_client(self, client_id: int, data: ClientUpdate) -> Client:
        """Update an existing client.

        Only the fields provided in ``data`` are changed.

        Raises:
            NotFoundError: If the client does not exist.
        """
        with self._repositories() as repositories:
            client = repositories.clients.get(client_id)
            if client is None:
                raise NotFoundError(f"No existe el cliente con id {client_id}.")

            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(client, field, value)
            repositories.session.flush()
            return client

    def delete_client(self, client_id: int) -> None:
        """Delete a client when it has no related records.

        Raises:
            NotFoundError: If the client does not exist.
            ConflictError: If the client still has locations or services.
        """
        with self._repositories() as repositories:
            client = repositories.clients.get(client_id)
            if client is None:
                raise NotFoundError(f"No existe el cliente con id {client_id}.")

            locations = repositories.locations.count_by_client(client_id)
            services = repositories.services.count_by_client(client_id)
            relations: list[str] = []
            if locations:
                relations.append(
                    self._relation_label(locations, "ubicación", "ubicaciones")
                )
            if services:
                relations.append(
                    self._relation_label(services, "servicio", "servicios")
                )
            if relations:
                raise ConflictError(
                    self._blocking_message("este cliente", relations)
                )

            repositories.clients.delete(client)
