import Foundation
import Combine
import SwiftData

@MainActor
final class ChatViewModel: ObservableObject {
    @Published private(set) var messages: [ChatMessageItem] = []
    @Published var inputText: String = ""
    @Published private(set) var isSending = false
    @Published private(set) var isUploadingMedia = false
    @Published private(set) var isGeneratingSheetMusic = false
    @Published private(set) var isTranscribingAudio = false
    @Published private(set) var isApplyingSheetEdit = false
    @Published private(set) var isSubmittingSetlistPreference = false
    @Published var errorMessage: String?
    @Published private(set) var presenceStates: [UserPresenceState] = []
    @Published private(set) var typingStatuses: [TypingStatus] = []
    @Published var activeEditContext: MusicEditContext?
    @Published var activeSetlistSession: SetlistSession?

    let conversationID: String
    let currentUserID: String
    let conversationTitle: String
    let isGroupConversation: Bool

    private let messageService: MessageService
    private let storageService: StorageService?
    private let presenceService: PresenceService?
    private let musicSheetService: MusicSheetService?
    private let participantIDs: [String]
    private let participantDetails: [String: ConversationParticipant]
    private let modelContext: ModelContext
    private var listenerToken: MessageListeningToken?
    private var presenceListener: PresenceListeningToken?
    private var typingListener: PresenceListeningToken?
    private var typingTask: Task<Void, Never>?
    private var isTypingActive = false

    init(conversationID: String,
         currentUserID: String,
         messageService: MessageService,
         storageService: StorageService?,
         presenceService: PresenceService?,
         musicSheetService: MusicSheetService?,
         participantIDs: [String],
         participantDetails: [String: ConversationParticipant],
         isGroupConversation: Bool,
         conversationTitle: String,
         modelContext: ModelContext) {
        self.conversationID = conversationID
        self.currentUserID = currentUserID
        self.messageService = messageService
        self.storageService = storageService
        self.presenceService = presenceService
        self.musicSheetService = musicSheetService
        self.participantIDs = participantIDs
        self.participantDetails = participantDetails
        self.isGroupConversation = isGroupConversation
        self.conversationTitle = conversationTitle
        self.modelContext = modelContext

        loadLocalMessages()
        startListening()
        observePresence()
        observeTyping()
    }

    private func uploadImageMessage(data: Data, localID: String) async {
        guard let storageService else {
            isUploadingMedia = false
            return
        }

        do {
            guard let processed = ImageCompressor.prepareImageData(data) else {
                throw NSError(domain: "Chat", code: 0, userInfo: [
                    NSLocalizedDescriptionKey: "Unable to process the selected image."
                ])
            }

            let remoteURL = try await storageService.uploadImage(data: processed,
                                                                 conversationID: conversationID,
                                                                 fileName: "\(localID).jpg",
                                                                 contentType: "image/jpeg")

            let remote = try await messageService.sendMessage(to: conversationID,
                                                              content: "Photo",
                                                              type: .image,
                                                              localID: localID,
                                                              metadata: ["mediaURL": remoteURL.absoluteString])
            try updateLocalMessage(localID: localID, with: remote)
        } catch {
            errorMessage = error.localizedDescription
            try? markMessageFailed(localID: localID)
        }

        isUploadingMedia = false
    }

    deinit {
        listenerToken?.stop()
        presenceListener?.stop()
        typingListener?.stop()
        typingTask?.cancel()
        Task { [presenceService, conversationID] in
            try? await presenceService?.setTypingState(conversationID: conversationID, isTyping: false)
        }
    }

    func sendTextMessage() {
        let trimmed = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        let localID = UUID().uuidString
        inputText = ""
        typingTask?.cancel()
        if isTypingActive {
            Task { [presenceService, conversationID] in
                try? await presenceService?.setTypingState(conversationID: conversationID, isTyping: false)
            }
            isTypingActive = false
        }

        do {
            try insertLocalMessage(localID: localID,
                                   content: trimmed,
                                   type: .text,
                                   mediaURL: nil,
                                   sheetMusic: nil)
        } catch {
            errorMessage = error.localizedDescription
        }

        Task {
            await sendMessage(content: trimmed,
                              type: .text,
                              localID: localID,
                              metadata: nil)
        }
    }

    func sendImageMessage(with data: Data) {
        guard storageService != nil else {
            errorMessage = "Image uploads are unavailable."
            return
        }
        guard !isUploadingMedia else { return }

        let localID = UUID().uuidString

        do {
            try insertLocalMessage(localID: localID,
                                   content: "Photo",
                                   type: .image,
                                   mediaURL: nil,
                                   sheetMusic: nil)
        } catch {
            errorMessage = error.localizedDescription
            return
        }

        isUploadingMedia = true

        Task { [weak self] in
            guard let self else { return }
            await self.uploadImageMessage(data: data, localID: localID)
        }
    }

    func submitMusicRequest() {
        let trimmed = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        generateSheetMusic(requestText: trimmed)
    }

    func beginEditingSheetMusic(for message: ChatMessageItem) {
        guard let attachment = message.sheetMusic else { return }
        let title = attachment.songName.isEmpty ? message.content : attachment.songName
        activeEditContext = MusicEditContext(sourceMessageID: message.id,
                                             songName: title.isEmpty ? "Untitled" : title,
                                             originalAttachment: attachment)
        inputText = ""
    }

    func cancelSheetMusicEditing() {
        activeEditContext = nil
        inputText = ""
    }

    func needsSetlistResponse(for userID: String) -> Bool {
        activeSetlistSession?.needsResponse(for: userID) ?? false
    }

