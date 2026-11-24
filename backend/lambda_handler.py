"""AWS Lambda entry point (behind API Gateway HTTP API).

POST /explain  body: {"label": "...", "type": "text", "options": [], "lang": "kn", "speak": true}
"""
import json

import core

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
}


def handler(event, context):
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {"statusCode": 204, "headers": HEADERS, "body": ""}
    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return {"statusCode": 400, "headers": HEADERS, "body": json.dumps({"error": "bad json"})}

    result = core.explain(payload)
    if payload.get("speak"):
        result["audio_b64"] = core.tts(result["explanation"], payload.get("lang", "en"))
    return {"statusCode": 200, "headers": HEADERS, "body": json.dumps(result, ensure_ascii=False)}
