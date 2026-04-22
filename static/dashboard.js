(function () {
  const DEFAULT_API_BASE_URL =
    window.location.origin.indexOf("127.0.0.1") !== -1 ||
    window.location.origin.indexOf("localhost") !== -1
      ? window.location.origin
      : "https://pii-scrabber.onrender.com";

  const EXAMPLE_PROMPT =
    "Hi, I'm Bobby. My Aadhaar is 1234 5678 9876, email is bobby@company.com and I need a refund update drafted politely.";

  const ENTITY_TONES = {
    PERSON: "tone-person",
    EMAIL: "tone-email",
    PHONE: "tone-phone",
    AADHAAR: "tone-aadhaar",
    PAN: "tone-pan",
    PIN: "tone-pin",
    ORG: "tone-org",
    LOC: "tone-loc"
  };

  const state = {
    apiBase: window.localStorage.getItem("privacy-gateway-api") || DEFAULT_API_BASE_URL,
    input: EXAMPLE_PROMPT,
    result: null,
    logs: [],
    loadingChat: false,
    loadingLogs: true,
    error: "",
    logsError: ""
  };

  const app = document.getElementById("app");

  function icon(path) {
    return (
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="icon">' +
      path +
      "</svg>"
    );
  }

  const icons = {
    shield: icon('<path d="M12 3l7 3v6c0 5-3.5 8.5-7 10-3.5-1.5-7-5-7-10V6l7-3z"></path>'),
    sparkles: icon('<path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z"></path><path d="M5 16l.75 2.25L8 19l-2.25.75L5 22l-.75-2.25L2 19l2.25-.75L5 16z"></path><path d="M19 14l.75 2.25L22 17l-2.25.75L19 20l-.75-2.25L16 17l2.25-.75L19 14z"></path>'),
    activity: icon('<path d="M3 12h4l3-7 4 14 3-7h4"></path>'),
    lock: icon('<rect x="4" y="11" width="16" height="10" rx="2"></rect><path d="M8 11V8a4 4 0 018 0v3"></path>'),
    bot: icon('<rect x="7" y="8" width="10" height="10" rx="2"></rect><path d="M12 4v4"></path><path d="M9 2h6"></path><circle cx="10" cy="13" r="1"></circle><circle cx="14" cy="13" r="1"></circle>'),
    wand: icon('<path d="M15 4l5 5"></path><path d="M7 21l11-11"></path><path d="M4 15l5 5"></path><path d="M9 3l1 3"></path><path d="M19 13l3 1"></path>'),
    radar: icon('<path d="M12 12l6-6"></path><path d="M12 12a9 9 0 119 9"></path><path d="M12 12a4 4 0 104 4"></path><circle cx="12" cy="12" r="1.3"></circle>'),
    clock: icon('<circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3 2"></path>'),
    alert: icon('<path d="M12 3l9 16H3l9-16z"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path>'),
    check: icon('<path d="M20 6L9 17l-5-5"></path>'),
    refresh: icon('<path d="M21 12a9 9 0 00-15.5-6.36L3 8"></path><path d="M3 3v5h5"></path><path d="M3 12a9 9 0 0015.5 6.36L21 16"></path><path d="M16 16h5v5"></path>')
  };

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function formatDate(value) {
    if (!value) return "Unknown";
    try {
      return new Intl.DateTimeFormat("en-IN", {
        dateStyle: "medium",
        timeStyle: "short"
      }).format(new Date(value));
    } catch (error) {
      return value;
    }
  }

  function metric(label, value, iconSvg) {
    return (
      '<div class="metric">' +
      '<div class="metric-label">' + iconSvg + "<span>" + label + "</span></div>" +
      '<div class="metric-value">' + escapeHtml(value) + "</div>" +
      "</div>"
    );
  }

  function skeletonLines(count) {
    let html = "";
    for (let i = 0; i < count; i += 1) {
      const width = i === count - 1 ? "70%" : "100%";
      html += '<div class="skeleton skeleton-line" style="width:' + width + ';"></div>';
    }
    return html;
  }

  function renderEntities() {
    const entities = state.result && state.result.detected_entities ? state.result.detected_entities : [];

    if (!entities.length) {
      return (
        '<div class="entity-card">' +
        '<div class="muted">No entities yet. Run a prompt through the gateway to inspect detected PII.</div>' +
        "</div>"
      );
    }

    return entities
      .map(function (entity) {
        return (
          '<div class="entity-card">' +
          '<div class="entity-top">' +
          '<span class="badge ' + (ENTITY_TONES[entity.label] || "") + '">' + escapeHtml(entity.label) + "</span>" +
          '<span class="badge code">' + escapeHtml(entity.placeholder) + "</span>" +
          "</div>" +
          '<div class="mono">' + escapeHtml(entity.value) + "</div>" +
          '<div class="subtle" style="margin-top:10px;">' + escapeHtml(entity.semantic) + "</div>" +
          "</div>"
        );
      })
      .join("");
  }

  function renderXrayCard(title, subtitle, iconSvg, value, success) {
    return (
      '<div class="xray-card">' +
      '<div class="xray-header">' +
      "<div>" +
      '<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">' + iconSvg + '<strong>' + escapeHtml(title) + "</strong></div>" +
      '<div class="muted" style="font-size:14px;">' + escapeHtml(subtitle) + "</div>" +
      "</div>" +
      (success
        ? '<div class="success-badge">' + icons.check + "<span>Success</span></div>"
        : "") +
      "</div>" +
      (state.loadingChat
        ? skeletonLines(7)
        : '<div class="xray-pre mono">' +
          escapeHtml(value || "No data yet. Submit a prompt to inspect the pipeline.") +
          "</div>") +
      "</div>"
    );
  }

  function renderLogs() {
    if (state.loadingLogs) {
      return (
        '<div class="audit-list">' +
        '<div class="skeleton skeleton-block"></div>' +
        '<div class="skeleton skeleton-block"></div>' +
        '<div class="skeleton skeleton-block"></div>' +
        "</div>"
      );
    }

    if (state.logsError) {
      return '<div class="status-error">' + icons.alert + "<div>" + escapeHtml(state.logsError) + "</div></div>";
    }

    const rows = state.logs.length
      ? state.logs
          .map(function (log) {
            const badges = (log.pii_types || [])
              .map(function (type) {
                return '<span class="badge ' + (ENTITY_TONES[type] || "") + '">' + escapeHtml(type) + "</span>";
              })
              .join(" ");

            return (
              "<tr>" +
              '<td class="mono">' + escapeHtml(log.request_id || "") + "</td>" +
              "<td>" + escapeHtml(formatDate(log.timestamp)) + "</td>" +
              "<td>" + escapeHtml(log.pii_count) + "</td>" +
              "<td>" + (badges || '<span class="muted">None</span>') + "</td>" +
              "</tr>"
            );
          })
          .join("")
      : '<tr><td colspan="4" class="muted">No audit events yet. Process a prompt to populate this table.</td></tr>';

    return (
      '<div class="table-wrap"><table>' +
      "<thead><tr><th>Request ID</th><th>Timestamp</th><th>PII Count</th><th>PII Types</th></tr></thead>" +
      "<tbody>" + rows + "</tbody>" +
      "</table></div>"
    );
  }

  function render() {
    const result = state.result || {};
    const entityCount = result.detected_entities ? result.detected_entities.length : 0;

    app.innerHTML =
      '<div class="shell">' +
      '<section class="panel hero">' +
      '<div class="hero-grid">' +
      "<div>" +
      '<div class="hero-badge">' + icons.shield + "<span>AI Privacy Gateway</span></div>" +
      "<h1>Enterprise visibility for every prompt crossing your AI boundary.</h1>" +
      "<p>Inspect masked input, observe model output, and confirm safe re-hydration in one security-first workflow.</p>" +
      "</div>" +
      '<div class="metrics">' +
      metric("Detected entities", entityCount, icons.radar) +
      metric("Audit events", state.logs.length, icons.activity) +
      metric("Gateway mode", "Protected", icons.shield) +
      "</div>" +
      "</div>" +
      "</section>" +

      '<div class="layout">' +
      '<section class="panel">' +
      '<div class="panel-header"><div><div class="eyebrow">Input Console</div><h2 class="title">Prompt Inspection</h2></div></div>' +
      '<div class="panel-body">' +
      (state.error ? '<div class="status-error">' + icons.alert + "<div>" + escapeHtml(state.error) + "</div></div>" : "") +
      '<form id="chat-form">' +
      '<div class="field-group">' +
      '<label for="api-base">API Base URL</label>' +
      '<input id="api-base" type="url" value="' + escapeHtml(state.apiBase) + '">' +
      "</div>" +
      '<div class="field-group">' +
      '<div class="label-row"><label for="prompt-text">Sensitive Prompt</label><button id="load-example" class="btn-ghost" type="button">Load Example</button></div>' +
      '<textarea id="prompt-text" placeholder="Paste prompts containing names, IDs, emails, and other regulated data...">' + escapeHtml(state.input) + "</textarea>" +
      "</div>" +
      '<div class="button-row">' +
      '<button class="btn-primary" type="submit">' + (state.loadingChat ? icons.refresh + "<span>Processing...</span>" : icons.sparkles + "<span>Run Privacy Scan</span>") + "</button>" +
      '<button class="btn-secondary" id="clear-session" type="button">' + icons.refresh + "<span>Clear Session</span></button>" +
      "</div>" +
      "</form>" +
      "</div>" +
      "</section>" +

      '<section class="panel">' +
      '<div class="panel-header"><div><div class="eyebrow">Entity Radar</div><h2 class="title">PII Intelligence</h2></div></div>' +
      '<div class="panel-body">' +
      '<div class="entity-summary">' +
      '<div style="display:flex;align-items:center;gap:10px;">' + icons.shield + '<strong>Detection Summary</strong></div>' +
      '<div class="entity-count">' + escapeHtml(entityCount) + "</div>" +
      '<div class="muted">Sensitive entities identified in the submitted prompt.</div>' +
      "</div>" +
      '<div class="entity-list">' + (state.loadingChat && !state.result ? skeletonLines(6) : renderEntities()) + "</div>" +
      "</div>" +
      "</section>" +
      "</div>" +

      '<section class="panel">' +
      '<div class="panel-header"><div><div class="eyebrow">Process Visualization</div><h2 class="title">X-Ray Pipeline</h2></div></div>' +
      '<div class="panel-body">' +
      '<div class="xray-grid">' +
      renderXrayCard("Masked", "Sanitized prompt sent into the model boundary.", icons.lock, result.masked, false) +
      renderXrayCard("AI Thinking", "Model output before sensitive fields are restored.", icons.bot, result.llm_response, false) +
      renderXrayCard("Re-hydrated", "Response returned to the user after controlled restoration.", icons.wand, result.final_response, true) +
      "</div>" +
      "</div>" +
      "</section>" +

      '<section class="panel">' +
      '<div class="panel-header">' +
      '<div><div class="eyebrow">Governance</div><h2 class="title">Audit Trail</h2></div>' +
      '<button class="btn-secondary" id="refresh-logs" type="button">' + icons.refresh + "<span>Refresh</span></button>" +
      "</div>" +
      '<div class="panel-body">' + renderLogs() + "</div>" +
      "</section>" +
      "</div>";

    bindEvents();
  }

  function bindEvents() {
    const form = document.getElementById("chat-form");
    const apiInput = document.getElementById("api-base");
    const promptInput = document.getElementById("prompt-text");
    const loadExample = document.getElementById("load-example");
    const clearSession = document.getElementById("clear-session");
    const refreshLogs = document.getElementById("refresh-logs");

    apiInput.addEventListener("input", function (event) {
      state.apiBase = event.target.value;
    });

    promptInput.addEventListener("input", function (event) {
      state.input = event.target.value;
    });

    loadExample.addEventListener("click", function () {
      state.input = EXAMPLE_PROMPT;
      render();
    });

    clearSession.addEventListener("click", function () {
      state.input = "";
      state.result = null;
      state.error = "";
      render();
    });

    refreshLogs.addEventListener("click", function () {
      fetchLogs();
    });

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      runChat();
    });
  }

  async function fetchLogs() {
    state.loadingLogs = true;
    state.logsError = "";
    render();

    try {
      const response = await fetch(state.apiBase + "/logs");
      if (!response.ok) {
        throw new Error("Audit log request failed");
      }

      const data = await response.json();
      state.logs = Array.isArray(data) ? data : [];
    } catch (error) {
      state.logsError =
        "Could not load audit logs. The server may be waking up on Render or the /logs endpoint may be unavailable.";
    } finally {
      state.loadingLogs = false;
      render();
    }
  }

  async function runChat() {
    if (!state.input.trim()) {
      state.error = "Enter a prompt before scanning the privacy gateway.";
      render();
      return;
    }

    state.loadingChat = true;
    state.error = "";
    render();

    try {
      window.localStorage.setItem("privacy-gateway-api", state.apiBase);

      const response = await fetch(state.apiBase + "/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: state.input.trim() })
      });

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      state.result = await response.json();
      fetchLogs();
    } catch (error) {
      state.error =
        "The privacy gateway could not be reached. Render may still be waking up, or the API URL may be incorrect.";
    } finally {
      state.loadingChat = false;
      render();
    }
  }

  render();
  fetchLogs();
})();
