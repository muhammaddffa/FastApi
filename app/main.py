from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.internal.api import auth_route
from app.internal.connection.prisma import connect_db, disconnect_db
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await connect_db()  
        print("Database connected")
    except Exception as e:
        print(f"Database connection failed: {e}")
    yield
    # Shutdown
    try:
        await disconnect_db()
        print("Database disconnected")
    except Exception as e:
        print(f"Database disconnect failed: {e}")

app = FastAPI(
    title="Payroll Management System",
    description="A comprehensive payroll management system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_route.router)
# app.include_router(auth_route.router) 

@app.get("/")
def read_root():    
    return {"message": "Awesome it works 🐻"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Payroll API is running"}