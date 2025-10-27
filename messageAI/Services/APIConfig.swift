import Foundation

struct APIConfig {
    // MARK: - Environment Configuration
    
    #if DEBUG
    // Local development - point to your microservice
    static let baseURL = "http://localhost:8000/api/v1"
    static let isLocalDevelopment = true
    #else
    // Production - point to deployed microservice
    static let baseURL = "https://your-microservice-url.com/api/v1"
    static let isLocalDevelopment = false
    #endif
    
    // MARK: - Legacy Lambda (for fallback)
    static let legacyLambdaURL = "https://7cg7rc13l0.execute-api.us-east-1.amazonaws.com/Prod"
    
    // MARK: - Helper Methods
    
    static func getBaseURL() -> URL {
        return URL(string: baseURL)!
    }
    
    static func getLegacyURL() -> URL {
        return URL(string: legacyLambdaURL)!
    }
    
    // MARK: - Feature Flags
    
    static let useMicroservice = true  // Set to false to use legacy Lambda
    static let enableAudioTranscription = true
    static let enableMelodyEditing = true
    static let enableClassicalSearch = true
}
