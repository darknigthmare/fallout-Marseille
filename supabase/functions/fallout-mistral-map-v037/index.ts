import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2.116.0";

const SERVICE = "fallout-mistral-map-v037";
const VERSION = "0.37.0";
const BUCKET = "fallout-mistral-map-v037";
const MAX_BYTES = 8_000_000;
const MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000;
const BASE_RANGES: Record<string, [number, number][]> = {"5994":[[8439,8453]],"5995":[[8439,8453]],"5996":[[8439,8453]],"5997":[[8439,8453]],"5998":[[8439,8453]],"5999":[[8432,8453]],"6000":[[8431,8453]],"6001":[[8431,8453]],"6002":[[8431,8453]],"6003":[[8431,8453]],"6004":[[8431,8453]],"6005":[[8431,8453]],"6006":[[8432,8453]],"6007":[[8434,8453]],"6008":[[8434,8453]],"6009":[[8434,8453]],"6010":[[8434,8453]],"6011":[[8434,8453]],"6012":[[8444,8453]]};
const CADASTRE_RANGES: Record<string, [number, number][]> = {"23976":[[33757,33787]],"23977":[[33757,33787]],"23978":[[33757,33815]],"23979":[[33757,33815]],"23980":[[33757,33815]],"23981":[[33757,33815]],"23982":[[33757,33815]],"23983":[[33757,33815]],"23984":[[33757,33815]],"23985":[[33757,33815]],"23986":[[33757,33815]],"23987":[[33757,33815]],"23988":[[33757,33815]],"23989":[[33757,33815]],"23990":[[33757,33815]],"23991":[[33757,33815]],"23992":[[33757,33815]],"23993":[[33757,33815]],"23994":[[33757,33815]],"23995":[[33757,33815]],"23996":[[33730,33815]],"23997":[[33730,33815]],"23998":[[33730,33815]],"23999":[[33730,33815]],"24000":[[33730,33815]],"24001":[[33730,33815]],"24002":[[33724,33815]],"24003":[[33724,33815]],"24004":[[33724,33815]],"24005":[[33724,33815]],"24006":[[33724,33815]],"24007":[[33724,33815]],"24008":[[33724,33815]],"24009":[[33724,33815]],"24010":[[33724,33815]],"24011":[[33724,33815]],"24012":[[33724,33815]],"24013":[[33724,33815]],"24014":[[33724,33815]],"24015":[[33724,33815]],"24016":[[33724,33815]],"24017":[[33724,33815]],"24018":[[33724,33815]],"24019":[[33724,33815]],"24020":[[33724,33815]],"24021":[[33730,33815]],"24022":[[33730,33815]],"24023":[[33730,33815]],"24024":[[33730,33815]],"24025":[[33730,33815]],"24026":[[33730,33815]],"24027":[[33738,33815]],"24028":[[33738,33812]],"24029":[[33738,33812]],"24030":[[33738,33812]],"24031":[[33738,33812]],"24032":[[33738,33812]],"24033":[[33738,33812]],"24034":[[33738,33812]],"24035":[[33738,33812]],"24036":[[33738,33812]],"24037":[[33738,33812]],"24038":[[33738,33812]],"24039":[[33738,33812]],"24040":[[33738,33812]],"24041":[[33738,33812]],"24042":[[33738,33812]],"24043":[[33738,33812]],"24044":[[33738,33812]],"24045":[[33738,33812]],"24046":[[33776,33812]],"24047":[[33776,33812]],"24048":[[33776,33812]],"24049":[[33776,33812]],"24050":[[33776,33812]]};
const MACROS = {"geo_marseille":[43.22,5.285,43.34,5.51],"geo_huveaune":[43.245,5.43,43.335,5.64],"geo_garlaban":[43.245,5.485,43.39,5.69],"geo_calanques":[43.145,5.33,43.285,5.65],"geo_laciotat":[43.125,5.54,43.255,5.735],"geo_frioul":[43.245,5.255,43.315,5.35],"geo_etoile":[43.3,5.435,43.42,5.6],"geo_saintebaume":[43.215,5.565,43.41,5.755]} as const;
const SOURCES = {
  base: { dataset: "france-vector", zoom: 14, count: 367, url: "https://openmaptiles.data.gouv.fr/data/france-vector/{z}/{x}/{y}.pbf", attribution: "© OpenStreetMap contributors — ODbL" },
  cadastre: { dataset: "cadastre", zoom: 16, count: 5517, url: "https://openmaptiles.data.gouv.fr/data/cadastre/{z}/{x}/{y}.pbf", attribution: "Cadastre Etalab / DGFiP — Licence Ouverte 2.0" },
} as const;

type SourceId = keyof typeof SOURCES;
const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, apikey, x-client-info, content-type",
  "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
  "Access-Control-Expose-Headers": "ETag, X-Map-Cache, X-Map-SHA256, X-Map-Bytes, X-Map-Fetched-At",
};

