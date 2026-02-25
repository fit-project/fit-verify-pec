from __future__ import annotations

import importlib

import pytest


@pytest.mark.unit
def test_load_translations_uses_selected_language(stub_external_modules) -> None:
    lang_module = importlib.reload(importlib.import_module("fit_verify_pec.lang"))

    translations = lang_module.load_translations("it")
    assert translations["OPEN_EML_FILE"] == "Apri .eml"


@pytest.mark.unit
def test_load_translations_falls_back_to_default(
    monkeypatch: pytest.MonkeyPatch, stub_external_modules
) -> None:
    lang_module = importlib.reload(importlib.import_module("fit_verify_pec.lang"))

    monkeypatch.setattr(lang_module, "DEFAULT_LANG", "en")
    translations = lang_module.load_translations("zz")

    assert translations["OPEN_EML_FILE"] == "Open .eml"


@pytest.mark.unit
def test_load_translations_uses_system_language_when_missing(
    monkeypatch: pytest.MonkeyPatch, stub_external_modules
) -> None:
    lang_module = importlib.reload(importlib.import_module("fit_verify_pec.lang"))

    monkeypatch.setattr(lang_module, "get_system_lang", lambda: "it")
    translations = lang_module.load_translations()

    assert translations["GENARATE_REPORT"] == "Generazione report"
