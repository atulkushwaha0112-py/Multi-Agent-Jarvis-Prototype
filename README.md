<div align="center">

# 🤖 JARVIS
### Voice-First Multi-Agent Personal Assistant

*Speak your intent. JARVIS understands. JARVIS acts.*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Orchestration-1C3C3C?style=flat-square)](https://www.langchain.com/langgraph)
[![LangChain](https://img.shields.io/badge/LangChain-Tool%20Integration-1C3C3C?style=flat-square)](https://www.langchain.com/)
[![Mistral AI](https://img.shields.io/badge/Mistral%20AI-mistral--small--latest-FF7000?style=flat-square)](https://mistral.ai/)
[![License](https://img.shields.io/badge/License-Unspecified-lightgrey?style=flat-square)]()

**A voice-first personal assistant that autonomously executes real-world tasks through natural speech. Zero typing, zero screens, zero physical interference.**

</div>

---

## 📖 Table of Contents

- [About JARVIS](#-about-jarvis)
- [What Makes JARVIS Different?](#-what-makes-jarvis-different)
- [Core Features](#-core-features)
- [System Architecture](#️-system-architecture)
- [End-to-End Execution Flow](#-end-to-end-execution-flow)
- [LangGraph Workflow](#-langgraph-workflow)
- [Confirmation Architecture](#-confirmation-architecture)
- [Persistent State](#-persistent-state)
- [Continuous Voice Loop & Shutdown](#️-continuous-voice-loop)
- [Error Handling](#️-error-handling)
- [Project Structure](#-project-structure)
- [File Responsibilities](#-file-responsibilities)
- [Environment Configuration](#-environment-configuration)
- [Installation](#️-installation)
- [Running JARVIS](#️-running-jarvis)
- [Example Interactions](#-example-interactions)
- [Planned Frontend](#-planned-frontend)
- [Future Roadmap](#-future-roadmap)
- [Multi-Agent Architecture: Future Direction](#-multi-agent-architecture--future-direction)
- [Design Principles](#️-design-principles)
- [Security Considerations](#-security-considerations)
- [Technology Stack](#-current-technology-stack)
- [Technical Summary](#-technical-summary)
- [Vision](#-vision)

---

## 💡 About JARVIS

**JARVIS** is an AI-powered, voice-first personal assistant designed to make human-computer interaction more natural and action-oriented.

Instead of requiring users to type commands, navigate applications, or manually perform repetitive tasks, JARVIS provides a conversational interface where the user simply **speaks a request**.

The system:

1. **Listens** to the user's voice
2. **Transcribes** speech into text
3. **Understands intent** using an LLM-powered agent
4. **Decides** whether a tool needs to be executed
5. **Performs** the required action
6. **Responds** back entirely through voice

### Interaction Model

```
                Human
                  │
                  │ Natural Speech
                  ▼
            ┌───────────┐
            │  JARVIS   │
            └─────┬─────┘
                  │
                  ▼
           Understand Intent
                  │
                  ▼
             Decide Action
                  │
                  ▼
             Execute Tool
                  │
                  ▼
               Get Result
                  │
                  ▼
           Generate Response
                  │
                  ▼
              Voice Output
                  │
                  ▼
                Human
```

> **The goal:** move from *"computer as a tool I operate"* toward *"computer as an assistant I communicate with."*

---

## 🚀 What Makes JARVIS Different?

| Traditional Software | JARVIS |
|---|---|
| Think → Type → Search → Click → Navigate → Execute | Think → Speak → Done |

For example, instead of manually opening a messaging app and composing a message, the user simply says:

> 🗣️ *"Send Rahul a message saying I'll reach in ten minutes."*

JARVIS understands the request, determines a messaging action is required, asks for confirmation when necessary, and executes the corresponding tool.

This same architecture extends naturally to email, music, productivity, memory, and future automation tools.

---

## ✨ Core Features

### 🎙️ Voice-First Interaction

JARVIS is built around continuous voice interaction, with no typing required.

```
Microphone → Speech-to-Text → JARVIS → Text-to-Speech → Speaker
```

### 🧠 LLM-Powered Reasoning

JARVIS uses **Mistral AI** via `ChatMistralAI` to understand natural-language requests.

- **Current model:** `mistral-small-latest`
- The model has direct access to the project's registered tools

### 🛠️ Tool-Based Task Execution

JARVIS isn't limited to generating text. The LLM decides *when* a tool needs to run.

```python
llm.bind_tools(ALL_TOOLS)
```

A LangGraph `ToolNode` then executes the requested tool, creating a clean separation of concerns:

```
        LLM
         │
         │  decides what needs to happen
         ▼
        Tool
         │
         │  actually performs the action
         ▼
       Result
```

### 🔊 Voice Responses

Responses are never just printed to a terminal. Every final reply is routed through:

```python
speak(reply)
```

### ⚡ Fast-Path Commands

Not every command needs a full LLM round trip. JARVIS implements a dedicated **fast path** for stopping music, bypassing the LLM entirely for deterministic phrases:

`stop` · `stop music` · `stop the music` · `stop playing` · `pause` · `pause music` · `quiet` · `silence` · `mute`

These route straight to `stop_music()`, reducing latency and unnecessary API usage.

### 🔐 Confirmation for Sensitive Actions

Certain potentially irreversible actions require explicit user confirmation before execution:

```
User:    Send Rahul a WhatsApp message saying I'll call later.
JARVIS:  Send it?
User:    Yes.
JARVIS:  Message sent.
```

Confirmation is required before: `send_whatsapp_tool`, `send_email_tool`. Read-only and other specified actions execute immediately.

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────┐
│                     USER                        │
│                 Natural Speech                  │
└───────────────────────┬──────────────────────────┘
                         ▼
┌────────────────────────────────────────────────┐
│               VOICE INPUT LAYER                 │
│           listen_and_transcribe()                │
│                Speech → Text                     │
└───────────────────────┬──────────────────────────┘
                         ▼
┌────────────────────────────────────────────────┐
│               APPLICATION LAYER                  │
│                    main.py                       │
│  • Continuous voice loop                          │
│  • Fast-path commands                              │
│  • State management                                │
│  • Graph invocation                                 │
│  • Response extraction                              │
└───────────────────────┬──────────────────────────┘
                         ▼
┌────────────────────────────────────────────────┐
│                  AGENT LAYER                     │
│                   graph.py                        │
│               LangGraph StateGraph                │
│                                                    │
│    START → Agent → Tool required?                  │
│                        ├── No  → END                │
│                        └── Yes → Tools → Agent → END │
└───────────────────────┬──────────────────────────┘
                         ▼
┌────────────────────────────────────────────────┐
│                   TOOL LAYER                     │
│                   ALL_TOOLS                       │
│      External actions / integrations / automation │
└───────────────────────┬──────────────────────────┘
                         ▼
┌────────────────────────────────────────────────┐
│               VOICE OUTPUT LAYER                 │
│                    speak()                        │
│                Text → Speech                       │
└───────────────────────┬──────────────────────────┘
                         ▼
                      🔊 User
```

---

## 🔄 End-to-End Execution Flow

### Step 1: Listen
`main.py` calls `listen_and_transcribe()`, converting microphone input into text.

> User says: *"Send an email to John."*
> App receives: `"Send an email to John."`

### Step 2: Check Fast-Path Commands

Before invoking the LLM, `main.py` checks whether the command matches a predefined music-stop trigger:

```python
if user_text.strip().lower() in STOP_MUSIC_TRIGGERS:
    status = stop_music()
```

This means `"stop music"` skips the LLM entirely:

```
Speech → STT → Fast-path → stop_music() → TTS
```

### Step 3: Add User Message to State

For normal requests, the message is appended to persistent conversation state:

```python
state["messages"] = state["messages"] + [
    HumanMessage(content=user_text)
]
```

### Step 4: Invoke LangGraph

```python
result = app.invoke(state)
```

The compiled graph (defined in `graph.py`) handles reasoning and execution.

---

## 🧠 LangGraph Workflow

The graph is a `StateGraph` built around `AgentState`, consisting of two nodes: `agent` and `tools`.

```
                 START
                   │
                   ▼
              ┌─────────┐
              │  agent  │
              └────┬────┘
                   │
                   ▼
           tools_condition
             /            \
        No tool          Tool call
           │                 │
           ▼                 ▼
          END             ┌───────┐
                           │ tools │
                           └───┬───┘
                               │
                               ▼
                             agent
                               │
                               ▼
                              END
```

```python
graph_builder.add_conditional_edges(
    "agent",
    tools_condition
)
```

### 🤖 Agent Node

Responsible for calling the LLM. The system prompt is prepended to the conversation:

```python
system_msg = SystemMessage(content=SYSTEM_PROMPT)
messages_with_system = [system_msg] + list(state["messages"])
```

```python
ChatMistralAI(
    model="mistral-small-latest",
    ...
)
```

### 🧰 Tool Binding

Tools are imported once and used at **two levels**:

```python
from tools import ALL_TOOLS

llm_with_tools = llm.bind_tools(ALL_TOOLS)   # LLM can request a tool
tool_node = ToolNode(ALL_TOOLS)              # LangGraph executes it
```

```
                ALL_TOOLS
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      LLM Binding           ToolNode
          │                   │
          ▼                   ▼
  Model requests a tool   LangGraph executes it
```

### 🔁 Agent → Tool → Agent Loop

```
User Request → Agent → Tool Call → Tool Execution → Tool Result → Agent → Final Response
```

**Example:**

```
User:  "What's the latest message from Rahul?"
  → Agent understands request
  → read_whatsapp_tool
  → Tool returns message
  → Agent summarizes result
  → JARVIS speaks response
```

### 💬 Voice-Oriented System Prompt

The system prompt is intentionally optimized for speech. JARVIS is instructed to:

- Respond in one short sentence
- Avoid markdown and long explanations
- Keep responses natural for speech
- Summarize tool results (never expose raw JSON/tool output)
- Follow confirmation rules
- Separate reading and sending WhatsApp actions
- Explain errors in plain English

> A response designed for a text interface does not necessarily work well as spoken output. That's why the prompt is deliberately voice-first.

---

## 🔐 Confirmation Architecture

| Action Type | Confirmation Required? |
|---|:---:|
| Send WhatsApp | ✅ Yes |
| Send Email | ✅ Yes |
| Read messages | ❌ No |
| Todo actions | ❌ No |
| Memory | ❌ No |
| Music | ❌ No |

```
                    User Request
                         │
                         ▼
                       Agent
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       Sensitive action       Non-sensitive action
              │                     │
              ▼                     ▼
        Ask confirmation        Execute tool
              │                     │
              ▼                     │
        User confirms                │
              │                     │
              └──────────┬──────────┘
                         ▼
                    Execute Tool
```

---

## 🧠 Persistent State

JARVIS initializes state once when the voice loop begins:

```python
state: AgentState = {
    "messages": [],
    "music": None,
    "last_contact": None,
    "pending_confirmation": None,
    "turn_count": 0,
}
```

State persists throughout the session and is updated after every graph invocation:

```python
state.update(result)
```

### 🔊 Response Generation

```python
_extract_reply(result)
```

Searches the returned message list **in reverse** and returns the latest non-empty AI response.

```
AIMessage → _extract_reply() → Text Response → speak() → Audio Output
```

---

## ♾️ Continuous Voice Loop

JARVIS remains active until explicitly terminated:

```python
while True:
    user_text = listen_and_transcribe()
    ...
    result = app.invoke(state)
    ...
    speak(reply)
```

This produces a genuine conversational experience rather than a one-command-per-process model.

### 🛑 Graceful Shutdown

```
Ctrl + C → "Goodbye!" → Text-to-Speech → Stop music → Exit
```

---

## ⚠️ Error Handling

Unexpected runtime errors are caught within the voice loop. Instead of crashing, JARVIS responds:

> *"Something went wrong. Please try again."*

The application then continues listening. This matters for a voice assistant, since a single failed API call or tool error shouldn't end the entire session.

---

## 📁 Project Structure

```
JARVIS/
│
├── main.py                    # Main voice loop & entry point
├── graph.py                   # LangGraph workflow & Mistral agent config
├── state.py                   # AgentState definition
├── tools.py                   # Tools exposed to the agent
│
├── voice/
│   ├── stt.py                 # Speech-to-Text
│   └── tts.py                 # Text-to-Speech
│
├── voice_music_app_fixed.py   # Music control (incl. stop functionality)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not committed)
├── .gitignore
└── README.md
```

> Additional modules may be present depending on the implementation of `ALL_TOOLS`.

## 📌 File Responsibilities

| File / Module | Responsibility |
|---|---|
| `main.py` | Main voice loop and application entry point |
| `graph.py` | LangGraph workflow and Mistral agent configuration |
| `state.py` | Definition of `AgentState` |
| `tools.py` | Available tools exposed to the agent |
| `voice/stt.py` | Speech-to-Text functionality |
| `voice/tts.py` | Text-to-Speech functionality |
| `voice_music_app_fixed.py` | Music control, including stop functionality |
| `.env` | Environment variables and API credentials |
| `requirements.txt` | Python dependencies |
| `README.md` | Project documentation |

---

## 🔑 Environment Configuration

JARVIS currently requires a Mistral API key. Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_mistral_api_key
```

Loaded via:

```python
load_dotenv()
os.getenv("MISTRAL_API_KEY")
```

Any additional credentials required by individual tools should also be configured through environment variables.

> ⚠️ **Never commit API keys to GitHub.**

**Recommended `.gitignore`:**

```gitignore
.env
__pycache__/
*.pyc
.venv/
Jarvis/
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd JARVIS
```

### 2. Create the virtual environment

**Windows:**

```bash
python -m venv Jarvis
Jarvis\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
MISTRAL_API_KEY=your_mistral_api_key
```

Add any other credentials required by the tools.

---

## ▶️ Running JARVIS

JARVIS is designed to run using the Python interpreter **inside** the JARVIS virtual environment.

**Windows:**

```bash
Jarvis\Scripts\python.exe main.py
```

> This is preferred over plain `python main.py`, since the project may depend on packages installed specifically inside the JARVIS virtual environment.

---

## 🎤 Example Interactions

<table>
<tr><td width="50%" valign="top">

**Example 1: General Request**

```
User:   What can you do?
JARVIS: I can help you manage tasks,
        messages, music, and other
        supported actions.
```

</td><td width="50%" valign="top">

**Example 2: WhatsApp**

```
User:   Send Rahul a WhatsApp message
        saying I'll call him later.
JARVIS: Send it?
User:   Yes.
JARVIS: Message sent.
```

</td></tr>
<tr><td width="50%" valign="top">

**Example 3: Reading Messages**

```
User:   What did Rahul say?
JARVIS: Rahul said he'll call you later.
```

*Reading and sending are intentionally treated as separate actions.*

</td><td width="50%" valign="top">

**Example 4: Music (Fast Path)**

```
User:   Stop music.
```

Recognized by the fast path → `stop_music()` executes without an LLM request.

```
JARVIS: Music stopped.
```

</td></tr>
</table>

---

## 🌐 Planned Frontend

The backend is currently a Python voice application. A web-based frontend can be layered on top **without replacing** the underlying agent architecture.

```
                 ┌───────────────────────┐
                 │    JARVIS FRONTEND     │
                 │  • Mic Button           │
                 │  • Waveform              │
                 │  • Status                 │
                 │  • Response UI             │
                 └───────────┬─────────────┘
                              │
                        API / WebSocket
                              │
                              ▼
                 ┌───────────────────────┐
                 │    JARVIS BACKEND      │
                 │       main.py            │
                 │          │                │
                 │          ▼                │
                 │      graph.py              │
                 │          │                │
                 │          ▼                │
                 │     Mistral AI              │
                 │          │                │
                 │          ▼                │
                 │       Tools                │
                 └───────────────────────┘
```

**Planned state visualization:**

```
IDLE → LISTENING → PROCESSING → EXECUTING → RESPONDING → IDLE
```

A real-time waveform connected to the microphone's audio stream would make the interface visually reflect the user's voice.

---

## 🔮 Future Roadmap

<table>
<tr><td valign="top" width="25%">

### 🎙️ Voice Experience
- Real-time mic waveform
- Voice activity detection
- Interruptible responses
- Wake-word detection
- Lower-latency streaming
- Better silence/noise handling

</td><td valign="top" width="25%">

### 🧠 Agent Intelligence
- Sophisticated task planning
- Long-term memory
- Context-aware actions
- Better confirmation handling
- Multi-step task execution
- Multiple specialized agents

</td><td valign="top" width="25%">

### 🔌 Integrations
- WhatsApp · Email
- Music · Calendar
- Reminders · Notes
- Weather
- Smart-home devices
- Browser / Desktop automation

</td><td valign="top" width="25%">

### 🖥️ Frontend
- Web-based dashboard
- Real-time WebSocket comms
- Animated voice waveform
- Live execution status
- Conversation history
- Tool execution visualization

</td></tr>
</table>

---

## 🧩 Multi-Agent Architecture: Future Direction

The project name and vision describe JARVIS as a *multi-agent* personal assistant, but the current `graph.py` implements a **single LLM agent with multiple tools**. This distinction matters.

### Current Architecture: Tool-Using Agent

```
             JARVIS Agent
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
      Tool 1    Tool 2    Tool 3
```

### Possible Future: True Multi-Agent Architecture

```
                    JARVIS
                      │
                Supervisor Agent
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
 Communication     Productivity    Entertainment
    Agent             Agent           Agent
       │                │               │
   WhatsApp           Todo            Music
   Email              Memory          Media
```

A supervisor would route requests to the correct specialized agent:

```
"Send Rahul an email."
   → Supervisor Agent
   → Communication Agent
   → Email Tool
   → Result
   → JARVIS Voice Response
```

This would make the system technically qualify as a genuine multi-agent architecture.

---

## 🏛️ Design Principles

| Principle | Description |
|---|---|
| **Voice First** | Voice is the primary interaction mechanism, not an add-on feature. |
| **Action Oriented** | JARVIS executes actions through tools rather than merely answering questions. |
| **Modular** | Voice, agent, state, and tool layers are separated so components evolve independently. |
| **Safe by Design** | Potentially irreversible operations require explicit confirmation. |
| **Efficient** | Deterministic operations bypass the LLM when reasoning isn't necessary. |
| **Extensible** | New tools can be added to `ALL_TOOLS` without changing the voice loop. |

---

## 🔒 Security Considerations

Because JARVIS interacts with external services, API credentials and tool permissions must be handled carefully.

**Never expose:**
- `MISTRAL_API_KEY`
- WhatsApp credentials
- Email credentials
- OAuth tokens
- API tokens

**Never commit:** `.env`, credentials, tokens, or private keys to a public repository.

For tools capable of sending messages, emails, or performing irreversible actions, confirmation and permission boundaries must be maintained at all times.

---

## 🧪 Development Philosophy

```
┌─────────────────────┐
│      Voice I/O       │
└──────────┬──────────┘
            ▼
┌─────────────────────┐
│   Application Loop    │
│       main.py          │
└──────────┬──────────┘
            ▼
┌─────────────────────┐
│    Agent Workflow      │
│      graph.py           │
└──────────┬──────────┘
            ▼
┌─────────────────────┐
│        Tools            │
└─────────────────────┘
```

This layered separation allows future components, such as a web frontend, additional agents, new tools, or alternative voice models, to be introduced without rewriting the entire application.

---

## 📊 Current Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Core application |
| **LangGraph** | Agent workflow orchestration |
| **LangChain** | LLM / tool integration |
| **Mistral AI** | Language model (`mistral-small-latest`) |
| **Speech-to-Text** | Voice input |
| **Rime TTS** | Voice output |
| **python-dotenv** | Environment configuration |

---

## 🧠 Technical Summary

At its current stage, JARVIS is a continuous voice application built around a tool-calling LangGraph agent.

```
Speech
  ↓
Speech-to-Text
  ↓
main.py
  ↓
Fast-path check
  │
  ├── Music stop → Direct tool execution
  │
  └── Normal command
          ↓
      LangGraph
          ↓
      Mistral AI
          ↓
     Tool decision
       /       \
      /         \
   No tool     Tool
     ↓           ↓
    END        Execute
                 ↓
               Agent
                 ↓
                END
                 ↓
            AIMessage
                 ↓
              speak()
                 ↓
               Speech
```

This architecture provides the foundation for evolving JARVIS into a larger personal-agent platform with specialized agents, richer memory, additional tools, and a real-time visual interface.

---

## 🚀 Vision

JARVIS is ultimately intended to make interaction with computers feel less like *operating software* and more like *communicating with an intelligent assistant*.

> **Don't make the user learn how to operate the computer.**
> **Let the user simply tell the computer what they want done.**

No typing. No unnecessary navigation. No repetitive clicking.

**Just speak. JARVIS understands. JARVIS acts.**

---

<div align="center">

### 👨‍💻 Project

**JARVIS: Voice-First Personal Assistant**

Built with Python, LangGraph, LangChain, Mistral AI, Speech-to-Text, Text-to-Speech, and tool-based AI execution.

</div>
