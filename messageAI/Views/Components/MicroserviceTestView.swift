import SwiftUI

struct MicroserviceTestView: View {
    @State private var testResults: [String] = []
    @State private var isTesting = false
    
    private let musicService = RemoteMusicSheetService()
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("Microservice Connection Test")
                    .font(.title2)
                    .fontWeight(.bold)
                
                if isTesting {
                    ProgressView("Testing connection...")
                        .padding()
                }
                
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 8) {
                        ForEach(testResults, id: \.self) { result in
                            Text(result)
                                .font(.system(.body, design: .monospaced))
                                .padding(.horizontal)
                        }
                    }
                }
                .background(Color.gray.opacity(0.1))
                .cornerRadius(8)
                
                Button("Run Tests") {
                    runTests()
                }
                .disabled(isTesting)
                .buttonStyle(.borderedProminent)
            }
            .padding()
            .navigationTitle("API Test")
        }
    }
    
    private func runTests() {
        isTesting = true
        testResults.removeAll()
        
        Task {
            // Test 1: Health Check
            await addResult("🔍 Testing health check...")
            do {
                let healthURL = URL(string: "http://localhost:8000/health")!
                let (data, response) = try await URLSession.shared.data(from: healthURL)
                if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                    await addResult("✅ Health check passed")
                } else {
                    await addResult("❌ Health check failed")
                }
            } catch {
                await addResult("❌ Health check error: \(error.localizedDescription)")
            }
            
            // Test 2: IMSLP Search
            await addResult("\n🔍 Testing AI route + execute...")
            do {
                let result = try await musicService.routeAndExecute(userInput: "Find Beethoven Moonlight Sonata", userID: "ios_test_user", conversationID: nil)
                switch result {
                case .pdf(let classical):
                    await addResult("✅ Classical lookup successful: \(classical.title)")
                case .abc(let sheet):
                    await addResult("✅ Music generation received: \(sheet.abcNotation.prefix(50))...")
                case .setlist(let plan):
                    await addResult("✅ Setlist design received: \(plan.title) with \(plan.pieces.count) pieces")
                }
            } catch {
                await addResult("❌ Route + execute error: \(error.localizedDescription)")
            }
            
            // Test 3: Audio Transcription
            await addResult("\n🔍 Testing audio transcription...")
            do {
                let testAudioData = "test".data(using: .utf8)!
                let result = try await musicService.transcribeAudio(audioData: testAudioData, format: "wav")
                await addResult("✅ Audio transcription successful: \(result.abcNotation.prefix(50))...")
            } catch {
                await addResult("❌ Audio transcription error: \(error.localizedDescription)")
            }
            
            // Test 4: Melody Editing
            await addResult("\n🔍 Testing melody editing...")
            do {
                let testABC = "X:1\nT:Test\nM:4/4\nL:1/4\nK:C\nC D E F |"
                let result = try await musicService.editMelody(abcNotation: testABC, instruction: "change the second note to A")
                await addResult("✅ Melody editing successful: \(result.abcNotation.prefix(50))...")
            } catch {
                await addResult("❌ Melody editing error: \(error.localizedDescription)")
            }
            
            await addResult("\n🎉 All tests completed!")
            isTesting = false
        }
    }
    
    @MainActor
    private func addResult(_ result: String) {
        testResults.append(result)
    }
}

#Preview {
    MicroserviceTestView()
}
