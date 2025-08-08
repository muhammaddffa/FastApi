from fastapi import FastAPI
from app.internal.api import user_route
from app.internal.connection.prisma import prisma

app = FastAPI()

app.include_router(user_route.router)

@app.on_event("startup")
async def startup():
    await prisma.connect()

@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()

@app.get("/")
def read_root():
    return {"message": "Awesome it works 🐻"}       