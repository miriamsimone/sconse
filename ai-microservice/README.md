# AI Microservice - Docker Setup

This is the AI microservice for the Musician Chat App, providing natural language to sheet music generation and other AI-powered music features.

## Features

- ✅ **Classical Music Search**: IMSLP/Mutopia Project integration
- ✅ **Natural Language to Sheet Music**: Convert text descriptions to ABC notation
- 🔄 **Conversational Sheet Music Editing**: Edit ABC notation through natural language
- 🔄 **Multi-Agent Setlist Designer**: AI-powered concert planning
- ✅ **Audio Transcription**: Convert audio to music notation

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (required)
- Optional: Anthropic API key, Brave Search API key

### Setup

1. **Clone and navigate to the microservice directory:**
   ```bash
   cd ai-microservice
   ```

2. **Run the setup script:**
   ```bash
   ./setup.sh
   ```

3. **Edit the `.env` file** with your API keys:
   ```bash
   nano .env
   ```

4. **Restart the service:**
   ```bash
   docker-compose up --build
   ```

### Manual Setup

1. **Create environment file:**
   ```bash
   cp env.template .env
   # Edit .env with your API keys
   ```

2. **Build and start:**
   ```bash
   docker-compose up --build
   ```

3. **Test the service:**
   ```bash
   python3 ../test_docker_music_generation.py
   ```

## API Endpoints

### Health Check
- `GET /` - Service status
- `GET /health` - Detailed health check

### Music Generation
- `POST /api/v1/music/generate` - Generate sheet music from natural language
- `GET /api/v1/music/generate/test` - Test endpoint

### Classical Music Search
- `POST /api/v1/search-imslp` - Search IMSLP for classical music

### Other Features
- `POST /api/v1/transcribe-audio` - Audio to notation transcription
- `POST /api/v1/edit-melody` - Melody editing
- `POST /api/v1/recommend` - Music recommendations

## Example Usage

### Generate Sheet Music

```bash
curl -X POST "http://localhost:8000/api/v1/music/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Time signature 3/4, key F minor, eighth notes: A-flat, G, F",
    "user_id": "test_user"
  }'
```

### Search Classical Music

```bash
curl -X POST "http://localhost:8000/api/v1/search-imslp" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Moonlight Sonata Beethoven",
    "user_id": "test_user"
  }'
```

## Development

### View Logs
```bash
docker-compose logs -f
```

### Rebuild After Changes
```bash
docker-compose up --build
```

### Stop Service
```bash
docker-compose down
```

### Access Container Shell
```bash
docker-compose exec ai-microservice bash
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for LLM |
| `ANTHROPIC_API_KEY` | No | Anthropic API key (alternative LLM) |
| `BRAVE_API_KEY` | No | Brave Search API for IMSLP search |
| `FIREBASE_SERVICE_ACCOUNT` | No | Firebase for image storage |
| `OPENAI_MODEL` | No | OpenAI model (default: gpt-4) |
| `OPENAI_TEMPERATURE` | No | LLM temperature (default: 0.2) |

### Port Configuration

- **Service Port**: 8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

## Architecture

```
┌─────────────────────────────────────┐
│           Docker Container          │
│  ┌─────────────────────────────────┐│
│  │        FastAPI App              ││
│  │  ┌─────────────────────────────┐││
│  │  │     API Endpoints           │││
│  │  │  - Music Generation         │││
│  │  │  - Classical Search         │││
│  │  │  - Audio Transcription      │││
│  │  └─────────────────────────────┘││
│  │  ┌─────────────────────────────┐││
│  │  │     Services                │││
│  │  │  - LLM Service              │││
│  │  │  - ABC Validator            │││
│  │  │  - ABC Renderer             │││
│  │  │  - IMSLP Service            │││
│  │  └─────────────────────────────┘││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

## Troubleshooting

### Service Won't Start
1. Check if port 8000 is available
2. Verify API keys in `.env` file
3. Check Docker logs: `docker-compose logs`

### API Errors
1. Ensure OpenAI API key is valid
2. Check request format matches API documentation
3. Verify service is running: `curl http://localhost:8000/`

### Build Issues
1. Clear Docker cache: `docker system prune`
2. Rebuild from scratch: `docker-compose build --no-cache`

## Next Steps

1. **Test the service** with the provided test script
2. **Integrate with iOS app** using the API endpoints
3. **Add more AI features** like conversational editing
4. **Deploy to production** using Docker in cloud environment