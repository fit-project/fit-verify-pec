from __future__ import annotations

import importlib
import inspect
import json
from pathlib import Path

import pytest


@pytest.mark.contract
def test_verify_pec_exposes_expected_api(stub_external_modules) -> None:
    module = importlib.reload(importlib.import_module("fit_verify_pec.view.verify_pec"))
    cls = module.VerifyPec

    assert callable(getattr(cls, "closeEvent", None))
    assert callable(getattr(cls, "move_window", None))
    assert callable(getattr(cls, "mousePressEvent", None))
    assert callable(getattr(cls, "_VerifyPec__verify", None))
    assert callable(getattr(cls, "_VerifyPec__generate_report", None))


@pytest.mark.contract
def test_verify_pec_constructor_accepts_optional_wizard(
    stub_external_modules,
) -> None:
    module = importlib.reload(importlib.import_module("fit_verify_pec.view.verify_pec"))
    signature = inspect.signature(module.VerifyPec.__init__)

    assert "wizard" in signature.parameters
    assert signature.parameters["wizard"].default is None


@pytest.mark.contract
def test_language_files_define_required_keys() -> None:
    lang_dir = Path(__file__).resolve().parents[2] / "fit_verify_pec" / "lang"
    en = json.loads((lang_dir / "en.json").read_text(encoding="utf-8"))
    it = json.loads((lang_dir / "it.json").read_text(encoding="utf-8"))

    required_keys = {
        "OPEN_EML_FILE",
        "EML_FILES",
        "CHECK_EXPIRATIONDATE",
        "CHECK_EXPIRATIONDATE_FAIL",
        "CHECK_SIGNATURE",
        "CHECK_REVOKED",
        "CHECK_AUTORITY",
        "GET_MAIL_INFO_FROM_EML",
        "NO_MAIL_INFO_FOUD_AFTER_CHECK_EXPIRATIONDATE",
        "GENARATE_REPORT",
        "SIGNATURE_NOT_EXIST",
        "SIGNATURE_EXIST",
        "INTEGRITY_FAIL",
        "INTEGRITY_SUCCESS",
        "PROVIDER_IS_ON_AGID_LIST",
        "PROVIDER_IS_NOT_ON_AGID_LIST",
        "PEC_ADDRESS_IS_NOT_REVOKED",
        "PEC_ADDRESS_IS_REVOKED",
        "REPORT_LABEL_DETAILS",
        "REPORT_LABEL_PROVIDER_CHECK",
    }

    assert required_keys.issubset(en.keys())
    assert required_keys.issubset(it.keys())

