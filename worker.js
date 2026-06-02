/**
 * Floret Capitals — PMEX Newsletter Worker
 *
 * Single Cloudflare Worker that:
 *   • /api/prices?symbols=...  → live prices from Yahoo Finance
 *   • /api/calendar            → high-impact economic calendar (ForexFactory feed)
 *   • everything else          → static assets (index.html, etc.)
 *
 * This replaces the Pages-style functions/ folder (which only works on Pages
 * projects). Works in the unified Workers + Assets model.
 */

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Content-Type": "application/json",
  "Cache-Control": "no-store",
};

async function handlePrices(request) {
  const url = new URL(request.url);
  const symbols = (url.searchParams.get("symbols") || "")
    .split(",").map(s => s.trim()).filter(Boolean);

  if (request.method === "OPTIONS") return new Response(null, { headers: CORS });
  if (symbols.length === 0)
    return new Response(JSON.stringify({ error: "No symbols provided" }), { status: 400, headers: CORS });

  const results = {};
  await Promise.all(symbols.map(async (sym) => {
    try {
      const yurl = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(sym)}?range=3mo&interval=1d`;
      const r = await fetch(yurl, {
        headers: { "User-Agent": "Mozilla/5.0 (compatible; FloretCapitals/1.0)" },
        signal: AbortSignal.timeout(12000),
      });
      if (!r.ok) { results[sym] = { error: `HTTP ${r.status}` }; return; }
      const j = await r.json();
      const res = j?.chart?.result?.[0];
      if (!res) { results[sym] = { error: "No data" }; return; }
      const meta = res.meta || {};
      const q = res.indicators?.quote?.[0] || {};
      const closes = (q.close || []).filter(v => v != null);
      const highs = (q.high || []).filter(v => v != null);
      const lows = (q.low || []).filter(v => v != null);
      results[sym] = {
        price: meta.regularMarketPrice ?? closes[closes.length - 1] ?? null,
        prevClose: meta.chartPreviousClose ?? closes[closes.length - 2] ?? null,
        currency: meta.currency || "USD",
        closes, highs, lows,
      };
    } catch (e) { results[sym] = { error: e.message }; }
  }));

  return new Response(JSON.stringify({ ok: true, ts: Date.now(), data: results }), { headers: CORS });
}

async function handleCalendar(request) {
  if (request.method === "OPTIONS") return new Response(null, { headers: CORS });
  const url = new URL(request.url);
  const range = url.searchParams.get("range") === "nextweek" ? "nextweek" : "thisweek";
  const feed = `https://nfs.faireconomy.media/ff_calendar_${range}.json`;
  try {
    const r = await fetch(feed, {
      headers: { "User-Agent": "Mozilla/5.0 (compatible; FloretCapitals/1.0)" },
      signal: AbortSignal.timeout(12000),
    });
    if (!r.ok) return new Response(JSON.stringify({ ok: false, error: `HTTP ${r.status}`, events: [] }), { headers: CORS });
    const all = await r.json();
    const events = (Array.isArray(all) ? all : [])
      .filter(e => (e.impact || "").toLowerCase() === "high")
      .map(e => ({
        title: e.title || "", country: e.country || "", date: e.date || "",
        forecast: e.forecast || "", previous: e.previous || "",
      }));
    return new Response(JSON.stringify({ ok: true, range, ts: Date.now(), events }), { headers: CORS });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: e.message, events: [] }), { headers: CORS });
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/prices") return handlePrices(request);
    if (url.pathname === "/api/calendar") return handleCalendar(request);
    // everything else → static assets (index.html etc.)
    return env.ASSETS.fetch(request);
  },
};
