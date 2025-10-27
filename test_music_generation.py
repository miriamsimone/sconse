#!/usr/bin/env python3
"""
Test script for music generation endpoint
"""
import requests
import json
import sys

def test_music_generation():
    """Test the music generation endpoint"""
    
    # Test data
    test_cases = [
        {
            "description": "Time signature 3/4, key F minor, eighth notes: A-flat, G, F",
            "user_id": "test_user_1"
        },
        {
            "description": "Quarter notes: C D E F, half note: G",
            "user_id": "test_user_2"
        },
        {
            "description": "Simple melody in C major: C C G G A A G F F E E D D C",
            "user_id": "test_user_3"
        }
    ]
    
    base_url = "http://localhost:8000"
    
    print("🎵 Testing Music Generation Endpoint")
    print("=" * 50)
    
    # Test 1: Check if service is running
    print("\n1. Testing service health...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Service is running")
            print(f"   Features: {response.json().get('features', [])}")
        else:
            print(f"❌ Service returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to service. Make sure it's running on localhost:8000")
        print("   Run: cd ai-microservice && python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error checking service: {e}")
        return False
    
    # Test 2: Test generation endpoint
    print("\n2. Testing music generation...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['description'][:50]}...")
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/music/generate",
                json=test_case,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success!")
                print(f"      Music ID: {result.get('music_id', 'N/A')}")
                print(f"      Title: {result.get('title', 'N/A')}")
                print(f"      Confidence: {result.get('confidence', 'N/A')}")
                print(f"      Validation: {result.get('validation_status', 'N/A')}")
                print(f"      ABC Preview: {result.get('abc_notation', '')[:100]}...")
                
                # Show ABC notation
                abc_lines = result.get('abc_notation', '').split('\n')
                print("      ABC Notation:")
                for line in abc_lines[:5]:  # Show first 5 lines
                    if line.strip():
                        print(f"        {line}")
                if len(abc_lines) > 5:
                    print("        ...")
                    
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                try:
                    error = response.json()
                    print(f"      Error: {error.get('detail', 'Unknown error')}")
                except:
                    print(f"      Error: {response.text}")
                    
        except requests.exceptions.Timeout:
            print("   ⏰ Request timed out (30s)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 3: Test error handling
    print("\n3. Testing error handling...")
    
    try:
        # Test with invalid request
        response = requests.post(
            f"{base_url}/api/v1/music/generate",
            json={"invalid": "request"},
            timeout=10
        )
        
        if response.status_code == 422:  # Validation error
            print("   ✅ Properly handles invalid requests")
        else:
            print(f"   ⚠️  Unexpected status for invalid request: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing error handling: {e}")
    
    print("\n" + "=" * 50)
    print("🎵 Test completed!")
    return True

if __name__ == "__main__":
    success = test_music_generation()
    sys.exit(0 if success else 1)
