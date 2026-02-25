"""
Setup validation script for Financial Document Analyzer.
Run this to verify your installation is correct.
"""

import sys
import os

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    errors = []
    
    try:
        import fastapi
        print("✓ FastAPI installed")
    except ImportError as e:
        errors.append(f"✗ FastAPI missing: {e}")
    
    try:
        import crewai
        print("✓ CrewAI installed")
    except ImportError as e:
        errors.append(f"✗ CrewAI missing: {e}")
    
    try:
        import pypdf
        print("✓ pypdf installed")
    except ImportError as e:
        errors.append(f"✗ pypdf missing: {e}")
    
    try:
        import dotenv
        print("✓ python-dotenv installed")
    except ImportError as e:
        errors.append(f"✗ python-dotenv missing: {e}")
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy installed")
    except ImportError as e:
        errors.append(f"✗ SQLAlchemy missing: {e}")
    
    try:
        import uvicorn
        print("✓ uvicorn installed")
    except ImportError as e:
        errors.append(f"✗ uvicorn missing: {e}")
    
    try:
        import litellm
        print("✓ LiteLLM installed")
    except ImportError as e:
        errors.append(f"✗ LiteLLM missing: {e}")
    
    # Optional dependencies
    try:
        import redis
        import rq
        print("✓ Redis + RQ installed (optional)")
    except ImportError:
        print("⚠ Redis/RQ not installed (optional - for async processing)")
    
    return errors

def test_env_file():
    """Test environment configuration"""
    print("\nTesting environment configuration...")
    
    if not os.path.exists(".env"):
        print("⚠ .env file not found")
        print("  Create .env file from .env.example")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("✗ GEMINI_API_KEY not set in .env")
        return False
    
    if api_key == "your_gemini_api_key_here":
        print("✗ GEMINI_API_KEY still has placeholder value")
        return False
    
    print("✓ GEMINI_API_KEY configured")
    
    model = os.getenv("LLM_MODEL", "gemini/gemini-1.5-flash")
    print(f"✓ LLM_MODEL: {model}")
    
    return True

def test_file_structure():
    """Test required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        "main.py",
        "agents.py",
        "task.py",
        "tools.py",
        "requirements.txt",
        "database.py",
        "worker.py",
        "main_async.py"
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} missing")
            missing.append(file)
    
    # Check data directory
    if os.path.exists("data"):
        print("✓ data/ directory exists")
    else:
        print("⚠ data/ directory missing (will be created automatically)")
    
    return missing

def test_imports_from_modules():
    """Test importing from project modules"""
    print("\nTesting project modules...")
    errors = []
    
    try:
        from tools import read_financial_document, search_tool
        print("✓ tools.py imports successfully")
    except Exception as e:
        errors.append(f"✗ tools.py error: {e}")
    
    try:
        from database import init_db, AnalysisRequest, AnalysisResult
        print("✓ database.py imports successfully")
    except Exception as e:
        errors.append(f"✗ database.py error: {e}")
    
    try:
        from agents import financial_analyst, verifier, investment_advisor, risk_assessor
        print("✓ agents.py imports successfully")
    except Exception as e:
        errors.append(f"✗ agents.py error: {e}")
    
    try:
        from task import analyze_financial_document, verification_task
        print("✓ task.py imports successfully")
    except Exception as e:
        errors.append(f"✗ task.py error: {e}")
    
    return errors

def main():
    """Run all tests"""
    print("=" * 60)
    print("Financial Document Analyzer - Setup Validation")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    import_errors = test_imports()
    if import_errors:
        print("\n❌ Import errors found:")
        for error in import_errors:
            print(f"  {error}")
        print("\nRun: pip install -r requirements.txt")
        all_passed = False
    
    # Test file structure
    missing_files = test_file_structure()
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        all_passed = False
    
    # Test environment
    env_ok = test_env_file()
    if not env_ok:
        print("\n❌ Environment configuration incomplete")
        print("  1. Copy .env.example to .env")
        print("  2. Add your GEMINI_API_KEY")
        print("  3. Get free key: https://aistudio.google.com/app/apikey")
        all_passed = False
    
    # Test module imports
    if all_passed:
        module_errors = test_imports_from_modules()
        if module_errors:
            print("\n❌ Module import errors:")
            for error in module_errors:
                print(f"  {error}")
            all_passed = False
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! You're ready to run the application.")
        print("\nNext steps:")
        print("  1. Run: python main.py")
        print("  2. Open: http://localhost:8000/docs")
        print("  3. Test the /analyze endpoint")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Configure .env: copy .env.example .env")
        print("  - Add your Gemini API key to .env")
        print("  - Get free key: https://aistudio.google.com/app/apikey")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
