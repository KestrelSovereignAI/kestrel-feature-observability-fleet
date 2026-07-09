// Fleet observability — orchestrator swimlane panel.
//
// Host-scoped console module. Renders the orchestrator tree (GET /tree) as
// swimlanes — one lane per orchestrator (with a top-level "Direct" lane for
// events that have no orchestrator) — and tails the live stream (GET /stream,
// a fetch-based text/event-stream with Last-Event-ID resumability).
//
// Registered via HostFeature.get_ui_contributions(); sovereign mounts this
// module and serves the sibling static assets.

const API_PREFIX = "/api/observability";

export const panel = {
  id: "observability-fleet-swimlane",
  title: "Fleet Swimlane",

  async fetchTree() {
    const res = await fetch(`${API_PREFIX}/tree`, { credentials: "include" });
    if (!res.ok) throw new Error(`tree ${res.status}`);
    return res.json();
  },

  // Fetch-based live stream. `onEvent` is called per event; resumes from the
  // last stream id after a reconnect via the Last-Event-ID header.
  async stream(onEvent, { signal, lastEventId } = {}) {
    const headers = {};
    if (lastEventId) headers["Last-Event-ID"] = String(lastEventId);
    const res = await fetch(`${API_PREFIX}/stream`, {
      credentials: "include",
      headers,
      signal,
    });
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let idx;
      while ((idx = buffer.indexOf("\n\n")) !== -1) {
        const frame = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 2);
        const idLine = frame.split("\n").find((l) => l.startsWith("id: "));
        const dataLine = frame.split("\n").find((l) => l.startsWith("data: "));
        if (dataLine) {
          const id = idLine ? Number(idLine.slice(4)) : undefined;
          onEvent(JSON.parse(dataLine.slice(6)), id);
        }
      }
    }
  },
};

export default panel;
