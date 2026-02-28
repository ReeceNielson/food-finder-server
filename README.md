# Django Project with Podman & Fly.io Deployment

This is a production-ready Django project configured for containerization with Podman and deployment to Fly.io.

## Prerequisites

- **Podman** (v4.0+): Replace Docker with Podman for secure container management
- **Python 3.11+**: For local development
- **Flyctl**: CLI tool for Fly.io deployment
- **Git**: Version control

## Installation & Setup

### 1. Clone or Navigate to the Project

```bash
cd /path/to/django_app
```

### 2. Create Environment File

```bash
cp .env.example .env
# Edit .env with your settings
```

## Local Development with Podman

### 3. Build the Container Image

```bash
podman build -t django-app:latest .
```

**What's happening**: Podman builds a multi-stage Docker image that:
- Installs Python dependencies efficiently
- Minimizes image size by separating build and runtime stages
- Sets up a non-root user for security

### 4. Run with Podman Compose (Recommended)

```bash
# Install podman-compose if not already installed
sudo apt install podman-compose  # Ubuntu/Debian
# or brew install podman-compose  # macOS

# Start the development server
podman-compose up -d

# View logs
podman-compose logs -f web
```

**What's happening**:
- Container runs on `http://localhost:8000`
- Auto-reloads on code changes (development mode)
- SQLite database stored in the container
- Migrations run automatically on startup

### 5. Run Migrations Manually (if needed)

```bash
podman-compose exec web python manage.py migrate
```

### 6. Create Admin User (if needed)

```bash
podman-compose exec web python manage.py createsuperuser
```

Access admin at `http://localhost:8000/admin/`

### 7. Stop Containers

```bash
podman-compose down
```

## Manual Podman Run (Alternative)

If you prefer not to use Podman Compose:

```bash
# Create a network for containers to communicate
podman network create django-network

# Run the container
podman run -it \
  --name django-app \
  --network django-network \
  -p 8000:8080 \
  -e DEBUG=True \
  -e DJANGO_SECRET_KEY=dev-key \
  -e ALLOWED_HOSTS=localhost,127.0.0.1 \
  -v $(pwd):/app \
  django-app:latest

# Access at http://localhost:8000
```

## Podman vs Docker

Podman is a drop-in replacement for Docker with these advantages:

- **Rootless**: Runs containers as non-root by default (more secure)
- **No daemon**: Better resource management
- **Pod support**: Orchestrate multiple containers easily
- **Compatible**: Uses the same Dockerfile syntax
- **OCI compliant**: Works with Docker images

**Key differences in usage**:
- Replace `docker` with `podman` in commands
- Replace `docker-compose` with `podman-compose`
- Network and volume management syntax is identical

## Deployment to Fly.io

### 1. Install Flyctl

```bash
curl -L https://fly.io/install.sh | sh
```

### 2. Login to Fly.io

```bash
flyctl auth login
```

### 3. Create a New Fly App

```bash
# First, update fly.toml with your app name
# Change: app = "my-django-app" to something unique

flyctl apps create
```

### 4. Set Environment Variables

```bash
# Set production secrets
flyctl secrets set DJANGO_SECRET_KEY=your-production-secret-key
flyctl secrets set ALLOWED_HOSTS=your-domain.fly.dev
flyctl secrets set DEBUG=False

# If using PostgreSQL
flyctl postgres create  # Follow prompts to create a database
flyctl secrets set DATABASE_URL=<connection-string-from-above>
```

### 5. Deploy the Application

```bash
flyctl deploy
```

Flyctl will:
1. Use Podman (or Docker) to build the image
2. Push the image to Fly's registry
3. Run migrations (release command in fly.toml)
4. Deploy to your specified region
5. Set up health checks

### 6. Monitor Deployment

```bash
# View logs
flyctl logs

# Check status
flyctl status

# SSH into the running app
flyctl ssh console
```

### 7. Run Commands on Fly

```bash
# Create a superuser
flyctl ssh console
python manage.py createsuperuser

# Or run directly
flyctl ssh console -C "python manage.py createsuperuser"
```

## Production Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` in settings.py or use environment variable
- [ ] Set `DEBUG=False`
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Configure a production database (PostgreSQL recommended)
- [ ] Set up static files serving (WhiteNoise is included)
- [ ] Configure email backend for production
- [ ] Install SSL certificate (Fly.io provides free Let's Encrypt)
- [ ] Set up proper logging and monitoring
- [ ] Test database migrations
- [ ] Configure backup strategy for data

## Database Configuration

### SQLite (Development)
Already configured, stored in `db.sqlite3`

### PostgreSQL (Production - Recommended)

1. **On Fly.io**:
```bash
flyctl postgres create
```

2. **Update fly.toml section**:
```toml
[env]
DB_ENGINE = "django.db.backends.postgresql"
```

3. **Update requirements.txt** (already included: `psycopg2-binary`)

4. **Configure in settings.py** (already done with environment variables)

## Troubleshooting

### Containers won't start
```bash
# Check logs
podman-compose logs

# Rebuild the image
podman build --no-cache -t django-app:latest .
```

### Port already in use
```bash
# Change port in docker-compose.yml or use:
podman-compose -p custom_name up
```

### Static files not serving
```bash
podman-compose exec web python manage.py collectstatic --noinput
```

### Database locked (SQLite)
```bash
# Remove the database and let Django recreate it
rm db.sqlite3
podman-compose restart
```

## Useful Commands

```bash
# Podman basics
podman images                          # List images
podman ps                              # List running containers
podman ps -a                           # List all containers
podman logs <container-id>             # View container logs
podman exec -it <container-id> bash    # Access container shell

# Podman Compose
podman-compose up -d                   # Start in background
podman-compose logs -f                 # Follow logs
podman-compose exec web bash           # Run command in web container
podman-compose down -v                 # Stop and remove volumes

# Django management
python manage.py makemigrations        # Create migration files
python manage.py migrate               # Apply migrations
python manage.py shell                 # Interactive Django shell
python manage.py test                  # Run tests
```

## Project Structure

```
django_app/
├── config/              # Django project configuration
│   ├── settings.py      # Main settings
│   ├── urls.py          # URL routing
│   ├── wsgi.py          # WSGI application
│   └── __init__.py
├── Dockerfile           # Container image definition
├── docker-compose.yml   # Local development setup
├── fly.toml             # Fly.io deployment config
├── .dockerignore        # Files to exclude from build
├── .env.example         # Environment variables template
├── manage.py            # Django CLI
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Adding Apps

To add a new Django app:

```bash
podman-compose exec web python manage.py startapp myapp
```

Then add `'myapp'` to `INSTALLED_APPS` in `config/settings.py`.

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Podman Documentation](https://podman.io/docs)
- [Podman Compose](https://github.com/containers/podman-compose)
- [Fly.io Deployment Guide](https://fly.io/docs/getting-started/)
- [Gunicorn Configuration](https://docs.gunicorn.org/)

## License

Your License Here
