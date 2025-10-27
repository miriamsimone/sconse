# Product Requirements Document: AI Features for Musician Chat App

## Executive Summary

This document outlines AI-powered features for an iOS chat application designed for musicians (band leaders, teachers, students, band members) to enhance collaboration through intelligent music notation, editing, and concert planning capabilities.

---

## 1. Overview

### 1.1 Product Context
- **Platform**: iOS mobile application
- **Target Users**: Musicians, band leaders, teachers, students
- **Core Function**: Chat-based collaboration with AI-enhanced music features

### 1.2 Key AI Features
1. **Classical Music Retrieval** ✅ (Implemented)
2. **Natural Language to Sheet Music Generation** ✅ (Implemented)
3. **Conversational Sheet Music Editing** ✅ (Implemented)
4. **AI Concert Setlist Designer** ✅ (Implemented)
5. **Intelligent AI Request Routing** ✅ (Implemented)
6. **Collaborative Setlist Design** ✅ (Implemented)

---

## 2. Feature Specifications

### 2.1 Feature 1: Classical Music Retrieval ✅
**Status**: Implemented

**Description**: Users can request classical music pieces, and the system retrieves free sheet music from Mutopia Project.

**User Flow**:
- User asks: "Can I get the sheet music for Beethoven's Moonlight Sonata?"
- System fetches and returns free PDF/notation from Mutopia Project

---

### 2.2 Feature 2: Natural Language to Sheet Music ✅
**Status**: Implemented

**Problem Statement**: Audio-to-MIDI transcription (using tools like Crepe) produces unreliable results, making the transcription → MIDI → notation pipeline challenging.

**Implemented Solution**: Skip audio transcription entirely. Allow users to dictate music using natural language, which gets converted to ABC notation using OpenAI GPT-4.

#### 2.2.1 User Flow

**Input Example**:
```
"Time signature 3/4, key F minor, 
eighth notes: A-flat, G, F, 
eighth notes: A-flat, B-flat, C, D-flat, 
quarter note: C"
```

**Processing**:
1. User sends natural language description in chat
2. Message sent to LLM API (GPT-4 or Claude) with structured prompt
3. LLM converts to ABC notation
4. System renders ABC notation as visual sheet music
5. Returns rendered image + ABC text to user

**Output (ABC Notation)**:
```abc
X:1
T:Untitled
M:3/4
K:Fm
L:1/8
A2G2F2| A/2B/2c/2_d/2 c2|
```

#### 2.2.2 Technical Requirements

**Input Processing**:
- Accept natural language descriptions via chat interface
- Support musical terminology (notes, durations, key signatures, time signatures)
- Handle common notation: whole, half, quarter, eighth, sixteenth notes
- Support accidentals: sharp, flat, natural

**Output Format**:
- Primary: ABC notation (text format)
- Secondary: Rendered sheet music image (generated from ABC)

**Validation**:
- Verify ABC syntax is valid before rendering
- Provide error feedback for invalid musical structures

---

### 2.3 Feature 3: Conversational Sheet Music Editing ✅
**Status**: Implemented

**Description**: Allow users to modify existing ABC notation through natural language commands.

#### 2.3.1 User Flow

**Starting Context**: User has generated or uploaded ABC notation

**Example Interactions**:
- "Add chord symbols: Fm, Cm, Db, C7"
- "Change the first note to a half note"
- "Add lyrics: 'This is my song'"
- "Transpose up a major third"
- "Change time signature to 4/4"
- "Make measures 2-4 repeat"

**Processing**:
1. User sends edit command
2. System sends current ABC notation + edit instruction to LLM
3. LLM returns modified ABC notation
4. System validates and renders updated sheet music
5. User sees before/after comparison

#### 2.3.2 Supported Edit Operations

**Notation Edits**:
- Modify note pitches
- Change note durations
- Add/remove/modify rests
- Transpose passages

