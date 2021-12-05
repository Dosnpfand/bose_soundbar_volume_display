# bose_soundbar_volume_display

This repo contains a python based implementation to poll a bose soundbar for its volume and display it if a change was detected. 

# Run it using docker
Assumtion: Docker is already running on the pi, your user is `pi` and this repo is checked out on `/home/pi/repos/bose_soundbar_volume_display/`
- Create/copy the script `vc` from the repo root which pulls the latest container from dockerhub and runs it attaching the X-server
- To have this start automatically on power on, create this file: `/home/pi/.config/autostart/vc.desktop`
- ```
  [Desktop Entry]
  Name=vc
  Exec=/home/pi/repos/bose_soundbar_volume_display/vc
  Type=application
  ```


# Developer installation
When you want to run stuff directly with python.

- Tested with python3.7 (windows) and python 3.9 (raspi3)
- Dependencies are handled via poetry

## Raspberry Pi
- install poetry: `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -`
  - py39/raspbian bullseye has extra depencencies: 
    - dependencies for `lxml`: `sudo apt-get install libxml2-dev libxslt-dev python-dev`
- Installation after poetry has been installed: `poetry install --no-root`

## Windows
- `poetry install --no-root -E windows`

## Docker build 

There is a dockerfile included. To build on the pi, run this in repo root:
- build image: `docker build -t soundbar_vol:latest .`
- run with mounting of display: `docker run --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" soundbar_vol:latest`

Push to registry

