"""
Simple startup script to test the backend
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

async def test_imports():
    """Test if all imports work correctly"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import fastapi
        print("✓ FastAPI imported successfully")
        
        import motor
        print("✓ Motor (MongoDB driver) imported successfully")
        
        import torch
        print("✓ PyTorch imported successfully")
        
        import transformers
        print("✓ Transformers imported successfully")
        
        # Test project imports
        from backend.app.config.settings import Settings
        print("✓ Settings imported successfully")
        
        from backend.app.models.schemas import ThreatType
        print("✓ Schemas imported successfully")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

async def test_ml_models():
    """Test ML model imports"""
    try:
        print("\nTesting ML model components...")
        
        # Test BERT tokenizer
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        print("✓ BERT tokenizer loaded successfully")
        
        # Test PyTorch tensor operations
        import torch
        tensor = torch.randn(2, 3)
        print(f"✓ PyTorch tensor created: shape {tensor.shape}")
        
        print("✅ ML components working!")
        return True
        
    except Exception as e:
        print(f"❌ ML model error: {e}")
        return False

async def main():
    """Main test function"""
    print("ScamCap Backend Test Suite")
    print("=" * 40)
    
    # Test imports
    import_success = await test_imports()
    
    # Test ML models if imports successful
    if import_success:
        ml_success = await test_ml_models()
    else:
        ml_success = False
    
    print("\n" + "=" * 40)
    if import_success and ml_success:
        print("🎉 All tests passed! Backend is ready.")
        print("\nTo start the server, run:")
        print(f"D:\\venvs\\scamcap\\Scripts\\python.exe -m uvicorn backend.app.main:app --reload")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    return import_success and ml_success

if __name__ == "__main__":
    asyncio.run(main())
