# Fly.io Deployment Guide

This guide walks through every step of deploying your Django application to Fly.io.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Deployment Steps](#deployment-steps)
4. [Post-Deployment](#post-deployment)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

### Install Flyctl CLI

```bash
# Linux/macOS
curl -L https://fly.io/install.sh | sh

# Verify installation
flyctl version
```

### Create a Fly.io Account

```bash
flyctl auth signup   # Create new account
# or
flyctl auth login    # Login to existing account
```

### Prepare Your App

1. Ensure all code is committed to git
2. Update `fly.toml` with your app name
3. Set up all required environment variables

## Initial Setup

### 1. Create a New Fly App

```bash
# In your django_app directory
flyctl apps create

# You'll be prompted to:
# - Choose an app name (must be globally unique)
# - Choose a region (closest to your users is best)
```

**Fly.io Regions:**
- `dfw` - Dallas
- `sfo` - San Francisco
- `lhr` - London
- `syd` - Sydney
- `nrt` - Tokyo
- And many more...

### 2. Update fly.toml

Edit `fly.toml` with your app details:

```toml
app = "your-unique-app-name"
primary_region = "dfw"  # Change to your preferred region
```

### 3. Set Secret Environment Variables

```bash
# Django secret key (generate a new one!)
flyctl secrets set DJANGO_SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Allowed hosts
flyctl secrets set ALLOWED_HOSTS="your-app-name.fly.dev"

# Set DEBUG to False
flyctl secrets set DEBUG=False
```

### 4. (Optional) Set Up PostgreSQL Database

```bash
# Create a managed PostgreSQL database
flyctl postgres create

# Follow the prompts:
# - Database name: django_db (or your choice)
# - Username: postgres
# - Password: (auto-generated, save it!)
# - Region: (should match your app region)

# The connection string will be automatically available as DATABASE_URL
```

Alternative: Use external database (AWS RDS, etc.) by setting `DATABASE_URL` manually:

```bash
flyctl secrets set DATABASE_URL="postgresql://user:password@host:port/dbname"
```

## Deployment Steps

### 1. Deploy Your Application

```bash
flyctl deploy
```

Flyctl will:
1. Build your Docker image using Podman
2. Push it to Fly's registry
3. Launch the application
4. Run the release command (migrations)
5. Set up health checks

**First deployment typically takes 3-5 minutes.**

### 2. Monitor Deployment

```bash
# Watch the live logs
flyctl logs -n 100

# Check deployment status
flyctl status

# View detailed app info
flyctl info
```

### 3. Test Your App

```bash
# Get the app URL
flyctl info | grep URL

# Visit your app
# https://your-app-name.fly.dev
```

## Post-Deployment

### Create Superuser

```bash
# Option 1: Interactive shell
flyctl ssh console
python manage.py createsuperuser
exit

# Option 2: Non-interactive (set password via env var)
DJANGO_SUPERUSER_PASSWORD=temppassword python manage.py createsuperuser \
  --noinput \
  --username=admin \
  --email=admin@example.com
```

### Collect Static Files

If not running automatically, collect static files:

```bash
flyctl ssh console -C "python manage.py collectstatic --noinput"
```

### View Logs

```bash
# Real-time logs
flyctl logs

# Last 100 lines
flyctl logs -n 100

# Specific instance
flyctl logs -i <instance-id>
```

### SSH Into Your App

```bash
# Interactive shell
flyctl ssh console

# Run a single command
flyctl ssh console -C "python manage.py shell"
```

### Database Management

```bash
# Connect to PostgreSQL directly
flyctl postgres connect -a your-database-app

# Or from your app's console
flyctl ssh console
python manage.py dbshell
```

## Making Updates

### Code Changes

```bash
# Commit your changes
git add .
git commit -m "Your changes"

# Redeploy
flyctl deploy

# Or deploy from git directly (if enabled)
flyctl deploy --build-only
```

### Environment Variables

```bash
# Set a secret
flyctl secrets set NEW_KEY=value

# List all secrets
flyctl secrets list

# Remove a secret
flyctl secrets unset OLD_KEY

# Reading secrets requires SSH
flyctl ssh console -C "echo \$DJANGO_SECRET_KEY"
```

## Scaling & Performance

### Scale Replicas (Horizontal Scaling)

```bash
# Deploy with multiple instances
flyctl scale count <number>

# Example: 2 instances for high availability
flyctl scale count 2
```

### Scaling Configuration in fly.toml

```toml
[[vm]]
cpu_kind = "shared"      # or "performance"
cpus = 1                 # 1, 2, or 4
memory_mb = 256          # 256, 512, 1024, 2048
processes = ["app"]
```

### Database Scaling (PostgreSQL)

```bash
# List database info
flyctl postgres list

# Attach to your app
flyctl postgres attach <database-app-name>

# Scale database (if managed)
# Use Fly dashboard or contact support
```

## Troubleshooting

### App Won't Start

**Check logs:**
```bash
flyctl logs -n 50
```

**Common issues:**
- Missing environment variables: Check with `flyctl secrets list`
- Database connection: Verify `DATABASE_URL` is correct
- Migration failures: Run migrations manually:
  ```bash
  flyctl ssh console -C "python manage.py migrate"
  ```

### Port Issues

The app must listen on `$PORT` environment variable (default 8080). Our Dockerfile already does this.

If issues persist, update `fly.toml`:
```toml
[[services]]
internal_port = 8080
```

### Out of Memory

Increase memory in `fly.toml`:
```toml
[[vm]]
memory_mb = 512  # Increased from 256
```

Then redeploy:
```bash
flyctl deploy
```

### Static Files Not Loading

1. Ensure WhiteNoise is in requirements.txt ✅
2. Run migrations: `flyctl ssh console -C "python manage.py migrate"`
3. Collect static files: `flyctl ssh console -C "python manage.py collectstatic --noinput"`

### Database Issues

```bash
# Check database status
flyctl postgres info

# Restart database
flyctl postgres restart

# If using external db, verify connection:
flyctl ssh console
python manage.py check --database default
```

### HTTPS/SSL Errors

Fly.io provides free automatic HTTPS with Let's Encrypt. If you experience issues:

```bash
# Force certificate renewal
flyctl certs list
flyctl certs show <domain>

# Add custom domain
flyctl certs add yourdomain.com
```

### Health Check Failures

Our health check endpoint is at `/health/` which returns `{"status": "healthy"}`.

If health checks are failing:
```bash
# Test locally
curl http://localhost:8080/health/

# Test on Fly
flyctl ssh console -C "curl http://localhost:8080/health/"
```

Update `fly.toml` if needed:
```toml
[checks.http_endpoint]
grace_period = "10s"      # Increase if migrations take longer
interval = "30s"
timeout = "10s"
```

## Advanced Configuration

### Custom Domain

```bash
# Add your domain
flyctl certs add yourdomain.com

# Update DNS settings
# Follow the instructions Fly provides
```

### Environment-Specific Configurations

Create separate `fly.staging.toml` and deploy with:
```bash
flyctl deploy -c fly.staging.toml
```

### Scheduled Tasks (Cron)

Add to `fly.toml`:
```toml
[[crons]]
cmd = "python manage.py clearsessions"
schedule = "0 0 * * *"  # Daily at midnight UTC
```

### Backup Strategy

For PostgreSQL:
```bash
# Manual backup
flyctl postgres backup create

# Automated backups (configure in Fly dashboard)
```

For file uploads (ensure you use cloud storage like S3):
```bash
# Don't rely on local filesystem - it's ephemeral
# Use django-storages + boto3 for S3
```

## Monitoring & Logging

### Set Up Log Drains

```bash
# Datadog
flyctl log-drains create datadog \
  --token=<datadog-api-key> \
  --region=<datadog-region>

# Papertrail
flyctl log-drains create papertrail \
  --url=syslog://logs.papertrailapp.com:port
```

### Monitor Resource Usage

```bash
flyctl metrics
flyctl metrics --type instance
```

## Cost Optimization

- Use `shared` CPU type instead of `performance` (default, cost-effective)
- Start with 1 instance and `256 MB` memory
- Use fly.io's built-in databases instead of external services
- Shut down unused apps: `flyctl apps destroy`

## Useful Commands Reference

```bash
# App management
flyctl create               # Create new app
flyctl deploy              # Deploy app
flyctl destroy             # Delete app
flyctl status              # App status

# Secrets & Config
flyctl secrets set KEY=val # Set secret
flyctl secrets list        # List secrets
flyctl config show         # Show config

# Monitoring
flyctl logs                # View logs
flyctl status              # Check status
flyctl info                # App details
flyctl metrics             # Resource usage

# Database
flyctl postgres create     # Create database
flyctl postgres list       # List databases
flyctl postgres connect    # Connect to database

# SSH & Debugging
flyctl ssh console         # SSH into app
flyctl ssh console -C cmd  # Run command

# Scaling
flyctl scale count N       # Set replica count
flyctl machines list       # List VM instances
```

## Additional Resources

- [Fly.io Documentation](https://fly.io/docs/)
- [Django Deployment Guide](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Fly PostgreSQL Docs](https://fly.io/docs/postgres/)
- [Fly Monitoring & Logging](https://fly.io/docs/monitoring/)

## Support

- Fly.io Community: https://community.fly.io
- Django Forum: https://forum.djangoproject.com
- GitHub Issues: Create issues in your app's repo
