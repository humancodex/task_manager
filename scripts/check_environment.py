#!/usr/bin/env python3
"""
Environment Check Script for Task Management API

This script verifies that all required dependencies and services
are available before starting the application.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.database import check_database_health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def check_python_version():
    """Check if Python version is supported"""
    logger.info("🐍 Checking Python version...")
    if sys.version_info < (3, 11):
        logger.error(f"❌ Python 3.11+ required, found {sys.version}")
        return False
    logger.info(f"✅ Python {sys.version.split()[0]} - OK")
    return True


def check_required_packages():
    """Check if required packages are installed"""
    logger.info("📦 Checking required packages...")
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'asyncpg', 
        'pydantic', 'alembic', 'dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ Missing packages: {', '.join(missing_packages)}")
        logger.error("   Install with: pip install -r requirements.txt")
        return False
    
    logger.info("✅ All required packages installed")
    return True


def check_environment_variables():
    """Check environment configuration"""
    logger.info("🔧 Checking environment configuration...")
    
    # Check database URL
    if not settings.database_url:
        logger.error("❌ DATABASE_URL not configured")
        return False
    
    if not settings.database_url.startswith('postgresql+asyncpg://'):
        logger.warning("⚠️  DATABASE_URL should use 'postgresql+asyncpg://' for async support")
        logger.info(f"   Current: {settings.database_url}")
    
    logger.info("✅ Environment configuration - OK")
    return True


async def check_database_connection():
    """Check database connectivity"""
    logger.info("🗄️  Checking database connection...")
    
    try:
        is_healthy = await check_database_health()
        if is_healthy:
            logger.info("✅ Database connection - OK")
            return True
        else:
            logger.error("❌ Database connection failed")
            logger.error("   💡 Start PostgreSQL with: docker-compose up -d postgres")
            return False
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        logger.error("   💡 Check that PostgreSQL is running and accessible")
        return False


def check_docker_services():
    """Check if Docker services are available"""
    logger.info("🐳 Checking Docker services...")
    
    try:
        import subprocess
        result = subprocess.run(
            ['docker', 'ps', '--format', 'table {{.Names}}\\t{{.Status}}'],
            capture_output=True, text=True, timeout=5
        )
        
        if result.returncode == 0:
            output = result.stdout
            if 'postgres' in output.lower():
                logger.info("✅ PostgreSQL container found and running")
                return True
            else:
                logger.warning("⚠️  PostgreSQL container not found in running containers")
                logger.info("   💡 Start with: docker-compose up -d postgres")
                return False
        else:
            logger.warning("⚠️  Docker not available or not responding")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        logger.warning("⚠️  Docker not available")
        logger.info("   💡 Make sure Docker is installed and running")
        return False


async def main():
    """Run all environment checks"""
    logger.info("🚀 Starting environment checks for Task Management API")
    logger.info("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("Environment Config", check_environment_variables),
        ("Docker Services", check_docker_services),
        ("Database Connection", check_database_connection),
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            results[check_name] = result
        except Exception as e:
            logger.error(f"❌ {check_name} check failed with error: {e}")
            results[check_name] = False
        
        logger.info("-" * 60)
    
    # Summary
    passed = sum(results.values())
    total = len(results)
    
    logger.info("📊 ENVIRONMENT CHECK SUMMARY")
    logger.info("=" * 60)
    
    for check_name, passed_check in results.items():
        status = "✅ PASS" if passed_check else "❌ FAIL"
        logger.info(f"{status} {check_name}")
    
    logger.info("-" * 60)
    logger.info(f"Overall: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("🎉 All checks passed! You can start the application with:")
        logger.info("   uvicorn app.main:app --reload")
        return 0
    else:
        logger.error("❌ Some checks failed. Please fix the issues above before starting the application.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)