output "api_url" {
  description = "The URL of the deployed API service"
  value       = render_web_service.api.url
}

output "api_service_id" {
  description = "The Render service ID for the API"
  value       = render_web_service.api.id
}

output "environment" {
  description = "The deployment environment"
  value       = var.environment
}

output "region" {
  description = "The deployment region"
  value       = var.region
}
