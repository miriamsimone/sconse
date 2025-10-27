import Foundation

struct SetlistPieceAttachment: Codable, Hashable, Sendable {
    let title: String
    let composer: String?
    let durationMinutes: Int?
    let difficultyLevel: String?
    let keySignature: String?
    let instruments: [String]?
    let genre: String?
    let reasoning: String?

    var formattedDuration: String? {
        guard let durationMinutes else { return nil }
        if durationMinutes >= 60 {
            let hours = durationMinutes / 60
            let minutes = durationMinutes % 60
            if minutes == 0 {
                return "\(hours)h"
            }
            return "\(hours)h \(minutes)m"
        }
        return "\(durationMinutes)m"
    }
}

struct SetlistPlanAttachment: Codable, Hashable, Sendable {
    let setlistID: String
    let title: String
    let totalDurationMinutes: Int
    let confidence: Double?
    let designReasoning: String?
    let pieces: [SetlistPieceAttachment]
    let agentContributions: [String: String]?

    var formattedDuration: String {
        if totalDurationMinutes >= 60 {
            let hours = totalDurationMinutes / 60
            let minutes = totalDurationMinutes % 60
            if minutes == 0 {
                return "\(hours)h"
            }
            return "\(hours)h \(minutes)m"
        }
        return "\(totalDurationMinutes)m"
    }

    var confidenceDisplay: String? {
        guard let confidence else { return nil }
        return "Confidence \(NumberFormatter.percent.string(from: NSNumber(value: confidence)) ?? "")"
    }
}

struct SetlistUpdate: Codable, Hashable, Sendable {
    let setlistID: String
    let action: String?
    let waitingForResponses: Bool?
    let requiredResponses: [String]?

    private enum CodingKeys: String, CodingKey {
        case setlistID = "setlist_id"
        case action
        case waitingForResponses = "waiting_for_responses"
        case requiredResponses = "required_responses"
    }
}

struct ChatSetlistQuestions: Codable, Hashable, Sendable {
    let generalQuestions: [String]
    let concertSpecificQuestions: [String]
    let collaborationQuestions: [String]

    init(general: [String]?, concert: [String]?, collaboration: [String]?) {
        self.generalQuestions = general ?? []
        self.concertSpecificQuestions = concert ?? []
        self.collaborationQuestions = collaboration ?? []
    }
}

private extension NumberFormatter {
    static let percent: NumberFormatter = {
        let formatter = NumberFormatter()
        formatter.numberStyle = .percent
        formatter.maximumFractionDigits = 0
        return formatter
    }()
}