function json(data: unknown, status = 200, extra: HeadersInit = {}) {
  return new Response(JSON.stringify(data), { status, headers: { ...cors, "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...extra } });
}
function validCoordinate(source: SourceId, z: number, x: number, y: number) {
  const def = SOURCES[source];
  if (!Number.isInteger(z) || !Number.isInteger(x) || !Number.isInteger(y) || z !== def.zoom || x < 0 || y < 0) return false;
  const ranges = source === "base" ? BASE_RANGES : CADASTRE_RANGES;
  return (ranges[String(y)] || []).some(([a,b]) => x >= a && x <= b);
}
function storagePath(source: SourceId, z: number, x: number, y: number) { return `${source}/${z}/${x}/${y}.pbf`; }
function sourceUrl(source: SourceId, z: number, x: number, y: number) { return SOURCES[source].url.replace("{z}",String(z)).replace("{x}",String(x)).replace("{y}",String(y)); }
async function sha256(data: Uint8Array) { const hash = await crypto.subtle.digest("SHA-256", data); return Array.from(new Uint8Array(hash), b => b.toString(16).padStart(2,"0")).join(""); }
function plausibleMvt(data: Uint8Array, contentType: string | null) {
  if (!data.length || data.length > MAX_BYTES) return false;
  const head = new TextDecoder().decode(data.subarray(0, Math.min(80, data.length))).trimStart().toLowerCase();
  if (head.startsWith("<") || head.startsWith("{") || head.startsWith("[")) return false;
  if (contentType && /text\/html|application\/json|text\/plain/i.test(contentType)) return false;
  return true;
}
function getSecretKey() {
  try { const keys = JSON.parse(Deno.env.get("SUPABASE_SECRET_KEYS") || "{}"); if (keys.default) return keys.default as string; } catch {}
  return Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
}
const supabaseUrl = Deno.env.get("SUPABASE_URL") || "";
const secretKey = getSecretKey();
let publishableKey = "";
try { publishableKey = JSON.parse(Deno.env.get("SUPABASE_PUBLISHABLE_KEYS") || "{}").default || ""; } catch {}
if (!publishableKey) publishableKey = Deno.env.get("SUPABASE_ANON_KEY") || "";
const admin = createClient(supabaseUrl, secretKey, { auth: { persistSession: false, autoRefreshToken: false } });
function authorized(req: Request) { const key = req.headers.get("apikey") || ""; const auth = req.headers.get("authorization") || ""; return !!publishableKey && (key === publishableKey || auth === `Bearer ${publishableKey}`); }

async function cachedObject(path: string) {
  const { data, error } = await admin.storage.from(BUCKET).download(path);
  if (error || !data) return null;
  const bytes = new Uint8Array(await data.arrayBuffer());
  return plausibleMvt(bytes, data.type) ? bytes : null;
}
async function fetchOfficial(source: SourceId, z: number, x: number, y: number, etag?: string | null) {
  const headers = new Headers({ "Accept": "application/x-protobuf,application/vnd.mapbox-vector-tile,application/octet-stream", "User-Agent": "Fallout-Mistral-Map-Cache/0.37" });
  if (etag) headers.set("If-None-Match", etag);
  const response = await fetch(sourceUrl(source,z,x,y), { headers, signal: AbortSignal.timeout(20_000) });
  if (response.status === 304) return { notModified: true, response, bytes: null as Uint8Array | null };
  if (!response.ok) throw new Error(`official HTTP ${response.status}`);
  const bytes = new Uint8Array(await response.arrayBuffer());
  if (!plausibleMvt(bytes, response.headers.get("content-type"))) throw new Error("official response is not a plausible MVT tile");
  return { notModified: false, response, bytes };
}
function tileResponse(bytes: Uint8Array, cache: string, metadata: any, method: string) {
  const headers = {
    ...cors,
    "Content-Type": metadata?.content_type || "application/x-protobuf",
    "Content-Length": String(bytes.byteLength),
    "Cache-Control": "public, max-age=86400, stale-while-revalidate=604800",
    "ETag": metadata?.etag || `"sha256-${metadata?.sha256 || "unknown"}"`,
    "X-Map-Cache": cache,
    "X-Map-SHA256": metadata?.sha256 || "",
    "X-Map-Bytes": String(bytes.byteLength),
    "X-Map-Fetched-At": metadata?.fetched_at || "",
    "Vary": "Authorization, apikey",
  };
  return new Response(method === "HEAD" ? null : bytes, { status: 200, headers });
}
async function serveTile(req: Request, source: SourceId, z: number, x: number, y: number) {
  if (!validCoordinate(source,z,x,y)) return json({ error: "tile_outside_manifest" }, 404);
  const path = storagePath(source,z,x,y);
  const { data: row } = await admin.from("mistral_map_tile_cache").select("source,z,x,y,storage_path,bytes,sha256,etag,content_type,fetched_at,last_accessed_at,hit_count").eq("source",source).eq("z",z).eq("x",x).eq("y",y).maybeSingle();
  const age = row?.fetched_at ? Date.now() - new Date(row.fetched_at).getTime() : Infinity;
  let stored: Uint8Array | null = null;
  if (row) stored = await cachedObject(row.storage_path || path);
  if (row && stored && age < MAX_AGE_MS) {
    if (!row.last_accessed_at || Date.now() - new Date(row.last_accessed_at).getTime() > 60*60*1000) admin.from("mistral_map_tile_cache").update({ last_accessed_at: new Date().toISOString(), hit_count: Number(row.hit_count || 0) + 1 }).eq("source",source).eq("z",z).eq("x",x).eq("y",y).then(()=>{});
    return tileResponse(stored,"hit",row,req.method);
  }
  try {
    const fresh = await fetchOfficial(source,z,x,y,row?.etag);
    if (fresh.notModified && stored) {
      const updated = { ...row, fetched_at: new Date().toISOString(), last_accessed_at: new Date().toISOString(), hit_count: Number(row?.hit_count || 0) + 1 };
      await admin.from("mistral_map_tile_cache").upsert(updated,{ onConflict: "source,z,x,y" });
      return tileResponse(stored,"revalidated",updated,req.method);
    }
    const bytes = fresh.bytes!;
    const digest = await sha256(bytes);
    const contentType = fresh.response.headers.get("content-type") || "application/x-protobuf";
    const etag = fresh.response.headers.get("etag") || `"sha256-${digest}"`;
    const { error: uploadError } = await admin.storage.from(BUCKET).upload(path, bytes, { contentType, cacheControl: "2592000", upsert: true });
    if (uploadError) throw uploadError;
    const metadata = { source,z,x,y,storage_path:path,bytes:bytes.byteLength,sha256:digest,etag,content_type:contentType,fetched_at:new Date().toISOString(),last_accessed_at:new Date().toISOString(),hit_count:Number(row?.hit_count || 0)+1 };
    const { error: dbError } = await admin.from("mistral_map_tile_cache").upsert(metadata,{ onConflict: "source,z,x,y" });
    if (dbError) throw dbError;
    return tileResponse(bytes,row ? "refresh" : "miss",metadata,req.method);
  } catch (error) {
    if (stored) return tileResponse(stored,"stale",row,req.method);
    return json({ error: "tile_unavailable", detail: String(error) }, 502);
  }
}
async function stats() {
  const { data, error } = await admin.from("mistral_map_tile_cache").select("source,bytes,fetched_at,hit_count");
  if (error) throw error;
  const result: Record<string, any> = { base: { count:0,bytes:0,hits:0 }, cadastre: { count:0,bytes:0,hits:0 } };
  let newest: string | null = null;
  for (const row of data || []) { const r = result[row.source]; if (!r) continue; r.count++; r.bytes += Number(row.bytes||0); r.hits += Number(row.hit_count||0); if (!newest || row.fetched_at > newest) newest = row.fetched_at; }
  return { ...result, total: result.base.count + result.cadastre.count, totalBytes: result.base.bytes + result.cadastre.bytes, newest };
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (!secretKey || !supabaseUrl || !publishableKey) return json({ error: "server_configuration" }, 503);
  if (!authorized(req)) return json({ error: "unauthorized" }, 401);
  const url = new URL(req.url); const parts = url.pathname.split("/").filter(Boolean); const tail = parts.slice(parts.indexOf(SERVICE)+1);
  if ((req.method === "GET" || req.method === "HEAD") && tail[0] === "tile" && (tail[1] === "base" || tail[1] === "cadastre")) {
    const source = tail[1] as SourceId, z = Number(tail[2]), x = Number(tail[3]), y = Number((tail[4]||"").replace(/\.pbf$/i,""));
    return serveTile(req,source,z,x,y);
  }
  if (req.method === "GET" && tail[0] === "coverage") { try { return json({ service:SERVICE,version:VERSION,plan:{base:367,cadastre:5517,total:5884},cache:await stats() }); } catch(e) { return json({error:"coverage_unavailable",detail:String(e)},500); } }
  if (req.method === "GET" && (tail[0] === "meta" || !tail.length)) {
    let cache = null; try { cache = await stats(); } catch {}
    return json({ service:SERVICE,version:VERSION,bounds:{west:5.255,south:43.125,east:5.755,north:43.42},macros:MACROS,sources:SOURCES,total:5884,cache,officialTerrainNumeric:false });
  }
  return json({ error: "not_found" },404);
});
