# AlgoGenie DSA Solver

## Overview
AlgoGenie DSA Solver is an interactive AI-driven system that helps users solve Data Structures & Algorithms (DSA) problems. It combines a reasoning LLM "problem solver" agent with a secure, containerized "code executor" agent. The UI (built with Streamlit) lets a user submit a problem, observe the multi‑agent conversation as it incrementally reasons, generates Python code, executes it inside a Docker sandbox, validates results with test cases, and finally provides a downloadable `solution.py` file.
## UI

<img width="1912" height="547" alt="d2" src="https://github.com/user-attachments/assets/f45530c4-d057-4571-b0a2-dc35b583e53b" />

<img width="1911" height="987" alt="d3" src="https://github.com/user-attachments/assets/eeea97a3-b619-48d9-9a7a-e585610b1518" />

<img width="1874" height="938" alt="d4" src="https://github.com/user-attachments/assets/e32ec56b-61e2-46ac-bbd6-8156a16f503f" />

<img width="1175" height="853" alt="d5" src="https://github.com/user-attachments/assets/07fe9257-ec9e-47a1-b7ed-afb38d369207" />

<img width="1900" height="620" alt="d6" src="https://github.com/user-attachments/assets/7e327dbe-4120-48cb-854f-9a73075910d3" />

 
## What the Code Does (High-Level Flow)
1. User enters a DSA problem statement in the Streamlit web interface and submits.
2. A two‑agent team is instantiated via `RoundRobinGroupChat`:
   - **DSA_Problem_Solver_Agent** (LLM) plans the approach, writes code (one block at a time), requests execution, analyzes results, and decides when to stop.
   - **CodeExecutorAgent** executes received Python code safely inside a Docker container and returns stdout / results.
3. A termination condition (`TextMentionTermination` on the keyword `STOP`) or `MAX_TURNS` ends the session.
4. Messages stream back to the UI in real time; any fenced Python code blocks are captured.
5. Collected code blocks are aggregated into a synthesized `solution.py` preview and made available for download.
6. When finished, the Docker sandbox is shut down cleanly.

## Core Components
| Layer | Responsibility | Key Files / Constructs |
|-------|----------------|------------------------|
| UI / Presentation | Collect problem input, render streaming dialogue, provide download button | `app.py` (Streamlit) |
| Team Orchestration | Manages turn-taking between agents, termination logic | `team/dsa_team.py` (`RoundRobinGroupChat`, `TextMentionTermination`) |
| Problem Solving Agent | Generates reasoning steps & Python solutions | `agents/problem_solver.py` (`AssistantAgent`) |
| Code Execution Agent | Runs code in isolated Docker environment | `agents/code_executor_agent.py` (`CodeExecutorAgent`) |
| Docker Execution Layer | Starts/stops container, executes code with timeout | `config/docker_utils.py`, `config/docker_executor.py` (`DockerCommandLineCodeExecutor`) |
| Configuration | Central constants & model setup | `config/constant.py`, `config/settings.py` |
| Temporary Workspace | Stores generated / executed code (e.g., `solution.py`) | `temp/` (via `WORK_DIR`) |

## Detailed Interaction Sequence
```
[User]
   |
   v
[Streamlit Frontend]
   |  (submit problem)
   v
[Team Factory get_dsa_team_and_docker()]
   |--> creates RoundRobinGroupChat with agents
   v
[Problem Solver Agent] --(code block)--> [Code Executor Agent]
   ^                                       |
   |<-- execution results (stdout / tests)--|
   |
   | (repeat turns until STOP or max turns)
   v
[Termination Condition Reached]
   v
[Collected Code Blocks -> solution.py -> Download]
   v
[Docker Container Stopped]
```

## Agent Roles
- **DSA_Problem_Solver_Agent**
  - Expert reasoning on DSA tasks.
  - Always outlines a plan first.
  - Emits Python code in fenced blocks (one at a time).
  - Requests execution and interprets results.
  - Signals completion with `STOP`.
- **CodeExecutorAgent**
  - Receives code blocks.
  - Executes them in a controlled Docker workspace (`work_dir=TEMP`).
  - Enforces a timeout (from `TIMEOUT`).

## Termination Logic
- Primary condition: The message stream contains the token `STOP` (configured in `TEXT_MENTION`).
- Fallback: Conversation reaches `MAX_TURNS` (e.g., 15 turns) to avoid runaway loops.

## Tech Stack
- **Language:** Python 3.12+
- **Frontend:** Streamlit (custom CSS theming, dynamic streaming UI)
- **Multi-Agent Framework:** `autogen-agentchat`, `autogen-core`, `autogen_ext`
- **LLM Integration:** OpenAI Chat Completion (`OpenAIChatCompletionClient`)
- **Async Orchestration:** `asyncio` (streamed message consumption, container lifecycle)
- **Containerized Execution:** Docker via `DockerCommandLineCodeExecutor`
- **Environment & Secrets:** `python-dotenv` for `OPENAI_API_KEY`
- **Token Utilities:** `tiktoken` (available if needed by agents / models)

## Configuration & Constants
Defined in `config/constant.py`:
- `MODEL` – LLM model name (e.g., `gpt-4o`).
- `TEXT_MENTION` – Termination keyword (`STOP`).
- `WORK_DIR` – Directory where executed code & artifacts live (`temp`).
- `TIMEOUT` – Max execution time for a single code run (seconds).
- `MAX_TURNS` – Conversation cap.

Model client is constructed in `config/settings.py` using `OPENAI_API_KEY` (loaded from `.env`).

## Safety & Isolation
- All user / agent code is executed in a Docker container, reducing host risk.
- Timeouts prevent long‑running or hanging executions.
- Conversation turn limit avoids infinite loops.

## Downloadable Solution Assembly
- Stream parser extracts fenced code blocks: ```python ... ```
- Blocks are de‑duplicated & concatenated with headers.
- A timestamped `solution.py` is generated in memory and offered via Streamlit's `download_button`.

## Extensibility Ideas
- Add more specialized agents (e.g., Complexity Analyzer, Test Generator).
- Support alternative model providers (Azure, local, etc.).
- Multi-language execution layers (e.g., C++ or Java sandbox containers).
- Persist session transcripts & solutions to a database.

## System Architecture (Conceptual)
```
<img width="853" height="659" alt="image" src="https://github.com/user-attachments/assets/43b6862b-4980-41e1-877e-abf99f4fb716" />

    


