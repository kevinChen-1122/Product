import uvicorn
from fastapi import FastAPI
from .routes import router
from .db import ensure_indexes

app = FastAPI(title="seller-config-service", version="0.1.0")
app.include_router(router)

@app.on_event("startup")
async def startup():
    await ensure_indexes()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=int( os.environ.get("PORT", "8080")), reload=False)
