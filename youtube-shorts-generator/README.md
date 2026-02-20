# YouTube Shorts Generator

Autonomous MCP-based system that generates and publishes high-quality YouTube Shorts daily using AI-generated video content.

## Overview

This system uses a Simple Agent Orchestration pattern with Python asyncio to coordinate specialized agents through a video generation pipeline. Each agent handles one stage of the pipeline, from content research to YouTube publishing.

## Features

- **Autonomous Content Generation**: AI-powered script and video generation
- **Multi-Agent Pipeline**: 8 specialized agents working in sequence
- **Cost Tracking**: Real-time cost monitoring per component
- **Quality Control**: Automated validation and uniqueness checking
- **Error Recovery**: Graceful failure handling with progress preservation

## Architecture

The system follows a Simple Agent Orchestration pattern:

- **Agents**: Specialized components for each pipeline stage (Research, Script, TTS, Video, Composition, Quality, Publishing)
- **Orchestration**: Sequential execution with message queue and state management
- **Services**: Abstraction layer for external APIs (OpenAI, ElevenLabs, RunwayML, YouTube)
- **Database**: SQLite for state persistence, execution history, and cost tracking

See `PROJECT_WORKSPACE.md` for detailed architecture documentation.

## Requirements

- Python 3.11+
- FFmpeg (for video processing)
- 8GB RAM minimum
- 10GB free disk space
- API keys for:
  - OpenAI (GPT-4, embeddings)
  - ElevenLabs (TTS)
  - RunwayML (video generation)
  - YouTube Data API v3

## Setup

Follow these steps from the project root (`youtube-shorts-generator/`).

### 1. Create a virtual environment

Create and activate a Python virtual environment so dependencies are isolated:

```bash
cd youtube-shorts-generator
python3 -m venv venv
```

**Activate the venv:**

- **macOS/Linux:** `source venv/bin/activate`
- **Windows (cmd):** `venv\Scripts\activate.bat`
- **Windows (PowerShell):** `venv\Scripts\Activate.ps1`

Your prompt should show `(venv)` when active. Use this same shell for the steps below.

### 2. Install dependencies

From the project root (with venv activated):

```bash
pip install -r requirements.txt
```

This installs core libraries (PyYAML, python-dotenv, pydantic, structlog), API clients (OpenAI, ElevenLabs, RunwayML, Google APIs), video tools (moviepy, ffmpeg-python), and dev dependencies (pytest). Ensure **FFmpeg** is installed on your system and on your PATH; the health check will verify it.

### 3. Environment variables (.env)

Copy the example env file and set your API keys:

```bash
cp .env.example .env
```

Edit `.env` and set at least these (required for full pipeline):

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Required. OpenAI API key for GPT and embeddings. |
| `ELEVENLABS_API_KEY` | Required for TTS. |
| `RUNWAYML_API_KEY` | Required for video generation. |
| `YOUTUBE_CLIENT_ID` | YouTube Data API v3 OAuth client ID. |
| `YOUTUBE_CLIENT_SECRET` | YouTube OAuth client secret. |
| `YOUTUBE_REFRESH_TOKEN` | Obtained after first OAuth flow; used for uploads. |

Optional overrides (leave blank to use defaults): `OPENAI_CHAT_MODEL`, `OPENAI_FALLBACK_CHAT_MODEL`, `OPENAI_EMBEDDING_MODEL`, `OPENAI_FALLBACK_EMBEDDING_MODEL`.  
**Do not commit `.env`** — it is gitignored.

### 4. Config file (config.yaml)

Copy the example config and adjust if needed:

```bash
cp config.example.yaml config.yaml
```

`config.yaml` controls timeouts, retries, quality thresholds, cost limits, content preferences, resource limits (disk/RAM), and paths (database, temp dir, output dir). You can run with the defaults; change values when you need different limits or paths. See **Configuration reference** below for main sections. Do not commit `config.yaml` if it contains secrets.

### 5. Run the health check

Verify environment, API keys, disk/RAM, and FFmpeg before generating:

```bash
python -m src.cli.main health
```

This prints a JSON report. All checks should show `"ok": true`. If any fail, fix the reported issue (e.g. missing key, low disk space) and run again. See **Troubleshooting** for common causes.

### 6. Generate a Short

Run the full pipeline (research → script → TTS → video → composition → quality → optional YouTube upload):

```bash
python -m src.cli.main generate
```

Ensure the health check passes first. Output videos are written to the directory configured in `config.yaml` (default: `output_videos/`).

## Project Structure

