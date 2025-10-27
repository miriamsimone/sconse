import SwiftUI
import PhotosUI

struct MessageInputView: View {
    enum AIMode {
        case standard
        case sheetEditing
        case setlistResponse
    }

    @Binding var text: String
    var isSending: Bool
    var isUploadingMedia: Bool
    var isProcessingAIAction: Bool
    var isTranscribingAudio: Bool
    var aiMode: AIMode = .standard
    var onSend: () -> Void
    var onTextChange: (String) -> Void
    var onMediaSelected: (Data) -> Void
    var onMusicRequest: () -> Void
    var onAudioTranscription: (Data, String) -> Void

    @State private var selectedPhotoItem: PhotosPickerItem?
    @State private var isLoadingPhoto = false
    @State private var isShowingAudioRecorder = false

    var body: some View {
        let trimmedText = text.trimmingCharacters(in: .whitespacesAndNewlines)
        let aiActionIcon: String = {
            switch aiMode {
            case .standard:
                return "music.note"
            case .sheetEditing:
                return "wand.and.stars"
            case .setlistResponse:
                return "person.3.sequence"
            }
        }()
        let disableAIButton = trimmedText.isEmpty || isSending || isUploadingMedia || isProcessingAIAction || isTranscribingAudio
        HStack(spacing: 12) {
            Button(action: onMusicRequest) {
                Group {
                    if isProcessingAIAction {
                        ProgressView()
                            .progressViewStyle(.circular)
                    } else {
                        Image(systemName: aiActionIcon)
                            .font(.system(size: 18, weight: .semibold))
                    }
                }
                .frame(width: 32, height: 32)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .disabled(disableAIButton)

            Button {
                isShowingAudioRecorder = true
            } label: {
                Group {
                    if isTranscribingAudio {
                        ProgressView()
                            .progressViewStyle(.circular)
                    } else {
                        Image(systemName: "mic")
                            .font(.system(size: 18, weight: .semibold))
                    }
                }
                .frame(width: 32, height: 32)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .disabled(isSending || isUploadingMedia || isProcessingAIAction || isTranscribingAudio)
            .sheet(isPresented: $isShowingAudioRecorder) {
                AudioRecorderSheet {
                    isShowingAudioRecorder = false
                    onAudioTranscription($0.data, $0.format)
                } onCancel: {
                    isShowingAudioRecorder = false
                }
            }

            PhotosPicker(selection: $selectedPhotoItem,
                         matching: .images,
                         photoLibrary: .shared()) {
                Group {
                    if isUploadingMedia || isLoadingPhoto {
                        ProgressView()
                            .progressViewStyle(.circular)
                    } else {
                        Image(systemName: "photo")
                            .font(.system(size: 22))
                    }
                }
                .frame(width: 32, height: 32)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
            .disabled(isSending || isUploadingMedia || isLoadingPhoto || isTranscribingAudio)
            .onChange(of: selectedPhotoItem) { newValue in
                guard let newValue else { return }
                Task {
                    await loadImage(from: newValue)
                }
            }

            TextField("Message", text: Binding(
                get: { text },
                set: { newValue in
                    text = newValue
                    onTextChange(newValue)
                }
            ), axis: .vertical)
                .textInputAutocapitalization(.sentences)
                .autocorrectionDisabled()
                .padding(10)
                .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 20))

            Button(action: onSend) {
                if isSending {
                    ProgressView()
                        .progressViewStyle(.circular)
                } else {
                    Image(systemName: "paperplane.fill")
                        .font(.system(size: 20, weight: .semibold))
                }
            }
            .buttonStyle(.borderedProminent)
            .disabled(trimmedText.isEmpty || isSending || isUploadingMedia || (aiMode == .setlistResponse && isProcessingAIAction))
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(.regularMaterial)
    }

    private func loadImage(from item: PhotosPickerItem) async {
        isLoadingPhoto = true
        defer {
            Task { @MainActor in
                isLoadingPhoto = false
                selectedPhotoItem = nil
            }
        }

        do {
            if let data = try await item.loadTransferable(type: Data.self) {
                await MainActor.run {
                    onMediaSelected(data)
                }
            }
        } catch {
            // Ignore transfer failures; a later retry can succeed.
        }
    }
}

#Preview {
    MessageInputView(text: .constant("Hello"),
                     isSending: false,
                     isUploadingMedia: false,
                     isProcessingAIAction: false,
                     isTranscribingAudio: false,
                     aiMode: .standard,
                     onSend: {},
                     onTextChange: { _ in },
                     onMediaSelected: { _ in },
                     onMusicRequest: {},
                     onAudioTranscription: { _, _ in })
}
