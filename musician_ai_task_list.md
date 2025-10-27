# Implementation Task List: AI Features for Musician Chat App

## 🎉 IMPLEMENTATION STATUS: COMPLETED ✅

**All core AI features have been successfully implemented and tested!**

### ✅ Completed Features:
1. **Natural Language to Sheet Music Generation** - Working with OpenAI GPT-4
2. **Conversational Sheet Music Editing** - Advanced editing with note grouping and duration changes
3. **AI Concert Setlist Designer** - Collaborative setlist creation with group preferences
4. **Intelligent AI Request Routing** - Automatic intent detection and service routing
5. **Collaborative Setlist Design** - Chat-based preference gathering and parsing
6. **Enhanced Music Editing** - Note grouping, duration changes, composer avoidance
7. **Ordering Preferences** - Respects "start with bebop", "end with blues" requests

### 🚀 Ready for Production:
- **Docker Containerized** - Easy deployment and dependency management
- **API Documentation** - Complete endpoint documentation
- **Error Handling** - Comprehensive validation and error responses
- **Testing** - All features tested with real user scenarios

### 📱 Next Steps:
- iOS app integration (Phase 5)
- Production deployment
- User testing and feedback

---

## Current Project Structure (Already Exists)

```
messageAI/
├── ai-microservice/                    # ✅ EXISTING - FastAPI microservice
│   ├── app/
│   │   ├── main.py                     # ✅ EXISTING - FastAPI app
│   │   ├── config.py                   # ✅ EXISTING - Configuration
│   │   ├── api/
│   │   │   ├── imslp.py               # ✅ EXISTING - Classical music search
│   │   │   ├── transcribe_audio.py    # ✅ EXISTING - Audio transcription
│   │   │   ├── edit_melody.py         # ✅ EXISTING - Melody editing
│   │   │   └── recommend.py           # ✅ EXISTING - Recommendations
│   │   ├── services/
│   │   │   ├── imslp_service.py       # ✅ EXISTING - IMSLP search service
│   │   │   └── audio_service.py       # ✅ EXISTING - Audio processing
│   │   └── models/
│   │       ├── requests.py            # ✅ EXISTING - Request models
│   │       └── responses.py           # ✅ EXISTING - Response models
│   └── requirements.txt               # ✅ EXISTING - Dependencies
├── backend/lambda/                     # ✅ EXISTING - AWS Lambda functions
│   ├── handlers/
│   │   ├── search_imslp.py            # ✅ EXISTING - Working classical search
│   │   ├── generate_sheet.py          # ✅ EXISTING - Sheet generation
│   │   └── edit_chords.py             # ✅ EXISTING - Chord editing
│   └── services/
│       └── search_service.py          # ✅ EXISTING - Search functionality
└── messageAI/                         # ✅ EXISTING - iOS app
    ├── Services/
    │   ├── MusicSheetService.swift    # ✅ EXISTING - Sheet music service
    │   ├── APIConfig.swift            # ✅ EXISTING - API configuration
    │   └── MessageService.swift       # ✅ EXISTING - Chat service
    ├── ViewModels/
    │   └── ChatViewModel.swift        # ✅ EXISTING - Chat view model
    └── Views/
        └── Chat/                      # ✅ EXISTING - Chat interface
```

## Integration Strategy

**Key Insight**: We need to enhance the existing `ai-microservice` to include the new AI features while preserving the working classical music lookup functionality. The iOS app already has the infrastructure to call the microservice.

---

## Phase 1: Enhance Existing AI Microservice ✅ COMPLETED

### Task 1.1: Add LLM Integration to Existing Microservice ✅ COMPLETED
**Description**: Enhanced the existing `ai-microservice` with LLM capabilities

**Files to Create**:
- `ai-microservice/app/services/llm_service.py`
- `ai-microservice/app/services/abc_validator.py`
- `ai-microservice/app/services/abc_renderer.py`

**Files to Edit**:
- `ai-microservice/app/config.py` (add LLM API keys)
- `ai-microservice/requirements.txt` (add openai, anthropic, langchain)