```
youtube-shorts-generator/
├── .claude/rules/           # Pilot code-quality rules (see Development)
├── src/
│   ├── agents/              # Agent implementations
│   ├── orchestration/       # Pipeline orchestration
│   ├── services/            # External API integrations
│   ├── database/             # Database layer
│   ├── utils/               # Shared utilities
│   └── cli/                 # CLI interface
├── tests/                   # Test suite
├── config.yaml              # System settings
├── .env                     # API keys (gitignored)
└── README.md
```

## Troubleshooting

Use this section when the health check fails, `generate` errors, or you see config/API errors. Where to look: **logs** (stdout from the CLI), **stderr** (config/startup errors), **health JSON** (`python -m src.cli.main health`), and **PROJECT_WORKSPACE.md** (at the workspace root) for implementation status and coordination.

### Missing or invalid .env

**Symptom:** Health check shows `ok: false` for `openai`, `elevenlabs`, or `runwayml` with messages like `OPENAI_API_KEY not set`; or the CLI prints `Missing or empty env: OPENAI_API_KEY` (and similar) to stderr before exiting.

**Remedies:**

- Ensure `.env` exists in the project root: `cp .env.example .env` then edit `.env`.
- Set every **required** variable with a non-empty value (no leading/trailing spaces). Required: `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`, `RUNWAYML_API_KEY`, `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`.
- For OpenAI: use a valid API key from the OpenAI dashboard; 401/403 usually mean wrong key or no access to the model.
- For Runway: the app accepts either `RUNWAYML_API_KEY` or `RUNWAYML_API_SECRET`; set one of them.
- Restart the shell or re-run from the project root so the process sees the updated `.env`. Never commit `.env`.

### Config errors (config.yaml)

**Symptom:** CLI prints validation errors to stderr at startup (e.g. when running `health` or `generate`), such as `timeouts.research must be a positive number` or `cost.target_per_video must be positive`.

**Remedies:**

- Copy the example: `cp config.example.yaml config.yaml` if you don’t have `config.yaml`.
- **Timeouts:** Under `timeouts`, every value must be a positive number (integer or float). Fix or remove any zero/negative or non-numeric values.
- **Cost:** `cost.target_per_video` must be positive. Set it to a number > 0 (e.g. `4.10`).
- **Paths:** `paths.database`, `paths.temp_dir`, and `paths.output_dir` must be valid; ensure the project directory is writable. Use relative paths from the project root or absolute paths.
- **YAML syntax:** Avoid tabs; use spaces. Check for duplicate keys or invalid indentation if you see parse errors.

### Health check failures

Run `python -m src.cli.main health` to get a JSON report. Use it to see which check failed and the `detail` field for the reason.

- **Missing or invalid API keys:** One or more of `openai`, `elevenlabs`, `runwayml` (or `youtube`) show `"ok": false`. Fix `.env` as in **Missing or invalid .env** above; re-run health.
- **Insufficient disk space:** The `disk_space` check fails if free space is below the configured minimum (default 10GB). Free space or increase `resources.min_disk_gb` in `config.yaml`.
- **Low RAM:** The `system_resources` check can fail if available RAM is below the minimum (default 8GB). Close other applications or adjust `resources.min_ram_gb` in `config.yaml`.
- **Database/SQLite:** Ensure the project directory is writable and `paths.database` (default `youtube_shorts.db`) is valid. Fix path or permissions and re-run.
- **FFmpeg not found:** Install FFmpeg and ensure it is on your PATH; required for video processing. The health check verifies FFmpeg availability.
- **API connectivity:** Keys set but check still fails: possible network issues, rate limits, or revoked keys. Verify keys in the provider dashboards and retry; see **API errors** below for provider-specific hints.

### API errors (OpenAI, ElevenLabs, Runway)

Errors from external APIs often appear in the **CLI stdout** (structlog JSON) or in the health report `detail` field. Typical cases:

- **OpenAI:** 401/403 usually mean invalid key or no access to the model. If you get 403 for the default model, set `OPENAI_CHAT_MODEL` or `OPENAI_FALLBACK_CHAT_MODEL` / `OPENAI_EMBEDDING_MODEL` / `OPENAI_FALLBACK_EMBEDDING_MODEL` in `.env` to models you have access to. Rate limits: retry later or reduce concurrency.
- **ElevenLabs:** Invalid key or quota exceeded. Check the ElevenLabs dashboard for usage and key validity; ensure `ELEVENLABS_API_KEY` is correct and has quota.
- **Runway:** Invalid or missing key (use `RUNWAYML_API_KEY` or `RUNWAYML_API_SECRET`). Rate limits or service errors: retry after a delay; check Runway status or docs if errors persist.

