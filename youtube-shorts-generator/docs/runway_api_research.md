# Runway API Research (Text-to-Video)

Short reference for the Runway API as used by youtube-shorts-generator. Implementation: `src/services/runwayml_service.py` (official **Runway Python SDK**, not raw HTTP).

## Auth

- **Runway docs**: Use `RUNWAYML_API_SECRET` as the Bearer token.
- **This project**: Supports both `RUNWAYML_API_KEY` and `RUNWAYML_API_SECRET` (either is accepted). Header: `Authorization: Bearer <key>`.
- **Base URL**: `https://api.dev.runwayml.com`
- **Version header**: `X-Runway-Version: 2024-11-06` (required).

## Models

- **Text-to-video**: `gen4.5` (no input image; omit `promptImage`).
- **Image-to-video**: Same endpoint with `promptImage` (URL or data URI); same model `gen4.5`.

## Task lifecycle (SDK)

1. **Create**: `client.text_to_video.create(model="gen4.5", prompt_text=..., ratio="720:1280", duration=5)`. Returns a waitable response with `id`.
2. **Wait**: Call `created.wait_for_task_output(timeout=600)`; SDK polls until `SUCCEEDED` or raises `TaskFailedError` / `TaskTimeoutError`.
3. **Output**: Completed task has `task.output` (list of URLs). Download first URL to local file (e.g. `tmp/runway_output.mp4`); URLs are ephemeral (24–48h).

## Request (text-to-video)

| Field        | Notes                                      |
|-------------|---------------------------------------------|
| `model`     | `"gen4.5"`                                  |
| `promptText`| 1–5000 chars (we cap at 1000)               |
| `ratio`     | `"768:1280"` (Shorts) or `"1280:768"` (API 2024-11-06) |
| `duration`  | Integer 2, 5, 8, or 10 seconds              |

## Output format

- Task response: `output` (or `outputs`) = list of video URLs (strings or objects with `url`).
- Download the first URL to get the MP4; do not expose ephemeral URLs in the product.

## References

- API docs: https://docs.dev.runwayml.com  
- Getting started: https://docs.dev.runwayml.com/guides/using-the-api  
- API version 2024-11-06: ratio values `768:1280`, `1280:768` (replacing 16:9 / 9:16).
