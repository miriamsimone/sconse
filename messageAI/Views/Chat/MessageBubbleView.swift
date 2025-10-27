import SwiftUI

struct MessageBubbleView: View {
    let message: ChatMessageItem
    let isCurrentUser: Bool
    let senderName: String?
    let senderAvatarURL: URL?
    let isGroupConversation: Bool
    var onSheetMusicEdit: ((ChatMessageItem) -> Void)? = nil

    private let maxImageWidth: CGFloat = 240

    var body: some View {
        HStack(alignment: .bottom, spacing: 8) {
            if isCurrentUser {
                Spacer(minLength: 40)
                contentStack(alignment: .trailing)
            } else {
                if isGroupConversation {
                    avatarView
                }
                contentStack(alignment: .leading)
                Spacer(minLength: 24)
            }
        }
        .frame(maxWidth: .infinity, alignment: isCurrentUser ? .trailing : .leading)
        .padding(.horizontal, 16)
        .padding(.vertical, 4)
    }

    @ViewBuilder
    private func contentStack(alignment: HorizontalAlignment) -> some View {
        VStack(alignment: alignment, spacing: 4) {
            if isGroupConversation && !isCurrentUser, let senderName, !senderName.isEmpty {
                Text(senderName)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }

            messageBody

            Text(message.timestamp, style: .time)
                .font(.caption2)
                .foregroundStyle(.secondary)
        }
    }

    @ViewBuilder
    private var messageBody: some View {
        switch message.type {
        case .text:
            Text(message.content)
                .padding(12)
                .background(isCurrentUser ? Color.accentColor : Color(.secondarySystemBackground))
                .foregroundStyle(isCurrentUser ? .white : .primary)
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        case .image:
            imageBody
        case .sheetMusic:
            sheetMusicBody
        case .musicRequest:
            musicRequestBody
        case .pdf:
            pdfBody
        case .setlist:
            setlistBody
        }
    }

