import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import get_config, ConfigManager

def debug_config():
    print("\n--- Debugging Config ---")
    
    # 1. Check Env Vars
    env_base_url = os.getenv("ANTHROPIC_BASE_URL")
    print(f"ENV ANTHROPIC_BASE_URL: {env_base_url}")
    
    # 2. Check YAML content directly
    yaml_path = Path("config/config.yaml").absolute()
    print(f"Reading YAML from: {yaml_path}")
    if yaml_path.exists():
        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "minimaxi" in content:
                print("!!! FOUND 'minimaxi' in config.yaml !!!")
            else:
                print("No 'minimaxi' in config.yaml")
                # Print Anthropic section lines
                for line in content.splitlines():
                    if "anthropic" in line or "base_url" in line:
                        print(f"YAML Line: {line.strip()}")

    # 3. Check Loaded Config
    config = get_config()
    anthropic_cfg = config.get_llm_provider_config("anthropic")
    print(f"Config Object Base URL: {anthropic_cfg.base_url}")
    
    # 4. Force reload
    print("\nForce reloading config...")
    ConfigManager.DEFAULT_CONFIG # Access to ensure class is loaded
    # Create new manager to bypass singleton for testing
    manager = ConfigManager(str(yaml_path))
    new_config = manager.config
    print(f"New Config Base URL: {new_config.llm_providers['anthropic'].base_url}")

if __name__ == "__main__":
    debug_config()
