#!/bin/bash

# AWS Deployment Script for ScamCap

set -e

echo "Starting ScamCap deployment to AWS..."

# Configuration
AWS_REGION="us-east-1"
EC2_INSTANCE_TYPE="t3.medium"
KEY_PAIR_NAME="scamcap-key"
SECURITY_GROUP_NAME="scamcap-sg"
S3_BUCKET_NAME="scamcap-media-storage"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker first."
    exit 1
fi

# Create S3 bucket for media storage
echo "Creating S3 bucket for media storage..."
aws s3 mb s3://$S3_BUCKET_NAME --region $AWS_REGION || echo "Bucket may already exist"

# Configure S3 bucket policy
cat > s3-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$S3_BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket $S3_BUCKET_NAME --policy file://s3-policy.json
rm s3-policy.json

# Create security group
echo "Creating security group..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name $SECURITY_GROUP_NAME \
    --description "Security group for ScamCap application" \
    --query 'GroupId' --output text 2>/dev/null || \
    aws ec2 describe-security-groups \
    --group-names $SECURITY_GROUP_NAME \
    --query 'SecurityGroups[0].GroupId' --output text)

# Configure security group rules
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 || echo "SSH rule may already exist"

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 || echo "HTTP rule may already exist"

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0 || echo "HTTPS rule may already exist"

# Create key pair if it doesn't exist
if ! aws ec2 describe-key-pairs --key-names $KEY_PAIR_NAME >/dev/null 2>&1; then
    echo "Creating key pair..."
    aws ec2 create-key-pair \
        --key-name $KEY_PAIR_NAME \
        --query 'KeyMaterial' \
        --output text > ${KEY_PAIR_NAME}.pem
    chmod 400 ${KEY_PAIR_NAME}.pem
    echo "Key pair saved as ${KEY_PAIR_NAME}.pem"
fi

# Create EC2 instance
echo "Creating EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ami-0c7217cdde317cfec \
    --count 1 \
    --instance-type $EC2_INSTANCE_TYPE \
    --key-name $KEY_PAIR_NAME \
    --security-group-ids $SECURITY_GROUP_ID \
    --user-data file://user-data.sh \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ScamCap-Server}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "Instance ID: $INSTANCE_ID"

# Wait for instance to be running
echo "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "Instance is running at: $PUBLIC_IP"

# Create environment file
cat > .env.production << EOF
# Production Environment Variables
MONGODB_URL=mongodb://localhost:27017/scamcap
JWT_SECRET_KEY=$(openssl rand -base64 32)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
FIREBASE_SERVICE_ACCOUNT=path/to/firebase-service-account.json
MONGO_ROOT_USERNAME=scamcap_admin
MONGO_ROOT_PASSWORD=$(openssl rand -base64 16)
AWS_S3_BUCKET=$S3_BUCKET_NAME
AWS_REGION=$AWS_REGION
ENVIRONMENT=production
EOF

echo "Deployment completed!"
echo "======================"
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "SSH Command: ssh -i ${KEY_PAIR_NAME}.pem ubuntu@$PUBLIC_IP"
echo "S3 Bucket: $S3_BUCKET_NAME"
echo ""
echo "Next steps:"
echo "1. Wait 5-10 minutes for the instance to fully initialize"
echo "2. Update .env.production with your actual API keys"
echo "3. SSH to the instance and deploy your application"
echo "4. Configure your domain and SSL certificates"