    @ViewBuilder
    private var imageBody: some View {
        Group {
            if let url = message.mediaURL {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .empty:
                        loadingPlaceholder
                    case .success(let image):
                        image
                            .resizable()
                            .scaledToFill()
                    case .failure:
                        failurePlaceholder
                    @unknown default:
                        failurePlaceholder
                    }
                }
                .frame(maxWidth: maxImageWidth, maxHeight: maxImageWidth * 1.2)
                .clipped()
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                .overlay(
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .stroke(isCurrentUser ? Color.accentColor.opacity(0.4) : Color.clear, lineWidth: 1)
                )
            } else {
                loadingPlaceholder
                    .frame(width: maxImageWidth * 0.75, height: maxImageWidth * 0.5)
                    .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            }
        }
    }

    private var loadingPlaceholder: some View {
        RoundedRectangle(cornerRadius: 16, style: .continuous)
            .fill(Color(.secondarySystemBackground))
            .overlay(
                ProgressView()
                    .progressViewStyle(.circular)
            )
    }

    private var failurePlaceholder: some View {
        RoundedRectangle(cornerRadius: 16, style: .continuous)
            .fill(Color(.secondarySystemBackground))
            .overlay(
                Image(systemName: "photo")
                    .font(.system(size: 24))
                    .foregroundStyle(.secondary)
            )
    }

    @ViewBuilder
    private var avatarView: some View {
        Group {
            if let url = senderAvatarURL {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .empty:
                        ProgressView()
                    case .success(let image):
                        image
                            .resizable()
                            .scaledToFill()
                    case .failure:
                        Circle().fill(Color(.secondarySystemBackground))
                            .overlay(
                                Image(systemName: "person.circle.fill")
                                    .foregroundStyle(.secondary)
                            )
                    @unknown default:
                        Circle().fill(Color(.secondarySystemBackground))
                    }
                }
            } else {
                Circle()
                    .fill(Color(.secondarySystemBackground))
                    .overlay(
                        Image(systemName: "person.circle.fill")
                            .foregroundStyle(.secondary)
                    )
            }
        }
        .frame(width: 32, height: 32)
        .clipShape(Circle())
    }

    @ViewBuilder
    private var sheetMusicBody: some View {
        Group {
            if let attachment = message.sheetMusic {
                VStack(alignment: .leading, spacing: 8) {
                    HStack(spacing: 6) {
                        Image(systemName: "music.note")
                            .font(.headline)
                        Text(attachment.songName)
                            .font(.headline)
                            .lineLimit(2)
                    }

                    ABCSheetMusicView(abcNotation: attachment.abcNotation)
                        .frame(minHeight: 140)

                    VStack(alignment: .leading, spacing: 4) {
                        Text(keyDescription(from: attachment))
                            .font(.caption)
                            .foregroundStyle(.secondary)

                    }

                    HStack(spacing: 12) {
                        if let onSheetMusicEdit {
                            Button {
                                onSheetMusicEdit(message)
                            } label: {
                                Label("Edit Music", systemImage: "wand.and.stars")
                                    .font(.caption.weight(.semibold))
                                    .padding(.horizontal, 10)
                                    .padding(.vertical, 6)
                                    .background(Color.accentColor.opacity(isCurrentUser ? 0.2 : 0.12))
                                    .foregroundStyle(isCurrentUser ? Color.white : Color.accentColor)
                                    .clipShape(Capsule())
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
                .padding(12)
                .background(sheetMusicBackgroundColor)
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                .overlay(
                    RoundedRectangle(cornerRadius: 18, style: .continuous)
                        .stroke(isCurrentUser ? Color.accentColor.opacity(0.25) : Color.clear, lineWidth: 1)
                )
            } else {
                Text("Sheet music unavailable.")
                    .font(.callout)
                    .foregroundStyle(.secondary)
                    .padding(12)
                    .background(Color(.secondarySystemBackground))
                    .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            }
        }
    }

    private var sheetMusicBackgroundColor: Color {
        isCurrentUser ? Color.accentColor.opacity(0.12) : Color(.secondarySystemBackground)
    }

    @ViewBuilder
    private var musicRequestBody: some View {
        let iconName = message.content.contains("🎙️") ? "mic.fill" : "music.note.list"
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Image(systemName: iconName)
                .font(.headline)
            Text(message.content)
                .font(.callout)
                .multilineTextAlignment(.leading)
        }
        .padding(12)
        .foregroundStyle(isCurrentUser ? Color.white : Color.accentColor)
        .background(isCurrentUser ? Color.accentColor : Color.accentColor.opacity(0.12))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    @ViewBuilder
    private var setlistBody: some View {
        if let attachment = message.setlist {
            SetlistPlanView(attachment: attachment)
        } else {
            Text("Setlist unavailable.")
                .font(.callout)
                .foregroundStyle(.secondary)
                .padding(12)
                .background(Color(.secondarySystemBackground))
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
    }

    @ViewBuilder
    private var pdfBody: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 6) {
                Image(systemName: "doc.richtext")
                    .font(.headline)
                Text(message.content.isEmpty ? "PDF Sheet Music" : message.content)
                    .font(.headline)
                    .lineLimit(2)
            }

            if let url = message.mediaURL {
                PDFPreviewView(url: url)
                    .frame(minHeight: 180)

                HStack(spacing: 12) {
                    Link(destination: url) {
                        Label("Open", systemImage: "arrow.up.forward.app")
                            .font(.caption.weight(.semibold))
                    }

                    if let host = url.host {
                        Text(host)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            } else {
                Text("PDF unavailable.")
                    .font(.callout)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(12)
        .background(isCurrentUser ? Color.accentColor.opacity(0.12) : Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(isCurrentUser ? Color.accentColor.opacity(0.25) : Color.clear, lineWidth: 1)
        )
    }

    private func keyDescription(from attachment: SheetMusicAttachment) -> String {
        if let transposed = attachment.transposedTo, !transposed.isEmpty {
            return "Key: \(attachment.key) · Transposed for \(transposed)"
        }
        if let original = attachment.originalKey, original != attachment.key {
            return "Key: \(attachment.key) (original \(original))"
        }
        return "Key: \(attachment.key)"
    }

}

#Preview {
    let sample = ChatMessageItem(id: "1",
                                 conversationID: "c1",
                                 senderID: "userA",
                                 content: "Hello there!",
                                 type: .text,
                                 mediaURL: nil,
                                 sheetMusic: nil,
                                 setlist: nil,
                                 timestamp: Date(),
                                 deliveryStatus: .sent,
                                 readBy: [],
                                 localID: nil)
    MessageBubbleView(message: sample,
                      isCurrentUser: true,
                      senderName: "Alex",
                      senderAvatarURL: nil,
                      isGroupConversation: false)
        .previewLayout(.sizeThatFits)

    let imageSample = ChatMessageItem(id: "2",
                                      conversationID: "c1",
                                      senderID: "userB",
                                      content: "Photo",
                                      type: .image,
                                      mediaURL: URL(string: "https://example.com/image.jpg"),
                                      sheetMusic: nil,
                                      setlist: nil,
                                      timestamp: Date(),
                                      deliveryStatus: .sent,
                                      readBy: [],
                                      localID: nil)
    MessageBubbleView(message: imageSample,
                      isCurrentUser: false,
                      senderName: "Jordan",
                      senderAvatarURL: nil,
                      isGroupConversation: true)
        .previewLayout(.sizeThatFits)

    let sheetAttachment = SheetMusicAttachment(songName: "Happy Birthday",
                                               abcNotation: "X:1\nT:Happy Birthday\nM:3/4\nL:1/4\nK:C\n\"C\"G2 G | \"C\"A2 G | \"F\"c2 B | \"C\"A3 |\n",
                                               key: "C",
                                               originalKey: "C",
                                               transposedTo: nil,
                                               confidence: 0.42,
                                               sources: ["https://example.com"],
                                               musicID: "music-preview-456",
                                               sheetMusicURL: "https://example.com/rendered.png")
    let sheetSample = ChatMessageItem(id: "3",
                                      conversationID: "c1",
                                      senderID: "userC",
                                     content: sheetAttachment.songName,
                                     type: .sheetMusic,
                                     mediaURL: nil,
                                      sheetMusic: sheetAttachment,
                                      setlist: nil,
                                      timestamp: Date(),
                                      deliveryStatus: .delivered,
                                      readBy: [],
                                      localID: nil)
    MessageBubbleView(message: sheetSample,
                      isCurrentUser: false,
                      senderName: "Morgan",
                      senderAvatarURL: nil,
                      isGroupConversation: false)
        .previewLayout(.sizeThatFits)

    let requestSample = ChatMessageItem(id: "4",
                                        conversationID: "c1",
                                        senderID: "userA",
                                        content: "🎵 Generating \"Happy Birthday\"",
                                        type: .musicRequest,
                                        mediaURL: nil,
                                        sheetMusic: nil,
                                        setlist: nil,
                                        timestamp: Date(),
                                        deliveryStatus: .sent,
                                        readBy: [],
                                        localID: nil)
    MessageBubbleView(message: requestSample,
                      isCurrentUser: true,
                      senderName: "Alex",
                      senderAvatarURL: nil,
                      isGroupConversation: false)
        .previewLayout(.sizeThatFits)

    let pdfSample = ChatMessageItem(id: "5",
                                     conversationID: "c1",
                                     senderID: "userB",
                                     content: "Moonlight Sonata - IMSLP",
                                     type: .pdf,
                                     mediaURL: URL(string: "https://example.com/moonlight.pdf"),
                                     sheetMusic: nil,
                                     setlist: nil,
                                     timestamp: Date(),
                                     deliveryStatus: .delivered,
                                     readBy: [],
                                     localID: nil)
    MessageBubbleView(message: pdfSample,
                      isCurrentUser: false,
                      senderName: "Jordan",
                      senderAvatarURL: nil,
                      isGroupConversation: true)
        .previewLayout(.sizeThatFits)

    let setlistPieces = [
        SetlistPieceAttachment(title: "Take Five",
                               composer: "Dave Brubeck",
                               durationMinutes: 7,
                               difficultyLevel: "Intermediate",
                               keySignature: "E♭ minor",
                               instruments: ["sax", "piano", "bass", "drums"],
                               genre: "Jazz",
                               reasoning: "Opens with a familiar groove and 5/4 meter."),
        SetlistPieceAttachment(title: "Blue Bossa",
                               composer: "Kenny Dorham",
                               durationMinutes: 6,
                               difficultyLevel: "Intermediate",
                               keySignature: "C minor",
                               instruments: ["horns", "rhythm section"],
                               genre: "Latin Jazz",
                               reasoning: "Provides contrast with a Latin feel and opportunities for solos.")
    ]

    let setlistAttachment = SetlistPlanAttachment(setlistID: "setlist-demo",
                                                  title: "Jazz Quartet – 60 Minute Show",
                                                  totalDurationMinutes: 48,
                                                  confidence: 0.8,
                                                  designReasoning: "Alternating energy levels and spotlight opportunities for each member.",
                                                  pieces: setlistPieces,
                                                  agentContributions: ["Coordinator": "Balanced flow", "Musicologist": "Ensured harmonic variety"])

    let setlistSample = ChatMessageItem(id: "6",
                                        conversationID: "c1",
                                        senderID: "ai",
                                        content: setlistAttachment.title,
                                        type: .setlist,
                                        mediaURL: nil,
                                        sheetMusic: nil,
                                        setlist: setlistAttachment,
                                        timestamp: Date(),
                                        deliveryStatus: .delivered,
                                        readBy: [],
                                        localID: nil)
    MessageBubbleView(message: setlistSample,
                      isCurrentUser: false,
                      senderName: "Setlist Assistant",
                      senderAvatarURL: nil,
                      isGroupConversation: true)
        .previewLayout(.sizeThatFits)
}
