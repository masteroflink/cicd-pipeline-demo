# Render Web Service for CI/CD Pipeline Demo
#
# This Terraform configuration manages the Render web service
# that hosts the FastAPI application.

resource "render_web_service" "api" {
  name   = var.service_name
  region = var.region
  plan   = "free"

  runtime_source = {
    docker = {
      repo_url        = "https://github.com/masteroflink/cicd-pipeline-demo"
      branch          = "main"
      dockerfile_path = "docker/Dockerfile"
      context         = "."
      auto_deploy     = true
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
