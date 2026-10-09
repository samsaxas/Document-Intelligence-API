#!/bin/bash
set -e

REGION=${AWS_REGION:-"us-east-1"}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "=========================================="
echo "Deploying Document Intelligence to AWS"
echo "Region: $REGION | Account: $ACCOUNT_ID"
echo "=========================================="

# Authenticate Docker to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build & Push Backend
echo "Building Backend Container..."
docker build -t $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/doc-intel-backend:latest -f backend/Dockerfile .
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/doc-intel-backend:latest

# Build & Push Frontend
echo "Building Frontend Container..."
docker build -t $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/doc-intel-frontend:latest -f frontend/Dockerfile .
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/doc-intel-frontend:latest

# Apply Terraform
echo "Applying Infrastructure..."
cd deploy/aws/terraform
terraform init
terraform apply -auto-approve

echo "Deployment Successful!"
