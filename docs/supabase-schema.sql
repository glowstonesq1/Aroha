-- Aroha: proposed Postgres schema for Supabase (v0.2 data model).
-- Not applied anywhere yet. Review, then run in a NEW project via Claude Code or the SQL editor.
-- Every table is private to its owner through Row Level Security.

create extension if not exists "pgcrypto";

create table public.profiles (
  id            uuid primary key references auth.users on delete cascade,
  name          text check (char_length(name) <= 60),
  goals         text[] not null default '{}',
  gender        text check (gender in ('male','female','skipped')),
  age           smallint check (age between 18 and 120),
  height        text,
  weight_kg     smallint check (weight_kg between 20 and 400),
  sought_help   text,
  medications   text,
  region        text,
  temp_unit     char(1) not null default 'F' check (temp_unit in ('C','F')),
  theme         text check (theme in ('light','dark')),
  consent_at    timestamptz,            -- DPDP: when the notice was accepted
  created_at    timestamptz not null default now()
);

create table public.daily_logs (
  user_id    uuid not null references auth.users on delete cascade,
  day        date not null,
  mood       text check (mood in ('happy','sad','neutral','gloomy','excited')),
  symptoms   text[] not null default '{}',
  notes      text check (char_length(notes) <= 2000),
  updated_at timestamptz not null default now(),
  primary key (user_id, day)
);

create table public.readings (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users on delete cascade,
  kind       text not null check (kind in ('heart_rate','temperature')),
  value      numeric not null,           -- BPM, or degrees Celsius
  source     text check (source in ('camera','manual','thermometer')),
  taken_at   timestamptz not null default now()
);

create table public.tasks (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users on delete cascade,
  day        date not null,
  title      text not null check (char_length(title) <= 80),
  done       boolean not null default false,
  carried_from date,
  steps      jsonb not null default '[]',  -- [{t, done}]
  created_at timestamptz not null default now()
);

create table public.contacts (
  id      uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users on delete cascade,
  name    text not null check (char_length(name) <= 60),
  phone   text check (phone ~ '^\+?[0-9 -]{8,16}$')
);

-- Photos, videos and voice notes go to a PRIVATE storage bucket named 'safebox';
-- this table only holds metadata and the object path.
create table public.memories (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users on delete cascade,
  kind       text not null check (kind in ('photo','video','voice','card')),
  title      text,
  body       text,                     -- text of a keepsake card
  object_path text,                    -- storage path in 'safebox'
  duration_s integer,
  favourite  boolean not null default false,
  created_at timestamptz not null default now()
);

create table public.trackers (
  user_id uuid not null references auth.users on delete cascade,
  kind    text not null check (kind in ('mood','sleep')),
  day     date not null,
  value   text not null,
  primary key (user_id, kind, day)
);

create table public.saved_items (
  user_id uuid not null references auth.users on delete cascade,
  item_id text not null,
  primary key (user_id, item_id)
);

-- Owner-only RLS on every personal table
do $$
declare t text;
begin
  foreach t in array array['daily_logs','readings','tasks','contacts','memories','trackers','saved_items'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('create policy "owner all" on public.%I for all using (auth.uid() = user_id) with check (auth.uid() = user_id)', t);
  end loop;
end $$;

alter table public.profiles enable row level security;
create policy "owner all" on public.profiles for all using (auth.uid() = id) with check (auth.uid() = id);

-- Community (posts, comments, chats) is deliberately NOT here: it needs moderation,
-- reporting, blocking and a safeguarding plan before any user-generated content goes live.
