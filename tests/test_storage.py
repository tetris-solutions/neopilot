"""Tests for local storage."""

from __future__ import annotations

import pytest

from neopilot.api.errors import InstanceNotFoundError
from neopilot.models.context import UserContext
from neopilot.storage.local_store import InstanceStore, UserContextStore


class TestInstanceStore:
    def test_add_and_list(self, tmp_data_dir):
        store = InstanceStore(data_dir=tmp_data_dir)
        store.add_instance("loreal", "token_lor", language="pt-BR")
        store.add_instance("mdlz", "token_mdlz", language="en-US")

        instances = store.list_instances()
        assert len(instances) == 2
        slugs = {i.slug for i in instances}
        assert slugs == {"loreal", "mdlz"}

    def test_active_instance(self, tmp_data_dir):
        store = InstanceStore(data_dir=tmp_data_dir)
        store.add_instance("loreal", "token_lor")
        store.add_instance("mdlz", "token_mdlz")

        # Last added should be active
        active = store.get_active()
        assert active.slug == "mdlz"

    def test_switch_active(self, tmp_data_dir):
        store = InstanceStore(data_dir=tmp_data_dir)
        store.add_instance("loreal", "token_lor")
        store.add_instance("mdlz", "token_mdlz")

        store.set_active("loreal")
        active = store.get_active()
        assert active.slug == "loreal"

    def test_switch_nonexistent_raises(self, tmp_data_dir):
        store = InstanceStore(data_dir=tmp_data_dir)
        store.add_instance("loreal", "token_lor")

        with pytest.raises(InstanceNotFoundError):
            store.set_active("nonexistent")

    def test_remove_instance(self, tmp_data_dir):
        store = InstanceStore(data_dir=tmp_data_dir)
        store.add_instance("loreal", "token_lor")
        store.add_instance("mdlz", "token_mdlz")

        store.remove_instance("loreal")
        instances = store.list_instances()
        assert len(instances) == 1
        assert instances[0].slug == "mdlz"

    def test_remove_nonexistent_raises(self, tmp_data_dir):
        store = InstanceStore(data_dir=tmp_data_dir)
        with pytest.raises(InstanceNotFoundError):
            store.remove_instance("nonexistent")

    def test_get_token(self, tmp_data_dir):
        store = InstanceStore(data_dir=tmp_data_dir)
        store.add_instance("loreal", "secret_token_123")

        assert store.get_token("loreal") == "secret_token_123"

    def test_get_token_nonexistent(self, tmp_data_dir):
        store = InstanceStore(data_dir=tmp_data_dir)
        with pytest.raises(InstanceNotFoundError):
            store.get_token("nope")

    def test_no_active_instance_raises(self, tmp_data_dir):
        store = InstanceStore(data_dir=tmp_data_dir)
        with pytest.raises(InstanceNotFoundError, match="No NeoDash instance"):
            store.get_active()

    def test_update_existing_instance(self, tmp_data_dir):
        store = InstanceStore(data_dir=tmp_data_dir)
        store.add_instance("loreal", "old_token")
        store.add_instance("loreal", "new_token")

        instances = store.list_instances()
        assert len(instances) == 1
        assert instances[0].api_token == "new_token"

    def test_fallback_to_last_instance(self, tmp_data_dir):
        """If no instance is marked active, fallback to the last one."""
        store = InstanceStore(data_dir=tmp_data_dir)
        store.add_instance("loreal", "token")

        # Manually deactivate
        data = store._load()
        for inst in data.instances:
            inst.is_active = False
        store._save(data)

        active = store.get_active()
        assert active.slug == "loreal"


class TestUserContextStore:
    def test_load_nonexistent_returns_defaults(self, tmp_data_dir):
        store = UserContextStore(data_dir=tmp_data_dir)
        ctx = store.load("loreal")
        assert ctx.slug == "loreal"
        assert ctx.dashboards_of_interest == []
        assert ctx.metrics_of_interest == []

    def test_save_and_load(self, tmp_data_dir):
        store = UserContextStore(data_dir=tmp_data_dir)
        ctx = UserContext(
            slug="loreal",
            dashboards_of_interest=["3000001", "3000002"],
            metrics_of_interest=["custo_total", "roi"],
            notes=["Focus on Amazon"],
        )
        store.save(ctx)

        loaded = store.load("loreal")
        assert loaded.dashboards_of_interest == ["3000001", "3000002"]
        assert loaded.metrics_of_interest == ["custo_total", "roi"]
        assert loaded.notes == ["Focus on Amazon"]
        assert loaded.last_updated is not None

    def test_update_dashboards(self, tmp_data_dir):
        store = UserContextStore(data_dir=tmp_data_dir)
        ctx = store.update_dashboards("loreal", ["3000001", "3000003"])
        assert ctx.dashboards_of_interest == ["3000001", "3000003"]

    def test_update_metrics(self, tmp_data_dir):
        store = UserContextStore(data_dir=tmp_data_dir)
        ctx = store.update_metrics("loreal", ["cpc", "ctr"])
        assert ctx.metrics_of_interest == ["cpc", "ctr"]

    def test_add_note(self, tmp_data_dir):
        store = UserContextStore(data_dir=tmp_data_dir)
        store.add_note("loreal", "First note")
        ctx = store.add_note("loreal", "Second note")
        assert len(ctx.notes) == 2
        assert ctx.notes[0] == "First note"
        assert ctx.notes[1] == "Second note"

    def test_separate_contexts_per_slug(self, tmp_data_dir):
        store = UserContextStore(data_dir=tmp_data_dir)
        store.update_dashboards("loreal", ["db1"])
        store.update_dashboards("mdlz", ["db2", "db3"])

        lor = store.load("loreal")
        mdlz = store.load("mdlz")
        assert lor.dashboards_of_interest == ["db1"]
        assert mdlz.dashboards_of_interest == ["db2", "db3"]
