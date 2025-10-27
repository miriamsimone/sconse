# Sconces Backend API Documentation

## Overview

The Sconces backend provides AI-powered music features for a messaging app, including sheet music generation, transposition, chord editing, and music recommendations.

**Base URL**: `https://7cg7rc13l0.execute-api.us-east-1.amazonaws.com/Prod`

## Authentication

All endpoints require no authentication for MVP. API keys are configured server-side.

## Endpoints

### 1. Generate Sheet Music

**Endpoint**: `POST /generate-sheet`

**Description**: Generates ABC notation sheet music from a song name, with optional transposition for different instruments.

**Request Body**:
```json
{
  "song_name": "Happy Birthday",
  "instrument": "C"
}
```

**Parameters**:
- `song_name` (string, required): Name of the song to generate sheet music for
- `instrument` (string, optional): Target instrument for transposition. Options: `"C"`, `"Bb"`, `"Eb"`, `"F"`. Defaults to `"C"` (concert pitch)

**Response**:
```json
{
  "status": "success",
  "abc_notation": "X:1\nT:Happy Birthday\nM:4/4\nL:1/4\nK:C\n\"C\"C C C2 | \"F\"F F F2 | \"G\"G G G2 | \"C\"C4 |",
  "confidence": 0.3,
  "key": "C",
  "original_key": "C",
  "transposed_to": null,
  "sources": [
    "https://www.ultimate-guitar.com/happy-birthday-chords",
    "https://www.songsterr.com/happy-birthday",
    "https://www.guitartabs.cc/happy-birthday"
  ]
}
```

**Response Fields**:
- `status`: Always "success" for successful requests
- `abc_notation`: ABC notation string for client-side rendering
- `confidence`: Confidence score (0.0-1.0) for the generated notation
- `key`: Key signature of the generated notation
- `original_key`: Original key before any transposition
- `transposed_to`: Target instrument if transposition was applied
- `sources`: Array of source URLs used for generation

**Error Response**:
```json
{
  "error": "No tabs found",
  "message": "Could not find enough tab sources for \"Song Name\""
}
```

**Example Usage**:
```bash
curl -X POST https://7cg7rc13l0.execute-api.us-east-1.amazonaws.com/Prod/generate-sheet \
  -H "Content-Type: application/json" \
  -d '{"song_name": "Twinkle Twinkle Little Star", "instrument": "Bb"}'
```

---

### 2. Edit Chord Symbols

**Endpoint**: `POST /edit-chords`

**Description**: Edits chord symbols in existing ABC notation using natural language commands.

**Request Body**:
```json
{
  "abc_notation": "X:1\nT:Song\nM:4/4\nL:1/4\nK:C\n\"C\"C C C2 | \"F\"F F F2 |",
  "edit_instruction": "change the first chord to Em"
}
```

**Parameters**:
- `abc_notation` (string, required): Current ABC notation to edit
- `edit_instruction` (string, required): Natural language instruction for the edit

**Response**:
```json
{
  "status": "success",
  "abc_notation": "X:1\nT:Song\nM:4/4\nL:1/4\nK:C\n\"Em\"C C C2 | \"F\"F F F2 |",
  "changes_made": "Changed chord in measure 1 from C to Em"
}
```

**Example Edit Instructions**:
- "change the first chord to Em"
- "remove the chord in bar 2"
- "add a Dm7 chord above the third note"

---

### 3. Search IMSLP (Classical Music)

**Endpoint**: `POST /search-imslp`

**Description**: Searches IMSLP (International Music Score Library Project) for classical/public domain sheet music.

**Request Body**:
```json
{
  "query": "Moonlight Sonata Beethoven"
}
```

**Parameters**:
- `query` (string, required): Search query for classical music

**Response**:
```json
{
  "status": "success",
  "image_url": "https://firebase-storage-url/imslp_xyz789.png",
  "title": "Piano Sonata No.14, Op.27 No.2",
  "composer": "Ludwig van Beethoven",
  "imslp_url": "https://imslp.org/wiki/..."
}
```

---

### 4. Get Music Recommendations

**Endpoint**: `POST /recommend`

**Description**: Generates music recommendations based on chat history.

**Request Body**:
```json
{
  "chat_history": [
    {"song": "Happy Birthday", "timestamp": "2024-01-01T10:00:00Z"},
    {"song": "Twinkle Twinkle", "timestamp": "2024-01-01T10:05:00Z"}
  ]
}
```

**Parameters**:
- `chat_history` (array, required): Array of song objects with timestamps

**Response**:
```json
{
  "status": "success",
  "recommendation": "Hot Cross Buns",
  "artist": "Traditional",
  "reasoning": "Based on your interest in simple, repetitive melodies suitable for beginners...",
  "abc_notation": "X:1\nT:Hot Cross Buns\nM:4/4\nL:1/4\nK:C\n\"C\"E D C2 | E D C2 |"
}
```

---

## ABC Notation Format

The API returns ABC notation strings that can be rendered client-side using the abcjs library:

