from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.internal.api import user_route, auth_route
from app.internal.connection.prisma import prisma

app = FastAPI()

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_route.router)
app.include_router(auth_route.router)


@app.on_event("startup")
async def startup():
    await prisma.connect()

@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()

@app.get("/")
def read_root():
    return {"message": "Awesome it works 🐻"}       