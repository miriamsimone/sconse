# Sconse - AI-Powered Musician Chat App

A comprehensive iOS chat application for musicians with integrated AI capabilities for music generation, editing, and collaborative setlist design.

## 🎵 Features

### Core Chat Functionality
- **Real-time Messaging**: Instant messaging with Firebase integration
- **Group Conversations**: Create and manage group chats
- **File Sharing**: Share images, audio, and sheet music
- **Push Notifications**: Real-time notifications for new messages

### AI Music Features
- **🎼 Classical Music Retrieval**: Search and find sheet music from IMSLP
- **🎹 Natural Language to Sheet Music**: Generate ABC notation from text descriptions
- **✏️ Conversational Music Editing**: Edit sheet music through natural language commands
- **🎪 AI Concert Setlist Designer**: Create collaborative setlists with group preferences
- **🧠 Intelligent AI Routing**: Automatically route requests to the appropriate AI service

### Collaborative Features
- **👥 Group Preference Gathering**: AI asks group members for setlist preferences
- **📝 Natural Language Parsing**: Parse preferences from plain text responses
- **🎯 Smart Filtering**: Respect composer/genre preferences and avoidances
- **📊 Ordering Preferences**: Honor "start with" and "end with" requests

## 🏗️ Architecture

### iOS App (Swift/SwiftUI)
- **Frontend**: SwiftUI-based chat interface
- **Backend Integration**: Firebase for real-time data
- **AI Integration**: RESTful API calls to AI microservice
- **Models**: Custom data models for messages, attachments, and AI responses

### AI Microservice (Python/FastAPI)
- **Framework**: FastAPI with Docker containerization
- **LLM Integration**: OpenAI GPT-4 and Anthropic Claude
- **Music Processing**: ABC notation validation and rendering
- **Multi-Agent System**: Specialized agents for different music tasks

### Backend Services
- **AWS Lambda**: Existing classical music search functionality
- **Firebase**: Real-time database and authentication
- **Docker**: Containerized AI microservice deployment

## 🚀 Quick Start

### Prerequisites
- iOS 15.0+ / macOS 12.0+
- Xcode 14.0+
- Python 3.11+
- Docker (for AI microservice)

### iOS App Setup
1. Clone the repository
2. Open `messageAI.xcodeproj` in Xcode
3. Add your Firebase configuration file
4. Build and run on simulator or device

### AI Microservice Setup
1. Navigate to `ai-microservice/` directory
2. Copy `.env.template` to `.env` and add your API keys
3. Build and run with Docker:
   ```bash
   docker build -t sconse-ai .
   docker run -p 8000:8000 sconse-ai
   ```

## 📱 Usage Examples

### Music Generation
```
User: "Create a jazz ballad in C major"
AI: Generates ABC notation and renders sheet music
```

### Music Editing
```
User: "Group the first four notes together"
AI: Applies beaming to the specified notes
```

### Setlist Design
```
User: "Plan a 60-minute jazz setlist for our quartet"
AI: Asks group members for preferences, then generates collaborative setlist
```

## 🔧 API Endpoints

### AI Router
- `POST /api/v1/ai/route-and-execute` - Intelligent request routing

### Music Generation
- `POST /api/v1/music/generate` - Generate sheet music from text
- `POST /api/v1/music/edit` - Edit existing sheet music

### Setlist Design
- `POST /api/v1/setlist/design` - Create setlist with preferences
- `POST /api/v1/setlist/chat` - Collaborative setlist design

### Classical Music
- `POST /api/v1/imslp/search` - Search IMSLP database

## 📁 Project Structure

```
sconse/
├── messageAI/                 # iOS app source code
│   ├── Models/               # Data models
│   ├── Services/            # Business logic
│   ├── Views/               # SwiftUI views
│   └── ViewModels/          # MVVM view models
├── ai-microservice/          # AI microservice
│   ├── app/
│   │   ├── api/             # FastAPI endpoints
│   │   ├── services/        # AI services
│   │   ├── models/          # Pydantic models
│   │   └── prompts/         # LLM prompts
│   ├── Dockerfile           # Container configuration
│   └── requirements.txt     # Python dependencies
├── backend/                  # AWS Lambda functions
└── docs/                     # Documentation
```

## 🛠️ Development

### Adding New AI Features
1. Create new service in `ai-microservice/app/services/`
2. Add API endpoint in `ai-microservice/app/api/`
3. Update AI router for intelligent routing
4. Add iOS integration in `messageAI/Services/`

### Testing
- **iOS**: Unit tests and UI tests in Xcode
- **AI Service**: API tests with pytest
- **Integration**: End-to-end testing with Docker

## 📚 Documentation

- [Product Requirements Document](musician_chat_ai_prd.md)
- [Task List](musician_ai_task_list.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Quick Start Guide](QUICK_START.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **IMSLP**: International Music Score Library Project
- **OpenAI**: GPT-4 for natural language processing
- **Anthropic**: Claude for AI assistance
- **Firebase**: Real-time database and authentication
- **ABC Notation**: Text-based music notation standard

## 📞 Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Contact the development team
- Check the documentation for common solutions

---

**Built with ❤️ for musicians by musicians**
