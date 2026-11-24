# Portal Guide Agent: Team Avyukt (Track 2: Beyond the Browser)

A browser agent that makes government portals understandable. It highlights the field you are on,
explains it in **Kannada / Hindi / English** by voice, and tells you which document to keep ready.

**Read-only by design.** The agent never types into a field, clicks, or submits. The user stays in control,
and no personal data is read or sent. Only the field label and type leave the browser.

## Problem
Rural students pay cyber cafés to fill portals like the Karnataka State Scholarship Portal (SSP) because the
jargon (RD number, IFSC, income certificate) is confusing and help is not available in their language.

## How it works
```
Chrome extension (content.js)  --label, type, lang-->  API Gateway + Lambda
   highlights field, shows panel                         |-- glossary (offline, common SSP fields)
   plays voice                  <--text + audio----------|-- Amazon Bedrock (any other field)
                                                         `-- ElevenLabs TTS (Kannada/Hindi/English voice)
```

## Run the demo locally (no keys needed)
1. `python backend/local_server.py`
2. Chrome → `chrome://extensions` → Developer mode → Load unpacked → select `extension/`
3. Open `demo/mock_ssp_form.html` (enable "Allow access to file URLs" for the extension) or the real SSP site.
4. Click a field. The panel explains it. Without ElevenLabs keys, the browser's built-in voice is used.

## Enable ElevenLabs and AWS
- Copy `.env.example` to `.env` and set the keys (export them before running the server).
- Deploy `backend/` as a Lambda (handler `lambda_handler.handler`) behind an API Gateway HTTP API.
  Set `BEDROCK_MODEL_ID`, `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` as environment variables.
  Give the Lambda role `bedrock:InvokeModel` permission.
- Put the API URL in `extension/background.js` (`API_URL`).

## Status (MVP)
- [x] Field detection, highlight, explanation panel
- [x] Glossary for common SSP fields in 3 languages
- [x] Lambda handler, Bedrock fallback, ElevenLabs voice
- [ ] Document checklist per scheme, caching in DynamoDB, more portals

## Team
Avyukt
