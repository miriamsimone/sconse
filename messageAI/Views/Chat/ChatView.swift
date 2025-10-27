import SwiftUI

struct ChatView: View {
    @StateObject private var viewModel: ChatViewModel
    init(viewModel: ChatViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
    }

    var body: some View {
        VStack(spacing: 0) {
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 8) {
                        ForEach(viewModel.messages) { message in
                            MessageBubbleView(message: message,
                                              isCurrentUser: message.senderID == viewModel.currentUserID,
                                              senderName: viewModel.displayName(for: message.senderID),
                                              senderAvatarURL: viewModel.avatarURL(for: message.senderID),
                                              isGroupConversation: viewModel.isGroupConversation,
                                              onSheetMusicEdit: message.type == .sheetMusic ? { viewModel.beginEditingSheetMusic(for: $0) } : nil)
                                .id(message.id)
                        }
                    }
                    .padding(.top, 16)
                }
                .onAppear {
                    scrollProxy = proxy
                    scrollToBottom(animated: false, deferred: true)
                }
                .onChange(of: viewModel.messages.count) { _ in
                    scrollProxy = proxy
                    scrollToBottom(animated: true, deferred: true)
                }
                .onChange(of: viewModel.messages.last?.id) { _ in
                    scrollProxy = proxy
                    scrollToBottom(animated: true, deferred: true)
                }
            }

            if let typingText = viewModel.typingIndicatorText {
                TypingIndicatorView(text: typingText)
                    .transition(.opacity)
                    .padding(.vertical, 4)
            }

            Divider()

            if let setlistSession = viewModel.activeSetlistSession {
                setlistBanner(for: setlistSession)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
            }

            if let context = viewModel.activeEditContext {
                editingBanner(for: context)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
            }

            let aiMode: MessageInputView.AIMode = {
                if viewModel.activeEditContext != nil {
                    return .sheetEditing
                }
                if viewModel.needsSetlistResponse(for: viewModel.currentUserID) {
                    return .setlistResponse
                }
                return .standard
            }()

            let isProcessingAI = viewModel.isGeneratingSheetMusic || viewModel.isApplyingSheetEdit || viewModel.isSubmittingSetlistPreference
            let aiAction: () -> Void = {
                switch aiMode {
                case .sheetEditing:
                    return { viewModel.submitEditInstruction(viewModel.inputText) }
                case .setlistResponse:
                    return { viewModel.submitSetlistPreferenceFromInput() }
                case .standard:
                    return { viewModel.submitMusicRequest() }
                }
            }()

            MessageInputView(text: $viewModel.inputText,
                             isSending: viewModel.isSending,
                             isUploadingMedia: viewModel.isUploadingMedia,
                             isProcessingAIAction: isProcessingAI,
                             isTranscribingAudio: viewModel.isTranscribingAudio,
                             aiMode: aiMode,
                             onSend: {
                                 viewModel.sendTextMessage()
                             },
                             onTextChange: { viewModel.handleInputChange($0) },
                             onMediaSelected: { data in
                                 viewModel.sendImageMessage(with: data)
                             },
                             onMusicRequest: aiAction,
                             onAudioTranscription: { data, format in
                                 viewModel.transcribeAudioSnippet(audioData: data, format: format)
                             })
        }
        .toolbar {
            ToolbarItem(placement: .principal) {
                VStack(spacing: 2) {
                    Text(viewModel.conversationTitle)
                        .font(.headline)
                    if !viewModel.presenceStatusText.isEmpty {
                        Text(viewModel.presenceStatusText)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .alert("Error", isPresented: errorBinding) {
            Button("OK", role: .cancel) {
                viewModel.errorMessage = nil
            }
        } message: {
            Text(viewModel.errorMessage ?? "")
        }
    }

    @State private var scrollProxy: ScrollViewProxy?

    private func scrollToBottom(animated: Bool, deferred: Bool = false) {
        guard let proxy = scrollProxy,
              let last = viewModel.messages.last else { return }

        let action = {
            if animated {
                withAnimation(.easeInOut) {
                    proxy.scrollTo(last.id, anchor: .bottom)
                }
            } else {
                proxy.scrollTo(last.id, anchor: .bottom)
            }
        }

        if deferred {
            DispatchQueue.main.async(execute: action)
        } else {
            action()
        }
    }

    private var errorBinding: Binding<Bool> {
        Binding(
            get: { viewModel.errorMessage != nil },
            set: { newValue in
                if !newValue {
                    viewModel.errorMessage = nil
                }
            }
        )
    }

    @ViewBuilder
    private func editingBanner(for context: MusicEditContext) -> some View {
        HStack(alignment: .center, spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                Text("Editing: \(context.songName)")
                    .font(.subheadline.weight(.semibold))
                if let latest = context.history.first {
                    Text("Last edit: \(latest.instruction)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                } else {
                    Text("Describe a change and tap the wand button to apply.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            Spacer()

            if viewModel.isApplyingSheetEdit {
                ProgressView()
                    .progressViewStyle(.circular)
            }

            if context.hasChangesFromOriginal {
                Button("Reset") {
                    viewModel.resetActiveEditContextToOriginal()
                }
                .disabled(viewModel.isApplyingSheetEdit)
            }

            Button("Done") {
                viewModel.cancelSheetMusicEditing()
            }
            .disabled(viewModel.isApplyingSheetEdit)
        }
        .padding(12)
        .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    @ViewBuilder
    private func setlistBanner(for session: SetlistSession) -> some View {
        HStack(alignment: .center, spacing: 12) {
            VStack(alignment: .leading, spacing: 6) {
                Text("Setlist planning in progress")
                    .font(.subheadline.weight(.semibold))

                if let questions = session.questions, !questions.generalQuestions.isEmpty {
                    Text("Skim the suggested topics and share your preferences in the chat.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                let pendingNames = session.pendingResponders.map { viewModel.nameOrHandle(for: $0) }
                if !pendingNames.isEmpty {
                    Text("Waiting for: \(pendingNames.joined(separator: ", "))")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                if session.needsResponse(for: viewModel.currentUserID) {
                    Text("Type your preferences, then tap the group icon to submit them to the AI.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            Spacer()

            if viewModel.isSubmittingSetlistPreference {
                ProgressView()
                    .progressViewStyle(.circular)
            }
        }
        .padding(12)
        .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}
