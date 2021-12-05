FROM arm32v7/python:3.7-bullseye

# install poetry and then python deps using poetry: this takes ~15min
RUN pip install --upgrade pip
COPY poetry.lock pyproject.toml poetry.toml /bose/
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
RUN cd /bose &&  /root/.poetry/bin/poetry install --no-root

# for python script to check if inside docker
ENV INSIDE_DOCKER yes  
# copy application: this is quite fast
COPY app/ /bose/app
CMD cd /bose && /root/.poetry/bin/poetry run python /bose/app/volume_ctrl.py
