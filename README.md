# fit-verify-pec

Verify PEC Module for the **FIT Project**, built using [PySide6](https://doc.qt.io/qtforpython/).

This module provides a graphical interface for verifying the PEC applied sent during the acquisition process.

---

## 🔗 Related FIT components

This package is part of the broader [fit](https://github.com/fit-project/fit) ecosystem and depends on:

- [`fit-common`](https://github.com/fit-project/fit-common) – shared utility and core logic
- [`fit-assets`](https://github.com/fit-project/fit-assets) – UI resources and assets
- [`fit-configurations`](https://github.com/fit-project/fit-configurations.git) – Configuration settings
- [`fit-cases`](https://github.com/fit-project/fit-cases.git) – Case information

---

## 🐍 Dependencies

Main dependencies are:

- Python `>3.9.0,<3.9.1` or `>3.9.1,<3.13`
- [`PySide6`](https://pypi.org/project/PySide6/) `6.9.0` – Qt for Python UI framework
- [`cryptography`](https://pypi.org/project/cryptography/) `^44.0.2` – Cryptographic operations
- [`bs4`](https://pypi.org/project/bs4/) `^0.0.2` – HTML/XML parsing (BeautifulSoup wrapper)
- [`xhtml2pdf`](https://pypi.org/project/xhtml2pdf/) `^0.2.17` – PDF generation from HTML
- [`pypdf2`](https://pypi.org/project/pypdf2/) `^3.0.1` – PDF manipulation
- [`jinja2`](https://pypi.org/project/Jinja2/) `^3.1.6` – Templating engine for HTML

Custom submodules:

- [`fit-cases`](https://github.com/fit-project/fit-cases.git`) – case information (installed via Git)

See `pyproject.toml` for full details.

---

## 🚀 Installation

Install the module using [Poetry](https://python-poetry.org/):

```bash
poetry install
