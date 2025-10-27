import Foundation

struct ChatMessageItem: Identifiable, Equatable, Sendable {
    let id: String
    let conversationID: String
    let senderID: String
    let content: String
    let type: MessageContentType
    let mediaURL: URL?
    let sheetMusic: SheetMusicAttachment?
    let setlist: SetlistPlanAttachment?
    let setlistUpdate: SetlistUpdate?
    let timestamp: Date
    let deliveryStatus: MessageDeliveryStatus
    let readBy: [String]
    let localID: String?

    init(id: String,
         conversationID: String,
         senderID: String,
         content: String,
         type: MessageContentType,
         mediaURL: URL?,
         sheetMusic: SheetMusicAttachment?,
         setlist: SetlistPlanAttachment? = nil,
         setlistUpdate: SetlistUpdate? = nil,
         timestamp: Date,
         deliveryStatus: MessageDeliveryStatus,
         readBy: [String],
         localID: String?) {
        self.id = id
        self.conversationID = conversationID
        self.senderID = senderID
        self.content = content
        self.type = type
        self.mediaURL = mediaURL
        self.sheetMusic = sheetMusic
        self.setlist = setlist
        self.setlistUpdate = setlistUpdate
        self.timestamp = timestamp
        self.deliveryStatus = deliveryStatus
        self.readBy = readBy
        self.localID = localID
    }
}

protocol MessageListeningToken {
    func stop()
}

protocol MessageService {
    func listenForMessages(in conversationID: String,
                           onChange: @escaping ([ChatMessageItem]) -> Void,
                           onError: @escaping (Error) -> Void) -> MessageListeningToken

    func sendMessage(to conversationID: String,
                     content: String,
                     type: MessageContentType,
                     localID: String?,
                     metadata: [String: Any]?) async throws -> ChatMessageItem

    func updateMessage(in conversationID: String,
                       messageID: String,
                       content: String,
                       type: MessageContentType,
                       metadata: [String: Any]?) async throws -> ChatMessageItem
}

#if canImport(FirebaseFirestore)
import FirebaseFirestore

final class FirestoreMessageService: MessageService {
    private let db = Firestore.firestore()
    private let currentUserID: String

    init(currentUserID: String) {
        self.currentUserID = currentUserID
    }

    func listenForMessages(in conversationID: String,
                           onChange: @escaping ([ChatMessageItem]) -> Void,
                           onError: @escaping (Error) -> Void) -> MessageListeningToken {
        let query = db.collection("conversations")
            .document(conversationID)
            .collection("messages")
            .order(by: "timestamp", descending: false)

        let registration = query.addSnapshotListener { snapshot, error in
            if let error {
                onError(error)
                return
            }

            guard let documents = snapshot?.documents else {
                onChange([])
                return
            }

            let messages: [ChatMessageItem] = documents.compactMap { doc in
                Self.makeChatMessageItem(from: doc.data(),
                                         documentID: doc.documentID,
                                         conversationID: conversationID)
            }

            onChange(messages)
        }

        return FirestoreListenerToken(registration: registration)
    }

    func sendMessage(to conversationID: String,
                     content: String,
                     type: MessageContentType,
                     localID: String?,
                     metadata: [String: Any]? = nil) async throws -> ChatMessageItem {
        let messagesRef = db.collection("conversations")
            .document(conversationID)
            .collection("messages")

        let newDoc = messagesRef.document()
        let now = Date()

        var payload: [String: Any] = [
            "senderId": currentUserID,
            "content": content,
            "type": type.rawValue,
            "timestamp": Timestamp(date: now),
            "deliveryStatus": MessageDeliveryStatus.sent.rawValue,
            "readBy": [currentUserID],
        ]

        if let mediaURL = metadata?["mediaURL"] as? String {
            payload["mediaURL"] = mediaURL
        }

        if let sheetMusic = metadata?["sheetMusic"] as? [String: Any] {
            payload["sheetMusic"] = sheetMusic
        }

        if let setlist = metadata?["setlist"] as? [String: Any] {
            payload["setlist"] = setlist
        }

        if let setlistUpdate = metadata?["setlistUpdate"] as? [String: Any] {
            payload["setlistUpdate"] = setlistUpdate
        }

        if let localID {
            payload["localId"] = localID
        }

        try await newDoc.setData(payload)

        let conversationRef = db.collection("conversations").document(conversationID)
        try await conversationRef.setData([
            "lastMessage": content,
            "lastMessageTimestamp": Timestamp(date: now),
            "lastMessageSenderId": currentUserID
        ], merge: true)

        return ChatMessageItem(id: newDoc.documentID,
                               conversationID: conversationID,
                               senderID: currentUserID,
                               content: content,
                               type: type,
                               mediaURL: (metadata?["mediaURL"] as? String).flatMap(URL.init(string:)),
                               sheetMusic: (metadata?["sheetMusic"] as? [String: Any]).flatMap {
                                   Self.parseSheetMusicAttachment(dictionary: $0, fallbackSongName: content)
                               },
                               setlist: (metadata?["setlist"] as? [String: Any]).flatMap(Self.parseSetlistAttachment(dictionary:)),
                               setlistUpdate: (metadata?["setlistUpdate"] as? [String: Any]).flatMap(Self.parseSetlistUpdate(dictionary:)),
                               timestamp: now,
                               deliveryStatus: .sent,
                               readBy: [currentUserID],
                               localID: localID)
    }

