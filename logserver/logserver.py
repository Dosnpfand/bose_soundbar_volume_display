from fastapi import HTTPException

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from starlette import status

app = FastAPI()


@app.get("/")
def read_root():
    return [{"msg": "Hello World"}]


class LogEntry(BaseModel):
    identifier: str
    payload: str


@app.post("/log")
def log(data: LogEntry):
    if data.identifier == "stef":
        print(f"payload: {data.payload}")
        return {"status": "success"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="unknown identifier",
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
