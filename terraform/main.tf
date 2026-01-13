# Render Web Service for CI/CD Pipeline Demo
#
# This Terraform configuration manages the Render web service
# that hosts the FastAPI application.

resource "render_web_service" "api" {
  name        = var.service_name
  region      = var.region
  plan        = "free"
  owner_id    = var.owner_id
  auto_deploy = true

  runtime_source = {
    docker = {
      repo_url        = "https://github.com/masteroflink/cicd-pipeline-demo"
      branch          = "main"
      dockerfile_path = "docker/Dockerfile"
      context         = "."
    }
  }

  env_vars = {
    ENVIRONMENT = {
      value = var.environment
    }
    LOG_LEVEL = {
      value = var.log_level
    }
    DATABASE_URL = {
      value = var.database_url
    }
  }

  health_check_path = "/health"

  # Note: Some features like custom domains require paid plans
}

# Output the service URL
output "service_url" {
  description = "URL of the deployed service"
  value       = render_web_service.api.url
}

output "service_id" {
  description = "Render service ID"
  value       = render_web_service.api.id
}
