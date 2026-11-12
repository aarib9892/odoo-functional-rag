import { useEffect, useRef, useState, type FormEvent } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

type Citation = { evidence_id: string; title: string; excerpt: string; documentation_url: string;
  source_url: string; source_path: string; commit: string; version: string };
type Answer = { request_id: string; status: 'answered' | 'needs_clarification' | 'insufficient_evidence';
  message: string; claims: { text: string; citations: { evidence_id: string; quote: string }[] }[];
  clarification_question: string | null; citations: Citation[];
  trace: { latency_ms: number; snapshot_id: string | null } };
type Feedback = { outcome: string; comment: string; task_minutes: number | null };
type Entry = { request_id: string; question: string; response: Answer | null; error: string | null; feedback: Feedback | null };
type Coverage = { release_id: string; documents: number; topics: string[]; reviewed_workflows: string[]; searchable_documents?: number; reference_only_documents?: number; state?: string };
type Session = { name: string; history: Entry[]; coverage?: Coverage };

class ApiError extends Error { constructor(message: string, public status: number) { super(message); } }
async function api<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`/api${path}`, { credentials: 'same-origin',
    ...(body === undefined ? {} : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }) });
  const result = await response.json();
  if (!response.ok) {
    const detail = result.detail;
    throw new ApiError(typeof detail === 'string' ? detail : detail?.message
      ? `${detail.message}${detail.request_id ? ` Request: ${detail.request_id}` : ''}`
      : 'The request could not be completed. Please try again.', response.status);
  }
  return result;
}

const examples = ['How do ordered and delivered quantity invoicing differ?',
  'How do I deliver part of an order and create a backorder?',
  'How do I return a product after the customer has been invoiced?'];
const supportedVersion = '19.0';
const fullExamples = ['How do I set up a POS shop with cash payments?',
  'How do I configure an online shop with delivery and pickup?',
  'How do I record a partial payment against an existing invoice?'];

function FeedbackForm({ entry, expired }: { entry: Entry; expired: () => void }) {
  const [outcome, setOutcome] = useState(entry.feedback?.outcome || '');
  const [comment, setComment] = useState(entry.feedback?.comment || '');
  const [minutes, setMinutes] = useState(entry.feedback?.task_minutes?.toString() || '');
  const [state, setState] = useState('');
  const [busy, setBusy] = useState(false);
  async function save(event: FormEvent) {
    event.preventDefault(); setBusy(true); setState('');
    try {
      await api(`/requests/${entry.request_id}/feedback`, { outcome, comment, task_minutes: minutes === '' ? null : Number(minutes) });
      setState('Feedback saved. Thank you.');
    } catch (error) { if (error instanceof ApiError && error.status === 401) expired(); setState((error as Error).message); }
    finally { setBusy(false); }
  }
  return <details className="feedback"><summary>Did this help you complete the task? {entry.feedback ? '· Feedback recorded' : ''}</summary>
    <form onSubmit={save}>
      <fieldset><legend>Task outcome</legend><div className="outcomes">
        {[['solved', 'Solved'], ['partially_solved', 'Partially solved'], ['unresolved', 'Unresolved']].map(([value, label]) =>
          <label key={value}><input type="radio" name={`outcome-${entry.request_id}`} value={value} checked={outcome === value} onChange={() => setOutcome(value)} required />{label}</label>)}
      </div></fieldset>
      <label>Correction or comment <span>(optional)</span><textarea maxLength={2000} rows={2} value={comment} onChange={e => setComment(e.target.value)} /></label>
      <label>Time spent on the task, in minutes <span>(optional)</span><input type="number" min="0" max="1440" step="0.1" value={minutes} onChange={e => setMinutes(e.target.value)} /></label>
      <button className="secondary" disabled={!outcome || busy}>{busy ? 'Saving…' : 'Save feedback'}</button>
      <p role="status">{state}</p>
    </form>
  </details>;
}