    func updateMessage(in conversationID: String,
                       messageID: String,
                       content: String,
                       type: MessageContentType,
                       metadata: [String: Any]? = nil) async throws -> ChatMessageItem {
        let messageDoc = db.collection("conversations")
            .document(conversationID)
            .collection("messages")
            .document(messageID)

        var payload: [String: Any] = [
            "content": content,
            "type": type.rawValue,
            "deliveryStatus": MessageDeliveryStatus.sent.rawValue
        ]

        if let metadata {
            for (key, value) in metadata {
                payload[key] = value
            }
        }

        try await messageDoc.setData(payload, merge: true)

        let snapshot = try await messageDoc.getDocument()
        guard let data = snapshot.data(),
              let item = Self.makeChatMessageItem(from: data,
                                                  documentID: snapshot.documentID,
                                                  conversationID: conversationID) else {
            throw NSError(domain: "ChatService",
                          code: -1,
                          userInfo: [NSLocalizedDescriptionKey: "Failed to parse updated message."])
        }

        let conversationRef = db.collection("conversations").document(conversationID)
        try await conversationRef.setData([
            "lastMessage": item.content,
            "lastMessageSenderId": item.senderID,
            "lastMessageTimestamp": Timestamp(date: Date())
        ], merge: true)

        return item
    }
}
#else
final class FirestoreMessageService: MessageService {
    init(currentUserID: String) {}

    func listenForMessages(in conversationID: String,
                           onChange: @escaping ([ChatMessageItem]) -> Void,
                           onError: @escaping (Error) -> Void) -> MessageListeningToken {
        onError(UserServiceError.firebaseSDKMissing)
        return EmptyConversationListener()
    }

    func sendMessage(to conversationID: String,
                     content: String,
                     type: MessageContentType,
                     localID: String?,
                     metadata: [String: Any]? = nil) async throws -> ChatMessageItem {
        throw UserServiceError.firebaseSDKMissing
    }

    func updateMessage(in conversationID: String,
                       messageID: String,
                       content: String,
                       type: MessageContentType,
                       metadata: [String: Any]? = nil) async throws -> ChatMessageItem {
        throw UserServiceError.firebaseSDKMissing
    }
}
#endif

private extension FirestoreMessageService {
    static func makeChatMessageItem(from data: [String: Any],
                                    documentID: String,
                                    conversationID: String) -> ChatMessageItem? {
        guard let senderID = data["senderId"] as? String,
              let typeString = data["type"] as? String,
              let statusString = data["deliveryStatus"] as? String else {
            return nil
        }

        let timestamp: Date
        if let ts = data["timestamp"] as? Timestamp {
            timestamp = ts.dateValue()
        } else if let date = data["timestamp"] as? Date {
            timestamp = date
        } else {
            timestamp = Date()
        }

        let type = MessageContentType(rawValue: typeString) ?? .text
        let status = MessageDeliveryStatus(rawValue: statusString) ?? .sent
        let mediaURL = (data["mediaURL"] as? String).flatMap(URL.init(string:))
        let sheetMusic = (data["sheetMusic"] as? [String: Any]).flatMap {
            Self.parseSheetMusicAttachment(dictionary: $0, fallbackSongName: data["content"] as? String)
        }
        let setlist = (data["setlist"] as? [String: Any]).flatMap(Self.parseSetlistAttachment(dictionary:))
        let setlistUpdate = (data["setlistUpdate"] as? [String: Any]).flatMap(Self.parseSetlistUpdate(dictionary:))
        let readBy = data["readBy"] as? [String] ?? []
        let localID = data["localId"] as? String

        return ChatMessageItem(id: documentID,
                               conversationID: conversationID,
                               senderID: senderID,
                               content: data["content"] as? String ?? "",
                               type: type,
                               mediaURL: mediaURL,
                               sheetMusic: sheetMusic,
                               setlist: setlist,
                               setlistUpdate: setlistUpdate,
                               timestamp: timestamp,
                               deliveryStatus: status,
                               readBy: readBy,
                               localID: localID)
    }

