create table if not exists public.mistral_corridor_certification (
  corridor_id text primary key,
  version text not null,
  storage_path text not null,
  status text not null check (status in ('certified','partial','failed')),
  start_point jsonb not null,
  end_point jsonb not null,
  distance_m double precision,
  direct_distance_m double precision,
  tile_count integer not null default 0,
  road_features integer not null default 0,
  graph_nodes integer not null default 0,
  graph_edges integer not null default 0,
  path_points integer not null default 0,
  start_snap_m double precision,
  end_snap_m double precision,
  macro_sequence text[] not null default '{}',
  sha256 text,
  bytes integer not null default 0,
  built_at timestamptz not null default now(),
  details jsonb not null default '{}'::jsonb
);
alter table public.mistral_corridor_certification enable row level security;
revoke all on table public.mistral_corridor_certification from anon, authenticated;
insert into storage.buckets (id,name,public,file_size_limit,allowed_mime_types)
values ('fallout-mistral-corridors-v040','fallout-mistral-corridors-v040',false,5000000,array['application/json'])
on conflict (id) do update set public=false,file_size_limit=excluded.file_size_limit,allowed_mime_types=excluded.allowed_mime_types;
create index if not exists mistral_corridor_certification_status_idx on public.mistral_corridor_certification(status,built_at desc);
