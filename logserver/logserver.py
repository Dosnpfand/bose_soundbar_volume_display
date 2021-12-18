import os
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import PlainTextResponse

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from starlette import status

app = FastAPI()

valid_ids = os.getenv('VALID_IDS', '').split(',')  # comma separated, e.g. "id1,id2,id3"


@app.get("/")
def read_root():
    return [{"msg": "Hello World"}]


class LogEntry(BaseModel):
    identifier: str
    payload: str


@app.post("/log")
def log(data: LogEntry):
    if data.identifier in valid_ids:

        if os.getenv('INSIDE_DOCKER', False):
            fpath = '/logs/' + data.identifier + '.log'
        else:
            fpath = data.identifier + '.log'

        with open(fpath, 'a') as f:
            f.write(f"{data.payload}\n")

        print(f"payload: {data.payload}")
        return {"status": "success"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="unknown identifier",
        )


@app.get("/logs/", response_class=PlainTextResponse)
def read_item(identifier: str):

    if identifier in valid_ids:
        if os.getenv('INSIDE_DOCKER', False):
            fpath = Path('/logs/' + identifier + '.log')
        else:
            fpath = Path(identifier + '.log')

        if fpath.exists():
            with open(fpath, 'r') as f:
                lines = f.read()
            return lines
        else:
            return "Nothing logged yet."
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="unknown identifier",
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
