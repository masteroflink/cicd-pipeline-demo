variable "service_name" {
  description = "Name of the Render web service"
  type        = string
  default     = "cicd-pipeline-demo"
}

variable "region" {
  description = "Render region for the service"
  type        = string
  default     = "oregon"

  validation {
    condition     = contains(["oregon", "ohio", "virginia", "frankfurt", "singapore"], var.region)
    error_message = "Region must be one of: oregon, ohio, virginia, frankfurt, singapore."
  }
}

variable "environment" {
  description = "Environment name (production, staging)"
  type        = string
  default     = "production"
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "INFO"
}

variable "database_url" {
  description = "PostgreSQL database connection URL (Supabase)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "owner_id" {
  description = "Render owner ID (user or team)"
  type        = string
}
