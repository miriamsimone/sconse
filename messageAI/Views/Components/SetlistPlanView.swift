import SwiftUI

struct SetlistPlanView: View {
    let attachment: SetlistPlanAttachment

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            headerSection

            if let reasoning = attachment.designReasoning, !reasoning.isEmpty {
                Text(reasoning)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            VStack(alignment: .leading, spacing: 10) {
                ForEach(Array(zip(attachment.pieces.indices, attachment.pieces)), id: \.0) { index, piece in
                    SetlistPieceRow(number: index + 1, piece: piece)
                    if index != attachment.pieces.indices.last {
                        Divider()
                    }
                }
            }

            if let contributions = attachment.agentContributions, !contributions.isEmpty {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Agent Notes")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.secondary)
                    ForEach(contributions.keys.sorted(), id: \.self) { key in
                        if let value = contributions[key], !value.isEmpty {
                            Text("• \(key): \(value)")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
            }
        }
        .padding(16)
        .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(attachment.title)
                .font(.title3.weight(.semibold))
                .lineLimit(2)

            HStack(spacing: 8) {
                Label(attachment.formattedDuration, systemImage: "clock")
                    .font(.caption.weight(.semibold))

                if let confidence = attachment.confidenceDisplay {
                    Label(confidence, systemImage: "checkmark.seal")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            .foregroundStyle(.secondary)
        }
    }
}

private struct SetlistPieceRow: View {
    let number: Int
    let piece: SetlistPieceAttachment

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(alignment: .firstTextBaseline, spacing: 8) {
                Text("\(number).")
                    .font(.headline)
                Text(piece.title)
                    .font(.headline)
                    .lineLimit(2)
            }

            HStack(spacing: 6) {
                if let composer = piece.composer, !composer.isEmpty {
                    Text(composer)
                }
                if let duration = piece.formattedDuration {
                    Text("· \(duration)")
                }
                if let difficulty = piece.difficultyLevel {
                    Text("· \(difficulty.capitalized)")
                }
            }
            .font(.caption)
            .foregroundStyle(.secondary)

            if let reasoning = piece.reasoning, !reasoning.isEmpty {
                Text(reasoning)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }
}

#Preview {
    let mockPieces = [
        SetlistPieceAttachment(title: "Take Five",
                               composer: "Dave Brubeck",
                               durationMinutes: 7,
                               difficultyLevel: "intermediate",
                               keySignature: "E♭ minor",
                               instruments: ["sax", "piano", "bass", "drums"],
                               genre: "Jazz",
                               reasoning: "Opens with a familiar groove and showcases 5/4 meter."),
        SetlistPieceAttachment(title: "Blue Bossa",
                               composer: "Kenny Dorham",
                               durationMinutes: 6,
                               difficultyLevel: "intermediate",
                               keySignature: "C minor",
                               instruments: ["horns", "rhythm section"],
                               genre: "Latin Jazz",
                               reasoning: "Provides contrast with a Latin feel and opportunities for solos.")
    ]

    let attachment = SetlistPlanAttachment(setlistID: "setlist-123",
                                           title: "Jazz Quartet – 60 Minute Show",
                                           totalDurationMinutes: 48,
                                           confidence: 0.82,
                                           designReasoning: "Balanced pacing with alternating energy levels and spotlight opportunities for each member.",
                                           pieces: mockPieces,
                                           agentContributions: ["Coordinator": "Ensured flow alternates upbeat and laid-back tunes."])
    return SetlistPlanView(attachment: attachment)
        .padding()
        .previewLayout(.sizeThatFits)
}
