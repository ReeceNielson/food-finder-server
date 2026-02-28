# Podman vs Docker: Complete Guide

This guide explains Podman and how to use it for this Django project.

## What is Podman?

**Podman** (Pod Manager) is a container engine developed by Red Hat that:
- Runs OCI (Open Container Initiative) containers
- Works without a daemon (unlike Docker)
- Supports rootless containers (better security)
- Is fully compatible with Docker images
- Provides pod support for grouping containers

## Why Use Podman?

### Security
- **Rootless**: Containers run as non-root users by default
- **No daemon escalation**: No need for privileged daemon
- **Better isolation**: Each container runs in its own user namespace

### Efficiency
- **No daemon overhead**: Resources aren't consumed by a background service
- **Better performance**: More efficient resource usage
- **Container compatibility**: Runs any Docker image

### Philosophy
- **Open source**: Fully open source with community support
- **Kubernetes-ready**: Better compatibility with Kubernetes
- **Industry support**: Backed by Red Hat/IBM

## Installation

### Ubuntu/Debian

```bash
# Install Podman
sudo apt update
sudo apt install podman

# Install Podman Compose (optional, but recommended)
sudo apt install podman-compose

# Or via pip
pip install podman-compose

# Verify installation
podman --version
podman-compose --version
```

### macOS (via Homebrew)

```bash
# Install Podman
brew install podman

# Install Podman Machine (VM runtime for macOS)
podman machine init

# Start the machine
podman machine start

# Install Podman Compose
brew install podman-compose

# Verify
podman --version
podman-compose --version
```

### Fedora/RHEL

```bash
# Podman is pre-installed, but update it
sudo dnf update podman podman-compose
```

## Docker vs Podman Commands

The commands are nearly identical. Replace `docker` with `podman`:

```bash
# Building
docker build -t name .          → podman build -t name .
docker images                   → podman images
docker rmi image-id             → podman rmi image-id

# Running
docker run -it image            → podman run -it image
docker ps                       → podman ps
docker ps -a                    → podman ps -a
docker stop container-id        → podman stop container-id
docker rm container-id          → podman rm container-id

# Logs & Inspection
docker logs container-id        → podman logs container-id
docker inspect container-id     → podman inspect container-id
docker exec -it id bash         → podman exec -it id bash

# Compose
docker-compose up               → podman-compose up
docker-compose down             → podman-compose down
docker-compose logs             → podman-compose logs
docker-compose exec service cmd → podman-compose exec service cmd
```

## Key Differences

### 1. Rootless by Default

**Docker:**
```bash
# Requires sudo or docker group membership
docker run busybox
# Error: permission denied
```

**Podman:**
```bash
# Works without sudo
podman run busybox
# ✅ Works fine
```

### 2. Socket Location

**Docker:**
```bash
/var/run/docker.sock
```

**Podman:**
```bash
# User podman (rootless)
/run/user/1000/podman/podman.sock

# Root podman
/run/podman/podman.sock
```

### 3. Networking

**Docker Compose:**
```bash
# Uses docker0 bridge
docker network ls
```

**Podman Compose:**
```bash
# Uses slirp4netns for rootless containers
podman network ls
```

### 4. Image Registries

**Podman** uses local registries configuration:

```bash
# Edit registry config
~/.config/containers/registries.conf

# Default registries
podman search image-name
```

## Using Podman with This Project

### Build the Image

```bash
# Build
podman build -t django-app:latest .

# Verify
podman images | grep django-app
```

### Run Without Compose

```bash
# Create a network for containers
podman network create django-network

# Run the container
podman run -d \
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

### Run with Podman Compose

```bash
# Start
podman-compose up -d

# View logs
podman-compose logs -f

# Stop
podman-compose down
```

## Rootless vs Rootful

### Rootless Containers (Recommended)

```bash
# Default for Podman - no sudo needed
podman run -it ubuntu bash

# Better security
# Lower privileges
# Each user has their own containers
```

### Rootful Containers

```bash
# If you need to run as root
sudo podman run -it ubuntu bash

# Needed for:
# - Binding to ports < 1024
# - All users sharing containers
# - Legacy setups
```

To allow rootless binding to privileged ports:

```bash
# As root
sudo sysctl net.ipv4.ip_unprivileged_port_start=0

# Make persistent
echo "net.ipv4.ip_unprivileged_port_start=0" | sudo tee /etc/sysctl.d/99-podman.conf
sudo sysctl -p /etc/sysctl.d/99-podman.conf
```

## Podman Pods

Unlike Docker, Podman supports grouping containers in "pods":

```bash
# Create a pod
podman pod create --name myapp -p 8000:8000

# Run containers in the pod
podman run -d \
  --pod myapp \
  --name web \
  django-app:latest

# List pods
podman pod ls

# Remove pod
podman pod rm myapp
```

## Volume Handling

### Bind Mounts

```bash
# Works the same as Docker
podman run -v /host/path:/container/path image
podman run -v $(pwd):/app image
```

### Named Volumes

```bash
# Create volume
podman volume create myvolume

# Use in container
podman run -v myvolume:/data image