    func resetActiveEditContextToOriginal() {
        guard let context = activeEditContext, context.hasChangesFromOriginal else { return }

        isApplyingSheetEdit = true

        Task { [weak self] in
            guard let self else { return }
            let originalAttachment = context.originalAttachment
            let songName = context.songName
            let messageID = context.sourceMessageID

            defer {
                Task { @MainActor in
                    self.isApplyingSheetEdit = false
                }
            }

            do {
                try await MainActor.run {
                    guard var latest = self.activeEditContext else { return }
                    latest.workingAttachment = originalAttachment
                    latest.history.insert(.init(instruction: "Reverted to original notation."),
                                          at: 0)
                    self.activeEditContext = latest
                    try self.updateLocalSheetMusicMessage(messageID: messageID,
                                                          newContent: songName,
                                                          newAttachment: originalAttachment)
                }

                let metadata: [String: Any] = [
                    "sheetMusic": Self.makeSheetMusicMetadataDictionary(from: originalAttachment),
                    "editInstruction": "Reverted to original notation.",
                    "sourceMessageId": messageID,
                    "aiService": "music_edit",
                    "routingIntent": "music_editing"
                ]

                let remote = try await self.messageService.updateMessage(in: self.conversationID,
                                                                          messageID: messageID,
                                                                          content: songName,
                                                                          type: .sheetMusic,
                                                                          metadata: metadata)

                try await MainActor.run {
                    try self.replaceLocalMessage(remoteID: messageID, with: remote)
                }
            } catch {
                await MainActor.run {
                    self.errorMessage = error.localizedDescription
                    self.activeEditContext = context
                    try? self.updateLocalSheetMusicMessage(messageID: messageID,
                                                           newContent: songName,
                                                           newAttachment: context.currentAttachment)
                }
            }
        }
    }

    func submitEditInstruction(_ instruction: String) {
        let trimmed = instruction.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        guard let context = activeEditContext else {
            errorMessage = "No sheet music selected for editing."
            return
        }
        guard let musicSheetService else {
            errorMessage = "Sheet music service is not configured."
            return
        }
        guard !isApplyingSheetEdit else { return }

        inputText = ""
        isApplyingSheetEdit = true
        let currentAttachment = context.currentAttachment
        let songName = context.songName
        let sourceMessageID = context.sourceMessageID

        Task { [weak self] in
            guard let self else { return }
            defer {
                Task { @MainActor in
                    self.isApplyingSheetEdit = false
                }
            }

            do {
                let response = try await musicSheetService.editMelody(abcNotation: currentAttachment.abcNotation,
                                                                      instruction: trimmed)
                var combinedSources = response.sources ?? currentAttachment.sources ?? []
                if let sheetURL = (response.sheetMusicURL ?? currentAttachment.sheetMusicURL), !sheetURL.isEmpty, !combinedSources.contains(sheetURL) {
                    combinedSources.append(sheetURL)
                }
                let normalizedSources = combinedSources.isEmpty ? nil : combinedSources

                let updatedAttachment = SheetMusicAttachment(songName: songName,
                                                             abcNotation: response.abcNotation.isEmpty ? currentAttachment.abcNotation : response.abcNotation,
                                                             key: response.key.isEmpty ? currentAttachment.key : response.key,
                                                             originalKey: response.originalKey ?? currentAttachment.originalKey,
                                                             transposedTo: response.transposedTo ?? currentAttachment.transposedTo,
                                                             confidence: response.confidence ?? currentAttachment.confidence,
                                                             sources: normalizedSources,
                                                             musicID: response.musicID ?? currentAttachment.musicID,
                                                             sheetMusicURL: response.sheetMusicURL ?? currentAttachment.sheetMusicURL)
                let historyEntry = MusicEditContext.HistoryEntry(instruction: trimmed,
                                                                 resultingKey: updatedAttachment.key,
                                                                 notes: response.status == "success" ? nil : response.status)

                try await MainActor.run {
                    guard var latest = self.activeEditContext else { return }
                    latest.workingAttachment = updatedAttachment
                    latest.history.insert(historyEntry, at: 0)
                    self.activeEditContext = latest
                    try self.updateLocalSheetMusicMessage(messageID: sourceMessageID,
                                                          newContent: songName,
                                                          newAttachment: updatedAttachment)
                }

                let metadata: [String: Any] = [
                    "sheetMusic": Self.makeSheetMusicMetadataDictionary(from: updatedAttachment),
                    "editInstruction": trimmed,
                    "sourceMessageId": sourceMessageID,
                    "aiService": "music_edit",
                    "routingIntent": "music_editing"
                ]

                do {
                    let remote = try await self.messageService.updateMessage(in: self.conversationID,
                                                                             messageID: sourceMessageID,
                                                                             content: songName,
                                                                             type: .sheetMusic,
                                                                             metadata: metadata)
                    try await MainActor.run {
                        try self.replaceLocalMessage(remoteID: sourceMessageID, with: remote)
                    }
                } catch {
                    await MainActor.run {
                        self.errorMessage = error.localizedDescription
                        if var latest = self.activeEditContext {
                            if !latest.history.isEmpty {
                                latest.history.removeFirst()
                            }
                            latest.workingAttachment = currentAttachment
                            self.activeEditContext = latest
                            try? self.updateLocalSheetMusicMessage(messageID: sourceMessageID,
                                                                   newContent: songName,
                                                                   newAttachment: currentAttachment)
                        }
                    }
                }
            } catch {
                await MainActor.run {
                    self.errorMessage = error.localizedDescription
                }
            }
        }
    }

