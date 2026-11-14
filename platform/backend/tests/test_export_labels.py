"""Export data-label tests."""

from __future__ import annotations

import app.services.export_labels as export_labels


class _Session:
    def close(self):
        pass


def _patch(monkeypatch, values):
    monkeypatch.setattr(export_labels, "SessionLocal", lambda: _Session())
    monkeypatch.setattr(
        export_labels.settings_service,
        "get_setting_fresh",
        lambda _db, key, default="": values.get(key, default),
    )


def test_labels_are_disabled_when_switched_off(monkeypatch):
    _patch(monkeypatch, {"export_label_enabled": "false"})
    assert export_labels.export_labels() is None


def test_labels_use_classification_owner_and_handling(monkeypatch):
    _patch(
        monkeypatch,
        {
            "export_label_enabled": "true",
            "export_classification": "confidential",
            "export_organisation": "Example Institute",
            "export_handling_note": "",
            "export_include_timestamp": "false",
        },
    )
    labels = export_labels.export_labels()
    assert labels["classification"] == "Confidential"
    assert labels["organisation"] == "Example Institute"
    assert "authorised recipients" in labels["handling"]
    assert "generated_at" not in labels


def test_unknown_classification_falls_back_to_internal(monkeypatch):
    _patch(
        monkeypatch,
        {
            "export_label_enabled": "true",
            "export_classification": "top-secret",
            "export_include_timestamp": "true",
        },
    )
    labels = export_labels.export_labels()
    assert labels["classification"] == "Internal"
    assert labels["generated_at"].endswith("+00:00")


def test_pdf_metadata_is_written(monkeypatch):
    from fpdf import FPDF

    _patch(
        monkeypatch,
        {
            "export_label_enabled": "true",
            "export_classification": "restricted",
            "export_organisation": "Example Institute",
            "export_include_timestamp": "false",
        },
    )
    pdf = FPDF()
    pdf.add_page()
    export_labels.apply_pdf_metadata(pdf, "Learner transcript", "Profile transcript")
    output = bytes(pdf.output())
    assert b"Example Institute" in output
    assert b"Restricted" in output

