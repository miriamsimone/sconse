#!/usr/bin/env swift

import Foundation

// Test script to verify the microservice connection
func testMicroserviceConnection() async {
    let baseURL = URL(string: "http://localhost:8000/api/v1")!
    
    // Test 1: Health check
    print("🔍 Testing health check...")
    do {
        let healthURL = URL(string: "http://localhost:8000/health")!
        let (data, response) = try await URLSession.shared.data(from: healthURL)
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
            print("✅ Health check passed")
        } else {
            print("❌ Health check failed")
        }
    } catch {
        print("❌ Health check error: \(error)")
    }
    
    // Test 2: IMSLP search
    print("\n🔍 Testing IMSLP search...")
    do {
        let endpoint = baseURL.appendingPathComponent("search-imslp")
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "query": "Beethoven Moonlight Sonata",
            "user_id": "test_user"
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body, options: [])
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let title = json["title"] as? String {
                print("✅ IMSLP search successful: \(title)")
            } else {
                print("❌ IMSLP search failed to parse response")
            }
        } else {
            print("❌ IMSLP search failed with status: \((response as? HTTPURLResponse)?.statusCode ?? -1)")
        }
    } catch {
        print("❌ IMSLP search error: \(error)")
    }
    
    // Test 3: Audio transcription
    print("\n🔍 Testing audio transcription...")
    do {
        let endpoint = baseURL.appendingPathComponent("transcribe-audio")
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "audio_file": "dGVzdA==", // Base64 for "test"
            "audio_format": "wav",
            "user_id": "test_user",
            "duration_seconds": 10
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body, options: [])
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let abcNotation = json["abc_notation"] as? String {
                print("✅ Audio transcription successful: \(abcNotation.prefix(50))...")
            } else {
                print("❌ Audio transcription failed to parse response")
            }
        } else {
            print("❌ Audio transcription failed with status: \((response as? HTTPURLResponse)?.statusCode ?? -1)")
        }
    } catch {
        print("❌ Audio transcription error: \(error)")
    }
    
    print("\n🎉 Microservice connection test completed!")
}

// Run the test
Task {
    await testMicroserviceConnection()
}
