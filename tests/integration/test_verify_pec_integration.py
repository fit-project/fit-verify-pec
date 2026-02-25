from __future__ import annotations

import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest
from PySide6 import QtWidgets


@pytest.mark.integration
def test_verification_flow_smoke(
    qapp,
    monkeypatch: pytest.MonkeyPatch,
    stub_external_modules,
    tmp_path: Path,
) -> None:
    module = importlib.reload(importlib.import_module("fit_verify_pec.view.verify_pec"))

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

    class FakeVerifyController:
        def check_expirationdate(self, _path):
            return {
                "reply_to": "from@example.com",
                "to": "to@example.com",
                "subject": "subject",
                "send_date": "today",
                "expiration_date": "tomorrow",
            }

        def check_signature_exist(self, _path):
            return {"is_signature": True, "message_text": "ok"}

        def check_revoked(self):
            return False

        def check_autority(self):
            return "Provider", True

        def get_mail_info_from_eml(self, _path):
            return {
                "reply_to": "from@example.com",
                "to": "to@example.com",
                "subject": "subject",
                "send_date": "today",
            }

        def ganerate_report(self, _report_info):
            return None

    monkeypatch.setattr(module.VerifyPec, "_VerifyPec__init_ui", fake_init_ui)
    monkeypatch.setattr(module, "verifyPecController", lambda: FakeVerifyController())
    monkeypatch.setattr(
        module,
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

    window = module.VerifyPec()

    eml_path = tmp_path / "doc.eml"
    eml_path.write_text("Subject: integration", encoding="utf-8")
    window.ui.eml_folder_input.setText(str(eml_path))

    window._VerifyPec__verify()

    assert window.ui.verification_status_list.count() == 5
    assert len(stub_external_modules["finish_calls"]) == 1

