import Foundation

struct SheetMusicAttachment: Codable, Hashable, Sendable {
    let songName: String
    let abcNotation: String
    let key: String
    let originalKey: String?
    let transposedTo: String?
    let confidence: Double?
    let sources: [String]?
    let musicID: String?
    let sheetMusicURL: String?

    init(songName: String,
         abcNotation: String,
         key: String,
         originalKey: String? = nil,
         transposedTo: String? = nil,
         confidence: Double? = nil,
         sources: [String]? = nil,
         musicID: String? = nil,
         sheetMusicURL: String? = nil) {
        self.songName = songName
        self.abcNotation = abcNotation
        self.key = key
        self.originalKey = originalKey
        self.transposedTo = transposedTo
        self.confidence = confidence
        self.sources = sources
        self.musicID = musicID
        self.sheetMusicURL = sheetMusicURL
    }
}
