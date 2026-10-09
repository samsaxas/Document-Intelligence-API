terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# --- VPC & Networking ---
resource "aws_vpc" "doc_intel_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "doc-intel-vpc"
  }
}

resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.doc_intel_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.doc_intel_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.doc_intel_vpc.id
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.doc_intel_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}

resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "b" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public_rt.id
}

# --- S3 Document Storage Bucket ---
resource "aws_s3_bucket" "document_storage" {
  bucket_prefix = "doc-intel-storage-"
  force_destroy = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "s3_encrypt" {
  bucket = aws_s3_bucket.document_storage.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# --- ECR Repositories ---
resource "aws_ecr_repository" "backend_repo" {
  name                 = "doc-intel-backend"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "frontend_repo" {
  name                 = "doc-intel-frontend"
  image_tag_mutability = "MUTABLE"
}

# --- ECS Cluster & Fargate Tasks ---
resource "aws_ecs_cluster" "doc_intel_cluster" {
  name = "doc-intel-cluster"
}

resource "aws_iam_role" "ecs_execution_role" {
  name = "doc_intel_ecs_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# --- Application Load Balancer ---
resource "aws_security_group" "alb_sg" {
  name        = "doc-intel-alb-sg"
  description = "Allow HTTP inbound"
  vpc_id      = aws_vpc.doc_intel_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "app_alb" {
  name               = "doc-intel-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}
