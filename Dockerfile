FROM arm32v7/python:3.7-bullseye

# install poetry and then python deps using poetry: this takes ~15min
COPY poetry.lock pyproject.toml /bose/
RUN pip install --upgrade pip
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
RUN cd /bose &&  /root/.poetry/bin/poetry install --no-root

# copy application: this is quite fast
COPY app/ /bose/app
CMD cd /bose && /root/.poetry/bin/poetry run python /bose/app/volume_ctrl.py
