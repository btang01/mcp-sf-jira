#!/bin/bash

# Docker Build Optimization Script
# This script helps manage Docker builds with better caching strategies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  dev         Build development images (default)"
    echo "  clean       Clean up Docker images and cache"
    echo "  rebuild     Force rebuild without cache"
    echo "  prune       Remove unused Docker resources"
    echo ""
    echo "Options:"
    echo "  --no-cache  Build without using cache"
    echo "  --parallel  Build images in parallel"
    echo "  --verbose   Show verbose output"
    echo ""
    echo "Examples:"
    echo "  $0 dev                    # Build development images"
    echo "  $0 clean                  # Clean up Docker resources"
    echo "  $0 rebuild --no-cache     # Force rebuild without cache"
}

# Function to build development images
build_dev() {
    print_status "Building development images..."
    
    if [[ "$PARALLEL" == "true" ]]; then
        print_status "Building images in parallel..."
        (cd docker && docker-compose build --parallel $CACHE_FLAG)
    else
        print_status "Building images sequentially for better layer sharing..."
        # Build base images first for better layer sharing
        docker build $CACHE_FLAG -t mcp-base -f docker/Dockerfile.mcp-server --target base .
        docker build $CACHE_FLAG -t mcp-ui-base -f docker/Dockerfile.ui --target base .
        
        # Then build final images
        (cd docker && docker-compose build $CACHE_FLAG)
    fi
    
    print_success "Development images built successfully!"
}


# Function to clean up Docker resources
clean_docker() {
    print_status "Cleaning up Docker resources..."
    
    # Stop and remove containers from docker directory
    (cd docker && docker-compose down --remove-orphans 2>/dev/null) || true
    
    # Remove project images
    docker images | grep -E "(mcp-|mcpdemo)" | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
    
    print_success "Docker cleanup completed!"
}

# Function to rebuild everything
rebuild_all() {
    print_status "Rebuilding all images from scratch..."
    clean_docker
    docker system prune -f
    build_dev
    print_success "Rebuild completed!"
}

# Function to prune Docker system
prune_docker() {
    print_status "Pruning Docker system..."
    docker system prune -af --volumes
    print_success "Docker system pruned!"
}

# Function to show build cache info
show_cache_info() {
    print_status "Docker build cache information:"
    docker system df
    echo ""
    print_status "Build cache details:"
    docker buildx du 2>/dev/null || echo "BuildKit cache information not available"
}

# Parse command line arguments
COMMAND=""
CACHE_FLAG=""
PARALLEL="false"
VERBOSE="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        dev|clean|rebuild|prune)
            COMMAND="$1"
            shift
            ;;
        --no-cache)
            CACHE_FLAG="--no-cache"
            shift
            ;;
        --parallel)
            PARALLEL="true"
            shift
            ;;
        --verbose)
            VERBOSE="true"
            set -x
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Show cache info before building
if [[ "$COMMAND" == "dev" ]]; then
    show_cache_info
    echo ""
fi

# Execute command
case $COMMAND in
    dev)
        build_dev
        ;;
    clean)
        clean_docker
        ;;
    rebuild)
        rebuild_all
        ;;
    prune)
        prune_docker
        ;;
    "")
        print_error "No command specified."
        show_usage
        exit 1
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac

# Show final cache info
if [[ "$COMMAND" == "dev" || "$COMMAND" == "rebuild" ]]; then
    echo ""
    show_cache_info
fi

print_success "Operation completed successfully!"