**Metadata Edits**:
- Add/edit chord symbols
- Add/edit lyrics
- Change key signature
- Change time signature
- Add dynamics markings
- Add articulations (staccato, legato, etc.)

**Structural Edits**:
- Add repeat signs
- Create multiple voices
- Add pickup measures
- Create multiple parts

#### 2.3.3 Technical Requirements

**Context Management**:
- Maintain current ABC notation state in conversation
- Support multi-step edits with conversation history
- Allow undo/redo of changes

**Version Control**:
- Store edit history per sheet music document
- Allow users to revert to previous versions

---

### 2.4 Feature 4: AI Concert Setlist Designer ✅
**Status**: Implemented

**Description**: Multi-agent system that collaborates with band members to design concert setlists through chat-based interaction.

#### 2.4.1 User Flow

**Initiation**:
1. Band leader creates "Setlist Planning Session" in group chat
2. AI agent introduces itself and the process

**Information Gathering**:
1. AI asks each band member individually (or in group):
   - "What songs would you like to perform?"
   - "What's your comfort level with each suggestion?"
   - "Any special considerations? (solos, vocals, technical difficulty)"
   - "What mood/theme should the concert have?"
   - "How long should the concert be?"

**Synthesis**:
1. AI aggregates all responses
2. Considers factors:
   - Song difficulty and member preferences
   - Pacing (fast/slow, loud/quiet variety)
   - Total duration
   - Key transitions
   - Showcasing different members
   - Thematic coherence

**Output**:
1. Proposed setlist with rationale
2. Alternative options
3. Estimated timing for each song
4. Transition notes
5. Potential issues flagged

**Iteration**:
- Band members provide feedback
- AI revises setlist based on input
- Process repeats until consensus

#### 2.4.2 Example Interaction

```
AI: "I'm gathering setlist ideas for our upcoming concert! 
     What songs would each of you like to perform?"

Member 1: "I'd love to do 'Take Five' - we haven't played it in a while"

Member 2: "How about 'Blue Bossa'? And maybe a ballad like 'Body and Soul'"

Member 3: "I'm comfortable with anything in the medium tempo range"

AI: "Thanks! A few questions:
     - How long should the concert be?
     - Any theme or mood you're going for?"

Member 1: "About 60 minutes, and let's make it upbeat jazz"

AI: "Based on your input, here's a proposed setlist:

1. Opening: 'Take Five' (7 min) - Medium swing, familiar
2. 'Cantaloupe Island' (6 min) - Funky, high energy
3. 'Blue Bossa' (8 min) - Latin groove, nice contrast
4. 'All Blues' (9 min) - Modal, features Member 3 solo
5. 'Body and Soul' (10 min) - Ballad, emotional centerpiece
6. Closing: 'Watermelon Man' (8 min) - Upbeat, crowd-pleaser

Total: ~48 minutes + announcements = ~60 min

Rationale:
- Opens strong with requested 'Take Five'
- Pacing varies: medium → upbeat → Latin → modal → ballad → high energy
- Keys transition smoothly (mostly Eb and F blues/jazz keys)
- Showcases different members
- Includes requested songs

Thoughts?"
```

#### 2.4.3 Technical Requirements

**Multi-Agent Architecture**:
- **Coordinator Agent**: Manages conversation flow, asks questions
- **Analyzer Agent**: Processes responses, identifies patterns
- **Music Knowledge Agent**: Provides context about songs (key, tempo, style, difficulty)
- **Synthesis Agent**: Creates setlist proposals with rationale

**Data Collection**:
- Track individual member responses
- Store song metadata (duration, key, tempo, style, difficulty ratings)
- Maintain band's song repertoire database

**Decision Factors**:
- Song preferences (weighted by member priority)
- Technical difficulty vs. member skill levels
- Pacing and energy flow
- Key transitions
- Total duration constraints
- Member feature opportunities (solos, vocals)

