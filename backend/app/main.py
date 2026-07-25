from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import tickets, engineers, admin, batch
from app.scheduler.sla_monitor import check_sla_and_escalate
from seed_data import seed
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
import os

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SwiftDesk Automation & Routing API",
    version="1.0.0",
    description="Enterprise Support Ticket Automation, AI Classification, and L1/L2/L3 Routing System"
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
app.include_router(tickets.router)
app.include_router(engineers.router)
app.include_router(admin.router)
app.include_router(batch.router)

# Initialize APScheduler for SLA monitoring
scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_scheduler():
    seed()
    scheduler.add_job(check_sla_and_escalate, "interval", seconds=60, id="sla_check_job", replace_existing=True)
    scheduler.start()

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()

@app.get("/")
def root():
    return {
        "system": "SwiftDesk API",
        "status": "online",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
