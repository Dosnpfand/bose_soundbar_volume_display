# bose_soundbar_volume_display

**installation**

- Tested with python3.7 and python 3.9
- Dependencies are handled via poetry

Raspberry:
- install poetry: `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -`
  - py39/raspbian bullseye: dependencies for `lxml`: `sudo apt-get install libxml2-dev libxslt-dev python-dev`
- `poetry install --no-root`

Windows:
- `poetry install --no-root -E windows`

