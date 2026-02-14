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

## Development

### Code Quality

This project uses Claude Pilot for automated code quality:
- Auto-formatting on save
- Linting and type-checking
- TDD enforcement
- Spec-driven development

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Project Status

See `PROJECT_WORKSPACE.md` for:
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

For issues, questions, or contributions, refer to `PROJECT_WORKSPACE.md` for agent coordination protocols.