    func transcribeAudioSnippet(audioData: Data, format: String) {
        guard !audioData.isEmpty else { return }

        guard let musicSheetService else {
            errorMessage = "Sheet music service is not configured."
            return
        }

        guard !isTranscribingAudio else { return }

        errorMessage = nil

        let requestLocalID = UUID().uuidString
        let requestContent = Self.audioRequestMessage()

        do {
            try insertLocalMessage(localID: requestLocalID,
                                   content: requestContent,
                                   type: .musicRequest,
                                   mediaURL: nil,
                                   sheetMusic: nil)
        } catch {
            errorMessage = error.localizedDescription
            return
        }

        isTranscribingAudio = true

        Task { [weak self] in
            guard let self else { return }
            do {
                let remote = try await self.messageService.sendMessage(to: self.conversationID,
                                                                       content: requestContent,
                                                                       type: .musicRequest,
                                                                       localID: requestLocalID,
                                                                       metadata: [
                                                                           "requestType": "audio_transcription",
                                                                           "audioFormat": format
                                                                       ])
                try await MainActor.run {
                    try self.updateLocalMessage(localID: requestLocalID, with: remote)
                }
            } catch {
                await MainActor.run {
                    self.errorMessage = error.localizedDescription
                    try? self.markMessageFailed(localID: requestLocalID)
                    self.isTranscribingAudio = false
                }
            }
        }

        let resultLocalID = UUID().uuidString

        Task { [weak self] in
            guard let self else { return }
            defer {
                Task { @MainActor in
                    self.isTranscribingAudio = false
                }
            }

            do {
                let response = try await musicSheetService.transcribeAudio(audioData: audioData,
                                                                           format: format)

                var combinedSources = response.sources ?? []
                if let sheetURL = response.sheetMusicURL, !sheetURL.isEmpty, !combinedSources.contains(sheetURL) {
                    combinedSources.append(sheetURL)
                }
                let normalizedSources = combinedSources.isEmpty ? nil : combinedSources

                let attachment = SheetMusicAttachment(songName: Self.audioTranscriptionTitle(),
                                                      abcNotation: response.abcNotation,
                                                      key: response.key,
                                                      originalKey: response.originalKey,
                                                      transposedTo: response.transposedTo,
                                                      confidence: response.confidence,
                                                      sources: normalizedSources,
                                                      musicID: response.musicID,
                                                      sheetMusicURL: response.sheetMusicURL)

                try await MainActor.run {
                    try self.insertLocalMessage(localID: resultLocalID,
                                                content: attachment.songName,
                                                type: .sheetMusic,
                                                mediaURL: nil,
                                                sheetMusic: attachment)
                }

                var metadata: [String: Any] = [
                    "sheetMusic": Self.makeSheetMusicMetadataDictionary(from: attachment),
                    "requestType": "audio_transcription"
                ]

                metadata["audioFormat"] = format
                metadata["aiService"] = "audio_transcription"

                await self.sendMessage(content: attachment.songName,
                                       type: .sheetMusic,
                                       localID: resultLocalID,
                                       metadata: metadata)
            } catch {
                await MainActor.run {
                    self.errorMessage = error.localizedDescription
                }
            }
        }
    }

    private func generateSheetMusic(requestText: String) {
        let trimmed = requestText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }

        guard let musicSheetService else {
            errorMessage = "Sheet music service is not configured."
            return
        }

        if isGeneratingSheetMusic { return }

        inputText = ""
        errorMessage = nil
        let requestLocalID = UUID().uuidString
        let requestContent = Self.musicRequestMessage(for: trimmed)

        do {
            try insertLocalMessage(localID: requestLocalID,
                                   content: requestContent,
                                   type: .musicRequest,
                                   mediaURL: nil,
                                   sheetMusic: nil)
        } catch {
            errorMessage = error.localizedDescription
            return
        }

        Task { [weak self] in
            guard let self else { return }
            do {
                let remote = try await self.messageService.sendMessage(to: self.conversationID,
                                                                       content: requestContent,
                                                                       type: .musicRequest,
                                                                       localID: requestLocalID,
                                                                       metadata: [
                                                                           "requestType": "sheet_music",
                                                                           "rawRequest": trimmed
                                                                       ])
                try await MainActor.run {
                    try self.updateLocalMessage(localID: requestLocalID, with: remote)
                }
            } catch {
                await MainActor.run {
                    self.errorMessage = error.localizedDescription
                    try? self.markMessageFailed(localID: requestLocalID)
                }
            }
        }

        isGeneratingSheetMusic = true
        let localID = UUID().uuidString

