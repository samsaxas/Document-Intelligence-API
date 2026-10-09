output "alb_dns_name" {
  description = "Public Load Balancer DNS endpoint"
  value       = aws_lb.app_alb.dns_name
}

output "s3_bucket_name" {
  description = "S3 bucket for document storage"
  value       = aws_s3_bucket.document_storage.bucket
}

output "ecr_backend_url" {
  description = "ECR Backend Image Repository URL"
  value       = aws_ecr_repository.backend_repo.repository_url
}

output "ecr_frontend_url" {
  description = "ECR Frontend Image Repository URL"
  value       = aws_ecr_repository.frontend_repo.repository_url
}
