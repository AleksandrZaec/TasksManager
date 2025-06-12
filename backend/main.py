from fastapi import FastAPI

app = FastAPI(title="Team Manager")


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok", "db": "not checked"}
