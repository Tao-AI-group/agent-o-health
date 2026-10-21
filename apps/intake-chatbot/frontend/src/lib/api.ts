import type { CardSession, ValidationResult } from "../types";

function tokenFromUrlFragment(): string {
  const fragment = new URLSearchParams(window.location.hash.replace(/^#/, ""));
  const token = fragment.get("access_token") || "";
  if (token) {
    sessionStorage.setItem("agento_access_token", token);
    window.history.replaceState(null, "", `${window.location.pathname}${window.location.search}`);
  }
  return token;
}

let accessToken = tokenFromUrlFragment() || sessionStorage.getItem("agento_access_token") || "";

export function setAccessToken(value: string) {
  accessToken = value;
  if (value) sessionStorage.setItem("agento_access_token", value);
  else sessionStorage.removeItem("agento_access_token");
}

function headers(contentType = true): HeadersInit {
  const value: Record<string, string> = {};
  if (contentType) value["Content-Type"] = "application/json";
  if (accessToken) value.Authorization = `Bearer ${accessToken}`;
  return value;
}

async function parse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(body.detail || "The request failed.");
  }
  return response.json() as Promise<T>;
}

export const api = {
  publicConfig: () => fetch("/api/config/public").then((response) => parse<Record<string, unknown>>(response)),
  health: () => fetch("/api/health").then((response) => parse<Record<string, string>>(response)),
  sessions: () => fetch("/api/sessions", { headers: headers(false) }).then((response) => parse<CardSession[]>(response)),
  session: (id: string) => fetch(`/api/sessions/${id}`, { headers: headers(false) }).then((response) => parse<CardSession>(response)),
  create: (name: string, intake_mode: string) => fetch("/api/sessions", { method: "POST", headers: headers(), body: JSON.stringify({ name, intake_mode }) }).then((response) => parse<CardSession>(response)),
  rename: (id: string, name: string) => fetch(`/api/sessions/${id}`, { method: "PATCH", headers: headers(), body: JSON.stringify({ name }) }).then((response) => parse<CardSession>(response)),
  remove: (id: string) => fetch(`/api/sessions/${id}`, { method: "DELETE", headers: headers(false) }),
  patchCard: (id: string, field_id: string, value: string) => fetch(`/api/sessions/${id}/card`, { method: "PATCH", headers: headers(), body: JSON.stringify({ updates: [{ field_id, value, replace: true }] }) }).then((response) => parse<{ session: CardSession }>(response)),
  undo: (id: string) => fetch(`/api/sessions/${id}/actions/undo`, { method: "POST", headers: headers(false) }).then((response) => parse<CardSession>(response)),
  skip: (id: string) => fetch(`/api/sessions/${id}/actions/skip`, { method: "POST", headers: headers(false) }).then((response) => parse<CardSession>(response)),
  notApplicable: (id: string, field_id: string, reason: string) => fetch(`/api/sessions/${id}/actions/not-applicable`, { method: "POST", headers: headers(), body: JSON.stringify({ field_id, reason }) }).then((response) => parse<CardSession>(response)),
  migrate: (id: string) => fetch(`/api/sessions/${id}/actions/migrate`, { method: "POST", headers: headers(false) }).then((response) => parse<CardSession>(response)),
  validate: (id: string) => fetch(`/api/sessions/${id}/actions/validate`, { method: "POST", headers: headers(false) }).then((response) => parse<ValidationResult>(response)),
  export: (id: string, includeDraft = true) => fetch(`/api/sessions/${id}/exports`, { method: "POST", headers: headers(), body: JSON.stringify({ include_draft: includeDraft }) }).then((response) => parse<{ id: string; download_url: string; filename: string }>(response)),
  import: (id: string, filename: string, content: string) => fetch(`/api/sessions/${id}/imports`, { method: "POST", headers: headers(), body: JSON.stringify({ filename, content }) }).then((response) => parse<{ session: CardSession }>(response)),
  download: async (url: string, filename: string) => {
    const response = await fetch(url, { headers: headers(false) });
    if (!response.ok) throw new Error("The export could not be downloaded.");
    const blob = await response.blob();
    const anchor = document.createElement("a");
    anchor.href = URL.createObjectURL(blob);
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(anchor.href);
  },
  streamMessage: async (
    id: string,
    content: string,
    signal: AbortSignal,
    onToken: (token: string) => void,
  ): Promise<CardSession> => {
    const response = await fetch(`/api/sessions/${id}/messages?stream=true`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({ content }),
      signal,
    });
    if (!response.ok || !response.body) throw new Error("The message could not be processed.");
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let completed: CardSession | null = null;
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split("\n\n");
      buffer = blocks.pop() || "";
      for (const block of blocks) {
        const event = block.match(/^event: (.+)$/m)?.[1];
        const raw = block.match(/^data: (.+)$/m)?.[1];
        if (!event || raw === undefined) continue;
        if (event === "token") onToken(raw);
        if (event === "done") completed = JSON.parse(raw).session;
      }
    }
    if (!completed) throw new Error("The response stream ended before completion.");
    return completed;
  },
};
