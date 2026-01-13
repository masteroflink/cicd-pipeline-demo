# Secrets Management

This document describes the secrets management approach for the CI/CD Pipeline Demo project.

## Overview

This project uses **GitHub Secrets** for secure storage and injection of sensitive credentials. All secrets are encrypted at rest and only exposed to workflows that explicitly reference them.

## Secrets Inventory

| Secret Name | Description | Used By | Rotation Frequency |
|-------------|-------------|---------|-------------------|
| `DATABASE_URL` | Supabase PostgreSQL connection string | CD, Terraform | On compromise |
| `RENDER_API_KEY` | Render API authentication | Terraform | Quarterly |
| `RENDER_DEPLOY_HOOK_URL` | Render deployment webhook | CD Pipeline | On regeneration |
| `RENDER_SERVICE_ID` | Render service identifier | Terraform | Never (static) |
| `RENDER_OWNER_ID` | Render account owner ID | Terraform | Never (static) |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook | CI, CD, Terraform | On compromise |
| `TF_API_TOKEN` | Terraform Cloud API token | Terraform | Quarterly |
| `TF_CLOUD_ORGANIZATION` | Terraform Cloud org name | Terraform | Never (static) |
| `GRAFANA_PROMETHEUS_URL` | Grafana Cloud metrics endpoint | App (future) | Never (static) |
| `GRAFANA_PROMETHEUS_USER` | Grafana Cloud user ID | App (future) | Never (static) |
| `GRAFANA_PROMETHEUS_API_KEY` | Grafana Cloud API key | App (future) | Quarterly |

## Security Principles

### 1. Least Privilege

Each secret is only accessible to workflows that require it:
- CI Pipeline: `SLACK_WEBHOOK_URL` (failure notifications only)
- CD Pipeline: `DATABASE_URL`, `RENDER_DEPLOY_HOOK_URL`, `SLACK_WEBHOOK_URL`
- Terraform: `RENDER_API_KEY`, `TF_API_TOKEN`, `DATABASE_URL`, `SLACK_WEBHOOK_URL`

### 2. No Secrets in Code

- Secrets are **never** committed to the repository
- `.env` files are gitignored
- `.env.example` provides templates without actual values
- Terraform variables use `sensitive = true` for secret values

### 3. Encryption at Rest

- GitHub encrypts all secrets using libsodium sealed boxes
- Secrets are only decrypted at runtime in the workflow runner
- Terraform Cloud encrypts state files containing sensitive outputs

## Adding a New Secret

1. **GitHub Repository Settings:**
   ```
   Settings → Secrets and variables → Actions → New repository secret
   ```

2. **Reference in Workflow:**
   ```yaml
   env:
     MY_SECRET: ${{ secrets.MY_SECRET }}
   ```

3. **For Terraform variables:**
   ```yaml
   env:
     TF_VAR_my_secret: ${{ secrets.MY_SECRET }}
   ```

## Rotation Procedures

### Rotating Database URL (Supabase)

1. Generate new password in Supabase Dashboard
2. Update connection string in GitHub Secrets
3. Update Render environment variable (or redeploy)
4. Verify application connectivity

### Rotating Render API Key

1. Create new API key in Render Dashboard
2. Update `RENDER_API_KEY` in GitHub Secrets
3. Revoke old API key in Render Dashboard
4. Trigger Terraform workflow to verify

### Rotating Slack Webhook

1. Create new webhook in Slack App settings
2. Update `SLACK_WEBHOOK_URL` in GitHub Secrets
3. Test by triggering a workflow
4. Remove old webhook from Slack App

### Rotating Terraform Cloud Token

1. Generate new token in Terraform Cloud User Settings
2. Update `TF_API_TOKEN` in GitHub Secrets
3. Revoke old token in Terraform Cloud
4. Trigger Terraform workflow to verify

## Emergency Response

### If a Secret is Compromised

1. **Immediately rotate** the compromised secret
2. **Review audit logs** for unauthorized access:
   - GitHub: Settings → Audit log
   - Render: Dashboard → Events
   - Supabase: Dashboard → Logs
3. **Check for unauthorized changes:**
   - Review recent deployments
   - Check Terraform state changes
   - Audit database access logs
4. **Document the incident** and update rotation schedule if needed

### Revoking All Access

In case of major compromise:

1. Regenerate all Render API keys
2. Reset Supabase database password
3. Regenerate Slack webhook
4. Regenerate Terraform Cloud token
5. Rotate GitHub repository secrets

## Best Practices

1. **Use environment-specific secrets** when possible
2. **Document all secrets** in this file
3. **Regular audits** - review secret usage quarterly
4. **Automated rotation** - implement where supported
5. **Monitor for leaks** - use GitHub secret scanning

## GitHub Secret Scanning

This repository has GitHub secret scanning enabled. If a secret is accidentally committed:

1. GitHub will alert repository administrators
2. The secret should be immediately rotated
3. The commit history should be rewritten if possible
4. All systems using the secret should be audited

## Future Improvements

- [ ] Implement HashiCorp Vault for dynamic secrets
- [ ] Add OIDC authentication for cloud providers (when supported)
- [ ] Automated secret rotation with AWS Secrets Manager or similar
- [ ] Secret usage monitoring and alerting
