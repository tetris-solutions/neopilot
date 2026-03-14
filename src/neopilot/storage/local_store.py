"""Local JSON file storage for instances and user context."""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime

from neopilot.api.errors import InstanceNotFoundError
from neopilot.infra.env import get_data_dir
from neopilot.models.context import UserContext
from neopilot.models.instance import InstanceInfo, InstancesFile

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Instance storage
# ------------------------------------------------------------------


class InstanceStore:
    """Manage slug:token pairs in ``~/.neopilot/instances.json``."""

    def __init__(self, data_dir: str | None = None) -> None:
        self._data_dir = data_dir or get_data_dir()
        self._path = os.path.join(self._data_dir, "instances.json")

    def _load(self) -> InstancesFile:
        if not os.path.exists(self._path):
            return InstancesFile()
        try:
            with open(self._path, encoding="utf-8") as f:
                return InstancesFile.model_validate_json(f.read())
        except Exception:
            logger.warning("Could not read %s, starting fresh.", self._path)
            return InstancesFile()

    def _save(self, data: InstancesFile) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            f.write(data.model_dump_json(indent=2))

    def add_instance(
        self,
        slug: str,
        api_token: str,
        language: str = "pt-BR",
    ) -> InstanceInfo:
        """Add or update an instance. Makes it the active instance."""
        data = self._load()

        # Remove existing entry with same slug
        data.instances = [i for i in data.instances if i.slug != slug]

        # Deactivate all others
        for inst in data.instances:
            inst.is_active = False

        now = datetime.now(UTC).isoformat()
        info = InstanceInfo(
            slug=slug,
            api_token=api_token,
            language=language,
            last_connected=now,
            is_active=True,
        )
        data.instances.append(info)
        self._save(data)
        logger.info("Instance '%s' added and set as active.", slug)
        return info

    def remove_instance(self, slug: str) -> None:
        """Remove an instance by slug."""
        data = self._load()
        before = len(data.instances)
        data.instances = [i for i in data.instances if i.slug != slug]
        if len(data.instances) == before:
            raise InstanceNotFoundError(f"Instance '{slug}' not found.")
        self._save(data)
        logger.info("Instance '%s' removed.", slug)

    def list_instances(self) -> list[InstanceInfo]:
        """List all saved instances."""
        return self._load().instances

    def get_active(self) -> InstanceInfo:
        """Return the active instance.

        Raises
        ------
        InstanceNotFoundError
            If no instance is active.
        """
        data = self._load()
        for inst in data.instances:
            if inst.is_active:
                return inst
        if data.instances:
            # Fall back to the last added instance
            data.instances[-1].is_active = True
            self._save(data)
            return data.instances[-1]
        raise InstanceNotFoundError(
            "No NeoDash instance connected. Use the connect_instance tool first."
        )

    def set_active(self, slug: str) -> InstanceInfo:
        """Switch the active instance.

        Raises
        ------
        InstanceNotFoundError
            If the slug does not exist.
        """
        data = self._load()
        found = False
        active_inst = None
        for inst in data.instances:
            if inst.slug == slug:
                inst.is_active = True
                inst.last_connected = datetime.now(UTC).isoformat()
                found = True
                active_inst = inst
            else:
                inst.is_active = False
        if not found:
            raise InstanceNotFoundError(f"Instance '{slug}' not found.")
        self._save(data)
        logger.info("Switched active instance to '%s'.", slug)
        return active_inst  # type: ignore[return-value]  # guarded by `found` check above

    def get_token(self, slug: str) -> str:
        """Return the API token for a slug."""
        data = self._load()
        for inst in data.instances:
            if inst.slug == slug:
                return inst.api_token
        raise InstanceNotFoundError(f"Instance '{slug}' not found.")


# ------------------------------------------------------------------
# User context storage
# ------------------------------------------------------------------


class UserContextStore:
    """Read/write user context from local JSON files."""

    def __init__(self, data_dir: str | None = None) -> None:
        self._data_dir = data_dir or get_data_dir()

    def _path(self, slug: str) -> str:
        return os.path.join(self._data_dir, f"user_context_{slug}.json")

    def load(self, slug: str) -> UserContext:
        """Load user context for a slug, returning defaults if absent."""
        path = self._path(slug)
        if not os.path.exists(path):
            return UserContext(slug=slug)
        try:
            with open(path, encoding="utf-8") as f:
                return UserContext.model_validate_json(f.read())
        except Exception:
            logger.warning("Could not read user context for '%s', using defaults.", slug)
            return UserContext(slug=slug)

    def save(self, ctx: UserContext) -> None:
        """Save user context to disk."""
        ctx.last_updated = datetime.now(UTC).isoformat()
        path = self._path(ctx.slug)
        with open(path, "w", encoding="utf-8") as f:
            f.write(ctx.model_dump_json(indent=2))
        logger.info("User context saved for '%s'.", ctx.slug)

    def update_dashboards(self, slug: str, dashboard_ids: list[str]) -> UserContext:
        """Set which dashboards the user wants to monitor."""
        ctx = self.load(slug)
        ctx.dashboards_of_interest = dashboard_ids
        self.save(ctx)
        return ctx

    def update_metrics(self, slug: str, metric_ids: list[str]) -> UserContext:
        """Set which metrics the user cares about."""
        ctx = self.load(slug)
        ctx.metrics_of_interest = metric_ids
        self.save(ctx)
        return ctx

    def add_note(self, slug: str, note: str) -> UserContext:
        """Add a personal context note."""
        ctx = self.load(slug)
        ctx.notes.append(note)
        self.save(ctx)
        return ctx