**Key Requirements**:
- Support for both OpenAI and Claude APIs
- Token counting and cost tracking
- Rate limiting
- Error handling and retries
- Response caching mechanism

**Note**: The microservice already exists with FastAPI, CORS, and basic structure.

---

### Task 1.2: Add Database Support (Optional for MVP)
**Description**: Add database support for conversation history and music storage

**Files to Create**:
- `ai-microservice/app/models/database.py`
- `ai-microservice/app/migrations/001_initial_schema.sql`

**Files to Edit**:
- `ai-microservice/app/config.py` (add database connection string)
- `ai-microservice/requirements.txt` (add sqlalchemy, psycopg2, alembic)

**Key Requirements**:
- SQLAlchemy ORM setup
- Tables: music_documents, edit_history, setlist_sessions
- **Note**: Can be skipped for MVP - use in-memory storage initially

---

### Task 1.3: Add Redis Cache (Optional for MVP)
**Description**: Add Redis for conversation context and response caching

**Files to Create**:
- `ai-microservice/app/utils/cache.py`

**Files to Edit**:
- `ai-microservice/app/config.py` (add Redis connection string)
- `ai-microservice/requirements.txt` (add redis, redis-py)

**Key Requirements**:
- Redis connection pool
- TTL-based caching
- Conversation context storage
- **Note**: Can be skipped for MVP - use in-memory storage initially

---

## Phase 2: Natural Language to Sheet Music Generation ✅ COMPLETED

### Task 2.1: Create ABC Notation Validator
**Description**: Build validation service for ABC notation syntax

**Files to Create**:
- `ai-microservice/app/services/abc_validator.py`

**Files to Edit**:
- `ai-microservice/requirements.txt` (add music21 or abc-parser library)

**Key Requirements**:
- Syntax validation
- Musical logic validation (valid time signatures, key signatures)
- Error message generation
- Support for basic ABC notation features

---

### Task 2.2: Create ABC Notation Renderer
**Description**: Build service to convert ABC notation to visual sheet music

**Files to Create**:
- `ai-microservice/app/services/abc_renderer.py`

**Files to Edit**:
- `ai-microservice/requirements.txt` (add abcjs via node subprocess or use Python alternative)

**Key Requirements**:
- ABC to PNG/SVG conversion
- ABC to MIDI conversion (optional)
- Image storage/CDN upload
- Error handling for malformed ABC

---

### Task 2.3: Create Generation Prompts
**Description**: Design and implement LLM prompts for NL → ABC conversion

**Files to Create**:
- `ai-microservice/app/prompts/generation_prompts.py`
- `ai-microservice/app/prompts/__init__.py`

**Key Requirements**:
- System prompt with ABC notation expertise
- Few-shot examples (10-15 examples of NL → ABC)
- Input sanitization templates
- Structured output formatting
- Support for various musical elements (notes, durations, key, time signature)

---

### Task 2.4: Build Music Generation Endpoint
**Description**: Create API endpoint for natural language to ABC conversion

**Files to Create**:
- `ai-microservice/app/api/music_generation.py`

**Files to Edit**:
- `ai-microservice/app/main.py` (register new route)
- `ai-microservice/app/models/requests.py` (add request models)
- `ai-microservice/app/models/responses.py` (add response models)

**Key Requirements**:
- POST `/api/v1/music/generate` endpoint
- Request validation
- Call LLM service with generation prompt
- Validate ABC output
- Render sheet music
- Return ABC text + image URL
- **Integration**: Works alongside existing `/api/v1/search-imslp` endpoint

---

### Task 2.5: Add Music Generation Tests
**Description**: Create unit and integration tests

**Files to Create**:
- `ai-microservice/tests/test_music_generation.py`
- `ai-microservice/tests/fixtures/sample_inputs.json`
- `ai-microservice/tests/fixtures/sample_abc_outputs.txt`

**Key Requirements**:
- Test valid NL inputs → valid ABC
- Test invalid inputs → error handling
- Test ABC validation
- Test rendering pipeline
- Mock LLM responses for consistent testing

---

## Phase 3: Conversational Sheet Music Editing ✅ COMPLETED

### Task 3.1: Create Editing Prompts
**Description**: Design prompts for ABC notation editing

