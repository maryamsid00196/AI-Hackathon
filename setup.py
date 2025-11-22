"""
Quick setup script for Skill Assessment API
"""
import os
import sys
import subprocess


def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("# OpenAI Configuration\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write("OPENAI_BASE_URL=https://api.openai.com/v1\n")
            f.write("OPENAI_MODEL=gpt-4-turbo-preview\n\n")
            f.write("# For custom OpenAI endpoints (proxy/alternative providers):\n")
            f.write("# OPENAI_API_KEY=028fa2e1-fb69-4cca-89aa-1e11ffc4dcc1\n")
            f.write("# OPENAI_BASE_URL=https://openai.dplit.com/v1\n\n")
            f.write("# Application Configuration\n")
            f.write("DEBUG=False\n")
            f.write("HOST=0.0.0.0\n")
            f.write("PORT=8000\n")
        print("✅ .env file created! Please update with your OpenAI API key and base URL.")
        return False
    else:
        print("✅ .env file already exists")
        return True


def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}.{version.micro}")
        return False


def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def main():
    """Run setup"""
    print("🚀 Skill Assessment API Setup\n")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Create .env file
    env_ready = create_env_file()
    
    # Install dependencies
    print("\n" + "="*60)
    install_deps = input("\nInstall dependencies from requirements.txt? (y/n): ")
    if install_deps.lower() == 'y':
        if not install_dependencies():
            return
    
    # Final instructions
    print("\n" + "="*60)
    print("✨ Setup Complete!\n")
    
    if not env_ready:
        print("⚠️  IMPORTANT: Update your .env file with your OpenAI API key before running the API\n")
    
    print("📖 Next Steps:")
    print("   1. Ensure your OpenAI API key is set in .env file")
    print("   2. Run the API:")
    print("      python main.py")
    print("      or")
    print("      uvicorn main:app --reload")
    print("\n   3. Access the API docs at http://localhost:8000/docs")
    print("   4. Try the example client:")
    print("      python example_client.py")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()

