JARVIS — Voice-First Multi-Agent Personal Assistant

A voice-first personal assistant designed to autonomously execute real-world tasks through natural speech and respond entirely through voice — zero typing, zero screens, zero physical interference.

About JARVIS

JARVIS is an AI-powered, voice-first personal assistant designed to make human-computer interaction more natural and action-oriented.

Instead of requiring users to type commands, navigate applications, or manually perform repetitive tasks, JARVIS provides a conversational interface where the user can simply speak a request.

The system listens to the user's voice, converts speech into text, understands the intent using an LLM-powered agent, decides whether a tool needs to be executed, performs the required action, and finally converts the response back into speech.

The intended interaction model is:

        Human
          │
          │ Natural Speech
          ▼
     ┌───────────┐
     │    JARVIS │
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

The goal is to move from "computer as a tool I operate" toward "computer as an assistant I communicate with."

🚀 What Makes JARVIS Different?

Traditional software interaction generally looks like:

Think → Type → Search → Click → Navigate → Execute

JARVIS aims for:

Think → Speak → Done

For example, instead of manually opening a messaging application and composing a message, the user can say:

"Send Rahul a message saying I'll reach in ten minutes."

JARVIS can understand the request, determine that a messaging action is required, ask for confirmation when necessary, and then execute the corresponding tool.

The same architecture can be extended to other real-world actions such as email, music, productivity, memory, and additional automation tools.

✨ Core Features
🎙️ Voice-First Interaction

JARVIS is designed around continuous voice interaction.

The user does not need to type commands into a terminal or application.

Microphone
    ↓
Speech-to-Text
    ↓
JARVIS
    ↓
Text-to-Speech
    ↓
Speaker
🧠 LLM-Powered Reasoning

JARVIS uses Mistral AI through ChatMistralAI to understand natural-language requests.

The current model configured in the project is:

mistral-small-latest

The model is also provided with access to the project's tools.

🛠️ Tool-Based Task Execution

JARVIS is not limited to generating text.

The LLM can decide when an available tool needs to be executed.

Tools are registered through:

ALL_TOOLS

and exposed to the model using:

llm.bind_tools(ALL_TOOLS)

The LangGraph ToolNode is then responsible for executing the requested tool.

This creates the fundamental separation:

LLM
 │
 │ decides what needs to happen
 ▼
Tool
 │
 │ actually performs the action
 ▼
Result
🔊 Voice Responses

JARVIS does not simply print responses to the terminal.

The final response is passed to:

speak(reply)

which handles Text-to-Speech.

Therefore, the intended interaction is completely voice-oriented.

⚡ Fast-Path Commands

Not every command needs an LLM round trip.

JARVIS currently implements a dedicated fast path for stopping music.

Commands such as:

stop
stop music
stop the music
stop playing
pause
pause music
quiet
silence
mute

are handled directly through:

stop_music()

instead of being sent to the LLM.

This reduces unnecessary latency and API usage for deterministic commands.

🔐 Confirmation for Sensitive Actions

JARVIS is configured to require confirmation before certain potentially irreversible actions.

For example:

User:
Send Rahul a WhatsApp message saying I'll call later.

JARVIS:
Send it?

User:
Yes.

JARVIS:
Message sent.

The system prompt specifically requires confirmation before:

send_whatsapp_tool
send_email_tool

while read-only and other specified actions do not require confirmation.

🏗️ System Architecture

The current implementation can be divided into several conceptual layers:

┌───────────────────────────────────────────────┐
│                  USER                        │
│              Natural Speech                  │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│              VOICE INPUT LAYER                │
│       listen_and_transcribe()                 │
│                                               │
│          Speech → Text                        │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│              APPLICATION LAYER                │
│                  main.py                      │
│                                               │
│  • Continuous voice loop                      │
│  • Fast-path commands                         │
│  • State management                            │
│  • Graph invocation                            │
│  • Response extraction                         │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│               AGENT LAYER                     │
│                  graph.py                     │
│                                               │
│          LangGraph StateGraph                 │
│                                               │
│              START                            │
│                ↓                              │
│              Agent                            │
│                ↓                              │
│        Tool required?                         │
│          ↙        ↘                           │
│        No          Yes                        │
│        ↓            ↓                         │
│       END         Tools                       │
│                     ↓                         │
│                   Agent                       │
│                     ↓                         │
│                    END                        │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│                TOOL LAYER                     │
│                  ALL_TOOLS                    │
│                                               │
│  External actions / integrations / automation │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│              VOICE OUTPUT LAYER               │
│                    speak()                    │
│                                               │
│             Text → Speech                     │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
                    🔊 User
