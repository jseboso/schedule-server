"""
Environment configuration loader for Schedule Server
Sebas Osorio
"""

import os
import sys
from typing import Dict, Any, Optional

def load_env_file(env_file_path: str = '.env') -> Dict[str, str]:
    """
    Load environment variables from a .env file
    
    Args:
        env_file_path: Path to the .env file
        
    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    
    try:
        if not os.path.exists(env_file_path):
            print(f"Warning: Environment file '{env_file_path}' not found.")
            return env_vars
            
        with open(env_file_path, 'r') as f:
            for line in f:
                # Skip empty lines and comments
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Parse key-value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error loading environment file: {e}")
    
    return env_vars

def get_env(key: str, default: Optional[Any] = None) -> Any:
    """
    Get an environment variable, with a fallback default value
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        The environment variable value or default
    """
    return os.environ.get(key, default)

def setup_environment(env_file_path: str = '.env') -> None:
    """
    Load environment variables and set them in os.environ
    
    Args:
        env_file_path: Path to the .env file
    """
    env_vars = load_env_file(env_file_path)
    
    # Add variables to environment
    for key, value in env_vars.items():
        os.environ[key] = value
    
    # Set up common configuration variables
    config = {
        'PORT': int(get_env('PORT', 8045)),
        'HOST': get_env('HOST', 'localhost'),
        'DEBUG': get_env('DEBUG', 'false').lower() in ('true', 'yes', '1'),
        'STATIC_DIR': get_env('STATIC_DIR', './static'),
        'FILES_DIR': get_env('FILES_DIR', './files'),
        'LOG_FILE': get_env('LOG_FILE', './response.log'),
    }
    
    return config

# Example usage
if __name__ == "__main__":
    config = setup_environment()
    print("Environment configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