        Task { [weak self] in
            guard let self else { return }
            defer {
                Task { @MainActor in
                    self.isGeneratingSheetMusic = false
                }
            }

            do {
                let result = try await musicSheetService.routeAndExecute(userInput: trimmed,
                                                                         userID: currentUserID,
                                                                         conversationID: conversationID)
                switch result {
                case .abc(let response):
                    var combinedSources = response.sources ?? []
                    if let sheetURL = response.sheetMusicURL, !sheetURL.isEmpty, !combinedSources.contains(sheetURL) {
                        combinedSources.append(sheetURL)
                    }
                    let normalizedSources = combinedSources.isEmpty ? nil : combinedSources

                    let attachment = SheetMusicAttachment(songName: trimmed,
                                                          abcNotation: response.abcNotation,
                                                          key: response.key,
                                                          originalKey: response.originalKey,
                                                          transposedTo: response.transposedTo,
                                                          confidence: response.confidence,
                                                          sources: normalizedSources,
                                                          musicID: response.musicID,
                                                          sheetMusicURL: response.sheetMusicURL)

                    try await MainActor.run {
                        try self.insertLocalMessage(localID: localID,
                                                    content: trimmed,
                                                    type: .sheetMusic,
                                                    mediaURL: nil,
                                                    sheetMusic: attachment)
                    }

                    let metadata: [String: Any] = [
                        "sheetMusic": Self.makeSheetMusicMetadataDictionary(from: attachment),
                        "aiService": "music_generation",
                        "routingIntent": "music_generation"
                    ]

                    await self.sendMessage(content: trimmed,
                                           type: .sheetMusic,
                                           localID: localID,
                                           metadata: metadata)

                case .pdf(let classical):
                    guard let pdfURL = URL(string: classical.pdfURL) else {
                        throw MusicSheetServiceError.decodingFailed
                    }

                    let pdfTitle = Self.classicalTitle(for: classical)

                    try await MainActor.run {
                        try self.insertLocalMessage(localID: localID,
                                                    content: pdfTitle,
                                                    type: .pdf,
                                                    mediaURL: pdfURL,
                                                    sheetMusic: nil)
                    }

                    var metadata: [String: Any] = [
                        "mediaURL": classical.pdfURL,
                        "aiService": "imslp_search",
                        "routingIntent": "classical_lookup"
                    ]
                    if let composer = classical.composer {
                        metadata["composer"] = composer
                    }
                    if let description = classical.description {
                        metadata["description"] = description
                    }
                    if let sources = classical.sources {
                        metadata["sources"] = sources
                    }

                    await self.sendMessage(content: pdfTitle,
                                           type: .pdf,
                                           localID: localID,
                                           metadata: metadata)

                case .setlist:
                    await self.startCollaborativeSetlistSession(requestText: trimmed)
                }
            } catch {
                await MainActor.run {
                    self.errorMessage = error.localizedDescription
                }
            }
        }
    }

    private func startCollaborativeSetlistSession(requestText: String) async {
        guard let musicSheetService else {
            await MainActor.run {
                self.errorMessage = "Sheet music service is not configured."
            }
            return
        }

        let organizerName = participantDetails[currentUserID]?.displayName?.trimmingCharacters(in: .whitespacesAndNewlines)
        let fallbackUsername = participantDetails[currentUserID]?.username?.trimmingCharacters(in: .whitespacesAndNewlines)
        let resolvedOrganizerName = (organizerName?.isEmpty == false ? organizerName : nil) ??
            (fallbackUsername?.isEmpty == false ? fallbackUsername : nil) ??
            currentUserID

        let requestPayload = ChatSetlistStartRequestPayload(userInput: requestText,
                                                             groupID: conversationID,
                                                             conversationID: conversationID,
                                                             organizerUserID: currentUserID,
                                                             organizerUsername: resolvedOrganizerName,
                                                             groupMemberIDs: participantIDs)

        do {
            let response = try await musicSheetService.startCollaborativeSetlist(request: requestPayload)
            let context = try await MainActor.run { try self.prepareSetlistStart(response: response) }
            await self.sendMessage(content: response.message,
                                   type: .musicRequest,
                                   localID: context.localID,
                                   metadata: context.metadata)

            if let plan = response.setlistData {
                let finalContext = try await MainActor.run { try self.prepareFinalSetlistMessage(from: plan) }
                await self.sendMessage(content: finalContext.content,
                                       type: .setlist,
                                       localID: finalContext.localID,
                                       metadata: finalContext.metadata)
            }
        } catch {
            await MainActor.run {
                self.errorMessage = error.localizedDescription
            }
        }
    }

    private func loadLocalMessages() {
        let descriptor = FetchDescriptor<Message>(
            predicate: #Predicate { $0.conversation?.remoteID == conversationID },
            sortBy: [SortDescriptor(\.timestamp, order: .forward)]
        )

        if let stored = try? modelContext.fetch(descriptor) {
            messages = stored.map {
                ChatMessageItem(id: $0.remoteID,
                                conversationID: conversationID,
                                senderID: $0.senderUserID,
                                content: $0.content,
                                type: $0.contentType,
                                mediaURL: $0.mediaURL,
                                sheetMusic: $0.sheetMusic,
                                setlist: $0.setlist,
                                setlistUpdate: $0.setlistUpdate,
                                timestamp: $0.timestamp,
                                deliveryStatus: $0.deliveryStatus,
                                readBy: $0.readByUserIDs,
                                localID: $0.localID)
            }
            updateSetlistSessionFromMessages()
        }
    }

    private func startListening() {
        listenerToken?.stop()
        listenerToken = messageService.listenForMessages(in: conversationID) { [weak self] items in
            guard let self else { return }
            Task { @MainActor in
                do {
                    try self.syncLocalMessages(with: items)
                    self.loadLocalMessages()
                } catch {
                    self.errorMessage = error.localizedDescription
                }
            }
        } onError: { [weak self] error in
            Task { @MainActor in
                self?.errorMessage = error.localizedDescription
            }
        }
    }

    private func insertLocalMessage(localID: String,
                                    content: String,
                                    type: MessageContentType,
                                    mediaURL: URL?,
                                    sheetMusic: SheetMusicAttachment?,
                                    setlist: SetlistPlanAttachment? = nil,
                                    setlistUpdate: SetlistUpdate? = nil) throws {
        guard let conversation = try fetchConversation() else { return }
        let message = Message(remoteID: localID,
                              localID: localID,
                              conversation: conversation,
                              senderUserID: currentUserID,
                              content: content,
                              contentType: type,
                              mediaURL: mediaURL,
                              sheetMusic: sheetMusic,
                              setlist: setlist,
                              setlistUpdate: setlistUpdate,
                              timestamp: Date(),
                              deliveryStatus: .sending,
                              readByUserIDs: [currentUserID])
        modelContext.insert(message)
        try modelContext.save()
        loadLocalMessages()
    }

    private func sendMessage(content: String,
                             type: MessageContentType,
                             localID: String,
                             metadata: [String: Any]?) async {
        await MainActor.run { self.isSending = true }

        if isTypingActive {
            Task { [presenceService, conversationID] in
                try? await presenceService?.setTypingState(conversationID: conversationID, isTyping: false)
            }
            isTypingActive = false
        }

        do {
            let remote = try await messageService.sendMessage(to: conversationID,
                                                              content: content,
                                                              type: type,
                                                              localID: localID,
                                                              metadata: metadata)
            try updateLocalMessage(localID: localID, with: remote)
        } catch {
            errorMessage = error.localizedDescription
            try? markMessageFailed(localID: localID)
        }
        await MainActor.run { self.isSending = false }
    }

    @MainActor
    private func updateSetlistSessionFromMessages() {
        if messages.contains(where: { $0.type == .setlist }) {
            activeSetlistSession = nil
            return
        }

        guard let latestUpdate = messages.last(where: { $0.setlistUpdate != nil })?.setlistUpdate else {
            return
        }

        if var session = activeSetlistSession, session.setlistID == latestUpdate.setlistID {
            session.update(requiredResponses: latestUpdate.requiredResponses,
                           waitingForResponses: latestUpdate.waitingForResponses,
                           respondedUserID: nil)
            activeSetlistSession = session
        } else if let required = latestUpdate.requiredResponses {
            var session = SetlistSession(setlistID: latestUpdate.setlistID,
                                         pendingResponders: Set(required),
                                         responded: [],
                                         waitingForResponses: latestUpdate.waitingForResponses ?? true,
                                         organizerID: currentUserID,
                                         questions: nil)
            activeSetlistSession = session
        }
    }

    @MainActor
    private func prepareSetlistStart(response: ChatSetlistResponsePayload) throws -> (localID: String, metadata: [String: Any]) {
        let localID = UUID().uuidString
        let update = response.toSetlistUpdate()

        try insertLocalMessage(localID: localID,
                               content: response.message,
                               type: .musicRequest,
                               mediaURL: nil,
                               sheetMusic: nil,
                               setlist: nil,
                               setlistUpdate: update)

        updateSetlistSession(with: response, respondedUserID: nil, questions: response.questions)

        let metadata = Self.makeSetlistMessageMetadata(from: response)
        return (localID, metadata)
    }

    @MainActor
    private func prepareSetlistFollowup(response: ChatSetlistResponsePayload, respondedUserID: String?) throws -> (localID: String, metadata: [String: Any]) {
        let localID = UUID().uuidString
        let update = response.toSetlistUpdate()

        let messageText = formattedSetlistMessage(for: response, respondedUserID: respondedUserID)

        try insertLocalMessage(localID: localID,
                               content: messageText,
                               type: .musicRequest,
                               mediaURL: nil,
                               sheetMusic: nil,
                               setlist: nil,
                               setlistUpdate: update)

        updateSetlistSession(with: response, respondedUserID: respondedUserID, questions: nil)

        let metadata = Self.makeSetlistMessageMetadata(from: response)
        return (localID, metadata)
    }

    private func formattedSetlistMessage(for response: ChatSetlistResponsePayload,
                                         respondedUserID: String?) -> String {
        guard response.action == "waiting_for_responses" else {
            return response.message
        }

        let responderName = respondedUserID.flatMap { nameOrHandle(for: $0) } ?? "Someone"
        let remaining = (response.requiredResponses ?? [])
            .filter { $0 != respondedUserID }
            .map { nameOrHandle(for: $0) }

        if remaining.isEmpty {
            return "Thanks \(responderName)! All responses are in."
        }

        return "Thanks \(responderName)! Still waiting for responses from: \(remaining.joined(separator: ", "))"
    }

    @MainActor
    private func prepareFinalSetlistMessage(from response: SetlistPlanResponse) throws -> (content: String, localID: String, metadata: [String: Any]) {
        let fallbackID = activeSetlistSession?.setlistID ?? response.setlistID ?? UUID().uuidString
        let attachment = Self.makeSetlistAttachment(from: response, fallbackID: fallbackID)
        let localID = UUID().uuidString

        try insertLocalMessage(localID: localID,
                               content: attachment.title,
                               type: .setlist,
                               mediaURL: nil,
                               sheetMusic: nil,
                               setlist: attachment,
                               setlistUpdate: SetlistUpdate(setlistID: attachment.setlistID,
                                                            action: "setlist_complete",
                                                            waitingForResponses: false,
                                                            requiredResponses: []))

        activeSetlistSession = nil

        let metadata: [String: Any] = [
            "setlist": Self.makeSetlistMetadataDictionary(from: attachment),
            "aiService": "setlist_design",
            "routingIntent": "setlist_design",
            "setlistUpdate": Self.makeSetlistUpdateDictionary(setlistID: attachment.setlistID,
                                                              action: "setlist_complete",
                                                              waitingForResponses: false,
                                                              requiredResponses: [])
        ]

        return (attachment.title, localID, metadata)
    }

    func submitSetlistPreferenceFromInput() {
        let trimmed = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        guard let session = activeSetlistSession,
              session.pendingResponders.contains(currentUserID) else {
            return
        }
        guard let musicSheetService else {
            errorMessage = "Sheet music service is not configured."
            return
        }
        guard let username = participantDetails[currentUserID]?.displayName ?? participantDetails[currentUserID]?.username else {
            errorMessage = "Unable to determine your display name for the setlist response."
            return
        }

        let preferenceText = trimmed
        inputText = preferenceText
        sendTextMessage()
        submitSetlistPreference(preferenceText: preferenceText,
                                session: session,
                                username: username,
                                service: musicSheetService)
    }

    private func submitSetlistPreference(preferenceText: String,
                                         session: SetlistSession,
                                         username: String,
                                         service: MusicSheetService) {
        guard !isSubmittingSetlistPreference else { return }

        let timestamp = ISO8601DateFormatter().string(from: Date())
        let requestPayload = ChatSetlistPreferencePayload(setlistID: session.setlistID,
                                                          userID: currentUserID,
                                                          username: username,
                                                          preferenceText: preferenceText,
                                                          responseTimestamp: timestamp)

        isSubmittingSetlistPreference = true

        Task { [weak self] in
            guard let self else { return }
            do {
                let response = try await service.submitSetlistPreferences(request: requestPayload)
                let context = try await MainActor.run { try self.prepareSetlistFollowup(response: response, respondedUserID: self.currentUserID) }
                await self.sendMessage(content: response.message,
                                       type: .musicRequest,
                                       localID: context.localID,
                                       metadata: context.metadata)

                if let plan = response.setlistData {
                    do {
                        let finalContext = try await MainActor.run { try self.prepareFinalSetlistMessage(from: plan) }
                        await self.sendMessage(content: finalContext.content,
                                               type: .setlist,
                                               localID: finalContext.localID,
                                               metadata: finalContext.metadata)
                    } catch {
                        await MainActor.run {
                            self.errorMessage = error.localizedDescription
                        }
                    }
                }
            } catch {
                await MainActor.run {
                    self.errorMessage = error.localizedDescription
                }
            }

            await MainActor.run {
                self.isSubmittingSetlistPreference = false
            }
        }
    }

    func handleInputChange(_ text: String) {
        typingTask?.cancel()
        guard let presenceService else { return }
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)

        if trimmed.isEmpty {
            if isTypingActive {
                typingTask = Task { [conversationID, weak self] in
                    try? await presenceService.setTypingState(conversationID: conversationID, isTyping: false)
                    await MainActor.run { self?.isTypingActive = false }
                }
            }
            return
        }

        typingTask = Task { [conversationID, weak self] in
            guard let self else { return }
            if !self.isTypingActive {
                try? await presenceService.setTypingState(conversationID: conversationID, isTyping: true)
                await MainActor.run { self.isTypingActive = true }
            }

            try? await Task.sleep(nanoseconds: 5_000_000_000)
            if Task.isCancelled { return }
            try? await presenceService.setTypingState(conversationID: conversationID, isTyping: false)
            await MainActor.run { self.isTypingActive = false }
        }
    }

    var presenceStatusText: String {
        let others = participantIDs.filter { $0 != currentUserID }
        guard !others.isEmpty else { return "" }

        let states = presenceStates.filter { others.contains($0.userID) }
        if others.count == 1, let userID = others.first,
           let state = states.first(where: { $0.userID == userID }) {
            if state.isOnline { return "Online" }
            if let lastSeen = state.lastSeen {
                return "Last seen " + Self.relativeFormatter.localizedString(for: lastSeen, relativeTo: Date())
            }
            return "Offline"
        }

        let onlineCount = states.filter { $0.isOnline }.count
        if onlineCount == 0 { return "No one online" }
        if onlineCount == states.count { return "All online" }
        return "\(onlineCount) online"
    }

    var typingIndicatorText: String? {
        let active = typingStatuses.filter { $0.isTyping }
        guard !active.isEmpty else { return nil }

        let others = participantIDs.filter { $0 != currentUserID }
        if others.count <= 1 {
            return "Typing..."
        }

        let names = active.compactMap { status -> String? in
            guard let info = participantDetails[status.userID] else { return nil }
            if let displayName = info.displayName, !displayName.isEmpty {
                return displayName
            }
            if let username = info.username, !username.isEmpty {
                return "@\(username)"
            }
            return nil
        }

        if names.count == 1 {
            return "\(names[0]) is typing..."
        }
        if names.count == 2 {
            return "\(names[0]) and \(names[1]) are typing..."
        }
        return "Multiple people typing..."
    }

    private func updateLocalMessage(localID: String, with remote: ChatMessageItem) throws {
        let descriptor = FetchDescriptor<Message>(
            predicate: #Predicate { $0.localID == localID && $0.conversation?.remoteID == conversationID }
        )
        guard let message = try modelContext.fetch(descriptor).first else {
            return
        }

        message.remoteID = remote.id
        message.content = remote.content
        message.contentType = remote.type
        message.mediaURL = remote.mediaURL
        message.sheetMusic = remote.sheetMusic
        message.setlist = remote.setlist
        message.setlistUpdate = remote.setlistUpdate
        message.timestamp = remote.timestamp
        message.deliveryStatus = remote.deliveryStatus
        message.readByUserIDs = remote.readBy
        try modelContext.save()
        loadLocalMessages()

        if activeEditContext == nil,
           remote.type == .sheetMusic,
           let attachment = remote.sheetMusic {
            let title = attachment.songName.isEmpty ? remote.content : attachment.songName
            activeEditContext = MusicEditContext(sourceMessageID: remote.id,
                                                 songName: title.isEmpty ? "Untitled" : title,
                                                 originalAttachment: attachment)
        }
    }

    private func markMessageFailed(localID: String) throws {
        let descriptor = FetchDescriptor<Message>(
            predicate: #Predicate { $0.localID == localID && $0.conversation?.remoteID == conversationID }
        )
        if let message = try modelContext.fetch(descriptor).first {
            message.deliveryStatus = .sending
            try modelContext.save()
            loadLocalMessages()
        }
    }

    private func syncLocalMessages(with remote: [ChatMessageItem]) throws {
        let descriptor = FetchDescriptor<Message>(
            predicate: #Predicate { $0.conversation?.remoteID == conversationID }
        )
        let stored = try modelContext.fetch(descriptor)

        var storedByRemoteID = Dictionary(uniqueKeysWithValues: stored.map { ($0.remoteID, $0) })
        let storedByLocalID = Dictionary(grouping: stored.filter { $0.localID != nil }, by: { $0.localID! })

        let remoteIDs = Set(remote.map(\.id))

        for item in remote {
            if let existing = storedByRemoteID.removeValue(forKey: item.id) {
                existing.content = item.content
                existing.contentType = item.type
                existing.timestamp = item.timestamp
                existing.deliveryStatus = item.deliveryStatus
                existing.readByUserIDs = item.readBy
                existing.mediaURL = item.mediaURL
                existing.sheetMusic = item.sheetMusic
                existing.setlist = item.setlist
                existing.setlistUpdate = item.setlistUpdate
                existing.senderUserID = item.senderID
            } else if let localID = item.localID,
                      let localExisting = storedByLocalID[localID]?.first {
                storedByRemoteID[localExisting.remoteID] = nil
                localExisting.remoteID = item.id
                localExisting.content = item.content
                localExisting.contentType = item.type
                localExisting.timestamp = item.timestamp
                localExisting.deliveryStatus = item.deliveryStatus
                localExisting.readByUserIDs = item.readBy
                localExisting.mediaURL = item.mediaURL
                localExisting.sheetMusic = item.sheetMusic
                localExisting.setlist = item.setlist
                localExisting.setlistUpdate = item.setlistUpdate
                localExisting.senderUserID = item.senderID
            } else {
                guard let conversation = try fetchConversation() else { continue }
                let newMessage = Message(remoteID: item.id,
                                         localID: item.localID,
                                         conversation: conversation,
                                         senderUserID: item.senderID,
                                         content: item.content,
                                         contentType: item.type,
                                         mediaURL: item.mediaURL,
                                         sheetMusic: item.sheetMusic,
                                         setlist: item.setlist,
                                         setlistUpdate: item.setlistUpdate,
                                         timestamp: item.timestamp,
                                         deliveryStatus: item.deliveryStatus,
                                         readByUserIDs: item.readBy)
                modelContext.insert(newMessage)
            }
        }

        for orphan in storedByRemoteID.values where !remoteIDs.contains(orphan.remoteID) {
            // Keep optimistic messages (likely sending). Don't delete for now.
            continue
        }

        try modelContext.save()

        if let context = activeEditContext,
           !remoteIDs.contains(context.sourceMessageID) {
            activeEditContext = nil
        }
    }

    private func updateLocalSheetMusicMessage(messageID: String,
                                             newContent: String,
                                             newAttachment: SheetMusicAttachment) throws {
        let descriptor = FetchDescriptor<Message>(
            predicate: #Predicate { $0.remoteID == messageID && $0.conversation?.remoteID == conversationID }
        )

        if let message = try modelContext.fetch(descriptor).first {
            message.content = newContent
            message.contentType = .sheetMusic
            message.mediaURL = nil
            message.sheetMusic = newAttachment
            try modelContext.save()
        }

        loadLocalMessages()
    }

    private func replaceLocalMessage(remoteID: String, with item: ChatMessageItem) throws {
        let descriptor = FetchDescriptor<Message>(
            predicate: #Predicate { $0.remoteID == remoteID && $0.conversation?.remoteID == conversationID }
        )

        if let message = try modelContext.fetch(descriptor).first {
            message.content = item.content
            message.contentType = item.type
            message.mediaURL = item.mediaURL
            message.sheetMusic = item.sheetMusic
            message.setlist = item.setlist
            message.timestamp = item.timestamp
            message.deliveryStatus = item.deliveryStatus
            message.readByUserIDs = item.readBy
            try modelContext.save()
        }

        loadLocalMessages()
    }

    private static func makeSheetMusicMetadataDictionary(from attachment: SheetMusicAttachment) -> [String: Any] {
        var dictionary: [String: Any] = [
            "songName": attachment.songName,
            "abcNotation": attachment.abcNotation,
            "key": attachment.key
        ]

        if let original = attachment.originalKey {
            dictionary["originalKey"] = original
        }

        if let transposed = attachment.transposedTo {
            dictionary["transposedTo"] = transposed
        }

        if let confidence = attachment.confidence {
            dictionary["confidence"] = confidence
        }

        if let sources = attachment.sources {
            dictionary["sources"] = sources
        }

        if let musicID = attachment.musicID {
            dictionary["musicId"] = musicID
            dictionary["music_id"] = musicID
        }

        if let sheetMusicURL = attachment.sheetMusicURL {
            dictionary["sheetMusicURL"] = sheetMusicURL
            dictionary["sheet_music_url"] = sheetMusicURL
        }

        return dictionary
    }

    private static func makeSetlistAttachment(from response: SetlistPlanResponse,
                                              fallbackID: String?) -> SetlistPlanAttachment {
        let identifier = response.setlistID ?? fallbackID ?? UUID().uuidString
        let pieces = response.pieces.map {
            SetlistPieceAttachment(title: $0.title,
                                   composer: $0.composer,
                                   durationMinutes: $0.durationMinutes,
                                   difficultyLevel: $0.difficultyLevel,
                                   keySignature: $0.keySignature,
                                   instruments: $0.instruments,
                                   genre: $0.genre,
                                   reasoning: $0.reasoning)
        }

        return SetlistPlanAttachment(setlistID: identifier,
                                     title: response.title,
                                     totalDurationMinutes: response.totalDuration,
                                     confidence: response.confidence,
                                     designReasoning: response.designReasoning,
                                     pieces: pieces,
                                     agentContributions: response.agentContributions)
    }

    private static func makeSetlistMetadataDictionary(from attachment: SetlistPlanAttachment) -> [String: Any] {
        var dictionary: [String: Any] = [
            "setlistId": attachment.setlistID,
            "title": attachment.title,
            "totalDuration": attachment.totalDurationMinutes
        ]

        if let confidence = attachment.confidence {
            dictionary["confidence"] = confidence
        }

        if let reasoning = attachment.designReasoning {
            dictionary["designReasoning"] = reasoning
        }

        if let contributions = attachment.agentContributions {
            dictionary["agentContributions"] = contributions
        }

        let piecesPayload: [[String: Any]] = attachment.pieces.map { piece in
            var pieceDictionary: [String: Any] = [
                "title": piece.title
            ]

            if let composer = piece.composer {
                pieceDictionary["composer"] = composer
            }
            if let duration = piece.durationMinutes {
                pieceDictionary["durationMinutes"] = duration
            }
            if let difficulty = piece.difficultyLevel {
                pieceDictionary["difficultyLevel"] = difficulty
            }
            if let key = piece.keySignature {
                pieceDictionary["keySignature"] = key
            }
            if let instruments = piece.instruments {
                pieceDictionary["instruments"] = instruments
            }
            if let genre = piece.genre {
                pieceDictionary["genre"] = genre
            }
            if let reasoning = piece.reasoning {
                pieceDictionary["reasoning"] = reasoning
            }

            return pieceDictionary
        }

        dictionary["pieces"] = piecesPayload
        return dictionary
    }

    private static func makeSetlistMessageMetadata(from response: ChatSetlistResponsePayload) -> [String: Any] {
        var metadata: [String: Any] = [
            "aiService": "setlist_chat",
            "routingIntent": "setlist_design"
        ]

        if let setlistID = response.setlistID {
            metadata["setlistId"] = setlistID
        }

        if let updateDict = makeSetlistUpdateDictionary(from: response) {
            metadata["setlistUpdate"] = updateDict
        }

        if let setlistData = response.setlistData {
            let attachment = makeSetlistAttachment(from: setlistData,
                                                   fallbackID: response.setlistID)
            metadata["setlist"] = makeSetlistMetadataDictionary(from: attachment)
        }

        return metadata
    }

    private static func makeSetlistUpdateDictionary(from response: ChatSetlistResponsePayload) -> [String: Any]? {
        guard let setlistID = response.setlistID else { return nil }
        return makeSetlistUpdateDictionary(setlistID: setlistID,
                                           action: response.action,
                                           waitingForResponses: response.waitingForResponses,
                                           requiredResponses: response.requiredResponses)
    }

    private static func makeSetlistUpdateDictionary(setlistID: String,
                                                    action: String?,
                                                    waitingForResponses: Bool?,
                                                    requiredResponses: [String]?) -> [String: Any] {
        var dictionary: [String: Any] = [
            "setlistId": setlistID
        ]

        if let action {
            dictionary["action"] = action
        }

        if let waitingForResponses {
            dictionary["waitingForResponses"] = waitingForResponses
        }

        if let requiredResponses {
            dictionary["requiredResponses"] = requiredResponses
        }

        return dictionary
    }

    private static func musicRequestMessage(for songName: String, instrument: String? = nil) -> String {
        if let instrument, !instrument.isEmpty, instrument != "C" {
            return "🎵 Generating \"\(songName)\" (\(instrument))"
        }
        return "🎵 Generating \"\(songName)\""
    }

    private static func audioRequestMessage() -> String {
        "🎙️ Transcribing audio snippet..."
    }

    private static func audioTranscriptionTitle() -> String {
        "Audio transcription"
    }

    private static func classicalTitle(for response: ClassicalSheetResponse) -> String {
        if let composer = response.composer, !composer.isEmpty {
            return "\(response.title) – \(composer)"
        }
        return response.title
    }

    @MainActor
    private func updateSetlistSession(with response: ChatSetlistResponsePayload,
                                      respondedUserID: String?,
                                      questions: ChatSetlistQuestionsResponse?) {
        guard let setlistID = response.setlistID ?? activeSetlistSession?.setlistID else { return }

        var session: SetlistSession

        if var existing = activeSetlistSession, existing.setlistID == setlistID {
            existing.update(requiredResponses: response.requiredResponses,
                             waitingForResponses: response.waitingForResponses,
                             respondedUserID: respondedUserID)
            session = existing
        } else {
            let info = ChatSetlistQuestions(general: questions?.generalQuestions,
                                            concert: questions?.concertSpecificQuestions,
                                            collaboration: questions?.collaborationQuestions)
            session = SetlistSession(setlistID: setlistID,
                                     pendingResponders: Set(response.requiredResponses ?? []),
                                     responded: [],
                                     waitingForResponses: response.waitingForResponses ?? true,
                                     organizerID: currentUserID,
                                     questions: info)

            if let respondedUserID {
                session.update(requiredResponses: response.requiredResponses,
                                waitingForResponses: response.waitingForResponses,
                                respondedUserID: respondedUserID)
            }
        }

        if response.setlistData != nil {
            activeSetlistSession = nil
        } else {
            activeSetlistSession = session
        }
    }

