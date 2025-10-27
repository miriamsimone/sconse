import Foundation

struct MusicSheetResponse: Codable, Sendable {
    let status: String
    let musicID: String?
    let abcNotation: String
    let sheetMusicURL: String?
    let confidence: Double?
    let key: String
    let originalKey: String?
    let transposedTo: String?
    let validationStatus: String?
    let sources: [String]?

    enum CodingKeys: String, CodingKey {
        case status
        case musicID = "music_id"
        case abcNotation = "abc_notation"
        case sheetMusicURL = "sheet_music_url"
        case confidence
        case key
        case originalKey = "original_key"
        case transposedTo = "transposed_to"
        case validationStatus = "validation_status"
        case sources
    }

}

struct ClassicalSheetResponse: Codable, Sendable {
    let status: String
    let classicalMusic: Bool?
    let pdfURL: String
    let title: String
    let composer: String?
    let opus: String?
    let mutopiaURL: String?
    let description: String?
    let message: String?
    let sources: [String]?

    enum CodingKeys: String, CodingKey {
        case status
        case classicalMusic = "classical_music"
        case pdfURL = "pdf_url"
        case title
        case composer
        case opus
        case mutopiaURL = "mutopia_url"
        case description
        case message
        case sources
    }
}

struct SetlistPlanPieceResponse: Codable, Sendable {
    let title: String
    let composer: String?
    let durationMinutes: Int?
    let difficultyLevel: String?
    let keySignature: String?
    let instruments: [String]?
    let genre: String?
    let reasoning: String?

    private enum CodingKeys: String, CodingKey {
        case title
        case composer
        case durationMinutes = "duration_minutes"
        case difficultyLevel = "difficulty_level"
        case keySignature = "key_signature"
        case instruments
        case genre
        case reasoning = "collaborative_reasoning"
        case legacyReasoning = "reasoning"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        title = try container.decode(String.self, forKey: .title)
        composer = try container.decodeIfPresent(String.self, forKey: .composer)
        durationMinutes = try container.decodeIfPresent(Int.self, forKey: .durationMinutes)
        difficultyLevel = try container.decodeIfPresent(String.self, forKey: .difficultyLevel)
        keySignature = try container.decodeIfPresent(String.self, forKey: .keySignature)
        instruments = try container.decodeIfPresent([String].self, forKey: .instruments)
        genre = try container.decodeIfPresent(String.self, forKey: .genre)
        reasoning = try container.decodeIfPresent(String.self, forKey: .reasoning) ??
            container.decodeIfPresent(String.self, forKey: .legacyReasoning)
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(title, forKey: .title)
        try container.encodeIfPresent(composer, forKey: .composer)
        try container.encodeIfPresent(durationMinutes, forKey: .durationMinutes)
        try container.encodeIfPresent(difficultyLevel, forKey: .difficultyLevel)
        try container.encodeIfPresent(keySignature, forKey: .keySignature)
        try container.encodeIfPresent(instruments, forKey: .instruments)
        try container.encodeIfPresent(genre, forKey: .genre)
        try container.encodeIfPresent(reasoning, forKey: .reasoning)
    }
}

struct SetlistPlanResponse: Codable, Sendable {
    var status: String
    let setlistID: String?
    let title: String
    let totalDuration: Int
    let confidence: Double?
    let designReasoning: String?
    let pieces: [SetlistPlanPieceResponse]
    let agentContributions: [String: String]?

    private enum CodingKeys: String, CodingKey {
        case status
        case setlistID = "setlist_id"
        case title
        case totalDuration = "total_duration"
        case confidence
        case designReasoning = "design_reasoning"
        case pieces
        case agentContributions = "agent_contributions"
    }

    init(status: String = "success",
         setlistID: String?,
         title: String,
         totalDuration: Int,
         confidence: Double? = nil,
         designReasoning: String? = nil,
         pieces: [SetlistPlanPieceResponse],
         agentContributions: [String: String]? = nil) {
        self.status = status
        self.setlistID = setlistID
        self.title = title
        self.totalDuration = totalDuration
        self.confidence = confidence
        self.designReasoning = designReasoning
        self.pieces = pieces
        self.agentContributions = agentContributions
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        status = try container.decodeIfPresent(String.self, forKey: .status) ?? "success"
        setlistID = try container.decodeIfPresent(String.self, forKey: .setlistID)
        title = try container.decode(String.self, forKey: .title)
        totalDuration = try container.decodeIfPresent(Int.self, forKey: .totalDuration) ?? 0
        confidence = try container.decodeIfPresent(Double.self, forKey: .confidence)
        designReasoning = try container.decodeIfPresent(String.self, forKey: .designReasoning)
        pieces = (try? container.decode([SetlistPlanPieceResponse].self, forKey: .pieces)) ?? []
        agentContributions = (try? container.decode([String: String].self, forKey: .agentContributions))
    }
}

