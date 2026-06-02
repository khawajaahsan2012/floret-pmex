/**
 * Floret Capitals — Economic Calendar Fetcher (Cloudflare Pages Function)
 * Endpoint: /api/calendar
 *
 * Pulls the free ForexFactory weekly calendar feed (via faireconomy.media —
 * no API key required) server-side, filters to HIGH-impact events, and returns
 * a clean list. The browser converts times to PKT and maps PMEX relevance.
 */

export async function onRequest(context) {
  const { request } = context;
  const cors = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
  };
  if (request.method === "OPTIONS") return new Response(null, { headers: cors });

  // Allow ?range=thisweek (default) or ?range=nextweek
  const url = new URL(request.url);
  const range = url.searchParams.get("range") === "nextweek" ? "nextweek" : "thisweek";
  const feed = `https://nfs.faireconomy.media/ff_calendar_${range}.json`;

  try {
    const r = await fetch(feed, {
      headers: { "User-Agent": "Mozilla/5.0 (compatible; FloretCapitals/1.0)" },
      signal: AbortSignal.timeout(12000),
    });
    if (!r.ok) {
      return new Response(JSON.stringify({ ok: false, error: `HTTP ${r.status}`, events: [] }), { headers: cors });
    }
    const all = await r.json();

    // Keep only HIGH-impact events
    const events = (Array.isArray(all) ? all : [])
      .filter(e => (e.impact || "").toLowerCase() === "high")
      .map(e => ({
        title: e.title || "",
        country: e.country || "",
        date: e.date || "",            // ISO with timezone offset
        forecast: e.forecast || "",
        previous: e.previous || "",
      }));

    return new Response(JSON.stringify({ ok: true, range, ts: Date.now(), events }), { headers: cors });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: e.message, events: [] }), { headers: cors });
  }
}