function AnswerCard({ entry, expired }: { entry: Entry; expired: () => void }) {
  const answer = entry.response;
  return <article className="answer-card">
    <div className="eyebrow">Your task</div><h2>{entry.question}</h2>
    {entry.error || !answer ? <p className="error">This request could not be completed. Please ask again. Reference: {entry.request_id}</p> : <>
      <div className={`state ${answer.status}`}>{({ answered: 'Documentation guidance', needs_clarification: 'One detail first', insufficient_evidence: 'More evidence needed' })[answer.status]}</div>
      <p className="answer-message">{answer.message}</p>
      {answer.clarification_question ? <p className="clarification">{answer.clarification_question}</p> : null}
      {answer.claims.length ? <ol className="claims">{answer.claims.map((claim, i) => <li key={i}><p>{claim.text}</p><div className="citation-tags">
        {claim.citations.map((ref, j) => <a key={j} href={`#${entry.request_id}-${ref.evidence_id}`} title={ref.quote}>{ref.evidence_id}</a>)}
      </div></li>)}</ol> : null}
      {answer.citations.length ? <section className="evidence"><h3>Check the evidence <span>{answer.citations.length} passages</span></h3>
        {answer.citations.map(citation => <details key={citation.evidence_id} id={`${entry.request_id}-${citation.evidence_id}`}>
          <summary><span className="evidence-id">{citation.evidence_id}</span>{citation.title}<span className="version">19.0</span></summary>
          <blockquote>{citation.excerpt}</blockquote>
          <div className="source-links"><a href={citation.documentation_url} target="_blank" rel="noreferrer">Read Odoo documentation ↗</a>
            <a href={citation.source_url} target="_blank" rel="noreferrer">Pinned source ↗</a></div>
          <small>Source commit {citation.commit.slice(0, 12)} · Documentation pages may change; the source link preserves the indexed version.</small>
        </details>)}
      </section> : null}
      <div className="trace">{(answer.trace.latency_ms / 1000).toFixed(1)}s · Request {entry.request_id.slice(0, 8)}</div>
      <FeedbackForm entry={entry} expired={expired} />
    </>}
  </article>;
}

