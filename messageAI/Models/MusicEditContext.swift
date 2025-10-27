import Foundation

struct MusicEditContext: Identifiable, Equatable, Sendable {
    struct HistoryEntry: Identifiable, Hashable, Sendable {
        let id: UUID
        let instruction: String
        let timestamp: Date
        let resultingKey: String?
        let notes: String?

        init(id: UUID = UUID(),
             instruction: String,
             timestamp: Date = .now,
             resultingKey: String? = nil,
             notes: String? = nil) {
            self.id = id
            self.instruction = instruction
            self.timestamp = timestamp
            self.resultingKey = resultingKey
            self.notes = notes
        }
    }

    let id: UUID
    let sourceMessageID: String
    let songName: String
    let originalAttachment: SheetMusicAttachment
    var workingAttachment: SheetMusicAttachment
    var history: [HistoryEntry]

    init(id: UUID = UUID(),
         sourceMessageID: String,
         songName: String,
         originalAttachment: SheetMusicAttachment,
         workingAttachment: SheetMusicAttachment? = nil,
         history: [HistoryEntry] = []) {
        self.id = id
        self.sourceMessageID = sourceMessageID
        self.songName = songName
        self.originalAttachment = originalAttachment
        self.workingAttachment = workingAttachment ?? originalAttachment
        self.history = history
    }

    var currentAttachment: SheetMusicAttachment {
        workingAttachment
    }

    var hasChangesFromOriginal: Bool {
        workingAttachment != originalAttachment
    }
}
