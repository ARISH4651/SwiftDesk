import os
import sys

# Ensure backend root is in python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import tickets, engineers, admin, batch, auth
from app.scheduler.sla_monitor import check_sla_and_escalate
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SwiftDesk Automation & Routing API",
    version="1.1.0",
    description="Enterprise Support Ticket Automation, AI Classification, L1/L2/L3 Routing System with JWT Authentication & RBAC"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(engineers.router)
app.include_router(admin.router)
app.include_router(batch.router)

# Initialize APScheduler for SLA monitoring
scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(check_sla_and_escalate, "interval", seconds=60, id="sla_check_job", replace_existing=True)
    scheduler.start()

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()

@app.get("/")
def root():
    return {
        "system": "SwiftDesk API",
        "auth": "JWT + RBAC enabled",
        "status": "online",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8005, reload=True)
