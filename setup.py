import os
import platform
import subprocess
import sys

def install_dependencies():
    """Install dependencies from requirements.txt."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def clean_previous_builds():
    """Remove previous build directories."""
    print("Cleaning previous builds...")
    for directory in ["build", "dist"]:
        if os.path.exists(directory):
            subprocess.call(["rmdir", "/s", "/q", directory], shell=True)
            print(f"Removed {directory} directory.")

def build_application():
    """Build the application using pyinstaller."""
    print("Building the application...")
    # Ensure the src directory is included in PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath("src") + os.pathsep + env.get("PYTHONPATH", "")
    
    build_command = (
        r"C:\Users\sknay\PycharmProjects\pipeline_app\venv\Scripts\pyinstaller.exe "
        r"--name PipelineManager "
        r"--add-data src\\ui\\stylesheets;ui\\stylesheets "
        r"--add-data src\\resources;resources "
        r"src\\main.py"
    )
    try:
        subprocess.check_call(build_command, shell=True, env=env)
        print("Build complete.")
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        sys.exit(1)

def setup_environment():
    """Prepare environment for Windows or MacOS."""
    print("Setting up the environment...")
    current_os = platform.system()
    if current_os == "Windows":
        print("Detected Windows.")
        # Add Windows-specific setup here if needed
    elif current_os == "Darwin":
        print("Detected MacOS.")
        # Add MacOS-specific setup here if needed
    else:
        print("Unsupported OS.")
        sys.exit(1)
    print("Environment setup complete.")

def main():
    """Main setup script entry point."""
    print("Starting setup...")
    install_dependencies()
    clean_previous_builds()
    setup_environment()
    build_application()
    print("Setup completed successfully.")

if __name__ == "__main__":
    main()