**Files to Create**:
- `ai-microservice/app/prompts/editing_prompts.py`

**Key Requirements**:
- System prompt for ABC editing expert
- Context window management (current ABC + history)
- Few-shot examples for various edit types:
  - Note modifications
  - Chord symbol additions
  - Lyric additions
  - Structural changes (repeats, transposition)
- Diff generation for showing changes

---

### Task 3.2: Build Edit History System (Optional for MVP)
**Description**: Version control for sheet music edits

**Files to Create**:
- `ai-microservice/app/models/edit_history.py`

**Key Requirements**:
- Store edit snapshots in memory (for MVP)
- Track edit instructions
- Support undo/redo
- Timestamp and user attribution
- **Note**: Can use in-memory storage for MVP

---

### Task 3.3: Build Music Editing Endpoint
**Description**: Create API endpoint for editing ABC notation

**Files to Create**:
- `ai-microservice/app/api/music_editing.py`

**Files to Edit**:
- `ai-microservice/app/main.py` (register new route)
- `ai-microservice/app/models/requests.py` (add request models)
- `ai-microservice/app/models/responses.py` (add response models)

**Key Requirements**:
- POST `/api/v1/music/edit` endpoint
- Retrieve current ABC from request
- Build context with conversation history
- Call LLM with editing prompt
- Validate edited ABC
- Render updated sheet music
- Return before/after comparison
- **Integration**: Works alongside existing endpoints

---

### Task 3.4: Add Conversation Memory Management (Optional for MVP)
**Description**: Manage conversation context for multi-turn edits

**Files to Create**:
- `ai-microservice/app/services/conversation_manager.py`

**Key Requirements**:
- Store conversation history in memory (for MVP)
- Sliding window for context (last N messages)
- Clear/reset conversation endpoint
- **Note**: Can use in-memory storage for MVP

---

### Task 3.5: Add Music Editing Tests
**Description**: Test editing functionality

**Files to Create**:
- `ai-microservice/tests/test_music_editing.py`
- `ai-microservice/tests/fixtures/edit_scenarios.json`

**Key Requirements**:
- Test various edit types (chords, lyrics, notes, transposition)
- Test multi-step edits with context
- Test invalid edit instructions
- Test undo/redo functionality

---

## Phase 4: Multi-Agent Setlist Designer ✅ COMPLETED

### Task 4.1: Set Up LangChain Agent Framework
**Description**: Configure LangChain for multi-agent orchestration

**Files to Create**:
- `backend/src/agents/__init__.py`

**Files to Edit**:
- `backend/requirements.txt` (add langchain, langchain-openai, langchain-anthropic)

**Key Requirements**:
- LangChain agent executor setup
- Memory management (ConversationBufferMemory)
- Tool/function calling support
- Agent state management

---

### Task 4.2: Build Music Knowledge Base
**Description**: Create service for song metadata and music theory knowledge

**Files to Create**:
- `backend/src/services/music_knowledge_base.py`
- `backend/src/models/setlist.py`

**Files to Edit**:
- `backend/migrations/003_song_library.sql`

**Key Requirements**:
- Query song metadata (key, tempo, duration, style)
- Calculate key transitions
- Analyze pacing (energy flow)
- Compute set duration
- Store/retrieve band repertoire

---

### Task 4.3: Build Coordinator Agent
**Description**: Create agent for gathering preferences from band members

**Files to Create**:
- `backend/src/agents/coordinator_agent.py`

**Files to Edit**:
- `backend/src/prompts/setlist_prompts.py`

**Key Requirements**:
- Ask questions to band members
- Parse and categorize responses
- Track who has responded
- Manage conversation flow
- Tools: ask_member, collect_responses, check_completion

---

### Task 4.4: Build Synthesis Agent
**Description**: Create agent for generating setlist proposals

**Files to Create**:
- `backend/src/agents/synthesis_agent.py`

**Files to Edit**:
- `backend/src/prompts/setlist_prompts.py`

**Key Requirements**:
- Aggregate member preferences
- Query music knowledge base
- Apply constraints (duration, pacing, keys)
- Generate ranked setlist options
- Provide rationale for selections
- Tools: query_kb, analyze_preferences, validate_constraints