```javascript
// Example ABC notation
const abcNotation = `X:1
T:Happy Birthday
M:4/4
L:1/4
K:C
"C"C C C2 | "F"F F F2 | "G"G G G2 | "C"C4 |`;

// Render with abcjs
ABCJS.renderAbc("paper", abcNotation, {
  responsive: "resize",
  scale: 1.2
});
```

**ABC Notation Structure**:
- `X:1` - Reference number
- `T:Title` - Song title
- `M:4/4` - Time signature
- `L:1/4` - Default note length
- `K:C` - Key signature
- `"C"` - Chord symbols (in quotes)
- `C C C2` - Notes and rhythms

---

## Client-Side Integration

### iOS Swift Integration

```swift
struct SheetMusicResponse: Codable {
    let status: String
    let abcNotation: String
    let confidence: Double
    let key: String
    let originalKey: String?
    let transposedTo: String?
    let sources: [String]
    
    enum CodingKeys: String, CodingKey {
        case status
        case abcNotation = "abc_notation"
        case confidence
        case key
        case originalKey = "original_key"
        case transposedTo = "transposed_to"
        case sources
    }
}

class MusicSheetService {
    let baseURL = "https://7cg7rc13l0.execute-api.us-east-1.amazonaws.com/Prod"
    
    func generateSheetMusic(songName: String, instrument: String = "C") async throws -> SheetMusicResponse {
        let endpoint = "\(baseURL)/generate-sheet"
        
        var request = URLRequest(url: URL(string: endpoint)!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = [
            "song_name": songName,
            "instrument": instrument
        ]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw NSError(domain: "API", code: 0, userInfo: [NSLocalizedDescriptionKey: "Request failed"])
        }
        
        return try JSONDecoder().decode(SheetMusicResponse.self, from: data)
    }
}
```

### WKWebView Integration for ABC Rendering

```swift
struct ABCSheetMusicView: UIViewRepresentable {
    let abcNotation: String
    @Binding var isLoading: Bool
    
    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.isOpaque = false
        webView.backgroundColor = .clear
        return webView
    }
    
    func updateUIView(_ webView: WKWebView, context: Context) {
        let html = generateHTML(abc: abcNotation)
        webView.loadHTMLString(html, baseURL: nil)
    }
    
    private func generateHTML(abc: String) -> String {
        """
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=3.0, user-scalable=yes">
            <script src="https://cdn.jsdelivr.net/npm/abcjs@6.2.3/dist/abcjs-basic-min.js"></script>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro';
                    background: transparent;
                    padding: 16px;
                }
                #sheet-music {
                    background: white;
                    border-radius: 12px;
                    padding: 16px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }
                svg {
                    max-width: 100%;
                    height: auto;
                }
            </style>
        </head>
        <body>
            <div id="sheet-music"></div>
            <script>
                try {
                    const abc = `\(abc)`;
                    
                    ABCJS.renderAbc("sheet-music", abc, {
                        responsive: "resize",
                        scale: 1.3,
                        staffwidth: window.innerWidth - 64,
                        add_classes: true,
                        paddingtop: 0,
                        paddingbottom: 0,
                        paddingright: 0,
                        paddingleft: 0
                    });
                } catch (error) {
                    document.body.innerHTML = '<div style="color: red; padding: 20px;">Error rendering music: ' + error.message + '</div>';
                }
            </script>
        </body>
        </html>
        """
    }
}
```

---

## Error Handling

### Common Error Responses

**429 Too Many Requests**:
```json
{
  "error": "Rate limit exceeded",
  "message": "API rate limit reached. Please try again later."
}
```

**500 Internal Server Error**:
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

**404 Not Found**:
```json
{
  "error": "No tabs found",
  "message": "Could not find enough tab sources for \"Song Name\""
}
```

---

## Rate Limits & Fallbacks

- **Brave Search API**: Free tier has rate limits. System automatically falls back to mock data when limits are reached.
- **OpenAI API**: Configured with proper error handling and fallbacks.
- **Mock Data**: Available for testing when external APIs are unavailable.

---

## Testing

### Test the API

```bash
# Test basic sheet music generation
curl -X POST https://7cg7rc13l0.execute-api.us-east-1.amazonaws.com/Prod/generate-sheet \
  -H "Content-Type: application/json" \
  -d '{"song_name": "Happy Birthday", "instrument": "C"}'

# Test with different instrument
curl -X POST https://7cg7rc13l0.execute-api.us-east-1.amazonaws.com/Prod/generate-sheet \
  -H "Content-Type: application/json" \
  -d '{"song_name": "Twinkle Twinkle", "instrument": "Bb"}'
```

### Expected Response Times
- **Normal requests**: 2-5 seconds
- **With fallback**: 1-2 seconds
- **Error responses**: < 1 second

---

## Architecture Notes

- **Backend**: AWS Lambda functions with Python 3.11
- **API Gateway**: RESTful endpoints with CORS enabled
- **Client-Side Rendering**: ABC notation rendered using abcjs in WKWebView
- **Vector Graphics**: All sheet music is rendered as scalable SVG
- **Offline Capable**: ABC notation can be cached and rendered offline

---

## Support

For integration support or questions about the API, refer to this documentation or check the CloudWatch logs for the Lambda functions in the AWS console.
