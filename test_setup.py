"""
Test script to verify setup before running the main system
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (need 3.10+)")
        return False


def check_env_file():
    """Check if .env file exists"""
    print("✓ Checking .env file...")
    env_path = Path(".env")
    if env_path.exists():
        print("  ✓ .env file exists")

        # Check if API key is set
        with open(env_path) as f:
            content = f.read()
            if "your-api-key-here" in content:
                print("  ⚠ Warning: API key not set (still has placeholder)")
                return False
            elif "GLM_API_KEY=" in content and len(content.split("GLM_API_KEY=")[1].split()[0]) > 10:
                print("  ✓ API key is set")
                return True
            else:
                print("  ✗ GLM_API_KEY not found or invalid")
                return False
    else:
        print("  ✗ .env file not found")
        print("  → Run: cp .env.example .env")
        return False


def check_docker():
    """Check if Docker is running"""
    print("✓ Checking Docker...")
    import subprocess
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("  ✓ Docker is running")
            return True
        else:
            print("  ✗ Docker command failed")
            return False
    except FileNotFoundError:
        print("  ✗ Docker not found")
        print("  → Install Docker: https://docs.docker.com/get-docker/")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def check_docker_compose():
    """Check if docker-compose services are running"""
    print("✓ Checking Docker Compose services...")
    import subprocess
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "--services", "--filter", "status=running"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            services = result.stdout.strip().split('\n')
            services = [s for s in services if s]  # Remove empty strings

            required = ["kafka", "zookeeper"]
            running = [s for s in required if s in services]

            if len(running) == len(required):
                print(f"  ✓ Required services running: {', '.join(running)}")
                return True
            else:
                missing = [s for s in required if s not in running]
                print(f"  ✗ Services not running: {', '.join(missing)}")
                print("  → Run: docker-compose up -d")
                return False
        else:
            print("  ✗ docker-compose command failed")
            return False
    except FileNotFoundError:
        print("  ✗ docker-compose not found")
        return False
    except Exception as e:
        print(f"  ⚠ Could not check services: {e}")
        return True  # Don't fail if we can't check


def check_dependencies():
    """Check if Python dependencies are installed"""
    print("✓ Checking Python dependencies...")

    required = [
        "aiohttp",
        "confluent_kafka",
        "pydantic",
        "pydantic_settings",
        "dotenv"
    ]

    missing = []
    for package in required:
        try:
            if package == "confluent_kafka":
                __import__(package.replace("_", "."))
            elif package == "pydantic_settings":
                __import__(package)
            elif package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package)
        except ImportError:
            missing.append(package)

    if not missing:
        print(f"  ✓ All dependencies installed")
        return True
    else:
        print(f"  ✗ Missing dependencies: {', '.join(missing)}")
        print("  → Run: pip install -r requirements.txt")
        return False


def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("🐝 Hive Five - Setup Verification")
    print("="*60 + "\n")

    checks = [
        check_python_version(),
        check_dependencies(),
        check_env_file(),
        check_docker(),
        check_docker_compose(),
    ]

    print("\n" + "="*60)

    if all(checks):
        print("✅ All checks passed! You're ready to run the system.")
        print("\nNext steps:")
        print("  1. Run: python main.py")
        print("  2. Watch the agents interact")
        print("  3. Open Kafka UI: http://localhost:8080")
        print("\n" + "="*60 + "\n")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nQuick fix checklist:")
        print("  □ Copy .env.example to .env")
        print("  □ Add your GLM_API_KEY to .env")
        print("  □ Run: pip install -r requirements.txt")
        print("  □ Run: docker-compose up -d")
        print("  □ Wait 30 seconds for services to start")
        print("\n" + "="*60 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