🔄 End-to-End Execution Flow

Every normal interaction follows this sequence.

Step 1 — Listen

main.py calls:

listen_and_transcribe()

The microphone input is converted into text.

Example:

User says:

"Send an email to John."

The application receives:

"Send an email to John."
Step 2 — Check Fast-Path Commands

Before invoking the LLM, main.py checks whether the command matches one of the predefined music-stop triggers.

if user_text.strip().lower() in STOP_MUSIC_TRIGGERS:
    status = stop_music()

This means:

"stop music"

does not need to travel through:

Speech → LLM → Tool → Response

Instead:

Speech
  ↓
STT
  ↓
Fast-path
  ↓
stop_music()
  ↓
TTS
Step 3 — Add User Message to State

For normal requests, the user's message is added to the persistent conversation state:

state["messages"] = state["messages"] + [
    HumanMessage(content=user_text)
]

This allows the graph to receive the conversation history.

Step 4 — Invoke LangGraph

The state is passed to the compiled LangGraph application:

result = app.invoke(state)

The graph is created in graph.py.

🧠 LangGraph Workflow

The graph is a StateGraph built around AgentState.

The current graph consists of two actual nodes:

agent
tools

with the following workflow:

                 START
                   │
                   ▼
              ┌─────────┐
              │  agent  │
              └────┬────┘
                   │
                   ▼
          tools_condition
             /          \
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

The conditional routing is handled through:

graph_builder.add_conditional_edges(
    "agent",
    tools_condition
)
🤖 Agent Node

The agent node is responsible for calling the LLM.

The system prompt is prepended to the existing conversation:

system_msg = SystemMessage(content=SYSTEM_PROMPT)

messages_with_system = [
    system_msg
] + list(state["messages"])

The model then receives the conversation and available tools.

The configured model is:

ChatMistralAI(
    model="mistral-small-latest",
    ...
)
🧰 Tool Binding

The tools are imported from:

from tools import ALL_TOOLS

They are bound to the LLM:

llm_with_tools = llm.bind_tools(ALL_TOOLS)

and registered with LangGraph:

tool_node = ToolNode(ALL_TOOLS)

This means the same tool collection is used at two levels:

                ALL_TOOLS
                  │
          ┌───────┴────────┐
          ▼                ▼
      LLM Binding       ToolNode
          │                │
          ▼                ▼
    Model can request   LangGraph
       a tool           executes it
🔁 Agent → Tool → Agent Loop

If the model decides that a tool is required, LangGraph routes execution to the tools node.

After the tool finishes, execution returns to the agent node.

This allows JARVIS to follow a loop such as:

User Request
     ↓
Agent
     ↓
Tool Call
     ↓
Tool Execution
     ↓
Tool Result
     ↓
Agent
     ↓
Final Response

For example:

User:
"What's the latest message from Rahul?"

        ↓

Agent understands request

        ↓

read_whatsapp_tool

        ↓

Tool returns message

        ↓

Agent summarizes result

        ↓

JARVIS speaks response
💬 Voice-Oriented System Prompt

The system prompt is intentionally optimized for speech.

JARVIS is instructed to:

Respond in one short sentence
Avoid markdown
Avoid long explanations
Keep responses natural for speech
Summarize tool results
Never expose raw JSON or tool output
Follow confirmation rules
Separate reading and sending WhatsApp actions
Explain errors in plain English

This is important because the response is eventually sent to:

speak(reply)

A response designed for a text interface does not necessarily work well as spoken output.

🔐 Confirmation Architecture

The assistant distinguishes between actions that require confirmation and actions that can be performed immediately.

Current prompt-level rules include:

Send WhatsApp → Confirmation required
Send Email    → Confirmation required

Read messages → No confirmation
Todo actions  → No confirmation
Memory        → No confirmation
Music         → No confirmation

Conceptually:

                    User Request
                         │
                         ▼
                       Agent
                         │
              ┌──────────┴──────────┐
              │                     │
       Sensitive action       Non-sensitive action
              │                     │
              ▼                     ▼
         Ask confirmation       Execute tool
              │                     │
              ▼                     │
         User confirms              │
              │                     │
              └──────────┬──────────┘
                         ▼
                    Execute Tool
🧠 Persistent State

JARVIS initializes its state once when the voice loop begins:

state: AgentState = {
    "messages": [],
    "music": None,
    "last_contact": None,
    "pending_confirmation": None,
    "turn_count": 0,
}

The state persists throughout the continuous voice session.

After each graph invocation:

state.update(result)

This allows information returned by LangGraph to remain available for subsequent turns.

