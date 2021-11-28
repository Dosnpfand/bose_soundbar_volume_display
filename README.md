# bose_soundbar_volume_display

## Develop installation

- Tested with python3.7 and python 3.9
- Dependencies are handled via poetry

### Raspberry Pi:
- install poetry: `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -`
  - py39/raspbian bullseye: dependencies for `lxml`: `sudo apt-get install libxml2-dev libxslt-dev python-dev`
- `poetry install --no-root`

### Windows:
- `poetry install --no-root -E windows`

## Docker build 

On Pi:
- build image: `docker build -t soundbar_vol:latest .`
- run with mounting of display: `docker run --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" soundbar_vol:latest`
