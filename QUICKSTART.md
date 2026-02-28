# Quick Start Guide

Get your Django app running with Podman in 5 minutes!

## Step 1: Install Podman

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install podman podman-compose
```

### macOS
```bash
brew install podman podman-compose
podman machine init
podman machine start
```

### Verify Installation
```bash
podman --version
podman-compose --version
```

## Step 2: Build the Docker Image

```bash
cd /home/reece/src/projects/django_app
podman build -t django-app:latest .
```

This creates a containerized version of your Django app.

## Step 3: Start the Application

### Option A: Using Podman Compose (Recommended)

```bash
# Copy environment file
cp .env.example .env

# Start containers
podman-compose up -d

# Check status
podman-compose logs -f web
```

### Option B: Using Makefile

```bash
cp .env.example .env
make up
make logs
```

### Option C: Manual Podman Command

```bash
podman run -it \
  --name django-app \
  -p 8000:8080 \
  -e DEBUG=True \
  -e DJANGO_SECRET_KEY=dev-key \
  -e ALLOWED_HOSTS=localhost,127.0.0.1 \
  -v $(pwd):/app \
  django-app:latest
```

## Step 4: Access Your App

Open your browser:
- **App**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/

Default credentials: `admin / admin` (set via docker-compose)

## Step 5: Create Admin User (if needed)

```bash
podman-compose exec web python manage.py createsuperuser
```

## Common Commands

```bash
# View containers
podman-compose ps

# View logs (live)
podman-compose logs -f

# Run migrations
podman-compose exec web python manage.py migrate

# Create Django app
podman-compose exec web python manage.py startapp myapp

# Run Django shell
podman-compose exec web python manage.py shell

# Run tests
podman-compose exec web python manage.py test

# Stop containers
podman-compose down

# Remove everything
podman-compose down -v
podman rmi django-app:latest
```

Or use the Makefile:
```bash
make help        # Show all available commands
make logs        # View logs
make migrate     # Run migrations
make createsuperuser
make test        # Run tests
make down        # Stop containers
make clean       # Remove everything
```

## Making Changes

1. **Edit code**: Make changes to your Python files
2. **Restart container** (if not using watch mode):
   ```bash
   podman-compose restart web
   ```
3. **Check logs**: `podman-compose logs -f web`

The Django development server auto-reloads on code changes!

## Next Steps

### Deploy to Fly.io

Once you're happy with your app locally:

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Deploy
flyctl deploy
```

See [FLYIO_DEPLOYMENT.md](FLYIO_DEPLOYMENT.md) for detailed deployment instructions.

### Learn More

- [PODMAN_GUIDE.md](PODMAN_GUIDE.md) - Detailed guide on Podman vs Docker
- [FLYIO_DEPLOYMENT.md](FLYIO_DEPLOYMENT.md) - Complete Fly.io deployment guide
- [Django Documentation](https://docs.djangoproject.com/)
- [Podman Documentation](https://docs.podman.io/)

## Troubleshooting

### "podman: command not found"
Install Podman first (see Step 1)

### Port 8000 already in use
```bash
# Change port in docker-compose.yml or:
podman-compose -p custom_app up -d
```

### Container won't start
```bash
podman-compose logs web  # Check error messages
podman-compose up web     # Run without -d to see output
```

### Permission denied (rootless)
```bash
sudo loginctl enable-linger $USER
# Log out and back in
```

### Database locked (SQLite)
```bash
podman-compose down -v  # Remove volume
podman-compose up -d    # Start fresh
```

## What's in the Box

- 🐍 **Django 4.2** - Web framework
- 🐘 **PostgreSQL** - Database (optional, SQLite by default)
- 🚀 **Gunicorn** - Production WSGI server
- 📦 **WhiteNoise** - Static file serving
- 🐳 **Podman** - Container engine (Docker alternative)
- ☁️ **Fly.io** - Deploy configuration
- ✨ **Multi-stage builds** - Optimized container images

## Project Structure

```
django_app/
├── config/              # Django configuration
├── core/                # Example Django app
├── Dockerfile           # Container definition
├── docker-compose.yml   # Local development
├── fly.toml             # Fly.io deployment
├── manage.py            # Django CLI
├── requirements.txt     # Python dependencies
├── README.md            # Full documentation
├── PODMAN_GUIDE.md      # Podman detailed guide
├── FLYIO_DEPLOYMENT.md  # Deployment guide
├── Makefile             # Useful commands
└── setup.sh             # Automated setup
```

## Tips

✅ **Use environment variables** for configuration  
✅ **Keep .env file private** (in .gitignore)  
✅ **Use Podman** for rootless, more secure containers  
✅ **Test locally** before deploying to Fly.io  
✅ **Use PostgreSQL** in production (not SQLite)  
✅ **Enable DEBUG=False** before deploying  

---

**Ready to deploy?** → See [FLYIO_DEPLOYMENT.md](FLYIO_DEPLOYMENT.md)

**Need help with Podman?** → See [PODMAN_GUIDE.md](PODMAN_GUIDE.md)

**Questions about Django?** → Visit https://docs.djangoproject.com/