---

### Task 4.5: Build Music Knowledge Agent
**Description**: Specialized agent for music theory and song information

**Files to Create**:
- `backend/src/agents/music_kb_agent.py`

**Key Requirements**:
- Retrieve song information
- Answer music theory questions
- Calculate transitions
- Suggest alternatives based on criteria
- Tools: get_song_info, find_similar_songs, calculate_transitions

---

### Task 4.6: Build Setlist Session Orchestrator
**Description**: Coordinate multi-agent workflow for setlist design

**Files to Create**:
- `backend/src/services/setlist_orchestrator.py`

**Key Requirements**:
- Manage agent collaboration
- State machine for session phases (gathering → synthesis → iteration)
- Handle timeouts and errors
- Support asynchronous responses
- Broadcast updates to all participants

---

### Task 4.7: Build Setlist Designer Endpoints
**Description**: Create API endpoints for setlist design sessions

**Files to Create**:
- `backend/src/routes/setlist_designer.py`

**Files to Edit**:
- `backend/src/main.py` (register routes)

**Key Requirements**:
- POST `/api/v1/setlist/session` - Create session
- POST `/api/v1/setlist/session/{id}/respond` - Submit member response
- GET `/api/v1/setlist/session/{id}` - Get session status
- POST `/api/v1/setlist/session/{id}/feedback` - Provide feedback on proposal
- POST `/api/v1/setlist/session/{id}/finalize` - Accept setlist

---

### Task 4.8: Add Setlist Designer Tests
**Description**: Test multi-agent system

**Files to Create**:
- `backend/tests/test_setlist_designer.py`
- `backend/tests/test_agent_coordination.py`
- `backend/tests/fixtures/band_scenarios.json`

**Key Requirements**:
- Test full workflow: question → response → synthesis
- Test agent coordination
- Test knowledge base queries
- Test constraint handling
- Test feedback iteration
- Mock agent responses

---

## Phase 5: iOS Integration - Enhance Existing Chat Interface

### UI Architecture Overview
All AI features are accessed through the existing chat interface with:
- **Regular Send Button**: Sends messages to group chat members (✅ EXISTING)
- **AI Assistant Button**: Sends messages to AI microservice for music operations (NEW)
- **AI Bot as Chat Member**: For setlist design, AI appears as a participant in the group chat (NEW)

### Task 5.1: Enhance Existing AI Service Layer ✅ PARTIALLY DONE
**Description**: Enhance the existing MusicSheetService to handle all AI features

**Files to Edit**:
- `messageAI/Services/MusicSheetService.swift` (✅ EXISTING - enhance)
- `messageAI/Services/APIConfig.swift` (✅ EXISTING - already points to microservice)

**Files to Create**:
- `messageAI/Services/AIService.swift` (new comprehensive AI service)
- `messageAI/Services/AIMessageRouter.swift` (message routing logic)

**Key Requirements**:
- REST API client with URLSession (✅ EXISTING)
- Request/response models matching backend API
- Error handling (✅ EXISTING)
- Loading states (✅ EXISTING)
- **Integration**: Works with existing MusicSheetService

---

### Task 5.2: Enhance Existing Data Models ✅ PARTIALLY DONE
**Description**: Enhance existing models for new AI features

**Files to Edit**:
- `messageAI/Models/SheetMusicAttachment.swift` (✅ EXISTING - enhance)
- `messageAI/Models/Message.swift` (✅ EXISTING - add AI message types)

**Files to Create**:
- `messageAI/Models/ABCNotation.swift`
- `messageAI/Models/EditHistory.swift`
- `messageAI/Models/AIMessage.swift`
- `messageAI/Models/Setlist.swift`

**Key Requirements**:
- Codable conformance for JSON parsing (✅ EXISTING pattern)
- Computed properties for display
- Message type discrimination (human vs AI)
- **Integration**: Works with existing message system

---

### Task 5.3: Add AI Button to Existing Chat Input ✅ EXISTING STRUCTURE
**Description**: Modify existing chat input to support dual-send functionality

