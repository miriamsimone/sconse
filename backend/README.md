# Sconces Backend

This is the backend infrastructure for the Sconces music AI chat application.

## Setup

### Prerequisites

1. **AWS CLI** - Install and configure with your AWS credentials
2. **AWS SAM CLI** - For local testing and deployment
3. **Python 3.11** - Required for Lambda functions

### Environment Variables

Create a `.env` file in the `lambda` directory with the following variables:

```bash
OPENAI_API_KEY=your_openai_api_key_here
BRAVE_API_KEY=your_brave_search_api_key_here
FIREBASE_SERVICE_ACCOUNT=base64_encoded_firebase_service_account_json
```

### Installation

1. Navigate to the lambda directory:
```bash
cd backend/lambda
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Local Testing

1. Test individual components:
```bash
cd backend
python test_generate_sheet.py
```

2. Test with SAM local:
```bash
cd lambda
sam build
sam local start-api
```

### Deployment

1. Build the application:
```bash
cd lambda
sam build
```

2. Deploy with guided setup:
```bash
sam deploy --guided
```

3. Follow the prompts to configure:
   - Stack name: `sconces-backend`
   - AWS Region: `us-east-1` (or your preferred region)
   - Parameter values for API keys

## API Endpoints

Once deployed, you'll have the following endpoints:

- `POST /generate-sheet` - Generate sheet music from song name
- `POST /edit-chords` - Edit chord symbols in ABC notation
- `POST /search-imslp` - Search IMSLP for classical music
- `POST /recommend` - Get music recommendations

## Testing

Use curl or Postman to test the endpoints:

```bash
curl -X POST https://YOUR_API_GATEWAY_URL/generate-sheet \
  -H "Content-Type: application/json" \
  -d '{"song_name": "Twinkle Twinkle Little Star", "instrument": "C"}'
```

## Architecture

- **AWS Lambda** - Serverless compute for each endpoint
- **API Gateway** - REST API with CORS enabled
- **OpenAI GPT-4** - AI reconciliation and natural language processing
- **Brave Search API** - Web search for guitar tabs
- **Firebase Storage** - For IMSLP PDF images (Phase 4)

## Development Phases

1. ✅ **Phase 1**: Backend Infrastructure Setup
2. 🔄 **Phase 2**: Tab Search & Reconciliation (in progress)
3. ⏳ **Phase 3**: Transposition Service
4. ⏳ **Phase 4**: Chord Editing
5. ⏳ **Phase 5**: IMSLP Search
6. ⏳ **Phase 6**: Music Recommendations
7. ⏳ **Phase 7**: iOS Integration
8. ⏳ **Phase 8**: Testing & Polish
