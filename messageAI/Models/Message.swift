import Foundation
import SwiftData

enum MessageContentType: String, Codable, Sendable {
    case text
    case image
    case sheetMusic
    case musicRequest
    case pdf
    case setlist
}

enum MessageDeliveryStatus: String, Codable, Sendable {
    case sending
    case sent
    case delivered
    case read
}

@Model
final class Message {
    @Attribute(.unique) var remoteID: String
    var localID: String?

    @Relationship var conversation: Conversation?

    var senderUserID: String
    var content: String
    var contentType: MessageContentType
    var mediaURL: URL?
    @Attribute(.externalStorage)
    private var sheetMusicData: Data?
    @Attribute(.externalStorage)
    private var setlistData: Data?
    @Attribute(.externalStorage)
    private var setlistUpdateData: Data?
    var timestamp: Date
    var deliveryStatus: MessageDeliveryStatus
    var readByUserIDs: [String]

    init(remoteID: String,
         localID: String? = nil,
         conversation: Conversation? = nil,
         senderUserID: String,
         content: String,
         contentType: MessageContentType = .text,
         mediaURL: URL? = nil,
         sheetMusic: SheetMusicAttachment? = nil,
         setlist: SetlistPlanAttachment? = nil,
         setlistUpdate: SetlistUpdate? = nil,
         timestamp: Date = .now,
         deliveryStatus: MessageDeliveryStatus = .sending,
         readByUserIDs: [String] = []) {
        self.remoteID = remoteID
        self.localID = localID
        self.conversation = conversation
        self.senderUserID = senderUserID
        self.content = content
        self.contentType = contentType
        self.mediaURL = mediaURL
        self.sheetMusicData = sheetMusic.flatMap { try? JSONEncoder().encode($0) }
        self.setlistData = setlist.flatMap { try? JSONEncoder().encode($0) }
        self.setlistUpdateData = setlistUpdate.flatMap { try? JSONEncoder().encode($0) }
        self.timestamp = timestamp
        self.deliveryStatus = deliveryStatus
        self.readByUserIDs = readByUserIDs
    }

    var sheetMusic: SheetMusicAttachment? {
        get {
            guard let sheetMusicData else { return nil }
            return try? JSONDecoder().decode(SheetMusicAttachment.self, from: sheetMusicData)
        }
        set {
            sheetMusicData = newValue.flatMap { try? JSONEncoder().encode($0) }
        }
    }

    var setlist: SetlistPlanAttachment? {
        get {
            guard let setlistData else { return nil }
            return try? JSONDecoder().decode(SetlistPlanAttachment.self, from: setlistData)
        }
        set {
            setlistData = newValue.flatMap { try? JSONEncoder().encode($0) }
        }
    }

    var setlistUpdate: SetlistUpdate? {
        get {
            guard let setlistUpdateData else { return nil }
            return try? JSONDecoder().decode(SetlistUpdate.self, from: setlistUpdateData)
        }
        set {
            setlistUpdateData = newValue.flatMap { try? JSONEncoder().encode($0) }
        }
    }
}