**Files to Edit**:
- `messageAI/Views/Chat/MessageInputView.swift` (✅ EXISTING - enhance)
- `messageAI/ViewModels/ChatViewModel.swift` (✅ EXISTING - enhance)

**Files to Create**:
- `messageAI/Views/Components/DualSendButton.swift`

**Key Requirements**:
- Keep existing "Send" button for group chat messages (✅ EXISTING)
- Add "AI Assistant" button (icon: sparkle/wand) next to send button
- Button enables when text is entered
- Visual feedback showing which mode is active
- **Integration**: Works with existing ChatViewModel

**UI Layout**:
```
┌─────────────────────────────────────────────────┐
│  [Text Input Field...                    ]      │
│                                    [Send] [✨AI] │
└─────────────────────────────────────────────────┘
```

---

### Task 5.4: Implement AI Message Routing ✅ EXISTING FOUNDATION
**Description**: Route messages to AI microservice when AI button is pressed

**Files to Edit**:
- `messageAI/ViewModels/ChatViewModel.swift` (✅ EXISTING - enhance)
- `messageAI/Services/MessageService.swift` (✅ EXISTING - enhance)

**Files to Create**:
- `messageAI/Services/AIMessageRouter.swift`

**Key Requirements**:
- Detect message intent (music generation, editing, classical music retrieval)
- Route to appropriate AI microservice endpoint
- Show loading state in chat (typing indicator) (✅ EXISTING)
- Display AI responses inline in chat (✅ EXISTING)
- Handle errors gracefully with user-friendly messages (✅ EXISTING)

**Message Type Detection**:
- Classical music query: "get [composer] [piece name]" → `/api/v1/search-imslp` (✅ EXISTING)
- Music generation: Natural language with musical terms → `/api/v1/music/generate` (NEW)
- Music editing: "edit [instruction]" or detected context → `/api/v1/music/edit` (NEW)
- General AI: Other queries → general assistant (NEW)

---

### Task 5.5: Create Inline Sheet Music Display
**Description**: Display rendered sheet music within chat messages

**Files to Create**:
- `ios/MusicianChat/Views/Components/InlineSheetMusicView.swift`
- `ios/MusicianChat/Views/Components/ABCNotationCard.swift`

**Files to Edit**:
- `ios/MusicianChat/Views/ChatMessageCell.swift` (existing)

**Key Requirements**:
- Display sheet music image within chat bubble
- Tap to expand full screen
- Zoom/pan in full screen mode
- Show ABC notation as collapsible text
- Download/save button
- Share to chat button
- "Edit this music" quick action button (triggers AI edit mode)

**Message Layout**:
```
┌────────────────────────────────────┐
│ AI Assistant                   Now │
│                                    │
│ Here's your music:                 │
│ ┌────────────────────────────┐    │
│ │   [Sheet Music Image]      │    │
│ │                            │    │
│ └────────────────────────────┘    │
│ [Show ABC] [Edit] [Save] [Share]  │
└────────────────────────────────────┘
```

---

### Task 5.6: Implement AI Edit Mode Context
**Description**: Track music editing context in conversation

**Files to Create**:
- `ios/MusicianChat/Models/MusicEditContext.swift`

**Files to Edit**:
- `ios/MusicianChat/ViewModels/ChatViewModel.swift` (existing)

**Key Requirements**:
- Store current music being edited in chat context
- Show context indicator when in edit mode
- "Edit this" button on sheet music enters edit mode
- All subsequent AI messages edit that music until context cleared
- Visual indicator showing which music is being edited
- "Done editing" button to clear context

**Edit Mode UI Indicator**:
```
┌────────────────────────────────────────────────┐
│ Editing: "Untitled Melody"            [Done X] │
└────────────────────────────────────────────────┘
│  [Text Input: "Add chord symbols Fm, Cm..." ]  │
│                                  [Send] [✨AI]  │
└────────────────────────────────────────────────┘
```

---

### Task 5.7: Add AI Bot as Virtual Chat Member
**Description**: Implement AI bot that appears as a participant for setlist design

