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

## Quick Start

### 1. Clone and Setup

```bash
cd youtube-shorts-generator
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

1. Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
# Edit .env with your API keys
```

2. Copy `config.example.yaml` to `config.yaml` and adjust settings:
```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your preferences
```

### 3. Health Check

Before running, verify all systems are ready:
```bash
python -m src.cli.main health
```

### 4. Generate Video

Run the pipeline:
```bash
python -m src.cli.main generate
```

## Project Structure

```
youtube-shorts-generator/
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

### Health check failures

Run `python -m src.cli.main health` to get a JSON report. Common causes:

- **Missing or invalid API keys**: One or more checks show `ok: false`. Ensure `.env` exists (copy from `.env.example`) and all required keys are set. See **Configuration reference** below for the list.
- **Insufficient disk space**: The `disk_space` check fails if free space is below the configured minimum (default 10GB). Free space or increase `resources.min_disk_gb` in `config.yaml`.
- **Low RAM**: The `system_resources` check can fail if available RAM is below the minimum (default 8GB). Close other applications or adjust `resources.min_ram_gb`.
- **Database/SQLite errors**: Ensure the project directory is writable and the path in `paths.database` (default `youtube_shorts.db`) is valid.
- **API connectivity**: OpenAI, ElevenLabs, RunwayML, or YouTube checks can fail due to invalid keys, network issues, or rate limits. Verify keys in the provider dashboards and retry.

### Common errors

- **ModuleNotFoundError or import errors**: Activate the venv (`source venv/bin/activate` or `venv\Scripts\activate`) and ensure `pip install -r requirements.txt` was run from the project root.
- **Permission denied on .env or config.yaml**: Ensure the files exist and are readable; do not commit `.env` or a `config.yaml` that contains secrets.
- **FFmpeg not found**: Install FFmpeg and ensure it is on your PATH (required for video processing).

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

**Using Pilot:** Run `/sync` in the project to generate or refresh project-specific rules. Pilot then provides formatting, linting, and type-checking (e.g. on save or on demand). Activate the project venv before running tests or tools that Pilot may invoke.

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

