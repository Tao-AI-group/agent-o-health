import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import {
  AlertTriangle,
  Archive,
  Bot,
  Check,
  ChevronRight,
  CircleHelp,
  ClipboardCheck,
  Download,
  FileInput,
  FileText,
  History,
  Info,
  Menu,
  MessageSquare,
  MoreHorizontal,
  PanelRight,
  Pencil,
  Plus,
  RefreshCw,
  Search,
  Send,
  ShieldCheck,
  SkipForward,
  Square,
  Trash2,
  Undo2,
  X,
} from "lucide-react";
import { api, setAccessToken } from "./lib/api";
import type { CardSession, Requirement, ValidationResult } from "./types";

type InspectorTab = "overview" | "sections" | "issues" | "preview" | "history";
type ModalState =
  | { type: "none" }
  | { type: "new" }
  | { type: "rename"; value: string }
  | { type: "edit"; requirement: Requirement; value: string }
  | { type: "na"; requirement: Requirement; reason: string }
  | { type: "export"; includeDraft: boolean }
  | { type: "delete" };

const modeOptions = [
  { id: "existing", title: "Describe an existing agent", description: "Document a system that is implemented or currently used." },
  { id: "planned", title: "Document a planned agent", description: "Capture intended architecture and governance before implementation." },
  { id: "import", title: "Import structured information", description: "Start from a text, Markdown, JSON, YAML, JSON-LD, or Turtle file." },
];

function pretty(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function StatusMark({ status }: { status: string }) {
  return <span className={`status status-${status}`}>{pretty(status)}</span>;
}

function IconButton({ label, children, onClick, disabled = false, active = false }: { label: string; children: React.ReactNode; onClick?: () => void; disabled?: boolean; active?: boolean }) {
  return <button type="button" className={`icon-button${active ? " active" : ""}`} aria-label={label} title={label} onClick={onClick} disabled={disabled}>{children}</button>;
}

function Modal({ state, onClose, onSubmit }: { state: ModalState; onClose: () => void; onSubmit: (state: ModalState) => void }) {
  const initialValue = state.type === "rename" || state.type === "edit" ? state.value : state.type === "na" ? state.reason : "";
  const [value, setValue] = useState(initialValue);
  useEffect(() => setValue(initialValue), [initialValue, state.type]);
  if (state.type === "none") return null;
  const title = state.type === "new" ? "Start a new Agent Card" : state.type === "rename" ? "Rename session" : state.type === "edit" ? `Edit ${state.requirement.label}` : state.type === "na" ? "Mark as not applicable" : state.type === "export" ? "Export Agent Card" : "Delete session";
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <header><h2 id="modal-title">{title}</h2><IconButton label="Close" onClick={onClose}><X size={18} /></IconButton></header>
        {state.type === "new" && <div className="mode-list">{modeOptions.map((mode) => <button key={mode.id} className="mode-option" onClick={() => onSubmit({ type: "rename", value: mode.id })}><span>{mode.title}</span><small>{mode.description}</small><ChevronRight size={18} /></button>)}</div>}
        {state.type === "rename" && <form onSubmit={(event) => { event.preventDefault(); onSubmit({ ...state, value }); }}><label>Session name<input autoFocus value={value} onChange={(event) => setValue(event.target.value)} /></label><div className="modal-actions"><button type="button" className="secondary-button" onClick={onClose}>Cancel</button><button className="primary-button" type="submit" disabled={!value.trim()}>Save</button></div></form>}
        {state.type === "edit" && <form onSubmit={(event) => { event.preventDefault(); onSubmit({ ...state, value }); }}><label>Reported value<textarea autoFocus rows={5} value={value} onChange={(event) => setValue(event.target.value)} /></label><p className="field-help">This creates a confirmed human-edit assertion with provenance.</p><div className="modal-actions"><button type="button" className="secondary-button" onClick={onClose}>Cancel</button><button className="primary-button" type="submit" disabled={!value.trim()}>Update field</button></div></form>}
        {state.type === "na" && <form onSubmit={(event) => { event.preventDefault(); onSubmit({ ...state, reason: value }); }}><p>Provide a reason. Not applicable is never assigned automatically.</p><label>Applicability reason<textarea autoFocus rows={4} value={value} onChange={(event) => setValue(event.target.value)} /></label><div className="modal-actions"><button type="button" className="secondary-button" onClick={onClose}>Cancel</button><button className="primary-button" type="submit" disabled={value.trim().length < 3}>Confirm</button></div></form>}
        {state.type === "export" && <><p>A draft bundle may include missing fields and validation findings. A conformant bundle requires all required reporting fields and no SHACL violations.</p><div className="export-options"><button className="secondary-button" onClick={() => onSubmit({ type: "export", includeDraft: true })}><FileText size={17} /><span><strong>Download draft</strong><small>Include current gaps and validation findings</small></span></button><button className="primary-button" onClick={() => onSubmit({ type: "export", includeDraft: false })}><ShieldCheck size={17} /><span><strong>Download conformant bundle</strong><small>Require complete reporting and SHACL conformance</small></span></button></div></>}
        {state.type === "delete" && <><p>This permanently deletes the session and its locally stored assertions.</p><div className="modal-actions"><button type="button" className="secondary-button" onClick={onClose}>Cancel</button><button className="danger-button" onClick={() => onSubmit(state)}>Delete session</button></div></>}
      </section>
    </div>
  );
}

