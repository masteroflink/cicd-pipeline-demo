terraform {
  required_version = ">= 1.0"

  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.0"
    }
  }

  # Store state in Terraform Cloud (free tier)
  cloud {
    organization = "master-of-link"

    workspaces {
      name = "cicd-pipeline-demo"
    }
  }
}

provider "render" {
  # API key is read from RENDER_API_KEY environment variable
  # Owner ID is read from RENDER_OWNER_ID environment variable
  owner_id = var.owner_id
}
