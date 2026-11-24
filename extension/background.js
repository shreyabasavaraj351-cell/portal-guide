// Relays explain requests to the backend (avoids page CORS issues).
// Change API_URL to your API Gateway URL after deploying the Lambda.
const API_URL = "http://localhost:8787/explain";

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type !== "explain") return;
  fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(msg.payload),
  })
    .then((r) => r.json())
    .then(sendResponse)
    .catch(() => sendResponse({ explanation: "Could not reach the guide service.", documents: [] }));
  return true; // async response
});
