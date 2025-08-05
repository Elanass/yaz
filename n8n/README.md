# n8n Integration for Surgify Platform

This directory contains n8n workflow automation for the Surgify platform, enabling intelligent orchestration of case management, deliverable generation, and team communications.

## Overview

The n8n integration provides three core workflows:

1. **Case Summarization** - Automatically generates AI summaries when cases are created
2. **Deliverable Processing** - Generates and emails PDF reports when deliverables are ready
3. **Daily Digest** - Aggregates daily activity and sends team notifications

## Setup Instructions

### 1. Environment Configuration

Create a `.env` file in this directory with the following variables:

```bash
# Copy from .env.example and fill in your values
cp .env.example .env
```

### 2. n8n Installation

#### Option A: Docker (Recommended)

```bash
# Run n8n with Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -e WEBHOOK_URL=http://localhost:5678/ \
  -v ~/.n8n:/home/node/.n8n \
  -v $(pwd)/workflows:/workflows \
  n8nio/n8n
```

#### Option B: npm Installation

```bash
npm install n8n -g
n8n start --tunnel
```

### 3. Workflow Import

1. Open n8n interface at `http://localhost:5678`
2. Go to **Workflows** → **Import from File**
3. Import each workflow JSON file from the `workflows/` directory:
   - `case-summarization.json`
   - `deliverable-processing.json`
   - `daily-digest.json`

### 4. Configure Credentials

Set up the following credentials in n8n:

#### HTTP Credentials
- **Name**: `surgify-api`
- **Authentication**: Header Auth
- **Name**: `Authorization`
- **Value**: `Bearer YOUR_API_TOKEN`

#### SMTP Credentials
- **Name**: `surgify-smtp`
- **Host**: Your SMTP server
- **Port**: 587 (or your SMTP port)
- **Security**: STARTTLS
- **Username**: Your email username
- **Password**: Your email password

#### Slack Credentials (Optional)
- **Name**: `surgify-slack`
- **Access Token**: Your Slack bot token

### 5. Webhook Configuration

After importing workflows, update the webhook URLs in your Surgify backend to trigger n8n workflows:

```python
# Example webhook endpoints
CASE_CREATED_WEBHOOK = "http://localhost:5678/webhook/case-created"
DELIVERABLE_READY_WEBHOOK = "http://localhost:5678/webhook/deliverable-ready"
```

## Workflow Details

### Case Summarization Workflow

**Trigger**: Case Created webhook
**Process**:
1. Receives case data via webhook
2. Calls Surgify `/api/v1/ai/summarize` endpoint
3. Updates case with AI-generated summary
4. Logs activity

**Expected Payload**:
```json
{
  "case_id": "uuid",
  "title": "Case title",
  "description": "Case description",
  "patient_info": {...},
  "medical_data": {...}
}
```

### Deliverable Processing Workflow

**Trigger**: Deliverable Ready webhook
**Process**:
1. Receives deliverable completion notification
2. Calls `/api/v1/deliverables/{id}/pdf` to generate PDF
3. Sends email with PDF attachment to stakeholders
4. Updates deliverable status

**Expected Payload**:
```json
{
  "deliverable_id": "uuid",
  "case_id": "uuid",
  "type": "report|analysis|recommendation",
  "recipients": ["email1@example.com", "email2@example.com"]
}
```

### Daily Digest Workflow

**Trigger**: Daily schedule (configurable)
**Process**:
1. Queries Surgify API for daily statistics
2. Aggregates new cases, completed deliverables, and messages
3. Formats digest report
4. Sends to Slack channel or email distribution list

## Monitoring and Maintenance

### Workflow Health Checks

Each workflow includes error handling and monitoring:
- Failed executions are logged
- Retry logic for API calls
- Fallback notifications for critical failures

### Logs and Debugging

- Check n8n execution logs for workflow status
- Surgify application logs contain webhook processing details
- Use n8n's built-in debugger for troubleshooting

### Scaling Considerations

For production deployments:
- Use n8n with a database backend (PostgreSQL recommended)
- Configure webhook authentication and rate limiting
- Set up monitoring and alerting for workflow failures
- Consider using n8n cloud for managed hosting

## Customization

### Adding New Workflows

1. Create workflow in n8n interface
2. Export as JSON to `workflows/` directory
3. Document trigger conditions and payload format
4. Update this README with workflow details

### Extending Existing Workflows

- Modify workflows through n8n interface
- Test changes in development environment
- Export updated JSON files
- Update documentation as needed

## Security Notes

- Store sensitive credentials in n8n credential store, not in workflow files
- Use HTTPS for all webhook endpoints in production
- Implement webhook signature verification for security
- Regularly rotate API tokens and credentials

## Support

For issues with n8n integration:
1. Check n8n execution logs
2. Verify webhook endpoints are accessible
3. Confirm API credentials are valid
4. Review Surgify application logs for backend issues

For more information, see the [n8n documentation](https://docs.n8n.io/) and [Surgify API documentation](../docs/api/README.md).
