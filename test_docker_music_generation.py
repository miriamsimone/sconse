#!/usr/bin/env python3
"""
Test script for Dockerized music generation endpoint
"""
import requests
import json
import sys
import time

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
    
    print("🐳 Testing Dockerized Music Generation Endpoint")
    print("=" * 60)
    
    # Test 1: Check if service is running
    print("\n1. Testing service health...")
    max_retries = 10
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ Service is running")
                data = response.json()
                print(f"   Service: {data.get('service', 'Unknown')}")
                print(f"   Version: {data.get('version', 'Unknown')}")
                features = data.get('features', [])
                print(f"   Features: {len(features)} available")
                for feature in features:
                    print(f"     - {feature}")
                break
            else:
                print(f"   Attempt {attempt + 1}: Status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"   Attempt {attempt + 1}: Connection refused, waiting...")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                print("❌ Cannot connect to service after 10 attempts")
                print("   Make sure Docker container is running:")
                print("   cd ai-microservice && docker-compose up --build")
                return False
        except Exception as e:
            print(f"   Attempt {attempt + 1}: Error - {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    
    # Test 2: Test generation endpoint
    print("\n2. Testing music generation...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['description'][:50]}...")
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/music/generate",
                json=test_case,
                timeout=60  # Longer timeout for LLM calls
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success!")
                print(f"      Music ID: {result.get('music_id', 'N/A')}")
                print(f"      Title: {result.get('title', 'N/A')}")
                print(f"      Confidence: {result.get('confidence', 'N/A')}")
                print(f"      Validation: {result.get('validation_status', 'N/A')}")
                
                # Show ABC notation
                abc_notation = result.get('abc_notation', '')
                if abc_notation:
                    abc_lines = abc_notation.split('\n')
                    print("      ABC Notation:")
                    for line in abc_lines[:8]:  # Show first 8 lines
                        if line.strip():
                            print(f"        {line}")
                    if len(abc_lines) > 8:
                        print("        ...")
                
                # Show metadata
                metadata = result.get('metadata', {})
                if metadata:
                    print(f"      Metadata: {len(metadata)} items")
                    if 'validation_errors' in metadata and metadata['validation_errors']:
                        print(f"        Validation errors: {metadata['validation_errors']}")
                    if 'validation_warnings' in metadata and metadata['validation_warnings']:
                        print(f"        Validation warnings: {metadata['validation_warnings']}")
                    
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                try:
                    error = response.json()
                    print(f"      Error: {error.get('detail', 'Unknown error')}")
                except:
                    print(f"      Error: {response.text}")
                    
        except requests.exceptions.Timeout:
            print("   ⏰ Request timed out (60s)")
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
    
    print("\n" + "=" * 60)
    print("🐳 Docker test completed!")
    return True

if __name__ == "__main__":
    success = test_music_generation()
    sys.exit(0 if success else 1)
