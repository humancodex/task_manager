#!/bin/bash

# PostgreSQL Setup Script for Task Management API
# Using Docker for reliable, consistent setup across all platforms
# 
# This script provides:
# - Automated Docker validation and setup
# - Intelligent container management
# - Database initialization and testing
# - Comprehensive error handling and diagnostics

set -e  # Exit on any error

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="postgres-db"
POSTGRES_VERSION="15"
POSTGRES_USER="taskuser"
POSTGRES_PASSWORD="taskpass"
POSTGRES_DB="taskdb"
POSTGRES_TEST_DB="taskdb_test"
POSTGRES_PORT="5432"

# Error handling
trap 'echo -e "\n${RED}❌ Setup failed! Check the error messages above.${NC}" >&2' ERR

# Function to print colored output
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_status "Setting up PostgreSQL for Task Management API using Docker..."
echo

# Function to check Docker installation
check_docker_installation() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo
        echo "📥 Installation instructions:"
        echo "  macOS:        brew install --cask docker"
        echo "  Ubuntu/Debian: sudo apt-get install docker.io docker-compose"
        echo "  Windows:      Download from https://docs.docker.com/get-docker/"
        echo "  Other:        Visit https://docs.docker.com/get-docker/"
        echo
        exit 1
    fi
    
    print_success "Docker is installed"
}

# Function to check Docker daemon status
check_docker_running() {
    print_status "Checking if Docker daemon is running..."
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running."
        echo
        echo "🚀 How to start Docker:"
        echo "  macOS:        Open Docker Desktop application"
        echo "  Linux:        sudo systemctl start docker"
        echo "  Windows:      Start Docker Desktop"
        echo
        print_status "Waiting 10 seconds for Docker to start..."
        sleep 10
        
        # Try again
        if ! docker info &> /dev/null; then
            print_error "Docker is still not responding. Please start Docker manually and try again."
            exit 1
        fi
    fi
    
    print_success "Docker daemon is running"
}

# Function to check for port conflicts
check_port_availability() {
    print_status "Checking if port $POSTGRES_PORT is available..."
    
    if command -v lsof &> /dev/null; then
        if lsof -i :$POSTGRES_PORT &> /dev/null; then
            print_warning "Port $POSTGRES_PORT is in use by another process"
            print_status "Checking if it's our PostgreSQL container..."
            
            if docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -q "$CONTAINER_NAME.*$POSTGRES_PORT"; then
                print_success "Port is used by our PostgreSQL container - this is expected"
            else
                print_warning "Port $POSTGRES_PORT is used by a different process"
                print_status "You may need to stop the other PostgreSQL service or change the port"
            fi
        else
            print_success "Port $POSTGRES_PORT is available"
        fi
    else
        print_status "Cannot check port availability (lsof not available), proceeding anyway..."
    fi
}

# Function to manage existing containers
manage_existing_container() {
    print_status "Checking for existing PostgreSQL container..."
    
    if docker ps -a --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
        print_warning "Found existing $CONTAINER_NAME container"
        
        # Check if it's running
        if docker ps --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
            print_status "Container is running. Stopping it..."
            docker stop $CONTAINER_NAME 2>/dev/null || true
        fi
        
        print_status "Removing existing container to ensure clean setup..."
        docker rm $CONTAINER_NAME 2>/dev/null || true
        print_success "Cleaned up existing container"
    else
        print_success "No existing container found"
    fi
}

# Function to start PostgreSQL container
start_postgresql_container() {
    print_status "Starting PostgreSQL $POSTGRES_VERSION container..."
    
    # Pull the latest image first
    print_status "Pulling PostgreSQL $POSTGRES_VERSION image (this may take a moment)..."
    if ! docker pull postgres:$POSTGRES_VERSION; then
        print_error "Failed to pull PostgreSQL image"
        exit 1
    fi
    
    # Start the container
    if docker run -d \
        --name $CONTAINER_NAME \
        -e POSTGRES_USER=$POSTGRES_USER \
        -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
        -e POSTGRES_DB=$POSTGRES_DB \
        -p $POSTGRES_PORT:5432 \
        --restart unless-stopped \
        postgres:$POSTGRES_VERSION; then
        print_success "PostgreSQL container started successfully"
    else
        print_error "Failed to start PostgreSQL container"
        docker logs $CONTAINER_NAME 2>/dev/null || true
        exit 1
    fi
}