**Collaboration Features**:
- Poll-style preference collection
- Voting on proposed setlists
- Conflict resolution (when preferences clash)
- Generate alternative setlists

---

## 2.5 Additional Implemented Features ✅

### 2.5.1 Intelligent AI Request Routing ✅
**Status**: Implemented

**Description**: Automatically determines user intent and routes requests to the appropriate AI service.

**Features**:
- Detects classical music lookup requests
- Identifies natural language music generation requests  
- Recognizes music editing commands
- Routes setlist design requests
- Handles collaborative setlist requests

**User Flow**:
- User sends any music-related message
- AI router analyzes intent using LLM
- Routes to appropriate service (IMSLP, generation, editing, setlist)
- Returns appropriate response

### 2.5.2 Collaborative Setlist Design ✅
**Status**: Implemented

**Description**: Chat-based collaborative setlist creation that works entirely through group chat messages.

**Key Features**:
- **Natural Language Parsing**: Extracts preferences from plain text responses
- **Ordering Preferences**: Respects "start with bebop", "end with blues" requests
- **Composer Avoidance**: Honors "no Miles Davis" preferences
- **Smart Filtering**: Filters pieces based on group preferences
- **Collaborative Scoring**: Ranks pieces by group compatibility

**User Flow**:
1. User requests collaborative setlist
2. AI asks group members for preferences via chat
3. Members respond with natural language preferences
4. AI parses preferences and generates personalized setlist
5. Setlist includes reasoning for each piece selection

**Example Interaction**:
```
User: "Create a jazz setlist for our group"
AI: "I'll help create a collaborative setlist! Please share your preferences..."

Cherry: "Start with bebop, I love jazz, play piano, intermediate level"
Blueberry: "End with blues, I enjoy jazz, play guitar, intermediate level"  
Alex: "I like ballads and blues, play guitar, beginner level, avoid complex pieces"

AI: "Collaborative Setlist Complete! 🎉
1. Confirmation - Charlie Parker (opens with bebop as requested)
2. Blue Bossa - Kenny Dorham (matches group preferences)
...
12. Blue Monk - Thelonious Monk (closes with blues as requested)"
```

### 2.5.3 Enhanced Music Editing ✅
**Status**: Implemented

**Description**: Advanced conversational music editing with specialized commands.

**New Features**:
- **Note Grouping**: "Group notes 567 and eight together" → proper beaming
- **Duration Changes**: "Turn the first note into a half note" → duration modification
- **Smart Detection**: Automatically detects edit type and applies appropriate prompts
- **No Tuplet Numbers**: Correctly beams eighth notes without adding tuplet numbers

**Example Commands**:
- "Group the first four notes together" → CDEF (beamed eighth notes)
- "Turn the middle notes into eighth notes" → duration changes
- "Make the last note a whole note" → duration modification

---

## 3. Technical Architecture ✅

### 3.1 Overall Architecture: AI Microservices ✅
**Status**: Implemented

**Current Implementation**: Dedicated FastAPI microservice containerized with Docker

#### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    iOS Chat App                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │  Chat UI    │  │ Music Viewer │  │ Setlist View  │ │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘ │
│         │                │                   │         │
│         └────────────────┴───────────────────┘         │
│                          │                             │
│                   ┌──────▼──────┐                      │
│                   │  API Client │                      │
│                   └──────┬──────┘                      │
└───────────────────────────┼─────────────────────────────┘
                            │
                    HTTPS / REST API
                            │