If the health check passes but `generate` fails mid-pipeline, inspect the **last log lines** on stdout for the failing component (research, script, tts, video, etc.) and the exception message.

### Other common errors

- **ModuleNotFoundError or import errors:** Activate the venv (`source venv/bin/activate` or `venv\Scripts\activate`) and run `pip install -r requirements.txt` from the project root (`youtube-shorts-generator/`).
- **Permission denied on .env or config.yaml:** Ensure the files exist in the project root and are readable by the current user; do not commit `.env` or a `config.yaml` that contains secrets.
- **FFmpeg not found:** Install FFmpeg and ensure it is on your PATH (required for video processing).

### Where to look

| What you need | Where to look |
|---------------|----------------|
| Config/startup validation errors | CLI **stderr** when running `health` or `generate` |
| Per-check pass/fail and API key issues | Output of `python -m src.cli.main health` (JSON) |
| Pipeline progress and API/service errors | CLI **stdout** (structlog JSON logs) |
| Project status, plan, and coordination | **PROJECT_WORKSPACE.md** at the workspace root |
| Configuration reference | This README: **Configuration reference** (env vars and config.yaml sections) |

## Configuration reference

### Environment variables (.env)

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI API (GPT-4, embeddings) |
| `ELEVENLABS_API_KEY` | ElevenLabs text-to-speech |
| `RUNWAYML_API_KEY` | RunwayML video generation |
| `YOUTUBE_CLIENT_ID` | YouTube Data API v3 OAuth |
| `YOUTUBE_CLIENT_SECRET` | YouTube OAuth |
| `YOUTUBE_REFRESH_TOKEN` | YouTube OAuth refresh token (after first auth) |

Copy `.env.example` to `.env` and fill in values. Never commit `.env`.

### config.yaml (main sections)

- **timeouts**: Per-component and pipeline time limits (seconds).
- **retry**: `max_retries` and `backoff_seconds` for retries.
- **quality**: Script coherence, uniqueness similarity, duration, resolution, FPS, file size limits.
- **cost**: Target/warning/critical per-video and monthly alerts (USD).
- **content**: Topic categories, relevance score, optional fallback topics.
- **resources**: `min_disk_gb`, `min_ram_gb`, `temp_storage_gb` (used by health check and local runs).
- **paths**: `database`, `temp_dir`, `output_dir`.

Copy `config.example.yaml` to `config.yaml` and adjust as needed.

## Development

### Code Quality

This project uses Claude Pilot for automated code quality:
- Auto-formatting on save
- Linting and type-checking
- TDD enforcement
- Spec-driven development

### Pilot (code quality)

Project-specific rules live in `.claude/rules/`:

- **agent-guidelines.mdc** — References PROJECT_WORKSPACE.md for agent coordination and work log.
- **python-development.mdc** — PEP 8, type hints, pytest layout, `src/` structure (applies to `**/*.py`).
- **content-generation.mdc** — Standards for script/research/uniqueness agents and services.
- **video-quality.mdc** — Standards for video pipeline and composition (config, service layer).
- **mcp-framework.mdc** — Message queue, state manager, and agent communication.

**Using Pilot:** Run `/sync` in the project to generate or refresh project-specific rules. Pilot then provides formatting, linting, and type-checking (e.g. on save or on demand). Activate the project venv before running tests or tools that Pilot may invoke. If Pilot is not installed, see the workspace root docs or run: `curl -fsSL https://raw.githubusercontent.com/maxritter/claude-pilot/main/install.sh | bash` in the project directory. Pilot handles code quality; project status and coordination are in `PROJECT_WORKSPACE.md` at the workspace root.

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Project Status

See `PROJECT_WORKSPACE.md` (at the workspace root) for:
- Current implementation status
- Agent coordination
- Approval workflows
- Development progress

## Cost Targets

- **Per Video**: <$5.00 (target: $4.10 with 20% buffer)
- **Monthly (30 videos)**: ~$130-166
- **Component Breakdown**:
  - Research: <$0.10
  - Script: <$0.40
  - TTS: <$0.90
  - Video: <$2.50
  - Other: <$0.20

## License

Part of the Multi-Agent Autonomous Development Workspace system.

## Support

For issues, questions, or contributions, refer to `PROJECT_WORKSPACE.md` (at the workspace root) for agent coordination protocols, current status, and next actions.

