# Testing the AI Microservice with iOS App

## 🚀 Quick Start

### 1. Start the Microservice
```bash
cd /Users/miriam/Desktop/messageAI/ai-microservice
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Update iOS App Configuration
The iOS app has been updated to point to `http://localhost:8000/api/v1` by default.

### 3. Test the Connection

#### Option A: Use the Test View
Add `MicroserviceTestView()` to your app to run automated tests.

#### Option B: Manual Testing
1. Open your iOS app
2. Try searching for classical music (e.g., "Beethoven Moonlight Sonata")
3. The app should now use the local microservice instead of Lambda

## 🔧 Configuration

### Local Development
- **URL**: `http://localhost:8000/api/v1`
- **Health Check**: `http://localhost:8000/health`
- **API Docs**: `http://localhost:8000/docs`

### Production Deployment
Update `APIConfig.swift` to point to your deployed microservice URL.

## 📱 iOS App Changes

### Updated Files:
- `MusicSheetService.swift` - Now points to microservice
- `APIConfig.swift` - Configuration management
- `MicroserviceTestView.swift` - Test interface

### New Features Available:
1. **Classical Music Search** - IMSLP/Mutopia Project integration
2. **Audio Transcription** - Hum-to-notation (mock response)
3. **Melody Editing** - Natural language editing
4. **Music Recommendations** - AI-powered suggestions

## 🧪 Testing Endpoints

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Classical Music Search
```bash
curl -X POST "http://localhost:8000/api/v1/search-imslp" \
  -H "Content-Type: application/json" \
  -d '{"query": "Beethoven Moonlight Sonata", "user_id": "test"}'
```

### 3. Audio Transcription
```bash
curl -X POST "http://localhost:8000/api/v1/transcribe-audio" \
  -H "Content-Type: application/json" \
  -d '{"audio_file": "dGVzdA==", "audio_format": "wav", "user_id": "test", "duration_seconds": 10}'
```

### 4. Melody Editing
```bash
curl -X POST "http://localhost:8000/api/v1/edit-melody" \
  -H "Content-Type: application/json" \
  -d '{"abc_notation": "X:1\nT:Test\nM:4/4\nL:1/4\nK:C\nC D E F |", "edit_instruction": "change the second note to A", "user_id": "test"}'
```

## 🎯 Expected Results

### Classical Music Search
- ✅ Finds Beethoven's Moonlight Sonata
- ✅ Returns PDF URL from Mutopia Project
- ✅ Includes composer, title, opus information

### Audio Transcription
- ✅ Returns mock ABC notation
- ✅ Includes confidence score
- ✅ Detects key and time signature

### Melody Editing
- ✅ Changes notes based on natural language
- ✅ Maintains ABC notation structure
- ✅ Returns confidence score

## 🚨 Troubleshooting

### Connection Issues
1. **Check microservice is running**: `curl http://localhost:8000/health`
2. **Verify iOS simulator can reach localhost**: Use `127.0.0.1` instead of `localhost`
3. **Check firewall settings**: Ensure port 8000 is accessible

### API Errors
1. **Check logs**: Look at the microservice terminal output
2. **Verify JSON format**: Ensure request body matches expected format
3. **Test with curl**: Use the provided curl commands to test endpoints

### iOS App Issues
1. **Check APIConfig**: Verify the base URL is correct
2. **Test with MicroserviceTestView**: Use the test view to debug
3. **Check network permissions**: Ensure app can make HTTP requests

## 🔄 Switching Between Local and Production

### For Local Development:
```swift
// In APIConfig.swift
static let baseURL = "http://localhost:8000/api/v1"
```

### For Production:
```swift
// In APIConfig.swift
static let baseURL = "https://your-microservice-url.com/api/v1"
```

## 📊 Performance Comparison

| Feature | Lambda | Microservice |
|---------|--------|--------------|
| **Development Speed** | Slow (deploy each change) | Fast (hot reload) |
| **Local Testing** | Limited | Full local testing |
| **Debugging** | CloudWatch logs | Local logs |
| **Cost** | Pay per request | Pay for hosting |
| **Scalability** | Auto-scaling | Manual scaling |

The microservice provides much faster development and testing capabilities!
