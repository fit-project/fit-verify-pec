# fit-verify-pec

**FIT Verify PEC Module** is a component of the [FIT Project](https://github.com/fit-project) ecosystem.

This module provides a graphical interface for verifying the PEC applied sent during the acquisition process.

---

## Related FIT components

This module depends on:

- [`fit-cases`](https://github.com/fit-project/fit-cases.git) – Case information

## Dependencies

Main dependencies are:

- Python `>=3.11,<3.13`
- [`PySide6`](https://pypi.org/project/PySide6/) 6.9.0
- `fit-cases` (custom submodule)

See `pyproject.toml` for full details.

---

## Requirements
- **Python** 3.11
- **Poetry** (recommended for development)

## 🚀 Installation

You can install the module using **Poetry**:

```bash
git clone https://github.com/fit-project/fit-verify-pec.git
cd fit-verify-pec
poetry install
```

To run the verify-pec:

```bash
poetry run python main.py
```
---

## Contributing
1. Fork this repository.  
2. Create a new branch (`git checkout -b feat/my-feature`).  
3. Commit your changes using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).  
4. Submit a Pull Request describing your modification.

---