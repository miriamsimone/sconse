import SwiftUI
import WebKit

struct ABCSheetMusicView: UIViewRepresentable {
    let abcNotation: String

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.defaultWebpagePreferences.preferredContentMode = .mobile
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.isOpaque = false
        webView.backgroundColor = .clear
        webView.scrollView.isScrollEnabled = false
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        webView.loadHTMLString(htmlTemplate(for: abcNotation), baseURL: nil)
    }

    private func htmlTemplate(for abc: String) -> String {
        let escaped = abc
            .replacingOccurrences(of: "\\", with: "\\\\")
            .replacingOccurrences(of: "`", with: "\\`")
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=2.0, user-scalable=yes">
            <script src="https://cdn.jsdelivr.net/npm/abcjs@6.2.3/dist/abcjs-basic-min.js"></script>
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    background: transparent;
                    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
                }
                #paper {
                    margin: 0;
                    padding: 0;
                }
                svg {
                    max-width: 100%;
                    height: auto;
                }
            </style>
        </head>
        <body>
            <div id="paper"></div>
            <script>
                (function() {
                    try {
                        const abc = `\(escaped)`;
                        ABCJS.renderAbc("paper", abc, {
                            responsive: "resize",
                            scale: 1.2,
                            add_classes: true
                        });
                    } catch (err) {
                        document.getElementById("paper").innerHTML = '<div style="color:#ff3b30;padding:16px;">Error rendering sheet music.</div>';
                    }
                })();
            </script>
        </body>
        </html>
        """
    }
}