enum MusicSheetServiceError: Error, LocalizedError {
    case invalidResponse
    case badStatusCode(Int)
    case decodingFailed
    case unsupportedService(String)
    case serviceMessage(String)
    case unknown

    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "The music service returned an invalid response."
        case .badStatusCode(let code):
            return "Music service request failed with status code \(code)."
        case .decodingFailed:
            return "Unable to parse the sheet music response."
        case .unsupportedService(let service):
            return "The AI router returned an unsupported service: \(service)."
        case .serviceMessage(let message):
            return message
        case .unknown:
            return "An unexpected error occurred while contacting the music service."
        }
    }
}

protocol MusicSheetService {
    func routeAndExecute(userInput: String, userID: String, conversationID: String?) async throws -> SheetMusicResult
    func transcribeAudio(audioData: Data, format: String) async throws -> MusicSheetResponse
    func editMelody(abcNotation: String, instruction: String) async throws -> MusicSheetResponse
    func startCollaborativeSetlist(request: ChatSetlistStartRequestPayload) async throws -> ChatSetlistResponsePayload
    func submitSetlistPreferences(request: ChatSetlistPreferencePayload) async throws -> ChatSetlistResponsePayload
}

enum SheetMusicResult: Sendable {
    case abc(MusicSheetResponse)
    case pdf(ClassicalSheetResponse)
    case setlist(SetlistPlanResponse)
}

struct ChatSetlistQuestionsResponse: Codable, Sendable {
    let generalQuestions: [String]?
    let concertSpecificQuestions: [String]?
    let collaborationQuestions: [String]?

    private enum CodingKeys: String, CodingKey {
        case generalQuestions = "general_questions"
        case concertSpecificQuestions = "concert_specific_questions"
        case collaborationQuestions = "collaboration_questions"
    }
}

struct ChatSetlistResponsePayload: Codable, Sendable {
    let status: String
    let action: String
    let message: String
    let setlistID: String?
    let waitingForResponses: Bool?
    let requiredResponses: [String]?
    let questions: ChatSetlistQuestionsResponse?
    let setlistData: SetlistPlanResponse?

    private enum CodingKeys: String, CodingKey {
        case status
        case action
        case message
        case setlistID = "setlist_id"
        case waitingForResponses = "waiting_for_responses"
        case requiredResponses = "required_responses"
        case questions
        case setlistData = "setlist_data"
    }
}

struct ChatSetlistStartRequestPayload: Codable, Sendable {
    let userInput: String
    let groupID: String
    let conversationID: String
    let organizerUserID: String
    let organizerUsername: String
    let groupMemberIDs: [String]

    private enum CodingKeys: String, CodingKey {
        case userInput = "user_input"
        case groupID = "group_id"
        case conversationID = "conversation_id"
        case organizerUserID = "organizer_user_id"
        case organizerUsername = "organizer_username"
        case groupMemberIDs = "group_member_ids"
    }
}

struct ChatSetlistPreferencePayload: Codable, Sendable {
    let setlistID: String
    let userID: String
    let username: String
    let preferenceText: String
    let responseTimestamp: String

    private enum CodingKeys: String, CodingKey {
        case setlistID = "setlist_id"
        case userID = "user_id"
        case username
        case preferenceText = "preference_text"
        case responseTimestamp = "response_timestamp"
    }
}

final class RemoteMusicSheetService: MusicSheetService, Sendable {
    private let baseURL: URL
    private let urlSession: URLSession

    init(baseURL: URL = APIConfig.getBaseURL(),
         urlSession: URLSession = .shared) {
        self.baseURL = baseURL
        self.urlSession = urlSession
    }

    func routeAndExecute(userInput: String, userID: String, conversationID: String?) async throws -> SheetMusicResult {
        let endpoint = baseURL.appendingPathComponent("ai/route-and-execute")
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        var body: [String: Any] = [
            "user_input": userInput,
            "user_id": userID
        ]
        if let conversationID, !conversationID.isEmpty {
            body["conversation_id"] = conversationID
        }

        request.httpBody = try JSONSerialization.data(withJSONObject: body, options: [])

        let (data, response) = try await urlSession.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw MusicSheetServiceError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw MusicSheetServiceError.badStatusCode(httpResponse.statusCode)
        }