function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [coverage, setCoverage] = useState<Coverage | null>(null);
  const [checking, setChecking] = useState(true);
  const [key, setKey] = useState('');
  const [error, setError] = useState('');
  const [question, setQuestion] = useState('');
  const [busy, setBusy] = useState(false);
  const [pending, setPending] = useState('');
  const [entries, setEntries] = useState<Entry[]>([]);
  const [readiness, setReadiness] = useState('');
  const questionInput = useRef<HTMLTextAreaElement>(null);
  const latest = useRef<HTMLDivElement>(null);
  const mounted = useRef(true);
  function expired() { setSession(null); setEntries([]); setKey(''); setError('Your session ended. Sign in again.'); }
  async function loadSession() {
    const current = await api<Session>('/session');
    if (mounted.current) { setSession(current); setEntries(current.history); setCoverage(current.coverage || null); }
    try { await api('/ready'); if (mounted.current) setReadiness('Documentation index connected'); }
    catch { if (mounted.current) setReadiness('Dependencies unavailable. Ask the operator to check the pilot.'); }
  }
  useEffect(() => {
    mounted.current = true;
    loadSession().catch(error => { if (mounted.current && (!(error instanceof ApiError) || error.status !== 401)) setError(error.message); })
      .finally(() => { if (mounted.current) setChecking(false); });
    return () => { mounted.current = false; };
  }, []);
  useEffect(() => { if (entries.length) latest.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, [entries.length]);
  async function login(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('');
    try { await api('/login', { access_key: key }); setKey(''); await loadSession(); }
    catch (error) { setError((error as Error).message); }
    finally { setBusy(false); }
  }
  async function logout() {
    setBusy(true); setError('');
    try { await api('/logout', {}); setSession(null); setEntries([]); setQuestion(''); }
    catch (error) { if (error instanceof ApiError && error.status === 401) expired(); else setError((error as Error).message); }
    finally { setBusy(false); }
  }
  async function ask(event: FormEvent) {
    event.preventDefault(); if (!question.trim() || busy) return;
    const submitted = question.trim(); setBusy(true); setError(''); setPending(submitted);
    try {
      const answer = await api<Answer>('/answers', { question: submitted, odoo_version: supportedVersion });
      setEntries(previous => [...previous, { request_id: answer.request_id, question: submitted, response: answer, error: null, feedback: null }]);
      setQuestion('');
    } catch (error) { if (error instanceof ApiError && error.status === 401) expired(); else setError((error as Error).message); }
    finally { setBusy(false); setPending(''); questionInput.current?.focus(); }
  }
  return <>
    <header><a className="brand" href="/" aria-label="Odoo Fieldguide home"><span className="brand-icon">f</span><span>Odoo <strong>Fieldguide</strong></span></a><span className="pilot-badge">INTERNAL PILOT</span>
      {session ? <div className="account"><span>{session.name}</span><button className="text-button" onClick={logout} disabled={busy}>Sign out</button></div> : null}
    </header>
    <main className={session ? 'workspace' : 'welcome'}>
      <aside><div className="eyebrow">A little clarity, grounded in the docs</div><h1>Move your<br /> Odoo task<br /> <em>forward.</em></h1>
        <p>Practical guidance with the source beside it. Ask about a workflow covered by this documentation release.</p>
        <div className="scope"><span className="dot" />Odoo 19 · English<span>{coverage ? `${coverage.topics.join(', ')} · ${coverage.documents} documentation pages` : 'Sign in to view documentation coverage'}</span></div>
        <div className="scope-note">{coverage && coverage.documents > 30 ? `${coverage.searchable_documents ?? 'Most'} pages contain searchable content; ${coverage.reference_only_documents ?? 'some'} are reference-only. Workflow correctness still requires review; screenshot interpretation is unavailable.` : coverage ? 'The current release covers Sales and Inventory with one Accounting page supporting returns and refunds.' : 'Sign in to see the active documentation scope. Screenshot interpretation is unavailable.'}</div>
        {coverage?.state === 'indexed_candidate' ? <p className="scope-note">Candidate preview · awaiting release review.</p> : null}
        {coverage ? <p className="scope-note">{coverage.reviewed_workflows.length} workflow families accepted by human review in this release.</p> : null}
        <div className="boundary"><strong>A guide for your review.</strong><p>This pilot cannot read or change your Odoo database. Review guidance against your setup.</p><p>Questions and feedback are saved for pilot review. Keep customer and confidential data out of this pilot.</p></div>
        <footer>Documentation: Odoo · <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noreferrer">CC BY-SA 4.0</a></footer>
      </aside>
      <section className="conversation" aria-label={session ? 'Ask Fieldguide' : 'Pilot sign in'}>
        {checking ? <p role="status">Opening your pilot session…</p> : !session ? <div className="login-panel"><div className="eyebrow">Your pilot workspace</div><h2>Welcome to Fieldguide</h2><p>Use the access key shared by your pilot operator.</p>
          <form onSubmit={login}><label>Pilot access key<input type="password" autoComplete="off" required maxLength={256} value={key} onChange={e => setKey(e.target.value)} /></label>
            <button disabled={busy}>{busy ? 'Signing in…' : 'Open workspace →'}</button></form></div> : <>
          <div className="workspace-heading"><div><div className="eyebrow">Your workspace</div><h2>From question to next step</h2></div><span className="readiness">{readiness}</span></div>
          {!entries.length ? <div className="starter"><h3>What are you working on?</h3><p>Include the workflow and what has already happened. The assistant will ask when a detail changes the guidance.</p><div className="examples">{(coverage && coverage.documents > 30 ? fullExamples : examples).map(example => <button className="example" key={example} onClick={() => { setQuestion(example); questionInput.current?.focus(); }}>{example}<span>↗</span></button>)}</div></div> : null}
          <div className="answers">{entries.map((entry, i) => <div key={entry.request_id} ref={i === entries.length - 1 ? latest : undefined}><AnswerCard entry={entry} expired={expired} /></div>)}</div>
          {pending ? <div className="loading" role="status"><span className="pulse" />Checking the documentation and supporting evidence…<p>{pending}</p></div> : null}
          <form className="composer" onSubmit={ask}><div className="composer-top"><label htmlFor="question">Your Odoo task</label><span className="supported-version">Odoo 19</span></div>
            <textarea ref={questionInput} id="question" placeholder="Describe your task and the current order, delivery or invoice status…" maxLength={1800} required rows={4} value={question} onChange={e => setQuestion(e.target.value)} disabled={busy} />
            <div className="composer-bottom"><span>{question.length}/1800 · Public documentation only</span><button disabled={busy || !question.trim()}>{busy ? 'Checking evidence…' : 'Ask Fieldguide →'}</button></div>
          </form>
        </>}
        {error ? <p className="error" role="alert">{error}</p> : null}
      </section>
    </main>
  </>;
}

createRoot(document.getElementById('root')!).render(<App />);