**Files to Create**:
- `ios/MusicianChat/Models/AIBotMember.swift`
- `ios/MusicianChat/Services/SetlistAIBotService.swift`

**Files to Edit**:
- `ios/MusicianChat/Models/ChatMember.swift` (existing)
- `ios/MusicianChat/ViewModels/ChatViewModel.swift` (existing)

**Key Requirements**:
- AI bot appears in member list with special badge/icon
- Bot has profile (name: "Setlist Assistant", avatar: music note icon)
- Bot can be @mentioned in regular chat
- Bot responds to regular Send button (no AI button needed)
- Bot initiates setlist design sessions
- Bot asks questions to all members
- Bot synthesizes responses and posts proposals
- Members can reply with regular chat messages
- Bot tracks conversation state

**Implementation Details**:
- AI bot member has `isBot: true` flag
- Messages to/from bot route through setlist designer API
- Bot messages styled differently (subtle background color)
- Bot typing indicator when processing
- Bot can send structured messages (setlist proposals with special UI)

**Bot Interaction Flow**:
```
┌────────────────────────────────────────────────┐
│ 🎵 Setlist Assistant              [Bot Badge] │
│ Let's design your setlist! What songs would    │
│ you like to perform?                           │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ John (You)                                     │
│ I'd like to do "Take Five" and "Blue Bossa"   │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ 🎵 Setlist Assistant                           │
│ Great choices! Here's a proposed setlist:      │
│ ┌──────────────────────────────────────────┐  │
│ │ 1. Take Five (Medium swing)              │  │
│ │ 2. Cantaloupe Island (Funk)              │  │
│ │ 3. Blue Bossa (Latin)                    │  │
│ └──────────────────────────────────────────┘  │
│ [👍 Approve] [💬 Suggest Changes]              │
└────────────────────────────────────────────────┘
```

---

### Task 5.8: Create Setlist Proposal Card
**Description**: Special message card for displaying setlist proposals

**Files to Create**:
- `ios/MusicianChat/Views/Components/SetlistProposalCard.swift`

**Key Requirements**:
- Display setlist in structured format
- Show song order, titles, descriptions
- Estimated duration per song
- Rationale for ordering
- Interactive buttons: Approve, Suggest Changes, View Details
- Voting indicators (if multiple members)
- Visual distinction from regular chat messages

---

### Task 5.9: Add Quick Action Buttons
**Description**: Context-aware quick actions in chat input

**Files to Create**:
- `ios/MusicianChat/Views/Components/AIQuickActions.swift`

**Files to Edit**:
- `ios/MusicianChat/Views/ChatInputView.swift` (existing)

**Key Requirements**:
- Show relevant quick action suggestions above keyboard
- Context-aware (change based on conversation state)
- Examples:
  - Default: "Find Classical Music", "Create Sheet Music"
  - When sheet music visible: "Edit Notes", "Add Chords", "Add Lyrics", "Transpose"
  - In setlist mode: "Suggest Songs", "View Full Setlist"
- Tapping quick action populates text input with template
- Swipe to see more actions

**Quick Actions UI**:
```
┌────────────────────────────────────────────────┐
│ < 🎼 Create Music  📝 Add Chords  🔄 Transpose >│
└────────────────────────────────────────────────┘
│  [Text Input Field...                    ]      │
│                                    [Send] [✨AI] │
└────────────────────────────────────────────────┘
```

---

### Task 5.10: Implement AI Response Streaming
**Description**: Show AI responses as they're generated (typing effect)

**Files to Create**:
- `ios/MusicianChat/Services/AIStreamingService.swift`

**Files to Edit**:
- `ios/MusicianChat/ViewModels/ChatViewModel.swift` (existing)

**Key Requirements**:
- SSE (Server-Sent Events) or WebSocket connection to backend
- Display partial AI responses as they arrive
- Typing indicator while waiting
- Smooth text appearance animation
- Handle connection interruptions gracefully

---

### Task 5.11: Add AI Feature Discovery
**Description**: Help users discover AI features naturally

**Files to Create**:
- `ios/MusicianChat/Views/Components/AIFeatureHint.swift`

**Files to Edit**:
- `ios/MusicianChat/Views/ChatView.swift` (existing)