        guard let jsonObject = try? JSONSerialization.jsonObject(with: data, options: []),
              let dictionary = jsonObject as? [String: Any] else {
            throw MusicSheetServiceError.decodingFailed
        }

        let status = (dictionary["status"] as? String) ?? "success"
        guard status.lowercased() == "success" else {
            throw MusicSheetServiceError.decodingFailed
        }

        guard let serviceResult = dictionary["service_result"] as? [String: Any],
              let serviceName = serviceResult["service"] as? String else {
            throw MusicSheetServiceError.decodingFailed
        }

        let resultPayload = serviceResult["result"] as? [String: Any] ?? [:]

        if let errorMessage = resultPayload["error"] as? String, !errorMessage.isEmpty {
            throw MusicSheetServiceError.decodingFailed
        }

        switch serviceName {
        case "imslp_search":
            guard let pdfURL = resultPayload["pdf_url"] as? String, !pdfURL.isEmpty else {
                throw MusicSheetServiceError.decodingFailed
            }

            let title = (resultPayload["title"] as? String).flatMap { !$0.isEmpty ? $0 : nil } ?? userInput
            let composer = resultPayload["composer"] as? String
            let mutopiaURL = resultPayload["mutopia_url"] as? String
            let description = resultPayload["description"] as? String
            let opus = resultPayload["opus"] as? String

            let classical = ClassicalSheetResponse(
                status: status,
                classicalMusic: true,
                pdfURL: pdfURL,
                title: title,
                composer: composer,
                opus: opus,
                mutopiaURL: mutopiaURL,
                description: description,
                message: description,
                sources: [mutopiaURL].compactMap { $0 }
            )
            return .pdf(classical)

        case "music_generation":
            guard let abcNotation = resultPayload["abc_notation"] as? String, !abcNotation.isEmpty else {
                throw MusicSheetServiceError.decodingFailed
            }

            let metadata = resultPayload["metadata"] as? [String: Any]
            let key = metadata?["key"] as? String ?? Self.detectKey(in: abcNotation)
            let originalKey = metadata?["original_key"] as? String
            let transposedTo = metadata?["transposed_to"] as? String
            let sources = metadata?["sources"] as? [String] ?? serviceResult["sources"] as? [String]

            let sheet = MusicSheetResponse(
                status: status,
                musicID: resultPayload["music_id"] as? String,
                abcNotation: abcNotation,
                sheetMusicURL: resultPayload["sheet_music_url"] as? String,
                confidence: resultPayload["confidence"] as? Double,
                key: key,
                originalKey: originalKey,
                transposedTo: transposedTo,
                validationStatus: resultPayload["validation_status"] as? String,
                sources: sources
            )
            return .abc(sheet)

        case "setlist_design":
            do {
                let data = try JSONSerialization.data(withJSONObject: resultPayload, options: [])
                var response = try JSONDecoder().decode(SetlistPlanResponse.self, from: data)
                response.status = status
                return .setlist(response)
            } catch {
                throw MusicSheetServiceError.decodingFailed
            }

        default:
            throw MusicSheetServiceError.unsupportedService(serviceName)
        }
    }

    private static func detectKey(in abcNotation: String) -> String {
        guard let line = abcNotation
            .split(whereSeparator: \.isNewline)
            .first(where: { $0.trimmingCharacters(in: .whitespaces).hasPrefix("K:") }) else {
            return "C"
        }
        let components = line.split(separator: ":", maxSplits: 1, omittingEmptySubsequences: true)
        if components.count == 2 {
            let keyValue = components[1].trimmingCharacters(in: .whitespaces)
            return keyValue.isEmpty ? "C" : keyValue
        }
        return "C"
    }
    
    func transcribeAudio(audioData: Data, format: String) async throws -> MusicSheetResponse {
        let endpoint = baseURL.appendingPathComponent("transcribe-audio")
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let base64Audio = audioData.base64EncodedString()
        let body: [String: Any] = [
            "audio_file": base64Audio,
            "audio_format": format,
            "user_id": "ios_user",
            "duration_seconds": 15
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body, options: [])
        
        let (data, response) = try await urlSession.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw MusicSheetServiceError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw MusicSheetServiceError.badStatusCode(httpResponse.statusCode)
        }
        
        guard let jsonObject = try? JSONSerialization.jsonObject(with: data, options: []),
              let dictionary = jsonObject as? [String: Any] else {
            throw MusicSheetServiceError.decodingFailed
        }

        let abcNotation = (dictionary["abc_notation"] as? String) ?? ""
        let detectedKey = (dictionary["key_detected"] as? String) ?? Self.detectKey(in: abcNotation)

        return MusicSheetResponse(
            status: (dictionary["status"] as? String) ?? "success",
            musicID: dictionary["music_id"] as? String,
            abcNotation: abcNotation,
            sheetMusicURL: dictionary["sheet_music_url"] as? String,
            confidence: dictionary["confidence"] as? Double,
            key: detectedKey,
            originalKey: nil,
            transposedTo: nil,
            validationStatus: dictionary["validation_status"] as? String,
            sources: nil
        )
    }

    func editMelody(abcNotation: String, instruction: String) async throws -> MusicSheetResponse {
        let endpoint = baseURL.appendingPathComponent("edit-melody")
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "abc_notation": abcNotation,
            "edit_instruction": instruction,
            "user_id": "ios_user"
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body, options: [])
        
        let (data, response) = try await urlSession.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw MusicSheetServiceError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw MusicSheetServiceError.badStatusCode(httpResponse.statusCode)
        }
        
        guard let jsonObject = try? JSONSerialization.jsonObject(with: data, options: []),
              let dictionary = jsonObject as? [String: Any] else {
            throw MusicSheetServiceError.decodingFailed
        }

        let abcNotation = (dictionary["abc_notation"] as? String) ?? ""
        let detectedKey = Self.detectKey(in: abcNotation)

        return MusicSheetResponse(
            status: (dictionary["status"] as? String) ?? "success",
            musicID: dictionary["music_id"] as? String,
            abcNotation: abcNotation,
            sheetMusicURL: dictionary["sheet_music_url"] as? String,
            confidence: dictionary["confidence"] as? Double,
            key: detectedKey,
            originalKey: nil,
            transposedTo: nil,
            validationStatus: dictionary["validation_status"] as? String,
            sources: nil
        )
    }

    func startCollaborativeSetlist(request: ChatSetlistStartRequestPayload) async throws -> ChatSetlistResponsePayload {
        let endpoint = baseURL.appendingPathComponent("setlist/chat-based")
        var urlRequest = URLRequest(url: endpoint)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .useDefaultKeys
        urlRequest.httpBody = try encoder.encode(request)

        let (data, response) = try await urlSession.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw MusicSheetServiceError.invalidResponse
        }
        guard (200...299).contains(httpResponse.statusCode) else {
            if let message = Self.extractServiceMessage(from: data) {
                throw MusicSheetServiceError.serviceMessage(message)
            }
            throw MusicSheetServiceError.badStatusCode(httpResponse.statusCode)
        }

        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .useDefaultKeys
        guard let payload = try? decoder.decode(ChatSetlistResponsePayload.self, from: data) else {
            throw MusicSheetServiceError.decodingFailed
        }
        return payload
    }

    func submitSetlistPreferences(request: ChatSetlistPreferencePayload) async throws -> ChatSetlistResponsePayload {
        let endpoint = baseURL.appendingPathComponent("setlist/preference-response")
        var urlRequest = URLRequest(url: endpoint)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .useDefaultKeys
        urlRequest.httpBody = try encoder.encode(request)

        let (data, response) = try await urlSession.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw MusicSheetServiceError.invalidResponse
        }
        guard (200...299).contains(httpResponse.statusCode) else {
            if let message = Self.extractServiceMessage(from: data) {
                throw MusicSheetServiceError.serviceMessage(message)
            }
            throw MusicSheetServiceError.badStatusCode(httpResponse.statusCode)
        }

        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .useDefaultKeys
        guard let payload = try? decoder.decode(ChatSetlistResponsePayload.self, from: data) else {
            throw MusicSheetServiceError.decodingFailed
        }
        return payload
    }

    private static func extractServiceMessage(from data: Data) -> String? {
        guard let json = try? JSONSerialization.jsonObject(with: data, options: []),
              let dictionary = json as? [String: Any] else {
            return nil
        }

        if let detail = dictionary["detail"] as? String, !detail.isEmpty {
            return detail
        }

        if let message = dictionary["message"] as? String, !message.isEmpty {
            return message
        }

        if let error = dictionary["error"] as? String, !error.isEmpty {
            return error
        }

        return nil
    }
}
