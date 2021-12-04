FROM arm32v7/python:3.7-bullseye

COPY app/ /bose

RUN pip install --upgrade pip
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
RUN export PATH=$PATH:/root/.poetry/bin

# cd into folder
RUN cd /bose && /root/.poetry/bin/poetry install --no-root
