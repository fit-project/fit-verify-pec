from __future__ import annotations

import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest
from PySide6 import QtWidgets


@pytest.fixture
def verify_module(stub_external_modules):
    return importlib.reload(importlib.import_module("fit_verify_pec.view.verify_pec"))


@pytest.fixture
def window_stub(
    qapp, verify_module, monkeypatch: pytest.MonkeyPatch
):
    def fake_init_ui(self):
        self.ui = SimpleNamespace(
            left_box=QtWidgets.QWidget(),
            minimize_button=QtWidgets.QPushButton(),
            close_button=QtWidgets.QPushButton(),
            version=QtWidgets.QLabel(),
            eml_folder_button=QtWidgets.QPushButton(),
            eml_folder_input=QtWidgets.QLineEdit(),
            verification_button=QtWidgets.QPushButton(),
            verification_status_list=QtWidgets.QListWidget(),
        )
        self.ui.verification_button.setEnabled(False)

    monkeypatch.setattr(verify_module.VerifyPec, "_VerifyPec__init_ui", fake_init_ui)
    monkeypatch.setattr(
        verify_module,
        "load_translations",
        lambda *args, **kwargs: {
            "OPEN_EML_FILE": "Open EML",
            "EML_FILES": "EML (*.eml)",
            "CHECK_EXPIRATIONDATE": "Check expiration date",
            "CHECK_SIGNATURE": "Check signature",
            "CHECK_REVOKED": "Check revoked",
            "CHECK_AUTORITY": "Check authority",
            "GET_MAIL_INFO_FROM_EML": "Get mail info",
            "NO_MAIL_INFO_FOUD_AFTER_CHECK_EXPIRATIONDATE": "No mail info found",
            "GENARATE_REPORT": "Generate report",
            "CHECK_EXPIRATIONDATE_FAIL": "Check expiration date failed",
        },
    )

    window = verify_module.VerifyPec()
    window.verify_pec_controller = SimpleNamespace(
        check_expirationdate=lambda _path: {
            "reply_to": "from@example.com",
            "to": "to@example.com",
            "subject": "subject",
            "send_date": "today",
            "expiration_date": "tomorrow",
        },
        check_signature_exist=lambda _path: {"is_signature": True, "message_text": "ok"},
        check_revoked=lambda: False,
        check_autority=lambda: ("Provider", True),
        get_mail_info_from_eml=lambda _path: {
            "reply_to": "from@example.com",
            "to": "to@example.com",
            "subject": "subject",
            "send_date": "today",
        },
        ganerate_report=lambda _report_info: None,
    )
    return window


@pytest.mark.unit
def test_enable_verify_button_depends_on_eml_field(window_stub) -> None:
    window = window_stub

    window.ui.eml_folder_input.setText("")
    window._VerifyPec__enable_verify_button()
    assert window.ui.verification_button.isEnabled() is False

    window.ui.eml_folder_input.setText("/tmp/mail.eml")
    window._VerifyPec__enable_verify_button()
    assert window.ui.verification_button.isEnabled() is True


@pytest.mark.unit
def test_select_eml_file_populates_input(
    window_stub, verify_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    window = window_stub
    monkeypatch.setattr(
        verify_module.QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: ("/tmp/demo.eml", True),
    )

    window._VerifyPec__select_eml_file()

    assert window.ui.eml_folder_input.text() == "/tmp/demo.eml"


@pytest.mark.unit
def test_check_expirationdate_failure_adds_label(
    window_stub, verify_module
) -> None:
    window = window_stub
    window.ui.eml_folder_input.setText("/tmp/fail.eml")

    def fail(_path):
        raise RuntimeError("invalid certificate")

    window.verify_pec_controller.check_expirationdate = fail

    status, email_info = window._VerifyPec__check_expirationdate()

    assert status == verify_module.Status.FAILURE
    assert email_info == {}
    assert window.ui.verification_status_list.count() == 1


@pytest.mark.unit
def test_verify_flow_success_generates_labels_and_report(window_stub, stub_external_modules) -> None:
    window = window_stub
    eml_path = Path("/tmp/pec_test.eml")
    eml_path.write_text("Subject: test\n\nbody", encoding="utf-8")
    window.ui.eml_folder_input.setText(str(eml_path))

    window._VerifyPec__verify()

    assert window.ui.verification_status_list.count() == 5
    assert len(stub_external_modules["finish_calls"]) == 1

