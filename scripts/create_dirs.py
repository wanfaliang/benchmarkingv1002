"""Create necessary directory structure for the application"""
import os
from pathlib import Path

def create_directories():
    """Create data directory structure"""
    base_dirs = [
        "data/shared",
        "data/analyses",
    ]
    
    for dir_path in base_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        # Create .gitkeep to preserve empty directories in git
        gitkeep = Path(dir_path) / ".gitkeep"
        gitkeep.touch(exist_ok=True)
    
    print("✅ Directory structure created successfully")

if __name__ == "__main__":
    create_directories()