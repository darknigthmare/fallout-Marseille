-- v0.38 cache metadata. Client roles cannot read this table or the private bucket.
create table if not exists public.mistral_map_tile_cache (
  source text not null check (source in ('base','cadastre')),
  z smallint not null,
  x integer not null,
  y integer not null,
  storage_path text not null,
  bytes integer not null check (bytes between 0 and 8000000),
  sha256 text,
  etag text,
  content_type text,
  fetched_at timestamptz not null default now(),
  last_accessed_at timestamptz not null default now(),
  hit_count bigint not null default 0,
  is_empty boolean not null default false,
  primary key(source,z,x,y)
);
alter table public.mistral_map_tile_cache enable row level security;
revoke all on public.mistral_map_tile_cache from anon, authenticated;
create index if not exists mistral_map_tile_cache_last_access_idx on public.mistral_map_tile_cache(last_accessed_at desc);
create index if not exists mistral_map_tile_cache_source_idx on public.mistral_map_tile_cache(source,z);
create index if not exists mistral_map_tile_cache_empty_idx on public.mistral_map_tile_cache(source,z,is_empty);
create or replace view public.mistral_map_cache_stats with (security_invoker=true) as
select source,count(*)::bigint coordinates,count(*) filter(where is_empty)::bigint empty_tiles,
       count(*) filter(where not is_empty)::bigint stored_pbf,coalesce(sum(bytes),0)::bigint bytes,
       coalesce(sum(hit_count),0)::bigint hits,max(fetched_at) newest
from public.mistral_map_tile_cache group by source;
revoke all on public.mistral_map_cache_stats from anon, authenticated;
grant select on public.mistral_map_cache_stats to service_role;
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
values('fallout-mistral-map-v037','fallout-mistral-map-v037',false,8000000,array['application/x-protobuf','application/vnd.mapbox-vector-tile','application/octet-stream'])
on conflict(id) do update set public=false,file_size_limit=excluded.file_size_limit,allowed_mime_types=excluded.allowed_mime_types;