🔊 Response Generation

Once LangGraph finishes processing the request, main.py extracts the latest AIMessage.

The helper function:

_extract_reply(result)

searches the returned message list in reverse order and returns the latest non-empty AI response.

The response is then sent to:

speak(reply)

Therefore the final pipeline is:

AIMessage
   ↓
_extract_reply()
   ↓
Text Response
   ↓
speak()
   ↓
Audio Output
♾️ Continuous Voice Loop

JARVIS is designed to remain active until the user terminates the application.

The core loop is:

while True:
    user_text = listen_and_transcribe()

    ...

    result = app.invoke(state)

    ...

    speak(reply)

This creates a conversational experience instead of a one-command-per-process architecture.

🛑 Graceful Shutdown

Pressing:

Ctrl + C

raises KeyboardInterrupt.

JARVIS handles this explicitly.

The shutdown sequence is:

Ctrl + C
   ↓
"Goodbye!"
   ↓
Text-to-Speech
   ↓
Stop music
   ↓
Exit
⚠️ Error Handling

Unexpected runtime errors are caught by the voice loop.

Instead of terminating immediately, JARVIS gives the user a simple spoken response:

Something went wrong. Please try again.

The application then continues listening.

This is particularly important for a voice assistant because a single failed API request or tool operation should not necessarily terminate the entire session.

📁 Project Structure

Based on the current files, the project can be organized approximately as:

JARVIS/
│
├── main.py
│
├── graph.py
│
├── state.py
│
├── tools.py
│
├── voice/
│   ├── stt.py
│   └── tts.py
│
├── voice_music_app_fixed.py
│
├── requirements.txt
│
├── .env
│
├── .gitignore
│
└── README.md

Additional modules may be present depending on the implementation of ALL_TOOLS.

📌 File Responsibilities
File / Module	Responsibility
main.py	Main voice loop and application entry point
graph.py	LangGraph workflow and Mistral agent configuration
state.py	Definition of AgentState
tools.py	Available tools exposed to the agent
voice/stt.py	Speech-to-Text functionality
voice/tts.py	Text-to-Speech functionality
voice_music_app_fixed.py	Music control, including stop functionality
.env	Environment variables and API credentials
requirements.txt	Python dependencies
README.md	Project documentation
🔑 Environment Configuration

JARVIS currently requires a Mistral API key.

Create a .env file in the project root:

MISTRAL_API_KEY=your_mistral_api_key

The key is loaded using:

load_dotenv()

and accessed through:

os.getenv("MISTRAL_API_KEY")

Any additional credentials required by individual tools should also be configured through environment variables.

Never commit API keys to GitHub.

A recommended .gitignore is:

.env
__pycache__/
*.pyc
.venv/
Jarvis/
⚙️ Installation
1. Clone the repository
git clone <YOUR_REPOSITORY_URL>
cd JARVIS
2. Create the virtual environment

On Windows:

python -m venv Jarvis

Activate it:

Jarvis\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables

Create:

.env

and add:

MISTRAL_API_KEY=your_mistral_api_key

Add any other credentials required by the tools.

▶️ Running JARVIS

The project is specifically designed to run using the Python interpreter inside the JARVIS virtual environment.

On Windows:

Jarvis\Scripts\python.exe main.py

This is preferred over:

python main.py

because the project may depend on packages installed specifically inside the JARVIS virtual environment.

🎤 Example Interaction
Example 1 — General Request
User:
What can you do?

JARVIS:
I can help you manage tasks, messages, music, and other supported actions.
Example 2 — WhatsApp
User:
Send Rahul a WhatsApp message saying I'll call him later.

JARVIS:
Send it?

User:
Yes.

JARVIS:
Message sent.
Example 3 — Reading Messages
User:
What did Rahul say?

JARVIS:
Rahul said he'll call you later.

Reading and sending are intentionally treated as separate actions.

Example 4 — Music
User:
Stop music.

The command is recognized by the fast path.

stop_music()

is executed without requiring an LLM request.

JARVIS then responds:

Music stopped.
🌐 Planned Frontend

The backend is currently designed as a Python voice application.

A web-based frontend can be added without replacing the underlying agent architecture.

The future architecture can look like:

                 ┌──────────────────────┐
                 │    JARVIS FRONTEND   │
                 │                      │
                 │  • Mic Button        │
                 │  • Waveform          │
                 │  • Status             │
                 │  • Response UI        │
                 └──────────┬───────────┘
                            │
                       API / WebSocket
                            │
                            ▼
                 ┌──────────────────────┐
                 │    JARVIS BACKEND    │
                 │                      │
                 │       main.py        │
                 │          │           │
                 │          ▼           │
                 │      graph.py        │
                 │          │           │
                 │          ▼           │
                 │     Mistral AI       │
                 │          │           │
                 │          ▼           │
                 │       Tools          │
                 └──────────────────────┘

