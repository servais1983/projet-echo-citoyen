from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any

from . import models, database
from .database import get_db

app = FastAPI()

@app.post("/alerts/")
def create_alert(alert: dict, db: Session = Depends(get_db)):
    db_alert = models.Alert(
        type=alert["type"],
        message=alert["message"],
        status=alert["status"]
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@app.get("/alerts/{alert_id}")
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@app.put("/alerts/{alert_id}")
def update_alert(alert_id: int, alert: dict, db: Session = Depends(get_db)):
    db_alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    for key, value in alert.items():
        setattr(db_alert, key, value)
    
    if alert.get("status") == "RESOLVED":
        db_alert.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_alert)
    return db_alert

@app.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    return {"message": "Alert deleted"}

@app.get("/alerts/")
def list_alerts(
    type: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Alert)
    
    if type:
        query = query.filter(models.Alert.type == type)
    if status:
        query = query.filter(models.Alert.status == status)
    
    return query.all()

@app.get("/alerts/stats")
def get_alert_stats(db: Session = Depends(get_db)):
    total_alerts = db.query(models.Alert).count()
    
    type_distribution = {}
    status_distribution = {}
    
    for alert in db.query(models.Alert).all():
        type_distribution[alert.type] = type_distribution.get(alert.type, 0) + 1
        status_distribution[alert.status] = status_distribution.get(alert.status, 0) + 1
    
    return {
        "total_alerts": total_alerts,
        "type_distribution": type_distribution,
        "status_distribution": status_distribution
    } 