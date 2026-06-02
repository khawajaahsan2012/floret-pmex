/**
 * Floret Capitals — Live Price Fetcher (Cloudflare Pages Function)
 * Endpoint: /api/prices?symbols=GC=F,SI=F,...
 *
 * Runs server-side on Cloudflare's free edge network, so it can call
 * Yahoo Finance's free JSON endpoint without browser CORS restrictions.
 * Returns current price, previous close, and ~3 months of daily OHLC
 * so the browser can compute real technical indicators.
 */

export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);
  const symbolsParam = url.searchParams.get("symbols") || "";
  const symbols = symbolsParam.split(",").map(s => s.trim()).filter(Boolean);

  const cors = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
  };

  if (request.method === "OPTIONS") {
    return new Response(null, { headers: cors });
  }

  if (symbols.length === 0) {
    return new Response(JSON.stringify({ error: "No symbols provided" }), {
      status: 400, headers: cors,
    });
  }

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
    } catch (e) {
      results[sym] = { error: e.message };
    }
  }));

  return new Response(JSON.stringify({ ok: true, ts: Date.now(), data: results }), {
    headers: cors,
  });
}
