"""
Quick test to verify Groq API is working correctly.
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_groq_api():
    """Test Groq API connection"""
    print("Testing Groq API connection...")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env")
        return False
    
    print(f"✓ API Key found: {api_key[:20]}...")
    
    # Test with CrewAI LLM
    try:
        from crewai import LLM
        
        llm = LLM(
            model=os.getenv("LLM_MODEL", "groq/llama-3.3-70b-versatile"),
            api_key=api_key,
            temperature=0.3
        )
        
        print(f"✓ LLM initialized: {llm.model}")
        
        # Test a simple call
        print("\nTesting API call...")
        response = llm.call(
            messages=[{"role": "user", "content": "Say 'Hello from Groq!' in exactly 3 words."}]
        )
        
        print(f"✓ API Response: {response}")
        print("\n" + "=" * 60)
        print("✅ Groq API is working correctly!")
        print("🚀 Groq is FAST and FREE - perfect for this project!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing Groq API: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your API key is correct")
        print("2. Verify you have internet connection")
        print("3. Check Groq API status: https://status.groq.com/")
        print("4. Verify API key at: https://console.groq.com/keys")
        return False

if __name__ == "__main__":
    success = test_groq_api()
    exit(0 if success else 1)
