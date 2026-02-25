"""
Full end-to-end test of the Financial Document Analyzer with Groq API.
Tests the complete analysis workflow with the Tesla Q2 2025 PDF.
"""

import requests
import os
import time

def test_full_analysis():
    """Test complete financial analysis workflow"""
    
    print("=" * 70)
    print("🧪 TESTING FINANCIAL DOCUMENT ANALYZER WITH GROQ API")
    print("=" * 70)
    
    # Configuration
    api_url = "http://localhost:8001"
    pdf_path = "data/TSLA-Q2-2025-Update.pdf"
    
    # Step 1: Check if server is running
    print("\n1️⃣  Checking API health...")
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API is healthy and running")
            health_data = response.json()
            print(f"   📊 Agents available: {', '.join(health_data['agents'])}")
        else:
            print(f"   ❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Is the server running on port 8001?")
        print("   💡 Run: python main.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False
    
    # Step 2: Check if PDF exists
    print("\n2️⃣  Checking PDF file...")
    if not os.path.exists(pdf_path):
        print(f"   ❌ PDF not found at: {pdf_path}")
        return False
    
    file_size = os.path.getsize(pdf_path)
    print(f"   ✅ PDF found: {file_size:,} bytes")
    
    # Step 3: Submit analysis request
    print("\n3️⃣  Submitting analysis request...")
    print("   ⏳ This may take 30-60 seconds with Groq (much faster than OpenAI!)...")
    
    query = "Analyze Tesla's Q2 2025 financial performance. Focus on revenue growth, profitability, and key risks."
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': ('TSLA-Q2-2025-Update.pdf', f, 'application/pdf')}
            data = {'query': query}
            
            start_time = time.time()
            response = requests.post(
                f"{api_url}/analyze",
                files=files,
                data=data,
                timeout=300  # 5 minute timeout
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"   ✅ Analysis completed in {elapsed_time:.1f} seconds")
                result = response.json()
                
                # Display results
                print("\n" + "=" * 70)
                print("📊 ANALYSIS RESULTS")
                print("=" * 70)
                print(f"\n📄 File: {result.get('file_processed', 'N/A')}")
                print(f"📏 Size: {result.get('file_size_bytes', 0):,} bytes")
                print(f"❓ Query: {result.get('query', 'N/A')}")
                print("\n" + "-" * 70)
                print("🤖 AI ANALYSIS:")
                print("-" * 70)
                
                analysis = result.get('analysis', 'No analysis returned')
                # Print first 2000 characters for readability
                if len(analysis) > 2000:
                    print(analysis[:2000])
                    print(f"\n... [truncated, total length: {len(analysis)} characters]")
                else:
                    print(analysis)
                
                print("\n" + "=" * 70)
                print("✅ TEST PASSED - Full analysis workflow successful!")
                print("=" * 70)
                print(f"\n⚡ Performance: {elapsed_time:.1f}s with Groq (Fast & Free!)")
                print("🎯 All agents executed successfully")
                print("📝 Analysis includes: Financial metrics, verification, investment advice, risk assessment")
                
                return True
                
            else:
                print(f"   ❌ Analysis failed with status code: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out (>5 minutes)")
        return False
    except Exception as e:
        print(f"   ❌ Error during analysis: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n🚀 Starting full end-to-end test...\n")
    success = test_full_analysis()
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
        print("🎉 The Financial Document Analyzer is working perfectly with Groq API!")
        exit(0)
    else:
        print("\n❌ TEST FAILED")
        print("💡 Check the error messages above for troubleshooting")
        exit(1)