**Key Requirements**:
- Show subtle hints on first use
- "Try the AI button to generate sheet music" tooltip
- "Tap sheet music to edit it" hint
- Dismissible tips
- Context-sensitive help
- Empty state with AI feature examples

**First-Time User Experience**:
```
┌────────────────────────────────────────────────┐
│                 (Empty Chat)                    │
│                                                 │
│  💡 Try asking the AI Assistant to:             │
│  • Find classical music: "Get Beethoven 5th"   │
│  • Create music: "Quarter notes: C D E F"      │
│  • Start setlist: "@Setlist Assistant help"    │
│                                                 │
│               [✨ Try AI Features]              │
└────────────────────────────────────────────────┘
```

---

### Task 5.12: Implement Offline Message Queue
**Description**: Queue AI requests when offline

**Files to Create**:
- `ios/MusicianChat/Services/OfflineQueueManager.swift`

**Files to Edit**:
- `ios/MusicianChat/Services/AIService.swift`

**Key Requirements**:
- Detect offline state
- Queue AI messages locally
- Show "Will send when online" indicator
- Retry when connection restored
- Preserve order
- Handle failures gracefully

---

## Phase 6: Testing & Quality Assurance

### Task 6.1: End-to-End Testing
**Description**: Test complete workflows across backend and iOS

**Files to Create**:
- `backend/tests/test_e2e_music_generation.py`
- `backend/tests/test_e2e_music_editing.py`
- `backend/tests/test_e2e_setlist_designer.py`

**Key Requirements**:
- Test full music generation flow
- Test multi-step editing conversation
- Test complete setlist design session
- Test error scenarios
- Test concurrent users

---

### Task 6.2: Performance Testing
**Description**: Ensure system meets response time requirements

**Files to Create**:
- `backend/tests/performance/load_test.py`
- `backend/tests/performance/benchmark.py`

**Key Requirements**:
- Load testing with Locust or similar
- Measure API response times
- Test LLM caching effectiveness
- Identify bottlenecks
- Test under concurrent load

---

### Task 6.3: User Acceptance Testing
**Description**: Test with real musicians

**Files to Create**:
- `docs/uat_test_plan.md`
- `docs/uat_feedback_template.md`

**Key Requirements**:
- Create test scenarios for musicians
- Collect feedback on:
  - Natural language understanding
  - ABC notation quality
  - Edit accuracy
  - Setlist suggestions quality
- Document pain points
- Gather feature requests

---

## Phase 7: Deployment & Documentation

### Task 7.1: Deploy Backend to Cloud
**Description**: Set up production deployment

**Files to Create**:
- `backend/deploy/kubernetes.yaml` (if using K8s)
- `backend/deploy/terraform/main.tf` (if using Terraform)
- `.github/workflows/deploy.yml` (CI/CD)

**Key Requirements**:
- Container deployment (AWS ECS/Google Cloud Run/Azure)
- Environment variable configuration
- Database migrations
- Redis setup
- Load balancer configuration
- SSL/TLS certificates
- Monitoring and logging

---

### Task 7.2: Create API Documentation
**Description**: Document all API endpoints

**Files to Create**:
- `docs/api/README.md`
- `docs/api/music_generation.md`
- `docs/api/music_editing.md`
- `docs/api/setlist_designer.md`

**Files to Edit**:
- `backend/src/main.py` (add OpenAPI/Swagger documentation)

**Key Requirements**:
- OpenAPI/Swagger spec
- Request/response examples
- Error codes documentation
- Authentication guide
- Rate limiting info

---

### Task 7.3: Create Developer Documentation
**Description**: Guide for maintaining and extending the system

**Files to Create**:
- `docs/developer/architecture.md`
- `docs/developer/setup.md`
- `docs/developer/prompt_engineering.md`
- `docs/developer/adding_features.md`
- `README.md`

**Key Requirements**:
- Architecture diagrams
- Local setup instructions
- How to modify prompts
- How to add new agents
- Code style guide
- Testing guide

---

### Task 7.4: Create User Documentation
**Description**: Help documentation for musicians using the app