┌───────────────────────────▼─────────────────────────────┐
│              AI Microservice (Backend)                  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │           API Gateway / Router                  │  │
│  └────┬────────────────┬────────────────┬─────────┘  │
│       │                │                 │            │
│  ┌────▼─────┐  ┌───────▼──────┐  ┌──────▼────────┐  │
│  │ Music    │  │ Sheet Music  │  │  Setlist      │  │
│  │ Retrieval│  │ Generation/  │  │  Designer     │  │
│  │ Service  │  │ Edit Service │  │  Agent System │  │
│  └────┬─────┘  └───────┬──────┘  └──────┬────────┘  │
│       │                │                 │            │
│  ┌────▼────────────────▼─────────────────▼────────┐  │
│  │          LLM Integration Layer                 │  │
│  │  (OpenAI GPT-4, Claude, or Azure OpenAI)      │  │
│  └────┬───────────────────────────────────────────┘  │
│       │                                               │
│  ┌────▼───────────────────────────────────────────┐  │
│  │        Supporting Services                     │  │
│  │  - ABC Notation Renderer (abcjs)              │  │
│  │  - Music Theory Utilities                     │  │
│  │  - Database (Song repertoire, edit history)   │  │
│  │  - Cache (Redis for conversation context)     │  │
│  └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Technology Stack Recommendations

#### Backend Microservice
**Framework Options**:
1. **Python + FastAPI** (Recommended)
   - Fast, modern async framework
   - Excellent LangChain integration
   - Rich ecosystem for music/AI libraries
   
2. **Node.js + Express**
   - Good abcjs integration (ABC notation rendering)
   - Lighter weight for simple text processing

**LLM Orchestration**:
- **LangChain** (Recommended for multi-agent setlist designer)
  - Built-in agent patterns
  - Conversation memory management
  - Tool/function calling support
  - Multi-agent orchestration

**LLM Providers**:
- **Primary**: OpenAI GPT-4 Turbo or GPT-4o
  - Best general music knowledge
  - Reliable structured output
- **Alternative**: Anthropic Claude 3.5 Sonnet
  - Strong reasoning for complex edits
  - Better at following ABC notation syntax
- **Cost-effective**: Azure OpenAI (if already using Azure)

#### iOS Integration
- **Networking**: URLSession or Alamofire
- **ABC Rendering**: abcjs via WebView or server-side rendering
- **Sheet Music Display**: PDFKit or custom UIView

### 3.3 Service-Specific Architecture

#### 3.3.1 Sheet Music Generation Service

**Endpoint**: `POST /api/music/generate`

**Request**:
```json
{
  "natural_language": "Time signature 3/4, key F minor...",
  "conversation_id": "uuid",
  "user_id": "uuid"
}
```

**Process Flow**:
1. Receive natural language input
2. Send to LLM with specialized prompt:
   - System prompt: Expert in ABC notation
   - Few-shot examples of NL → ABC conversions
   - Structured output format
3. Validate ABC syntax
4. Render to image using abcjs
5. Return both ABC text and image URL

**Response**:
```json
{
  "abc_notation": "X:1\nT:Untitled...",
  "sheet_music_url": "https://...",
  "music_id": "uuid",
  "validation_status": "valid"
}
```

#### 3.3.2 Sheet Music Editing Service

**Endpoint**: `POST /api/music/edit`

**Request**:
```json
{
  "music_id": "uuid",
  "current_abc": "X:1\nT:...",
  "edit_instruction": "Add chord symbols Fm, Cm",
  "conversation_history": [...]
}
```

**Process Flow**:
1. Retrieve current ABC notation
2. Build LLM prompt:
   - Current ABC notation
   - Edit instruction
   - Conversation history for context
3. LLM returns modified ABC
4. Validate changes
5. Render updated sheet music
6. Store version in history

**LangChain Implementation**:
```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

edit_prompt = PromptTemplate(
    input_variables=["current_abc", "instruction", "history"],
    template="""You are an expert music notation editor using ABC notation.

Current ABC notation:
{current_abc}

Edit instruction: {instruction}

Previous edits: {history}

Provide the modified ABC notation:"""
)

chain = LLMChain(
    llm=llm,
    prompt=edit_prompt,
    memory=ConversationBufferMemory()
)
```

#### 3.3.3 Setlist Designer Multi-Agent System

**Endpoint**: `POST /api/setlist/session`

