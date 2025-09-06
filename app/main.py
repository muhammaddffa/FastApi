from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.internal.connection.prisma import connect_db, disconnect_db
from app.internal.api import auth_route
from app.internal.connection.prisma import db

app = FastAPI(
    title="Payroll Management System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_route.router)

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

@app.get("/")
async def root():
    return {"message": "Awesome it works 🐻"}
