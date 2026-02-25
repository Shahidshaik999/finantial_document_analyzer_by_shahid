"""
Simple test with minimal document size to verify Groq API works.
"""

import requests
import os

def test_simple_analysis():
    """Test with a very small query to verify the system works"""
    
    print("=" * 70)
    print("🧪 SIMPLE TEST - Verifying Groq API Integration")
    print("=" * 70)
    
    api_url = "http://localhost:8001"
    pdf_path = "data/TSLA-Q2-2025-Update.pdf"
    
    # Check health
    print("\n✓ Checking API health...")
    response = requests.get(f"{api_url}/health")
    if response.status_code != 200:
        print("❌ API not healthy")
        return False
    print("✓ API is healthy")
    
    # Simple analysis with minimal query
    print("\n✓ Testing analysis with minimal document...")
    query = "What company is this document about? Give a 2-sentence summary."
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': ('TSLA-Q2-2025-Update.pdf', f, 'application/pdf')}
            data = {'query': query}
            
            response = requests.post(
                f"{api_url}/analyze",
                files=files,
                data=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n" + "=" * 70)
                print("✅ SUCCESS! Analysis completed")
                print("=" * 70)
                print(f"\nQuery: {query}")
                print(f"\nResponse preview:")
                analysis = result.get('analysis', '')
                print(analysis[:500] if len(analysis) > 500 else analysis)
                print("\n" + "=" * 70)
                print("✅ Groq API integration is working!")
                print("=" * 70)
                return True
            else:
                print(f"\n❌ Failed: {response.status_code}")
                print(f"Error: {response.json().get('detail', 'Unknown error')}")
                return False
                
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_simple_analysis()
    exit(0 if success else 1)