**LangChain Multi-Agent Architecture**:

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool

# Agent 1: Coordinator
coordinator_agent = create_react_agent(
    llm=llm,
    tools=[ask_band_member, collect_preferences],
    prompt=coordinator_prompt
)

# Agent 2: Music Knowledge Base
music_kb_tool = Tool(
    name="music_knowledge",
    func=query_song_database,
    description="Get song metadata: key, tempo, style, duration"
)

# Agent 3: Setlist Synthesizer
synthesis_agent = create_react_agent(
    llm=llm,
    tools=[music_kb_tool, analyze_preferences, check_constraints],
    prompt=synthesis_prompt
)

# Orchestration
class SetlistDesignerOrchestrator:
    def run_session(self, band_members, constraints):
        # Phase 1: Gather preferences
        preferences = coordinator_agent.run(
            {"band_members": band_members}
        )
        
        # Phase 2: Synthesize setlist
        setlist = synthesis_agent.run({
            "preferences": preferences,
            "constraints": constraints
        })
        
        # Phase 3: Iterate with feedback
        return setlist
```

**Database Schema**:
```sql
-- Song repertoire
CREATE TABLE songs (
    id UUID PRIMARY KEY,
    band_id UUID,
    title VARCHAR(255),
    key VARCHAR(10),
    tempo_bpm INT,
    duration_seconds INT,
    style VARCHAR(50),
    difficulty_rating INT,
    last_performed DATE
);

-- Setlist sessions
CREATE TABLE setlist_sessions (
    id UUID PRIMARY KEY,
    band_id UUID,
    status VARCHAR(50),
    concert_date DATE,
    target_duration INT,
    created_at TIMESTAMP
);