# List volumes
podman volume ls
```

### Rootless Volume Permissions

Important: In rootless mode, volume permissions might differ:

```bash
# If permissions are issues, use :z or :Z flags
podman run -v $(pwd):/app:z image     # Shared SELinux context
podman run -v $(pwd):/app:Z image     # Private SELinux context
```

## Networking

### Port Mapping

```bash
# Expose single port
podman run -p 8000:8000 image

# Expose range
podman run -p 8000-8010:8000-8010 image

# Expose all
podman run -P image
```

### Container Networks

```bash
# Create network
podman network create mynetwork

# Run on network
podman run --network mynetwork --name web image

# Containers can reach each other by name
podman run --network mynetwork busybox ping web
```

### DNS

```bash
# Add DNS server
podman run --dns=8.8.8.8 image

# Add hosts entry
podman run --add-host myhost:127.0.0.1 image
```

## Troubleshooting

### Permissions Issues

```bash
# If you get permission errors:
sudo loginctl enable-linger $USER
# Then log out and log back in

# Verify
podman ps  # Should work without sudo
```

### Rootless Networking

```bash
# If ports aren't exposed:
# Check slirp4netns
ps aux | grep slirp4netns

# Restart the service
systemctl --user restart podman
```

### Image Pull Issues

```bash
# Check registries config
cat ~/.config/containers/registries.conf

# Force pull with specific registry
podman pull docker.io/library/ubuntu
```

### Storage Space

```bash
# Check storage location
podman info | grep graphRoot

# Clean up unused images/containers
podman image prune
podman container prune
podman system prune -a

# Check disk usage
podman system df
```

## Using Podman with Fly.io

Fly.io supports Podman! When you run `flyctl deploy`:

```bash
# Flyctl automatically detects and uses Podman if available
flyctl deploy

# Or explicitly use Podman
DOCKER_HOST=unix:///run/user/1000/podman/podman.sock flyctl deploy
```

## systemd Integration

Run containers as systemd services:

```bash
# Generate systemd unit file
podman generate systemd --name django-app > ~/.config/systemd/user/django-app.service

# Start service
systemctl --user start django-app

# Enable on boot
systemctl --user enable django-app

# Check status
systemctl --user status django-app
```

## Resource Limits

```bash
# Limit memory
podman run -m 512m image

# Limit CPU
podman run --cpus 1 image

# Memory and CPU together
podman run -m 512m --cpus 1 image
```

## Advanced: Building for Different Architectures

```bash
# Build for ARM64 (Raspberry Pi, Apple Silicon, etc.)
podman build --platform linux/arm64 -t django-app:arm64 .

# Build for AMD64
podman build --platform linux/amd64 -t django-app:amd64 .

# Build for multiple architectures (requires buildah)
podman run --rm --privileged multiarch/qemu-user-static --reset -p yes
podman buildx build --platform linux/amd64,linux/arm64 -t django-app:latest .
```

## Performance Tips

1. **Use .dockerignore**: Reduces build context size
2. **Multi-stage builds**: Smaller final images
3. **Rootless mode**: More secure and efficient
4. **Allocate resources wisely**: Don't over-allocate
5. **Use health checks**: Allows container orchestration

## Migration from Docker

If you currently use Docker:

```bash
# Docker images are compatible
docker build -t myapp .  →  podman build -t myapp .

# Docker containers work as-is
docker run mydocker      →  podman run mydocker

# Docker Compose files work
docker-compose up        →  podman-compose up

# Migration steps
# 1. Install podman and podman-compose
# 2. Test: podman pull docker.io/library/busybox
# 3. Build images with podman
# 4. Update scripts/docs to use podman commands
# 5. Gradual migration: keep Docker during transition
```

## Useful Podman Commands

```bash
# System info
podman version
podman info
podman system df

# Cleanup
podman image prune -a    # Remove unused images
podman container prune   # Remove stopped containers
podman volume prune      # Remove unused volumes
podman system prune -a   # Complete cleanup

# Debugging
podman logs container
podman inspect container
podman top container
podman stats

# Container management
podman ps -a
podman start container
podman stop container
podman rm container
podman kill container

# Image management
podman images
podman pull image
podman tag source:tag target:tag
podman rmi image
podman save image > image.tar
podman load < image.tar
```

## Additional Resources

- [Podman Official Documentation](https://docs.podman.io/)
- [Podman Compose GitHub](https://github.com/containers/podman-compose)
- [Podman vs Docker Comparison](https://docs.podman.io/en/latest/)
- [Getting Started with Podman](https://podman.io/getting-started/)
- [Rootless Containers Guide](https://docs.podman.io/en/latest/markdown/podman.1.html#rootlessmode)

## FAQ

**Q: Can I use Podman and Docker together?**
A: Yes, but keep them separate. Each has its own image storage and containers.

**Q: Is Podman production-ready?**
A: Yes, used in production by many organizations. Red Hat officially supports it.

**Q: Can I use Podman with Kubernetes?**
A: Yes, Podman works with Kubernetes. Use `podman-compose` for local testing.

**Q: What about Apple Silicon Macs?**
A: Use Podman with `podman machine`. Performance is equivalent to Docker Desktop.

**Q: Is Rootless mode slower?**
A: Minimal performance impact, gain in security is worth it.

**Q: How do I share images between Docker and Podman?**
A: Export and import using `podman save` and `podman load`.
