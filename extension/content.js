// READ-ONLY by design: this script never sets a field value, clicks, or submits.
// It only highlights the focused field and shows an explanation panel.
(() => {
  let lang = "kn";
  const panel = document.createElement("div");
  panel.id = "pga-panel";
  panel.innerHTML = `
    <div class="pga-head">
      <b>Portal Guide</b>
      <select id="pga-lang">
        <option value="kn">ಕನ್ನಡ</option>
        <option value="hi">हिन्दी</option>
        <option value="en">English</option>
      </select>
    </div>
    <div id="pga-text">Click any field and I will explain it.</div>
    <div id="pga-docs"></div>
    <button id="pga-listen">🔊 Listen</button>`;
  document.body.appendChild(panel);

  const textEl = panel.querySelector("#pga-text");
  const docsEl = panel.querySelector("#pga-docs");
  let audioB64 = null;

  panel.querySelector("#pga-lang").addEventListener("change", (e) => (lang = e.target.value));
  panel.querySelector("#pga-listen").addEventListener("click", () => {
    if (audioB64) {
      new Audio("data:audio/mpeg;base64," + audioB64).play();
    } else if ("speechSynthesis" in window) {
      // Fallback when ElevenLabs is not configured
      const u = new SpeechSynthesisUtterance(textEl.textContent);
      u.lang = { kn: "kn-IN", hi: "hi-IN", en: "en-IN" }[lang];
      speechSynthesis.speak(u);
    }
  });

  function labelFor(el) {
    if (el.id) {
      const l = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
      if (l) return l.textContent.trim();
    }
    const wrap = el.closest("label");
    if (wrap) return wrap.textContent.trim();
    return el.getAttribute("aria-label") || el.placeholder || el.name || "";
  }

  let current = null;
  document.addEventListener("focusin", (e) => {
    const el = e.target;
    if (!el.matches || !el.matches("input, select, textarea")) return;
    if (current) current.classList.remove("pga-highlight");
    current = el;
    el.classList.add("pga-highlight");

    const options = el.tagName === "SELECT" ? [...el.options].map((o) => o.text).slice(0, 15) : [];
    textEl.textContent = "…";
    docsEl.textContent = "";
    chrome.runtime.sendMessage(
      { type: "explain", payload: { label: labelFor(el), type: el.type || el.tagName, options, lang, speak: true } },
      (res) => {
        if (!res) return;
        textEl.textContent = res.explanation;
        audioB64 = res.audio_b64 || null;
        docsEl.textContent = res.documents?.length ? "📄 Keep ready: " + res.documents.join(", ") : "";
        if (audioB64) new Audio("data:audio/mpeg;base64," + audioB64).play();
      }
    );
  });
})();
