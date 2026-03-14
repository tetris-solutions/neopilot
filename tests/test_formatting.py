"""Tests for formatting and i18n modules."""

from __future__ import annotations

from neopilot.infra.formatting import format_metric_value
from neopilot.infra.i18n import resolve_label


class TestResolveLabel:
    def test_string_label(self):
        assert resolve_label("Simple Label") == "Simple Label"

    def test_dict_label_pt_br(self):
        label = {"pt-BR": "Custo Total", "en-US": "Total Cost"}
        assert resolve_label(label, "pt-BR") == "Custo Total"

    def test_dict_label_en_us(self):
        label = {"pt-BR": "Custo Total", "en-US": "Total Cost"}
        assert resolve_label(label, "en-US") == "Total Cost"

    def test_dict_label_fallback(self):
        label = {"pt-BR": "Custo Total"}
        assert resolve_label(label, "en-US") == "Custo Total"  # Falls back to pt-BR

    def test_dict_label_empty(self):
        assert resolve_label({}, "pt-BR") == ""

    def test_none_label(self):
        assert resolve_label(None) == ""

    def test_numeric_label(self):
        assert resolve_label(42) == "42"


class TestFormatMetricValue:
    # Currency
    def test_currency_pt_br(self):
        result = format_metric_value(1234.56, "currency", "pt-BR")
        assert "R$" in result
        assert "1.234,56" in result

    def test_currency_en_us(self):
        result = format_metric_value(1234.56, "currency", "en-US")
        assert "$" in result
        assert "1,234.56" in result

    # Percent
    def test_percent_pt_br(self):
        result = format_metric_value(0.1234, "percent", "pt-BR")
        assert "12,34%" in result

    def test_percent_en_us(self):
        result = format_metric_value(0.1234, "percent", "en-US")
        assert "12.34%" in result

    def test_percent_already_multiplied(self):
        result = format_metric_value(12.34, "percent", "en-US")
        assert "12.34%" in result

    # Number
    def test_number_integer(self):
        result = format_metric_value(1500, "number", "en-US")
        assert result == "1,500"

    def test_number_float(self):
        result = format_metric_value(1500.75, "number", "en-US")
        assert result == "1,500.75"

    def test_number_pt_br(self):
        result = format_metric_value(1500, "number", "pt-BR")
        assert result == "1.500"

    # Duration
    def test_duration_seconds(self):
        assert format_metric_value(45, "duration") == "45s"

    def test_duration_minutes(self):
        assert format_metric_value(125, "duration") == "2m 5s"

    def test_duration_hours(self):
        assert format_metric_value(3725, "duration") == "1h 2m 5s"

    # Edge cases
    def test_none_value(self):
        assert format_metric_value(None) == "—"

    def test_nan_value(self):
        assert format_metric_value(float("nan")) == "—"

    def test_inf_value(self):
        assert format_metric_value(float("inf")) == "—"

    def test_zero(self):
        result = format_metric_value(0, "currency", "en-US")
        assert "$0.00" in result
