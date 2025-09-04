from prisma import Prisma
from contextlib import asynccontextmanager

db = Prisma()

async def connect_db():
    await db.connect()
    print("Database connected")

async def disconnect_db():
    await db.disconnect()
    print("Database disconnected")

async def get_db() -> Prisma:
    if not db.is_connected():
        await db.connect()
    return db