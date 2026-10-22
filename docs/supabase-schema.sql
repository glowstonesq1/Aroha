-- Aroha: proposed Postgres schema for Supabase (v0.4 data model).
-- Not applied anywhere yet. Review, then run in a NEW project via Claude Code or the SQL editor.
-- Every table is private to its owner through Row Level Security.

create extension if not exists "pgcrypto";

create table public.profiles (
  id            uuid primary key references auth.users on delete cascade,
  name          text check (char_length(name) <= 60),
  goals         text[] not null default '{}',
  region        text,
  theme         text check (theme in ('light','dark')),
  consent_at    timestamptz,            -- DPDP: when the notice was accepted
  created_at    timestamptz not null default now()
);

create table public.daily_logs (
  user_id    uuid not null references auth.users on delete cascade,
  day        date not null,
  mood       text check (mood in ('happy','calm','neutral','anxious','sad')),
  sleep      text check (sleep in ('<5h','5-6h','6-7h','7-8h','8h+')),
  symptoms   text[] not null default '{}',
  notes      text check (char_length(notes) <= 2000),
  updated_at timestamptz not null default now(),
  primary key (user_id, day)
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

-- Photos and voice notes go to a PRIVATE storage bucket named 'safebox';
-- this table only holds metadata and the object path.
create table public.memories (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users on delete cascade,
  kind       text not null check (kind in ('photo','voice','card')),
  title      text,
  body       text,                     -- text of a keepsake card
  object_path text,                    -- storage path in 'safebox'
  duration_s integer,
  favourite  boolean not null default false,
  created_at timestamptz not null default now()
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
  foreach t in array array['daily_logs','tasks','contacts','memories','saved_items'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('create policy "owner all" on public.%I for all using (auth.uid() = user_id) with check (auth.uid() = user_id)', t);
  end loop;
end $$;

alter table public.profiles enable row level security;
create policy "owner all" on public.profiles for all using (auth.uid() = id) with check (auth.uid() = id);

-- No vitals (heart rate, temperature): removed in v0.4, see docs/feature-audit.md.
-- Community (posts, comments, chats) is deliberately NOT here: it needs moderation,
-- reporting, blocking and a safeguarding plan before any user-generated content goes live.
