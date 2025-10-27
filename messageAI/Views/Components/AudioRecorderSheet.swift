import SwiftUI
import Combine
import AVFoundation

struct AudioRecordingResult: Sendable, Equatable {
    let data: Data
    let format: String
}

struct AudioRecorderSheet: View {
    @Environment(\.dismiss) private var dismiss
    @StateObject private var controller = AudioRecorderController()
    @State private var didFinish = false

    let onComplete: (AudioRecordingResult) -> Void
    let onCancel: () -> Void

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                recorderContent
                Spacer()
                if let error = controller.errorMessage {
                    Text(error)
                        .font(.footnote)
                        .foregroundStyle(.red)
                        .multilineTextAlignment(.center)
                }
            }
            .padding(24)
            .navigationTitle("Record Audio")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        handleCancel()
                    }
                }
            }
        }
        .presentationDetents([.medium, .large])
        .onAppear {
            controller.checkPermission()
        }
        .onChange(of: controller.completedRecording) { result in
            guard let result else { return }
            handleAutoSend(with: result)
        }
        .onDisappear {
            if !didFinish {
                controller.discardRecording()
                onCancel()
            }
        }
    }

    @ViewBuilder
    private var recorderContent: some View {
        if controller.permissionDenied {
            VStack(spacing: 12) {
                Image(systemName: "mic.slash")
                    .font(.system(size: 48))
                    .foregroundStyle(.secondary)
                Text("Microphone access is required to record audio.")
                    .font(.headline)
                    .multilineTextAlignment(.center)
                Text("Enable microphone permissions in Settings and try again.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
            }
        } else {
            VStack(spacing: 20) {
                Button {
                    controller.toggleRecording()
                } label: {
                    ZStack {
                        Circle()
                            .fill(controller.isRecording ? Color.red : Color.accentColor.opacity(0.15))
                            .frame(width: 96, height: 96)
                        Image(systemName: controller.isRecording ? "stop.fill" : "mic.fill")
                            .font(.system(size: 32, weight: .bold))
                            .foregroundStyle(controller.isRecording ? .white : .accentColor)
                    }
                }
                .buttonStyle(.plain)
                .accessibilityLabel(controller.isRecording ? "Stop recording" : "Start recording")
                .accessibilityHint("Records a short audio snippet for notation")

                if controller.isRecording {
                    Text("Recording…")
                        .font(.headline)
                } else if controller.hasRecording {
                    Text("Recorded \(formattedDuration(controller.recordedDuration))")
                        .font(.headline)
                } else {
                    Text("Tap the microphone to record up to 15 seconds.")
                        .font(.headline)
                }

                Text("Hold the device close to your instrument and stop recording when ready; it will send automatically.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
            }
        }
    }

    private func handleCancel() {
        didFinish = true
        controller.discardRecording()
        onCancel()
        dismiss()
    }

    private func handleAutoSend(with result: AudioRecordingResult) {
        guard !didFinish else { return }
        didFinish = true
        onComplete(result)
        controller.discardRecording()
        dismiss()
    }

    private func formattedDuration(_ duration: TimeInterval) -> String {
        let formatter = DateComponentsFormatter()
        formatter.allowedUnits = duration >= 60 ? [.minute, .second] : [.second]
        formatter.unitsStyle = .brief
        return formatter.string(from: duration.rounded()) ?? "\(Int(duration))s"
    }
}

@MainActor
private final class AudioRecorderController: NSObject, ObservableObject, AVAudioRecorderDelegate {
    @Published var isRecording = false
    @Published var hasRecording = false
    @Published var recordedDuration: TimeInterval = 0
    @Published var permissionDenied = false
    @Published var errorMessage: String?
    @Published var completedRecording: AudioRecordingResult?

    private var recorder: AVAudioRecorder?
    private var recordingURL: URL?

    func checkPermission() {
        let session = AVAudioSession.sharedInstance()
        switch session.recordPermission {
        case .granted:
            permissionDenied = false
        case .denied:
            permissionDenied = true
        case .undetermined:
            session.requestRecordPermission { [weak self] allowed in
                Task { @MainActor in
                    guard let self else { return }
                    self.permissionDenied = !allowed
                    if !allowed {
                        self.errorMessage = "Microphone access is required to record audio."
                    }
                }
            }
        @unknown default:
            permissionDenied = true
        }
    }

    func toggleRecording() {
        if isRecording {
            stopRecording()
        } else {
            startRecording()
        }
    }

    func startRecording() {
        let session = AVAudioSession.sharedInstance()

        switch session.recordPermission {
        case .granted:
            permissionDenied = false
        case .denied:
            permissionDenied = true
            errorMessage = "Microphone access is required to record audio."
            return
        case .undetermined:
            session.requestRecordPermission { [weak self] allowed in
                Task { @MainActor in
                    guard let self else { return }
                    self.permissionDenied = !allowed
                    if allowed {
                        self.startRecording()
                    } else {
                        self.errorMessage = "Microphone access is required to record audio."
                    }
                }
            }
            return
        @unknown default:
            permissionDenied = true
            errorMessage = "Microphone access is required to record audio."
            return
        }

        do {
            if let url = recordingURL {
                try? FileManager.default.removeItem(at: url)
                recordingURL = nil
            }

            try session.setCategory(.playAndRecord,
                                    mode: .default,
                                    options: [.defaultToSpeaker, .allowBluetooth])
            try session.setActive(true, options: .notifyOthersOnDeactivation)

            let url = FileManager.default.temporaryDirectory
                .appendingPathComponent("audio-\(UUID().uuidString).m4a")

            let settings: [String: Any] = [
                AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
                AVSampleRateKey: 44_100,
                AVNumberOfChannelsKey: 1,
                AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
            ]

            let recorder = try AVAudioRecorder(url: url, settings: settings)
            recorder.delegate = self
            recorder.prepareToRecord()
            recorder.record(forDuration: 15)

            self.recorder = recorder
            recordingURL = url
            isRecording = true
            hasRecording = false
            recordedDuration = 0
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func stopRecording() {
        recorder?.stop()
    }

    func discardRecording() {
        if isRecording {
            stopRecording()
        }

        recorder?.delegate = nil
        recorder = nil

        if let url = recordingURL {
            try? FileManager.default.removeItem(at: url)
        }

        recordedDuration = 0
        hasRecording = false
        isRecording = false
        completedRecording = nil

        deactivateSession()
    }

    func audioRecorderDidFinishRecording(_ recorder: AVAudioRecorder, successfully flag: Bool) {
        Task { @MainActor in
            let url = self.recordingURL
            self.isRecording = false
            self.recorder = nil
            self.deactivateSession()

            guard flag, let url else {
                self.hasRecording = false
                if !flag {
                    self.errorMessage = "Recording failed."
                }
                return
            }

            let asset = AVURLAsset(url: url)
            var duration = CMTimeGetSeconds(asset.duration)
            if !duration.isFinite || duration <= 0 {
                duration = recorder.currentTime
            }

            self.recordedDuration = duration

            let minimumDuration: TimeInterval = 0.2
            guard duration >= minimumDuration else {
                try? FileManager.default.removeItem(at: url)
                self.recordingURL = nil
                self.hasRecording = false
                self.errorMessage = "Recording was too short. Try again."
                return
            }

            do {
                let data = try Data(contentsOf: url)
                let format = url.pathExtension.isEmpty ? "m4a" : url.pathExtension
                self.completedRecording = AudioRecordingResult(data: data, format: format)
                self.hasRecording = true
            } catch {
                self.errorMessage = error.localizedDescription
                self.hasRecording = false
            }
        }
    }

    func audioRecorderEncodeErrorDidOccur(_ recorder: AVAudioRecorder, error: Error?) {
        Task { @MainActor in
            self.errorMessage = error?.localizedDescription ?? "Recording failed."
            self.discardRecording()
        }
    }

    private func deactivateSession() {
        let session = AVAudioSession.sharedInstance()
        try? session.setActive(false, options: .notifyOthersOnDeactivation)
    }

    deinit {
        recorder?.stop()
        if let url = recordingURL {
            try? FileManager.default.removeItem(at: url)
        }
    }
}
