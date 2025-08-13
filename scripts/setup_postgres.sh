#!/bin/bash

# PostgreSQL Setup Script for Task Management API

echo "Setting up PostgreSQL for Task Management API..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install PostgreSQL first."
    echo "On macOS: brew install postgresql"
    echo "On Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

# Check if PostgreSQL service is running
if ! pg_isready -q; then
    echo "Starting PostgreSQL service..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start postgresql
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo service postgresql start
    fi
fi

# Create database and user
echo "Creating database and user..."

# Create user and database
psql -c "CREATE USER taskuser WITH PASSWORD 'taskpass';" postgresql://postgres@localhost/postgres 2>/dev/null || echo "User taskuser already exists"
psql -c "CREATE DATABASE taskdb OWNER taskuser;" postgresql://postgres@localhost/postgres 2>/dev/null || echo "Database taskdb already exists"
psql -c "CREATE DATABASE taskdb_test OWNER taskuser;" postgresql://postgres@localhost/postgres 2>/dev/null || echo "Database taskdb_test already exists"
psql -c "GRANT ALL PRIVILEGES ON DATABASE taskdb TO taskuser;" postgresql://postgres@localhost/postgres
psql -c "GRANT ALL PRIVILEGES ON DATABASE taskdb_test TO taskuser;" postgresql://postgres@localhost/postgres

echo "PostgreSQL setup completed!"
echo "Database URL: postgresql://taskuser:taskpass@localhost:5432/taskdb"
echo "Test Database URL: postgresql://taskuser:taskpass@localhost:5432/taskdb_test"