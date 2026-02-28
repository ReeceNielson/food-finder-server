#!/bin/bash

# Colima Configuration
# This script uses Colima (lightweight Docker runtime) for local Fly.io deployments.
# 
# Disk Size: 10 GB
# - App RootFS size on Fly.io: ~640 MB (Node + app code + node_modules)
# - Build process needs: base image (~200-400 MB) + build cache (~500MB-1GB) + system files (~1-2GB)
# - 10 GB provides safe headroom for builds while minimizing host disk usage
#
# To recreate Colima with this configuration:
#   colima delete
#   colima start --cpu 2 --memory 4 --disk 10
#
# Previous allocation was 20 GB - reduced to save ~10 GB of host disk space.

colima start
# Ensure Docker CLI and child processes (like Fly) use Colima's Docker socket
export DOCKER_HOST="unix://$HOME/.colima/default/docker.sock"
# Also switch the Docker context for good measure
docker context use colima >/dev/null 2>&1 || true

fly deploy --local-only --ha=false
colima stop