function AccessScreen({ onConnect, error }: { onConnect: (value: string) => void; error: string }) {
  const [token, setToken] = useState("");
  return <main className="access-screen"><section className="access-panel"><div className="brand-mark"><ShieldCheck size={24} /><strong>AGENT-O</strong></div><h1>Connect to Agent Card Intake</h1><p>Enter the access token supplied by your internal deployment administrator.</p><form onSubmit={(event) => { event.preventDefault(); onConnect(token); }}><label>Access token<input type="password" autoFocus autoComplete="current-password" value={token} onChange={(event) => setToken(event.target.value)} /></label>{error && <p className="form-error">{error}</p>}<button className="primary-button" type="submit" disabled={!token}>Connect</button></form><p className="privacy-note"><Info size={15} /> Do not enter patient identifiers or PHI unless this deployment has been institutionally approved.</p></section></main>;
}

function App() {
  const [config, setConfig] = useState<Record<string, unknown> | null>(null);
  const [sessions, setSessions] = useState<CardSession[]>([]);
  const [active, setActive] = useState<CardSession | null>(null);
  const [composer, setComposer] = useState("");
  const [search, setSearch] = useState("");
  const [streaming, setStreaming] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [authNeeded, setAuthNeeded] = useState(false);
  const [tab, setTab] = useState<InspectorTab>("overview");
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [modal, setModal] = useState<ModalState>({ type: "none" });
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const timelineRef = useRef<HTMLDivElement>(null);

  async function loadSessions(selectFirst = true) {
    try {
      const values = await api.sessions();
      setSessions(values);
      setAuthNeeded(false);
      if (selectFirst && !active && values[0]) setActive(await api.session(values[0].id));
    } catch (requestError) {
      if (String(requestError).includes("Authentication")) setAuthNeeded(true);
      else setError(requestError instanceof Error ? requestError.message : "Unable to load sessions.");
    }
  }

  useEffect(() => {
    api.publicConfig().then((value) => { setConfig(value); loadSessions(); }).catch((requestError) => setError(String(requestError)));
  }, []);

  useEffect(() => {
    timelineRef.current?.scrollTo({ top: timelineRef.current.scrollHeight, behavior: "smooth" });
  }, [active?.messages?.length, streaming]);

  async function selectSession(id: string) {
    setBusy(true); setError("");
    try { setActive(await api.session(id)); setValidation(null); setSidebarOpen(false); }
    catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to open session."); }
    finally { setBusy(false); }
  }

  async function createSession(mode: string, name = "Untitled Agent Card") {
    setBusy(true); setError("");
    try { const created = await api.create(name, mode); setActive(created); await loadSessions(false); setModal({ type: "none" }); setSidebarOpen(false); }
    catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to create session."); }
    finally { setBusy(false); }
  }

  async function send(event?: FormEvent, retryText?: string) {
    event?.preventDefault();
    const text = (retryText ?? composer).trim();
    if (!text || !active || busy) return;
    const optimistic = { id: `local-${Date.now()}`, role: "user" as const, content: text, status: "sending", created_at: new Date().toISOString() };
    setActive({ ...active, messages: [...(active.messages || []), optimistic] });
    setComposer(""); setStreaming(""); setBusy(true); setError("");
    const controller = new AbortController(); abortRef.current = controller;
    try {
      const updated = await api.streamMessage(active.id, text, controller.signal, (token) => setStreaming((value) => value + token));
      setActive(updated); setStreaming(""); await loadSessions(false);
    } catch (requestError) {
      if ((requestError as Error).name !== "AbortError") setError(requestError instanceof Error ? requestError.message : "Unable to send message.");
      try { setActive(await api.session(active.id)); } catch { /* The optimistic text remains visible until the next reload. */ }
      setStreaming("");
    } finally { setBusy(false); abortRef.current = null; }
  }

  async function action(fn: () => Promise<CardSession>) {
    if (!active) return;
    setBusy(true); setError("");
    try { setActive(await fn()); await loadSessions(false); }
    catch (requestError) { setError(requestError instanceof Error ? requestError.message : "The action failed."); }
    finally { setBusy(false); }
  }

  async function validate() {
    if (!active) return;
    setBusy(true); setError(""); setTab("issues"); setInspectorOpen(true);
    try { const result = await api.validate(active.id); setValidation(result); setActive(await api.session(active.id)); }
    catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Validation failed."); }
    finally { setBusy(false); }
  }

  async function exportBundle(includeDraft = true) {
    if (!active) return;
    setBusy(true); setError("");
    try { const result = await api.export(active.id, includeDraft); await api.download(result.download_url, result.filename); setActive(await api.session(active.id)); setModal({ type: "none" }); }
    catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Export failed."); }
    finally { setBusy(false); }
  }

  async function importFile(file: File) {
    if (!active) return;
    setBusy(true); setError("");
    try { const text = await file.text(); const result = await api.import(active.id, file.name, text); setActive(result.session); }
    catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Import failed."); }
    finally { setBusy(false); if (fileRef.current) fileRef.current.value = ""; }
  }

  async function submitModal(state: ModalState) {
    if (state.type === "new") return;
    if (state.type === "rename") {
      if (modeOptions.some((mode) => mode.id === state.value)) { await createSession(state.value); return; }
      if (active) await action(() => api.rename(active.id, state.value));
      setModal({ type: "none" }); return;
    }
    if (!active) return;
    if (state.type === "edit") { await action(async () => (await api.patchCard(active.id, state.requirement.id, state.value)).session); setModal({ type: "none" }); }
    if (state.type === "na") { await action(() => api.notApplicable(active.id, state.requirement.id, state.reason)); setModal({ type: "none" }); }
    if (state.type === "export") { await exportBundle(state.includeDraft); }
    if (state.type === "delete") { await api.remove(active.id); setActive(null); setModal({ type: "none" }); await loadSessions(); }
  }

  const filtered = sessions.filter((session) => session.name.toLowerCase().includes(search.toLowerCase()));
  const requirements = active?.completeness?.requirements || [];
  const missing = requirements.filter((item) => item.status === "missing" || item.status === "partial");
  const current = active?.current_question ? requirements.find((item) => item.id === active.current_question?.id) : undefined;

  if (!config) return <main className="loading-screen"><RefreshCw className="spin" /><span>Loading ontology profile...</span></main>;
  if (authNeeded) return <AccessScreen error={error} onConnect={(value) => { setAccessToken(value); setError(""); loadSessions(); }} />;

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "mobile-open" : ""}`} aria-label="Card sessions">
        <div className="brand"><div className="brand-mark"><ShieldCheck size={20} /><strong>AGENT-O</strong></div><IconButton label="Close sessions" onClick={() => setSidebarOpen(false)}><X size={18} /></IconButton></div>
        <button className="new-button" onClick={() => setModal({ type: "new" })}><Plus size={17} /> New Card</button>
        <label className="search-box"><Search size={16} /><span className="sr-only">Search sessions</span><input placeholder="Search sessions" value={search} onChange={(event) => setSearch(event.target.value)} /></label>
        <nav className="session-list">{filtered.map((session) => <button key={session.id} className={`session-item ${active?.id === session.id ? "selected" : ""}`} onClick={() => selectSession(session.id)}><FileText size={17} /><span><strong>{session.name}</strong><small>{session.completeness_summary.score ?? 0}% reported</small></span></button>)}{!filtered.length && <p className="empty-list">No matching sessions</p>}</nav>
        <footer><span>Profile {String(config.profile_version)}</span><span>Ontology {active?.ontology_snapshot_id || "ready"}</span></footer>
      </aside>

      <main className="workspace">
        <header className="topbar"><div className="mobile-actions"><IconButton label="Open sessions" onClick={() => setSidebarOpen(true)}><Menu size={19} /></IconButton></div><div className="title-block"><h1>{active?.name || "Agent Card Intake"}</h1>{active && <span>{pretty(active.intake_mode)} agent</span>}</div>{active && <div className="top-actions"><IconButton label="Undo last update" onClick={() => action(() => api.undo(active.id))} disabled={busy}><Undo2 size={18} /></IconButton><button className="secondary-button compact" onClick={validate} disabled={busy}><ClipboardCheck size={17} /> Validate</button><button className="primary-button compact" onClick={() => setModal({ type: "export", includeDraft: true })} disabled={busy}><Download size={17} /> Export</button><IconButton label="Open Card Inspector" onClick={() => setInspectorOpen(true)}><PanelRight size={19} /></IconButton><IconButton label="More session actions" onClick={() => setModal({ type: "rename", value: active.name })}><MoreHorizontal size={19} /></IconButton></div>}</header>

        {!active ? <section className="onboarding"><div className="onboarding-heading"><div className="symbol"><Bot size={28} /></div><h2>Build a structured Agent Card</h2><p>Describe the system naturally. AGENT-O will organize reported facts, identify gaps, validate the RDF graph, and prepare an export for human review.</p></div><div className="mode-grid">{modeOptions.map((mode) => <button key={mode.id} onClick={() => createSession(mode.id)}><span>{mode.title}</span><small>{mode.description}</small><ChevronRight size={18} /></button>)}</div><p className="boundary-note"><CircleHelp size={17} /> Reporting completeness is separate from agent quality, safety, and deployment readiness.</p></section> : <>
          {!active.ontology_snapshot_current && <div className="warning-banner" role="status"><AlertTriangle size={17} /><span>This session uses an earlier ontology snapshot. Review migration changes before validation or export.</span><button onClick={() => action(() => api.migrate(active.id))}>Migrate snapshot</button></div>}
          <div className="timeline" ref={timelineRef} aria-live="polite">{active.messages?.map((message, index) => <article key={message.id} className={`message ${message.role}`}><div className="avatar">{message.role === "assistant" ? <Bot size={18} /> : "You"}</div><div className="message-body"><ReactMarkdown rehypePlugins={[rehypeSanitize]}>{message.content}</ReactMarkdown>{message.status === "error" && <><span className="message-state">Update unavailable</span><button className="message-retry" onClick={() => { const previous = active.messages?.slice(0, index).reverse().find((item) => item.role === "user"); if (previous) send(undefined, previous.content); }}><RefreshCw size={14} /> Retry last message</button></>}</div></article>)}{streaming && <article className="message assistant"><div className="avatar"><Bot size={18} /></div><div className="message-body streaming-text">{streaming}<span className="cursor" /></div></article>}</div>
          {error && <div className="error-banner" role="alert"><AlertTriangle size={17} /><span>{error}</span><button onClick={() => setError("")} aria-label="Dismiss error"><X size={16} /></button></div>}
          <section className="composer-area">{active.current_question && <div className="question-context"><span>Current topic</span><strong>{active.current_question.label}</strong></div>}<div className="quick-actions"><button onClick={() => setComposer("I don't know")}><CircleHelp size={15} /> I don't know</button><button disabled={!current} onClick={() => current && setModal({ type: "na", requirement: current, reason: "" })}><Archive size={15} /> Not applicable</button><button onClick={() => action(() => api.skip(active.id))}><SkipForward size={15} /> Skip for now</button><button onClick={() => { setTab("sections"); setInspectorOpen(true); }}><FileText size={15} /> Review extracted facts</button></div><form className="composer" onSubmit={send}><textarea aria-label="Message" placeholder="Describe the agent or answer the current question" rows={2} value={composer} onChange={(event) => setComposer(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); send(); } }} /><input ref={fileRef} type="file" hidden accept=".txt,.md,.json,.jsonld,.yaml,.yml,.ttl" onChange={(event) => event.target.files?.[0] && importFile(event.target.files[0])} /><IconButton label="Import a supported file" onClick={() => fileRef.current?.click()} disabled={busy}><FileInput size={19} /></IconButton>{busy ? <IconButton label="Stop response" onClick={() => abortRef.current?.abort()}><Square size={18} /></IconButton> : <button className="send-button" type="submit" aria-label="Send message" title="Send message" disabled={!composer.trim()}><Send size={18} /></button>}</form><p>Do not enter patient identifiers or PHI unless this deployment is approved for that use.</p></section>
        </>}
      </main>

      {active && <aside className={`inspector ${inspectorOpen ? "mobile-open" : ""}`} aria-label="Card Inspector"><header><div><span>Card Inspector</span><small>{active.completeness?.unresolved_required_count} required items unresolved</small></div><IconButton label="Close Card Inspector" onClick={() => setInspectorOpen(false)}><X size={18} /></IconButton></header><nav className="inspector-tabs" aria-label="Inspector views">{(["overview", "sections", "issues", "preview", "history"] as InspectorTab[]).map((value) => <button key={value} title={pretty(value)} aria-label={pretty(value)} className={tab === value ? "active" : ""} onClick={() => setTab(value)}>{value === "overview" ? <Info /> : value === "sections" ? <FileText /> : value === "issues" ? <AlertTriangle /> : value === "preview" ? <MessageSquare /> : <History />}</button>)}</nav><div className="inspector-content">
        {tab === "overview" && active.completeness && <><section className="status-block"><h2>Review status</h2><dl><div><dt>SHACL conformance</dt><dd><StatusMark status={active.completeness.shacl_conformance} /></dd></div><div><dt>Reporting completeness</dt><dd><strong>{active.completeness.reporting_completeness_score ?? 0}%</strong></dd></div><div><dt>Review readiness</dt><dd><StatusMark status={active.completeness.review_readiness} /></dd></div></dl></section><section className="score-block"><div className="score-ring"><strong>{active.completeness.reporting_completeness_score || 0}</strong><span>of 100</span></div><p>{active.completeness.score_interpretation}</p></section><section><h2>Coverage dimensions</h2><div className="dimension-list">{active.completeness.dimensions.map((dimension) => <div key={dimension.id}><span>{dimension.label}</span><strong>{dimension.fraction === null ? "N/A" : `${Math.round(dimension.fraction * 100)}%`}</strong><progress aria-label={`${dimension.label} reporting completeness`} max={1} value={dimension.fraction || 0} /></div>)}</div></section></>}
        {tab === "sections" && active.completeness && <section><h2>Reporting sections</h2><div className="section-list">{active.completeness.sections.map((section) => <div key={section.id} className="section-row"><button onClick={() => setExpandedSection(expandedSection === section.id ? null : section.id)}><StatusMark status={section.status} /><span><strong>{section.label}</strong><small>{section.counts.present || 0} present · {(section.counts.missing || 0) + (section.counts.partial || 0)} unresolved</small></span><ChevronRight className={expandedSection === section.id ? "rotated" : ""} size={17} /></button>{expandedSection === section.id && <div className="requirement-list">{requirements.filter((item) => item.section === section.id).map((item) => <button key={item.id} onClick={() => setModal({ type: "edit", requirement: item, value: item.value || "" })}><StatusMark status={item.status} /><span><strong>{item.label}</strong><small>{item.value || item.question}</small></span><Pencil size={15} /></button>)}</div>}</div>)}</div></section>}
        {tab === "issues" && <section><div className="section-heading"><h2>Validation issues</h2><button className="secondary-button compact" onClick={validate} disabled={busy}><RefreshCw size={15} /> Run validation</button></div>{!validation ? <div className="empty-state"><ClipboardCheck size={28} /><p>Run validation to check the current RDF graph against all three AGENT-O SHACL suites.</p></div> : <><div className={`validation-summary ${validation.conforms ? "success" : "warning"}`}>{validation.conforms ? <Check /> : <AlertTriangle />}<div><strong>{validation.conforms ? "Conformant" : "Needs attention"}</strong><span>{validation.results.length} findings across {validation.data_triples} data triples</span></div></div><div className="issue-list">{validation.results.map((item, index) => <article key={`${item.source_shape}-${index}`}><StatusMark status={item.severity.toLowerCase()} /><strong>{item.message}</strong><code title={item.path}>{item.path ? item.path.split("#").pop() : "Node constraint"}</code></article>)}</div></>}</section>}
        {tab === "preview" && <section><h2>Card preview</h2><div className="card-preview"><h3>{active.name}</h3><p className="preview-notice">Draft for reporting and human review. Not a quality or safety certification.</p>{active.completeness?.sections.map((section) => <div key={section.id}><h4>{section.label}</h4>{requirements.filter((item) => item.section === section.id && item.value).map((item) => <p key={item.id}><strong>{item.label}</strong><span>{item.value}</span></p>)}</div>)}</div></section>}
        {tab === "history" && <section><h2>Assertion history</h2><div className="history-list">{active.assertions?.slice().reverse().map((item) => <article key={item.id}><div><strong>{requirements.find((field) => field.id === item.field_id)?.label || item.field_id}</strong><StatusMark status={item.review_state} /></div><p>{item.value}</p><small>Evidence: “{item.source_evidence}” · {Math.round(item.confidence * 100)}% confidence</small><code title={item.predicate_uri}>{item.predicate_uri.split("#").pop()}</code></article>)}{!active.assertions?.length && <div className="empty-state"><History size={28} /><p>No structured updates yet.</p></div>}</div></section>}
      </div><footer className="inspector-footer"><button className="secondary-button" onClick={() => setModal({ type: "delete" })}><Trash2 size={16} /> Delete</button><button className="primary-button" onClick={() => setModal({ type: "export", includeDraft: true })}><Download size={16} /> Export</button></footer></aside>}
      {(sidebarOpen || inspectorOpen) && <button className="mobile-scrim" aria-label="Close open panel" onClick={() => { setSidebarOpen(false); setInspectorOpen(false); }} />}
      <Modal state={modal} onClose={() => setModal({ type: "none" })} onSubmit={submitModal} />
    </div>
  );
}

export default App;
