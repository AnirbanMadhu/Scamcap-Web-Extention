// MongoDB initialization script
db = db.getSiblingDB('scamcap');

// Create collections
db.createCollection('users');
db.createCollection('threat_logs');
db.createCollection('mfa_sessions');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "created_at": 1 });

db.threat_logs.createIndex({ "user_id": 1 });
db.threat_logs.createIndex({ "timestamp": 1 });
db.threat_logs.createIndex({ "threat_type": 1 });
db.threat_logs.createIndex({ "risk_level": 1 });

db.mfa_sessions.createIndex({ "user_id": 1 });
db.mfa_sessions.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 });
db.mfa_sessions.createIndex({ "challenge_id": 1 }, { unique: true });

print('Database initialized successfully!');
