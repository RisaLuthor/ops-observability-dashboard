"use client";

import { useEffect, useMemo, useState } from "react";

type Metrics = {
  service: string;
  uptime_seconds: number;
  requests_total: number;
  errors_total: number;
  by_status: Record<string, number>;
  by_route: Array<{ route: string; method: string; count: number; errors: number; avg_ms: number }>;
};

type EventItem = {
  id: string;
  ts: string;
  level: string;
  service: string;
  message: string;
  meta: Record<string, any>;
};

export default function Home() {
  const API_BASE = useMemo(() => process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8001", []);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [m, e, s] = await Promise.all([
        fetch(`${API_BASE}/metrics`, { cache: "no-store" }),
        fetch(`${API_BASE}/events?limit=25`, { cache: "no-store" }),
        fetch(`${API_BASE}/events/summary`, { cache: "no-store" }),
      ]);

      if (!m.ok) throw new Error(`/metrics failed: ${m.status}`);
      if (!e.ok) throw new Error(`/events failed: ${e.status}`);
      if (!s.ok) throw new Error(`/events/summary failed: ${s.status}`);

      setMetrics(await m.json());
      setEvents(await e.json());
      setSummary(await s.json());
    } catch (err: any) {
      setError(err?.message ?? "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const id = setInterval(load, 8000);
    return () => clearInterval(id);
  }, []);

  return (
    <main style={{ fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif", padding: 24, maxWidth: 1200, margin: "0 auto" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 16 }}>
        <div>
          <h1 style={{ margin: 0 }}>Ops Observability Dashboard</h1>
          <p style={{ marginTop: 6, color: "#555" }}>
            Live view of API health, request metrics, and operational events.
          </p>
        </div>
        <button onClick={load} disabled={loading} style={{ padding: "10px 14px", borderRadius: 8, border: "1px solid #ddd", background: "#fff", cursor: "pointer" }}>
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </header>

      {error && (
        <div style={{ marginTop: 16, padding: 12, borderRadius: 10, background: "#fff3f3", border: "1px solid #ffd1d1" }}>
          <strong>UI Error:</strong> {error}
          <div style={{ marginTop: 6, color: "#666" }}>API base: {API_BASE}</div>
        </div>
      )}

      <section style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginTop: 18 }}>
        <Card title="Uptime" value={metrics ? `${metrics.uptime_seconds}s` : "—"} />
        <Card title="Requests" value={metrics ? metrics.requests_total : "—"} />
        <Card title="Errors" value={metrics ? metrics.errors_total : "—"} />
        <Card title="Service" value={metrics ? metrics.service : "—"} />
      </section>

      <section style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 12, marginTop: 16 }}>
        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 14 }}>
          <h2 style={{ margin: "0 0 10px 0", fontSize: 16 }}>Endpoint metrics</h2>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", color: "#666" }}>
                <th style={th}>Method</th>
                <th style={th}>Route</th>
                <th style={th}>Count</th>
                <th style={th}>Errors</th>
                <th style={th}>Avg (ms)</th>
              </tr>
            </thead>
            <tbody>
              {(metrics?.by_route ?? []).map((r, i) => (
                <tr key={`${r.method}-${r.route}-${i}`} style={{ borderTop: "1px solid #f0f0f0" }}>
                  <td style={td}>{r.method}</td>
                  <td style={tdMono}>{r.route}</td>
                  <td style={td}>{r.count}</td>
                  <td style={td}>{r.errors}</td>
                  <td style={td}>{r.avg_ms}</td>
                </tr>
              ))}
              {!metrics?.by_route?.length && (
                <tr>
                  <td style={td} colSpan={5}>No route data yet. Hit a few endpoints.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 14 }}>
          <h2 style={{ margin: "0 0 10px 0", fontSize: 16 }}>Event summary</h2>
          <pre style={{ background: "#fafafa", border: "1px solid #eee", borderRadius: 10, padding: 12, overflowX: "auto" }}>
            {summary ? JSON.stringify(summary, null, 2) : "—"}
          </pre>
        </div>
      </section>

      <section style={{ border: "1px solid #eee", borderRadius: 12, padding: 14, marginTop: 16 }}>
        <h2 style={{ margin: "0 0 10px 0", fontSize: 16 }}>Recent events</h2>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ textAlign: "left", color: "#666" }}>
              <th style={th}>Time (UTC)</th>
              <th style={th}>Level</th>
              <th style={th}>Service</th>
              <th style={th}>Message</th>
            </tr>
          </thead>
          <tbody>
            {events.map((ev) => (
              <tr key={ev.id} style={{ borderTop: "1px solid #f0f0f0" }}>
                <td style={tdMono}>{ev.ts}</td>
                <td style={td}>{ev.level}</td>
                <td style={td}>{ev.service}</td>
                <td style={td}>{ev.message}</td>
              </tr>
            ))}
            {!events.length && (
              <tr>
                <td style={td} colSpan={4}>No events yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>

      <footer style={{ marginTop: 18, color: "#777", fontSize: 12 }}>
        Auto-refresh every ~8s • API: {API_BASE}
      </footer>
    </main>
  );
}

function Card({ title, value }: { title: string; value: any }) {
  return (
    <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 14 }}>
      <div style={{ color: "#666", fontSize: 12 }}>{title}</div>
      <div style={{ marginTop: 6, fontSize: 20, fontWeight: 700 }}>{value}</div>
    </div>
  );
}

const th: React.CSSProperties = { padding: "8px 6px", fontSize: 12 };
const td: React.CSSProperties = { padding: "8px 6px", verticalAlign: "top" };
const tdMono: React.CSSProperties = { ...td, fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" };