    static func parseSheetMusicAttachment(dictionary: [String: Any], fallbackSongName: String?) -> SheetMusicAttachment? {
        guard let abc = dictionary["abcNotation"] as? String ?? dictionary["abc_notation"] as? String else {
            return nil
        }

        let song = (dictionary["songName"] as? String) ??
            (dictionary["song_name"] as? String) ??
            fallbackSongName ??
            "Unknown"

        let key = (dictionary["key"] as? String) ??
            (dictionary["keySignature"] as? String) ??
            (dictionary["key_signature"] as? String) ??
            Self.detectKey(in: abc)

        let originalKey = dictionary["originalKey"] as? String ?? dictionary["original_key"] as? String
        let transposedTo = dictionary["transposedTo"] as? String ?? dictionary["transposed_to"] as? String
        let confidence = dictionary["confidence"] as? Double
        var sources = dictionary["sources"] as? [String] ?? []
        let musicID = dictionary["musicId"] as? String ?? dictionary["music_id"] as? String
        let sheetMusicURL = dictionary["sheetMusicURL"] as? String ?? dictionary["sheet_music_url"] as? String

        if let sheetMusicURL, !sheetMusicURL.isEmpty, !sources.contains(sheetMusicURL) {
            sources.append(sheetMusicURL)
        }
        let normalizedSources = sources.isEmpty ? nil : sources

        return SheetMusicAttachment(songName: song,
                                    abcNotation: abc,
                                    key: key,
                                    originalKey: originalKey,
                                    transposedTo: transposedTo,
                                    confidence: confidence,
                                    sources: normalizedSources,
                                    musicID: musicID,
                                    sheetMusicURL: sheetMusicURL)
    }

    static func detectKey(in abc: String) -> String {
        guard let line = abc.split(whereSeparator: \.isNewline).first(where: { $0.trimmingCharacters(in: .whitespaces).hasPrefix("K:") }) else {
            return "C"
        }
        let components = line.split(separator: ":", maxSplits: 1, omittingEmptySubsequences: true)
        if components.count == 2 {
            let value = components[1].trimmingCharacters(in: .whitespaces)
            return value.isEmpty ? "C" : value
        }
        return "C"
    }

    static func parseSetlistAttachment(dictionary: [String: Any]) -> SetlistPlanAttachment? {
        guard let setlistID = (dictionary["setlistId"] as? String) ?? (dictionary["setlist_id"] as? String),
              let title = dictionary["title"] as? String else {
            return nil
        }

        let totalDuration = (dictionary["totalDuration"] as? Int) ??
            (dictionary["total_duration"] as? Int) ??
            0

        let confidence = dictionary["confidence"] as? Double
        let designReasoning = dictionary["designReasoning"] as? String ?? dictionary["design_reasoning"] as? String
        let agentContributions = dictionary["agentContributions"] as? [String: String] ??
            dictionary["agent_contributions"] as? [String: String]

        let piecesArray = dictionary["pieces"] as? [[String: Any]] ?? []
        let pieces: [SetlistPieceAttachment] = piecesArray.compactMap { piece in
            let title = piece["title"] as? String ?? "Untitled"
            let composer = piece["composer"] as? String
            let durationValue = piece["durationMinutes"] ?? piece["duration_minutes"]
            let duration: Int?
            if let intValue = durationValue as? Int {
                duration = intValue
            } else if let doubleValue = durationValue as? Double {
                duration = Int(doubleValue.rounded())
            } else if let stringValue = durationValue as? String, let intFromString = Int(stringValue) {
                duration = intFromString
            } else {
                duration = nil
            }
            let difficulty = piece["difficultyLevel"] as? String ?? piece["difficulty_level"] as? String
            let keySignature = piece["keySignature"] as? String ?? piece["key_signature"] as? String
            let instruments = piece["instruments"] as? [String]
            let genre = piece["genre"] as? String
            let reasoning = piece["reasoning"] as? String

            return SetlistPieceAttachment(title: title,
                                          composer: composer,
                                          durationMinutes: duration,
                                          difficultyLevel: difficulty,
                                          keySignature: keySignature,
                                          instruments: instruments,
                                          genre: genre,
                                          reasoning: reasoning)
        }

        return SetlistPlanAttachment(setlistID: setlistID,
                                     title: title,
                                     totalDurationMinutes: totalDuration,
                                     confidence: confidence,
                                     designReasoning: designReasoning,
                                     pieces: pieces,
                                     agentContributions: agentContributions)
    }

    static func parseSetlistUpdate(dictionary: [String: Any]) -> SetlistUpdate? {
        guard let setlistID = dictionary["setlistId"] as? String ?? dictionary["setlist_id"] as? String else {
            return nil
        }

        let action = dictionary["action"] as? String
        let waiting = dictionary["waitingForResponses"] as? Bool ?? dictionary["waiting_for_responses"] as? Bool
        let required = dictionary["requiredResponses"] as? [String] ?? dictionary["required_responses"] as? [String]

        return SetlistUpdate(setlistID: setlistID,
                             action: action,
                             waitingForResponses: waiting,
                             requiredResponses: required)
    }
}