**Files to Create**:
- `docs/user/music_generation_guide.md`
- `docs/user/editing_guide.md`
- `docs/user/setlist_designer_guide.md`
- `docs/user/faq.md`

**Key Requirements**:
- Natural language syntax examples
- Video tutorials/GIFs
- Common edit commands
- Troubleshooting guide
- Best practices

---

## Phase 8: Monitoring & Optimization

### Task 8.1: Set Up Monitoring
**Description**: Track system health and performance

**Files to Create**:
- `backend/src/utils/metrics.py`
- `backend/src/middleware/logging.py`

**Files to Edit**:
- `backend/src/main.py` (add metrics middleware)

**Key Requirements**:
- Request/response logging
- LLM usage tracking (tokens, costs)
- Error rate monitoring
- Response time tracking
- Database query performance
- Integration with DataDog/Grafana/CloudWatch

---

### Task 8.2: Implement Cost Optimization
**Description**: Reduce LLM API costs

**Files to Create**:
- `backend/src/services/prompt_optimizer.py`
- `backend/src/services/response_cache.py`

**Files to Edit**:
- `backend/src/services/llm_service.py`

**Key Requirements**:
- Aggressive response caching
- Prompt compression techniques
- Use smaller models for simple tasks
- Batch requests where possible
- Token usage alerts
- Cost reporting dashboard

---

### Task 8.3: Prompt Engineering Refinement
**Description**: Improve prompt quality based on usage data

**Files to Edit**:
- `backend/src/prompts/generation_prompts.py`
- `backend/src/prompts/editing_prompts.py`
- `backend/src/prompts/setlist_prompts.py`

**Key Requirements**:
- Analyze failed generations
- Add more few-shot examples
- Refine system prompts
- A/B test prompt variations
- Document prompt versioning

---

## Appendix: Dependencies Summary

### Backend Python Requirements
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
redis==5.0.1
openai==1.3.5
anthropic==0.7.0
langchain==0.0.340
langchain-openai==0.0.2
langchain-anthropic==0.1.0
pydantic==2.5.0
python-dotenv==1.0.0
python-multipart==0.0.6
music21==9.1.0
Pillow==10.1.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

### iOS Swift Dependencies
```
No external dependencies required (use built-in URLSession)
Optional: Alamofire for enhanced networking
```

---

## Key Integration Points

### ✅ Already Working
1. **Classical Music Lookup**: IMSLP/Mutopia Project search via `ai-microservice/app/api/imslp.py`
2. **iOS Chat Interface**: Complete chat system with message handling
3. **API Configuration**: iOS app already configured to call microservice
4. **Sheet Music Display**: Basic sheet music attachment system

### 🔄 Integration Strategy
1. **Preserve Existing Functionality**: Keep the working classical music lookup
2. **Enhance AI Microservice**: Add new endpoints alongside existing ones
3. **Extend iOS Services**: Enhance existing MusicSheetService and ChatViewModel
4. **Unified Chat Interface**: Add AI button to existing chat input

### 🎯 Priority Order
1. **Phase 1**: Add LLM integration to microservice (foundation)
2. **Phase 2**: Natural language to ABC generation (core feature)
3. **Phase 5**: iOS integration (user-facing features)
4. **Phase 3**: Conversational editing (advanced feature)
5. **Phase 4**: Setlist designer (complex multi-agent system)

### 💡 Key Benefits of This Approach
- **Leverages Existing Work**: Builds on working classical music lookup
- **Minimal Disruption**: Enhances existing chat interface rather than replacing it
- **Incremental Development**: Each phase adds value independently
- **Proven Architecture**: Uses existing, working patterns

## Notes

- **AI-Assisted Development**: These tasks are designed to be completed with AI coding assistance (Claude Code, GitHub Copilot, etc.)
- **No Time Estimates**: Task complexity varies; use AI to accelerate implementation
- **Iterative Development**: Test each phase before moving to the next
- **Parallel Work**: Some tasks can be done concurrently (e.g., iOS views while backend endpoints are being built)
- **Flexibility**: Adjust task order based on priorities and dependencies
- **Existing Foundation**: Leverage the working classical music lookup as the foundation for all new AI features