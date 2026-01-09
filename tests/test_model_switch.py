import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import get_config
from src.core.engine import ResumeSniperEngine

def test_config_loading():
    print("--- Testing Config Loading ---")
    config = get_config()
    openai_cfg = config.get_llm_provider_config("openai")
    
    print(f"OpenAI Enabled: {openai_cfg.enabled}")
    print(f"Base URL: {openai_cfg.base_url}")
    print(f"Default Model: {openai_cfg.default_model}")
    print(f"API Key (masked): {openai_cfg.api_key[:5]}..." if openai_cfg.api_key else "API Key: None")
    
    if openai_cfg.base_url != "http://127.0.0.1:8045/v1":
        print("❌ Config mismatch: Base URL not updated!")
        return False
    if openai_cfg.default_model != "claude-opus-4-5-thinking":
        print("❌ Config mismatch: Default model not updated!")
        return False
        
    print("✅ Config loaded successfully from .env")
    return True

def test_engine_connection():
    print("\n--- Testing Engine Connection ---")
    try:
        # Initialize engine with openai provider
        engine = ResumeSniperEngine(llm_provider="openai")
        print(f"Engine initialized with provider: {engine._llm_provider.provider_name}")
        
        # Simple chat test
        print("Sending test request...")
        response = engine._llm_provider.chat(
            messages=[{"role": "user", "content": "Hello, are you Claude?"}],
            model="claude-opus-4-5-thinking",
            max_tokens=50
        )
        
        print("\n✅ Response received:")
        print(f"Model: {response.model}")
        print(f"Content: {response.content}")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_config_loading():
        test_engine_connection()