-- Member preferences
CREATE TABLE member_preferences (
    session_id UUID,
    member_id UUID,
    song_id UUID,
    preference_level INT, -- 1-5
    notes TEXT
);
```

### 3.4 Deployment Architecture

**Recommended**: Cloud-native microservice

**Option 1: Containerized (Recommended)**
- Docker container
- Deploy to: AWS ECS, Google Cloud Run, or Azure Container Instances
- Auto-scaling based on request load
- Benefits: Scalable, isolated, easy CI/CD

**Option 2: Serverless**
- AWS Lambda / Google Cloud Functions
- API Gateway for routing
- Benefits: Cost-effective for low traffic, no server management
- Drawbacks: Cold start latency, execution time limits

**Option 3: Traditional VPS**
- Single server deployment
- Good for MVP/early stage
- Lower complexity

### 3.5 Cost Considerations

**LLM API Costs** (Primary expense):
- GPT-4 Turbo: ~$0.01-0.03 per request (depending on complexity)
- Claude Sonnet: ~$0.003-0.015 per request
- Budget: Implement caching and prompt optimization

**Optimization Strategies**:
1. Cache common ABC conversions
2. Use smaller models (GPT-3.5) for simple edits
3. Batch requests when possible
4. Set max token limits
5. Implement rate limiting per user

### 3.6 Security Considerations

**API Security**:
- Authentication: JWT tokens from iOS app
- Rate limiting: Prevent abuse
- Input validation: Sanitize natural language inputs
- API keys: Store LLM API keys in environment variables, not code

**Data Privacy**:
- Store only necessary conversation context
- Implement data retention policies
- Allow users to delete their music/chat history

---

## 4. Implementation Status ✅

### Phase 1: Foundation ✅ (Completed)
- ✅ Set up FastAPI microservice infrastructure
- ✅ Implemented OpenAI GPT-4 integration
- ✅ Created ABC notation validation utilities
- ✅ Set up abcjs rendering pipeline
- ✅ Containerized with Docker for easy deployment

### Phase 2: Core Features ✅ (Completed)
- ✅ **Natural Language → ABC generation**: Fully implemented with OpenAI GPT-4
- ✅ **Conversational editing system**: Advanced editing with note grouping and duration changes
- ✅ **AI Request Routing**: Intelligent routing to appropriate services
- ✅ **Collaborative Setlist Design**: Chat-based collaborative setlist creation

### Phase 3: Multi-Agent System ✅ (Simplified & Completed)
- ✅ **Simplified Architecture**: Template-based setlist generation for MVP
- ✅ **Collaborative Features**: Group preference gathering and parsing
- ✅ **Smart Filtering**: Preference-based piece selection and ordering
- ✅ **Natural Language Processing**: Advanced preference parsing

### Phase 4: Testing & Refinement ✅ (Completed)
- ✅ **User Testing**: Tested with real user scenarios
- ✅ **Prompt Engineering**: Optimized prompts for music generation and editing
- ✅ **Performance Tuning**: Fast response times (<3s for generation)
- ✅ **Bug Fixes**: Fixed composer avoidance, ordering preferences, and title generation

### Phase 5: Polish & Launch ✅ (Ready for Production)
- ✅ **API Documentation**: Complete API documentation
- ✅ **Error Handling**: Comprehensive error handling and validation
- ✅ **Production Ready**: Docker containerized and deployable
- ✅ **Feature Complete**: All core features implemented and tested

---

## 5. Current Implementation Details

### Feature Adoption
- % of users who try NL → music generation
- % of users who make at least 3 edits to generated music
- % of bands who complete a setlist session

### Quality Metrics
- ABC notation accuracy (valid syntax %)
- User satisfaction with generated music (survey)
- Setlist acceptance rate (% of AI suggestions used)

### Technical Metrics
- API response time (target: <3s for generation, <2s for edits)
- LLM API cost per request
- Error rate

---

## 6. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM produces invalid ABC notation | High | Multi-layer validation, fallback templates |
| High LLM API costs | Medium | Caching, prompt optimization, smaller models for simple tasks |
| Users don't understand NL syntax | Medium | Provide templates, examples, autocomplete |
| Setlist agent makes poor suggestions | Medium | Human-in-the-loop, allow manual overrides |
| Cold start latency in serverless | Low | Use containerized deployment or warm-up functions |

---

## 7. Open Questions

1. Should ABC notation be stored server-side or only in iOS local storage?
2. What's the expected concurrent user load?
3. Do we need real-time collaboration for setlist planning?
4. Should we support importing existing MusicXML/MIDI files?
5. Privacy: Can other band members see all sheet music, or only shared ones?

---

## Appendix A: ABC Notation Primer

ABC notation is a text-based music notation format:

**Example**:
```abc
X:1
T:Simple Melody
M:4/4
L:1/4
K:C
C D E F | G4 | A B c d | c4 |
```

**Components**:
- `X:` - Reference number
- `T:` - Title
- `M:` - Meter/time signature
- `L:` - Default note length
- `K:` - Key signature
- `|` - Bar lines
- Notes: C D E F G A B c d (lowercase = higher octave)
- Durations: `/2` (half), `2` (double), no modifier (default)

**Benefits**:
- Text-based (easy for LLMs)
- Compact
- Widely supported (abcjs, EasyABC, etc.)
- Can be version controlled

---

## Appendix B: Sample API Documentation

### Generate Sheet Music from Natural Language

**Endpoint**: `POST /api/v1/music/generate`

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "description": "Time signature 3/4, key F minor, eighth notes: A-flat, G, F",
  "user_id": "uuid",
  "conversation_id": "uuid" (optional)
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "music_id": "uuid",
    "abc_notation": "X:1\nT:Untitled\nM:3/4\nK:Fm...",
    "sheet_music_url": "https://cdn.example.com/sheet/uuid.png",
    "midi_url": "https://cdn.example.com/midi/uuid.mid" (optional)
  }
}
```

**Error Response** (400 Bad Request):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_NOTATION",
    "message": "Could not parse musical description",
    "details": "Time signature must be specified"
  }
}
```