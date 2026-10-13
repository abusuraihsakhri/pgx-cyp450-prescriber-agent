"""Regression tests for finite metrics and conservative PGx interpretation."""
import math
import pytest

from cli import _csv_bool as platform_csv_bool, _csv_float as platform_csv_float
from pgx_cyp450_prescriber_agent.cli import _csv_bool as package_csv_bool
from pgx_prescriber import _csv_bool as legacy_csv_bool
from pgx_cyp450_prescriber_agent.panel_interpreter import PanelInterpreter, MetabolizerPhenotype
from pgx_cyp450_prescriber_agent.drug_gene_alert_engine import (
    DrugGeneAlertEngine, AlertSeverity,
)
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from agents.base import SecurityException


@pytest.mark.parametrize("parser", [platform_csv_bool, package_csv_bool, legacy_csv_bool])
@pytest.mark.parametrize("value,expected", [
    ("False", False), ("false", False), (" 0 ", False), ("", False),
    ("True", True), ("YES", True), ("1", True),
])
def test_csv_booleans(parser, value, expected):
    assert parser(value) is expected


@pytest.mark.parametrize("parser", [platform_csv_bool, package_csv_bool, legacy_csv_bool])
def test_csv_bool_invalid(parser):
    with pytest.raises(ValueError):
        parser("sometimes")


@pytest.mark.parametrize("value", ["NaN", "inf", "-Infinity"])
def test_reject_nonfinite_csv(value):
    with pytest.raises(ValueError):
        platform_csv_float(value)


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_reject_nonfinite_api_metric(value):
    with pytest.raises(ValueError):
        SystemTaskPayload(task_id="synthetic-01", target_identifier="synthetic-02", primary_metric=value)


@pytest.mark.parametrize("gene,alleles,expected,score", [
    ("CYP2D6", ("*1", "*4"), MetabolizerPhenotype.INTERMEDIATE, 1.0),
    ("CYP2D6", ("*1", "*10"), MetabolizerPhenotype.NORMAL, 1.25),
    ("CYP2D6", ("*10", "*10"), MetabolizerPhenotype.INTERMEDIATE, 0.5),
    ("CYP2D6", ("*4", "*4"), MetabolizerPhenotype.POOR, 0),
    ("CYP2D6", ("*1", "*1"), MetabolizerPhenotype.NORMAL, 2.0),
    ("CYP2C19", ("*1", "*17"), MetabolizerPhenotype.RAPID, None),
    ("CYP2C19", ("*17", "*17"), MetabolizerPhenotype.ULTRARAPID, None),
    ("CYP2C19", ("*2", "*17"), MetabolizerPhenotype.INTERMEDIATE, None),
    ("CYP2C19", ("*8", "*1"), MetabolizerPhenotype.INTERMEDIATE, None),
    ("CYP2C19", ("*2", "*2"), MetabolizerPhenotype.POOR, None),
])
def test_gene_specific_translation(gene, alleles, expected, score):
    result = PanelInterpreter().interpret_diplotype(gene, *alleles)
    assert result is not None
    assert result.phenotype == expected
    assert result.activity_score == score


@pytest.mark.parametrize("gene,alleles", [
    ("CYP2C9", ("*1", "*3")),
    ("SLCO1B1", ("*1A", "*5")),
    ("CYP3A5", ("*1", "*3")),
])
def test_unimplemented_gene_fails_closed(gene, alleles):
    result = PanelInterpreter().interpret_diplotype(gene, *alleles)
    assert result.phenotype == MetabolizerPhenotype.INDETERMINATE
    assert result.activity_score is None
    assert result.confidence == "LOW"


def test_unresolved_copy_number_not_guessed():
    assert PanelInterpreter().interpret_diplotype("CYP2D6", "*1", "*xN") is None


def test_panel_flags_only_supported_interactions():
    panel = PanelInterpreter().interpret_panel({
        "CYP2D6": ("*4", "*4"),
        "CYP2C19": ("*1", "*17"),
        "SLCO1B1": ("*1A", "*5"),
        "CYP3A5": ("*1", "*3"),
    })
    assert panel.panel_confidence == "LOW"
    assert all(alert.get("severity") == "REVIEW" for alert in panel.combined_drug_alerts)
    assert not any(alert.get("gene") in ("SLCO1B1", "CYP3A5") for alert in panel.combined_drug_alerts)


def test_unsupported_panel_allele_not_silently_skipped():
    panel = PanelInterpreter().interpret_panel({"CYP2D6": ("*999", "*1")})
    assert panel.panel_confidence == "LOW"
    assert panel.combined_drug_alerts[0]["severity"] == "REVIEW"


def test_normalized_gene_and_string_phenotypes():
    engine = DrugGeneAlertEngine()
    alerts = engine.check_prescription("CODEINE", {"cyp2d6": "um"})
    assert len(alerts) == 1
    assert alerts[0].severity == AlertSeverity.CRITICAL
    assert alerts[0].phenotype.value == "UM"


def test_unknown_phenotype_rejected():
    with pytest.raises(ValueError):
        DrugGeneAlertEngine().check_prescription("codeine", {"CYP2D6": "NOT_VALID"})


def test_non_codeine_pm_not_automatically_critical():
    alerts = DrugGeneAlertEngine().check_prescription("warfarin", {"CYP2C9": "PM"})
    assert len(alerts) == 1
    assert alerts[0].severity == AlertSeverity.WARNING


def test_phi_in_nested_task_attributes_blocked():
    payload = SystemTaskPayload(
        task_id="SYN-001", target_identifier="synthetic-02", primary_metric=1,
        attributes={"note": "Contact patient at 555-123-4567"},
    )
    with pytest.raises(SecurityException):
        SystemSupervisor().process_task(payload)


def test_finite_csv_number():
    assert platform_csv_float("12.5") == 12.5
