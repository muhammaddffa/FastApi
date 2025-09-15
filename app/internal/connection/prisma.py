from prisma import Prisma

prisma = Prisma()

db = prisma
async def connect_db():
    if not prisma.is_connected():
        await prisma.connect()
    return prisma

async def disconnect_db():
    if prisma.is_connected():
        await prisma.disconnect()

async def get_db() -> Prisma:
    if not prisma.is_connected():
        await prisma.connect()
    return prisma
