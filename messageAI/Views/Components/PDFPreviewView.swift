import SwiftUI
import PDFKit

struct PDFPreviewView: View {
    let url: URL

    @State private var document: PDFDocument?
    @State private var isLoading = false
    @State private var loadError: String?

    var body: some View {
        Group {
            if let document {
                PDFKitRepresentable(document: document)
                    .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .stroke(Color.primary.opacity(0.1), lineWidth: 1)
                    )
            } else if isLoading {
                VStack(spacing: 8) {
                    ProgressView()
                    Text("Loading PDF…")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity, minHeight: 160)
                .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
            } else if let loadError {
                VStack(spacing: 8) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.title2)
                        .foregroundStyle(.secondary)
                    Text(loadError)
                        .font(.caption)
                        .multilineTextAlignment(.center)
                        .foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity, minHeight: 160)
                .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
            } else {
                Color.clear
                    .frame(height: 160)
            }
        }
        .task {
            await loadDocument()
        }
    }

    private func loadDocument() async {
        guard document == nil, !isLoading else { return }
        await MainActor.run {
            isLoading = true
            loadError = nil
        }

        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            if let pdf = PDFDocument(data: data) {
                await MainActor.run {
                    self.document = pdf
                    self.isLoading = false
                }
            } else {
                throw NSError(domain: "PDFPreviewView", code: -1, userInfo: [NSLocalizedDescriptionKey: "Unable to open PDF"])
            }
        } catch {
            await MainActor.run {
                self.loadError = error.localizedDescription
                self.isLoading = false
            }
        }
    }
}

private struct PDFKitRepresentable: UIViewRepresentable {
    let document: PDFDocument

    func makeUIView(context: Context) -> PDFView {
        let view = PDFView()
        view.autoScales = true
        view.displayMode = .singlePageContinuous
        view.displayDirection = .vertical
        view.backgroundColor = .clear
        return view
    }

    func updateUIView(_ pdfView: PDFView, context: Context) {
        if pdfView.document != document {
            pdfView.document = document
        }
    }
}