The frontend could visualize the assistant's state:

IDLE
  ↓
LISTENING
  ↓
PROCESSING
  ↓
EXECUTING
  ↓
RESPONDING
  ↓
IDLE

A real-time waveform can also be connected to the microphone's audio stream, making the interface visually reflect the user's voice.

🔮 Future Roadmap

Potential improvements include:

Voice Experience
Real-time microphone waveform
Voice activity detection
Interruptible responses
Wake-word detection
Lower-latency streaming
Better handling of silence and background noise
Agent Intelligence
More sophisticated task planning
Long-term memory
Context-aware actions
Better confirmation handling
Multi-step task execution
Multiple specialized agents if required
Integrations
WhatsApp
Email
Music
Calendar
Reminders
Notes
Weather
Smart-home devices
Browser automation
Desktop automation
Frontend
Web-based JARVIS dashboard
Real-time WebSocket communication
Animated voice waveform
Live execution status
Conversation history
Tool execution visualization
🧩 Multi-Agent Architecture — Future Direction

The project name and vision describe JARVIS as a multi-agent personal assistant, but the currently provided graph.py implements a single LLM agent with multiple tools.

The distinction is important.

Current Architecture
             JARVIS Agent
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
      Tool 1    Tool 2    Tool 3

This is a tool-using agent architecture.

Possible Future Multi-Agent Architecture

A true multi-agent implementation could look like:

                    JARVIS
                      │
                Supervisor Agent
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
 Communication     Productivity    Entertainment
    Agent             Agent            Agent
       │              │              │
   WhatsApp         Todo            Music
   Email            Memory          Media

The supervisor could decide which specialized agent should handle a particular request.

For example:

"Send Rahul an email."

        ↓

Supervisor Agent

        ↓

Communication Agent

        ↓

Email Tool

        ↓

Result

        ↓

JARVIS Voice Response

This would make the system technically qualify as a multi-agent architecture.

🏛️ Design Principles
Voice First

Voice is the primary interaction mechanism rather than an additional feature.

Action Oriented

JARVIS is designed to execute actions through tools rather than merely answer questions.

Modular

The voice, agent, state, and tool layers are separated so that individual components can evolve independently.

Safe by Design

Potentially irreversible operations can require explicit confirmation.

Efficient

Deterministic operations can bypass the LLM when reasoning is unnecessary.

Extensible

New tools can be added to ALL_TOOLS without fundamentally changing the voice loop.

🔒 Security Considerations

Because JARVIS can potentially interact with external services, API credentials and tool permissions should be treated carefully.

Never expose:
MISTRAL_API_KEY
WhatsApp credentials
Email credentials
OAuth tokens
API tokens
Never commit:
.env
credentials
tokens
private keys

to a public repository.

For tools capable of sending messages, emails, or performing irreversible actions, confirmation and permission boundaries should be maintained.

🧪 Development Philosophy

The system follows a layered architecture:

┌─────────────────────┐
│      Voice I/O      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Application Loop  │
│       main.py       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Agent Workflow   │
│      graph.py       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│        Tools        │
└─────────────────────┘

This separation allows future components such as a web frontend, additional agents, new tools, or alternative voice models to be introduced without rewriting the entire application.

📊 Current Technology Stack
Technology	Purpose
Python	Core application
LangGraph	Agent workflow orchestration
LangChain	LLM/tool integration
Mistral AI	Language model
Speech-to-Text	Voice input
Rime TTS	Voice output
Python-dotenv	Environment configuration
🧠 Technical Summary

At its current stage, JARVIS is a continuous voice application built around a tool-calling LangGraph agent.

The critical execution pipeline is:

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

This architecture provides the foundation for evolving JARVIS into a larger personal-agent platform with specialized agents, richer memory, additional tools, and a real-time visual interface.

🚀 Vision

JARVIS is ultimately intended to make interaction with computers feel less like operating software and more like communicating with an intelligent assistant.

The long-term goal is simple:

Don't make the user learn how to operate the computer. Let the user simply tell the computer what they want done.

No typing.
No unnecessary navigation.
No repetitive clicking.

Just speak.
JARVIS understands.
JARVIS acts.
👨‍💻 Project

JARVIS — Voice-First Personal Assistant

Built with Python, LangGraph, LangChain, Mistral AI, Speech-to-Text, Text-to-Speech, and tool-based AI execution.
