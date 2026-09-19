"""Dashboard screen with key metrics and recent activity."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TypeVar

import flet as ft

from app.components.badges import StatusBadge
from app.components.cards import EmptyState, GlassCard, SectionHeader, StatCard
from app.components.theme import FontSize, Metrics, Palette
from app.database.models import Incident, Service, ServiceStatus
from app.utils.dates import format_datetime
from app.utils.i18n import t
from app.views.base_view import BaseView

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DashboardView(BaseView):
    """Overview of the technician's workload."""

    title = "Panel de control"
    icon = ft.Icons.DASHBOARD_OUTLINED

    def build(self) -> ft.Control:
        return ft.Column(
            controls=[
                SectionHeader(
                    "Panel de control",
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                ),
                self._stats(),
                self._services_section(),
                self._incidents_section(),
            ],
            spacing=Metrics.SPACING,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _safe(self, callback: Callable[[], T], default: T) -> T:
        """Run a data callback, returning a default value on failure."""
        try:
            return callback()
        except Exception:  # noqa: BLE001 - the dashboard must not crash
            logger.exception("No se pudieron cargar datos del panel")
            return default

    def _stats(self) -> ft.Control:
        clients = self._safe(self.services.clients.count_clients, 0)
        equipment = self._safe(self.services.equipment.count_equipment, 0)
        pending = self._safe(
            lambda: self.services.services.count_services_by_status(
                ServiceStatus.PENDING
            ),
            0,
        )
        completed = self._safe(
            lambda: self.services.services.count_services_by_status(
                ServiceStatus.COMPLETED
            ),
            0,
        )
        incidents = self._safe(self.services.incidents.count_open_incidents, 0)

        column = {"sm": 12, "md": 6, "lg": 3}
        cards = [
            StatCard(
                "Clientes",
                clients,
                ft.Icons.PEOPLE_OUTLINED,
                Palette.PRIMARY,
                col=column,
            ),
            StatCard(
                "Equipos",
                equipment,
                ft.Icons.BUILD_OUTLINED,
                Palette.INFO,
                col=column,
            ),
            StatCard(
                "Servicios pendientes",
                pending,
                ft.Icons.SCHEDULE_OUTLINED,
                Palette.WARNING,
                col=column,
            ),
            StatCard(
                "Servicios completados",
                completed,
                ft.Icons.CHECK_CIRCLE_OUTLINED,
                Palette.SUCCESS,
                col=column,
            ),
            StatCard(
                "Incidencias abiertas",
                incidents,
                ft.Icons.WARNING_AMBER_OUTLINED,
                Palette.DANGER,
                col=column,
            ),
        ]
        return ft.ResponsiveRow(
            controls=cards,
            spacing=Metrics.SPACING,
            run_spacing=Metrics.SPACING,
        )

    def _services_section(self) -> ft.Control:
        recent = self._safe(
            lambda: self.services.services.list_recent_services(5), []
        )
        upcoming = self._safe(
            lambda: self.services.services.list_upcoming_services(5), []
        )
        return ft.ResponsiveRow(
            controls=[
                self._services_card(
                    "Servicios recientes",
                    ft.Icons.HISTORY_OUTLINED,
                    recent,
                    self._created_subtitle,
                ),
                self._services_card(
                    "Próximos servicios",
                    ft.Icons.EVENT_OUTLINED,
                    upcoming,
                    self._scheduled_subtitle,
                ),
            ],
            spacing=Metrics.SPACING,
            run_spacing=Metrics.SPACING,
        )

    def _services_card(
        self,
        title: str,
        icon: ft.IconData,
        services: list[Service],
        subtitle_builder: Callable[[Service], str],
    ) -> GlassCard:
        if services:
            body: ft.Control = ft.Column(
                controls=[
                    self._service_row(service, subtitle_builder(service))
                    for service in services
                ],
                spacing=Metrics.SPACING_SMALL,
            )
        else:
            body = ft.Container(
                content=EmptyState(
                    "Sin servicios",
                    "No hay servicios en esta sección.",
                    icon=ft.Icons.ASSIGNMENT_OUTLINED,
                ),
                padding=Metrics.SPACING,
                alignment=ft.Alignment.CENTER,
            )

        return GlassCard(
            content=ft.Column(
                controls=[SectionHeader(title, icon=icon), body],
                spacing=Metrics.SPACING,
            ),
            col={"sm": 12, "md": 6},
        )

    def _service_row(self, service: Service, subtitle: str) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                service.service_type,
                                size=FontSize.BODY,
                                weight=ft.FontWeight.W_500,
                                color=Palette.TEXT,
                            ),
                            ft.Text(
                                subtitle,
                                size=FontSize.CAPTION,
                                color=Palette.TEXT_MUTED,
                            ),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                    StatusBadge(service.status),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(vertical=6),
        )

    def _incidents_section(self) -> ft.Control:
        incidents = self._safe(
            lambda: self.services.incidents.list_open_incidents(5), []
        )
        if incidents:
            body: ft.Control = ft.Column(
                controls=[
                    self._incident_row(incident) for incident in incidents
                ],
                spacing=Metrics.SPACING_SMALL,
            )
        else:
            body = ft.Container(
                content=EmptyState(
                    "Sin incidencias abiertas",
                    "No hay incidencias pendientes de resolver.",
                    icon=ft.Icons.CHECK_CIRCLE_OUTLINED,
                ),
                padding=Metrics.SPACING,
                alignment=ft.Alignment.CENTER,
            )

        return GlassCard(
            content=ft.Column(
                controls=[
                    SectionHeader(
                        "Incidencias prioritarias",
                        icon=ft.Icons.WARNING_AMBER_OUTLINED,
                    ),
                    body,
                ],
                spacing=Metrics.SPACING,
            )
        )

    def _incident_row(self, incident: Incident) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                incident.title,
                                size=FontSize.BODY,
                                weight=ft.FontWeight.W_500,
                                color=Palette.TEXT,
                            ),
                            ft.Text(
                                f"{t('Registrada')}: "
                                f"{format_datetime(incident.created_at)}",
                                size=FontSize.CAPTION,
                                color=Palette.TEXT_MUTED,
                            ),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                    StatusBadge(incident.priority),
                    StatusBadge(incident.status),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=Metrics.SPACING_SMALL,
            ),
            padding=ft.Padding.symmetric(vertical=6),
        )

    @staticmethod
    def _created_subtitle(service: Service) -> str:
        return f"{t('Creado')}: {format_datetime(service.created_at)}"

    @staticmethod
    def _scheduled_subtitle(service: Service) -> str:
        if service.scheduled_date is not None:
            return f"{t('Programado')}: {format_datetime(service.scheduled_date)}"
        return f"{t('Creado')}: {format_datetime(service.created_at)}"
