import asyncio
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from ..models.schemas import ThreatType, ThreatLogCreate, RiskLevel
from ..config.database import get_database
import uuid

logger = logging.getLogger(__name__)

class ThreatLogger:
    def __init__(self):
        pass

    async def log_threat(
        self,
        user_id: str,
        threat_type: ThreatType,
        risk_score: float,
        url: Optional[str] = None,
        content_hash: Optional[str] = None,
        detection_details: Optional[Dict[str, Any]] = None,
        user_action: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log a threat detection event"""
        try:
            db = get_database()
            if db is None:
                logger.warning("Database not available, cannot log threat")
                return
            
            # Determine risk level based on score
            risk_level = self._calculate_risk_level(risk_score)
            
            # Create threat log document
            threat_log = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "threat_type": threat_type.value,
                "risk_score": risk_score,
                "risk_level": risk_level.value,
                "url": url,
                "content_hash": content_hash,
                "detection_details": detection_details or {},
                "user_action": user_action,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow(),
                "logged_at": datetime.utcnow()
            }
            
            # Insert threat log
            await db.threat_logs.insert_one(threat_log)
            
            # Update user threat statistics
            await self._update_user_stats(user_id, threat_type, risk_score)
            
            logger.info(f"Threat logged: {threat_type.value} - Risk: {risk_score} - User: {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to log threat: {e}")

    async def log_feedback(
        self,
        user_id: str,
        feedback_type: str,
        feedback: str,
        url: Optional[str] = None,
        content_hash: Optional[str] = None
    ):
        """Log user feedback for model improvement"""
        try:
            db = get_database()
            if db is None:
                logger.warning("Database not available, cannot log feedback")
                return
            
            feedback_doc = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "feedback_type": feedback_type,  # "false_positive", "false_negative", "suggestion"
                "feedback": feedback,
                "url": url,
                "content_hash": content_hash,
                "timestamp": datetime.utcnow(),
                "processed": False
            }
            
            await db.user_feedback.insert_one(feedback_doc)
            
            logger.info(f"Feedback logged: {feedback_type} - User: {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to log feedback: {e}")

    async def get_user_threat_history(
        self,
        user_id: str,
        limit: int = 50,
        threat_type: Optional[ThreatType] = None
    ) -> list:
        """Get threat history for a user"""
        try:
            db = get_database()
            if db is None:
                logger.warning("Database not available, cannot get threat history")
                return []
            db = get_database()
            
            # Build query
            query = {"user_id": user_id}
            if threat_type:
                query["threat_type"] = threat_type.value
            
            # Get threat logs
            cursor = db.threat_logs.find(query).sort("timestamp", -1).limit(limit)
            threat_logs = await cursor.to_list(length=limit)
            
            return threat_logs
            
        except Exception as e:
            logger.error(f"Failed to get threat history: {e}")
            return []

    async def get_threat_statistics(
        self,
        user_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get threat statistics"""
        try:
            db = get_database()
            
            # Build match query
            match_query = {
                "timestamp": {
                    "$gte": datetime.utcnow() - timedelta(days=days)
                }
            }
            
            if user_id:
                match_query["user_id"] = user_id
            
            # Aggregation pipeline
            pipeline = [
                {"$match": match_query},
                {
                    "$group": {
                        "_id": None,
                        "total_threats": {"$sum": 1},
                        "phishing_count": {
                            "$sum": {"$cond": [{"$eq": ["$threat_type", "phishing"]}, 1, 0]}
                        },
                        "deepfake_count": {
                            "$sum": {"$cond": [{"$eq": ["$threat_type", "deepfake"]}, 1, 0]}
                        },
                        "high_risk_count": {
                            "$sum": {"$cond": [{"$gte": ["$risk_score", 0.8]}, 1, 0]}
                        },
                        "avg_risk_score": {"$avg": "$risk_score"},
                        "max_risk_score": {"$max": "$risk_score"}
                    }
                }
            ]
            
            result = await db.threat_logs.aggregate(pipeline).to_list(length=1)
            
            if result:
                stats = result[0]
                del stats["_id"]
                return stats
            else:
                return {
                    "total_threats": 0,
                    "phishing_count": 0,
                    "deepfake_count": 0,
                    "high_risk_count": 0,
                    "avg_risk_score": 0.0,
                    "max_risk_score": 0.0
                }
            
        except Exception as e:
            logger.error(f"Failed to get threat statistics: {e}")
            return {}

    async def get_top_threat_domains(self, limit: int = 10) -> list:
        """Get top domains by threat count"""
        try:
            db = get_database()
            
            pipeline = [
                {"$match": {"url": {"$ne": None}}},
                {
                    "$group": {
                        "_id": {"$regex": "^https?://([^/]+)", "input": "$url"},
                        "threat_count": {"$sum": 1},
                        "avg_risk_score": {"$avg": "$risk_score"},
                        "latest_detection": {"$max": "$timestamp"}
                    }
                },
                {"$sort": {"threat_count": -1}},
                {"$limit": limit}
            ]
            
            domains = await db.threat_logs.aggregate(pipeline).to_list(length=limit)
            return domains
            
        except Exception as e:
            logger.error(f"Failed to get top threat domains: {e}")
            return []

    def _calculate_risk_level(self, risk_score: float) -> RiskLevel:
        """Calculate risk level from risk score"""
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    async def _update_user_stats(self, user_id: str, threat_type: ThreatType, risk_score: float):
        """Update user threat statistics"""
        try:
            from bson import ObjectId
            db = get_database()
            
            # Update user document with latest threat info
            update_data = {
                "last_threat_detected": datetime.utcnow(),
                f"total_{threat_type.value}_detected": 1
            }
            
            if risk_score >= 0.8:
                update_data["high_risk_threats"] = 1
            
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$inc": update_data,
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to update user stats: {e}")

    async def export_threat_logs(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export threat logs for analysis"""
        try:
            db = get_database()
            
            # Build query
            query = {}
            if user_id:
                query["user_id"] = user_id
            if start_date or end_date:
                query["timestamp"] = {}
                if start_date:
                    query["timestamp"]["$gte"] = start_date
                if end_date:
                    query["timestamp"]["$lte"] = end_date
            
            # Get threat logs
            cursor = db.threat_logs.find(query).sort("timestamp", -1)
            threat_logs = await cursor.to_list(length=None)
            
            # Convert ObjectId to string for JSON serialization
            for log in threat_logs:
                log["_id"] = str(log["_id"])
            
            return {
                "total_records": len(threat_logs),
                "export_format": format,
                "exported_at": datetime.utcnow().isoformat(),
                "data": threat_logs
            }
            
        except Exception as e:
            logger.error(f"Failed to export threat logs: {e}")
            return {"error": str(e)}
