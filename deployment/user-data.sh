#!/bin/bash

# User data script for AWS EC2 instance setup

# Update system
apt-get update -y
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install other dependencies
apt-get install -y git nginx certbot python3-certbot-nginx awscli

# Create application directory
mkdir -p /opt/scamcap
chown ubuntu:ubuntu /opt/scamcap

# Clone repository (replace with your actual repository)
# cd /opt/scamcap
# git clone https://github.com/your-username/scamcap.git .

# Create systemd service for Docker Compose
cat > /etc/systemd/system/scamcap.service << 'EOF'
[Unit]
Description=ScamCap Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/opt/scamcap
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
systemctl enable scamcap.service

# Set up log rotation
cat > /etc/logrotate.d/scamcap << 'EOF'
/opt/scamcap/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}
EOF

# Configure firewall
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# Create deployment script
cat > /opt/scamcap/deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "Deploying ScamCap application..."

# Pull latest changes
git pull origin main

# Build and start services
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be healthy
sleep 30

# Check if services are running
docker-compose ps

echo "Deployment completed!"
EOF

chmod +x /opt/scamcap/deploy.sh
chown ubuntu:ubuntu /opt/scamcap/deploy.sh

echo "EC2 setup completed!" > /var/log/user-data.log