private func fetchConversation() throws -> Conversation? {
        let descriptor = FetchDescriptor<Conversation>(
            predicate: #Predicate { $0.remoteID == conversationID }
        )
        return try modelContext.fetch(descriptor).first
    }

    private func observePresence() {
        guard let presenceService else { return }
        let targets = participantIDs.filter { $0 != currentUserID }
        guard !targets.isEmpty else { return }

        presenceListener?.stop()
        presenceListener = presenceService.listenForPresence(userIDs: targets) { [weak self] states in
            Task { @MainActor in
                self?.presenceStates = states
            }
        } onError: { [weak self] error in
            Task { @MainActor in
                self?.errorMessage = error.localizedDescription
            }
        }
    }

    private func observeTyping() {
        guard let presenceService else { return }
        typingListener?.stop()
        typingListener = presenceService.listenForTyping(conversationID: conversationID) { [weak self] statuses in
            Task { @MainActor in
                self?.typingStatuses = statuses
            }
        } onError: { [weak self] error in
            Task { @MainActor in
                self?.errorMessage = error.localizedDescription
            }
        }
    }

    func displayName(for userID: String) -> String? {
        guard let info = participantDetails[userID] else { return nil }
        if let displayName = info.displayName, !displayName.isEmpty {
            return displayName
        }
        if let username = info.username, !username.isEmpty {
            return "@\(username)"
        }
        return nil
    }

    func nameOrHandle(for userID: String) -> String {
        if let display = displayName(for: userID), !display.isEmpty {
            return display
        }
        if let username = participantDetails[userID]?.username, !username.isEmpty {
            return "@\(username)"
        }
        if userID.count > 6 {
            return "User \(userID.suffix(4))"
        }
        return userID
    }

    func avatarURL(for userID: String) -> URL? {
        participantDetails[userID]?.profilePictureURL
    }

    private static let relativeFormatter: RelativeDateTimeFormatter = {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .short
        return formatter
    }()
}

struct SetlistSession: Equatable, Sendable {
    let setlistID: String
    var pendingResponders: Set<String>
    var responded: Set<String>
    var waitingForResponses: Bool
    let organizerID: String
    let questions: ChatSetlistQuestions?

    mutating func update(requiredResponses: [String]?, waitingForResponses: Bool?, respondedUserID: String?) {
        if let required = requiredResponses {
            pendingResponders = Set(required)
            responded.subtract(pendingResponders)
        }

        if let respondedUserID {
            responded.insert(respondedUserID)
            pendingResponders.remove(respondedUserID)
        }

        if let waitingForResponses {
            self.waitingForResponses = waitingForResponses
        }
    }

    func needsResponse(for userID: String) -> Bool {
        pendingResponders.contains(userID)
    }
}

private extension ChatSetlistResponsePayload {
    func toSetlistUpdate() -> SetlistUpdate? {
        guard let setlistID else { return nil }
        return SetlistUpdate(setlistID: setlistID,
                             action: action,
                             waitingForResponses: waitingForResponses,
                             requiredResponses: requiredResponses)
    }
}