# Function to wait for PostgreSQL to be ready
wait_for_postgresql() {
    print_status "Waiting for PostgreSQL to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec $CONTAINER_NAME pg_isready -U $POSTGRES_USER -d $POSTGRES_DB &> /dev/null; then
            print_success "PostgreSQL is ready! (attempt $attempt/$max_attempts)"
            return 0
        fi
        
        printf "${YELLOW}⏳ Waiting for PostgreSQL... (attempt $attempt/$max_attempts)${NC}\r"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "PostgreSQL failed to become ready after $max_attempts attempts"
    print_status "Container logs:"
    docker logs $CONTAINER_NAME
    exit 1
}

# Function to verify container is running
verify_container_running() {
    print_status "Verifying container is running..."
    
    if docker ps --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
        print_success "Container is running successfully"
        
        # Show container details
        print_status "Container details:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep $CONTAINER_NAME
    else
        print_error "Container failed to start or is not running"
        print_status "Container logs:"
        docker logs $CONTAINER_NAME 2>/dev/null || print_error "Could not retrieve logs"
        exit 1
    fi
}

# Function to create test database
create_test_database() {
    print_status "Creating test database..."
    
    if docker exec $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE DATABASE $POSTGRES_TEST_DB;" 2>/dev/null; then
        print_success "Test database '$POSTGRES_TEST_DB' created successfully"
    else
        # Check if it already exists
        if docker exec $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -c "\l" | grep -q $POSTGRES_TEST_DB; then
            print_success "Test database '$POSTGRES_TEST_DB' already exists"
        else
            print_error "Failed to create test database"
            exit 1
        fi
    fi
}

# Function to test database connections
test_database_connections() {
    print_status "Testing database connections..."
    
    # Test main database
    if docker exec $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT version();" &> /dev/null; then
        print_success "Main database connection successful"
    else
        print_error "Failed to connect to main database"
        exit 1
    fi
    
    # Test test database
    if docker exec $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_TEST_DB -c "SELECT 1;" &> /dev/null; then
        print_success "Test database connection successful"
    else
        print_error "Failed to connect to test database"
        exit 1
    fi
}

# Function to display setup summary
display_setup_summary() {
    echo
    print_success "PostgreSQL setup completed successfully!"
    echo
    echo "📊 Setup Summary:"
    echo "  Container: $CONTAINER_NAME"
    echo "  PostgreSQL Version: $POSTGRES_VERSION"
    echo "  Port: $POSTGRES_PORT"
    echo "  Main Database: $POSTGRES_DB"
    echo "  Test Database: $POSTGRES_TEST_DB"
    echo
    echo "🔗 Database URLs:"
    echo "  Main: postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:$POSTGRES_PORT/$POSTGRES_DB"
    echo "  Test: postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:$POSTGRES_PORT/$POSTGRES_TEST_DB"
    echo
    echo "🛠️  Container Management Commands:"
    echo "  View logs:    docker logs $CONTAINER_NAME"
    echo "  Stop:         docker stop $CONTAINER_NAME"
    echo "  Start:        docker start $CONTAINER_NAME"
    echo "  Restart:      docker restart $CONTAINER_NAME"
    echo "  Remove:       docker rm $CONTAINER_NAME"
    echo "  Connect:      docker exec -it $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB"
    echo
    echo "🚀 Next Steps:"
    echo "  1. Run environment check: python scripts/check_environment.py"
    echo "  2. Apply migrations: PYTHONPATH=. alembic upgrade head"
    echo "  3. Start the API: uvicorn app.main:app --reload"
    echo
}

# Main execution
main() {
    print_status "🐘 PostgreSQL Setup Script for Task Management API"
    echo "================================================================="
    echo
    
    check_docker_installation
    check_docker_running
    check_port_availability
    manage_existing_container
    start_postgresql_container
    wait_for_postgresql
    verify_container_running
    create_test_database
    test_database_connections
    display_setup_summary
    
    print_success "Setup completed! PostgreSQL is ready for use."
}

# Run main function
main