-- SecureShift Database Schema
-- Run this in Supabase SQL Editor

-- Users table
create table if not exists users (
  id uuid primary key,
  email text unique not null,
  name text,
  avatar_url text,
  role text not null default 'user',  -- user | admin | super_admin | enterprise_manager
  status text not null default 'active', -- active | suspended
  last_active_at timestamptz,
  created_at timestamptz default now()
);

-- Repositories table
create table if not exists repositories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  repo_name text not null,
  repo_url text not null,
  description text,
  language text,
  stars int default 0,
  created_at timestamptz default now()
);

-- Scans table
create table if not exists scans (
  id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(id) on delete cascade,
  status text not null default 'pending', -- pending | running | completed | failed
  total_vulnerabilities int default 0,
  critical_count int default 0,
  high_count int default 0,
  medium_count int default 0,
  low_count int default 0,
  pr_url text,
  scan_started_at timestamptz,
  scan_completed_at timestamptz,
  error_message text,
  created_at timestamptz default now()
);

-- Vulnerabilities table
create table if not exists vulnerabilities (
  id uuid primary key default gen_random_uuid(),
  scan_id uuid references scans(id) on delete cascade,
  file_path text not null,
  vulnerability_type text not null,
  severity text not null default 'low', -- low | medium | high | critical
  description text not null,
  line_number int,
  code_snippet text,
  tool text,
  cwe_id text,
  cvss_score float,
  is_fixed bool default false,
  detected_at timestamptz default now()
);

-- AI Fixes table
create table if not exists ai_fixes (
  id uuid primary key default gen_random_uuid(),
  vulnerability_id uuid references vulnerabilities(id) on delete cascade,
  suggested_fix text not null,
  fixed_code text,
  ai_model text default 'openrouter',
  confidence_score float default 0.5,
  is_applied bool default false,
  applied_at timestamptz,
  created_at timestamptz default now()
);

-- CVE Findings table
create table if not exists cve_findings (
  id uuid primary key default gen_random_uuid(),
  scan_id uuid references scans(id) on delete cascade,
  package_name text not null,
  package_version text not null,
  ecosystem text not null,
  source_file text not null,
  cve_id text not null,
  cvss_score float,
  severity text not null default 'unknown',
  description text,
  fix_version text,
  reference_url text,
  source text not null default 'osv',
  created_at timestamptz default now()
);

-- Scan Logs table
create table if not exists scan_logs (
  id uuid primary key default gen_random_uuid(),
  scan_id uuid references scans(id) on delete cascade,
  log_message text not null,
  log_level text not null default 'info',
  created_at timestamptz default now()
);

-- Audit Logs table
create table if not exists audit_logs (
  id uuid primary key default gen_random_uuid(),
  actor_id uuid,
  actor_email text,
  action text not null,
  target_type text,
  target_id text,
  metadata jsonb default '{}',
  ip_address text,
  created_at timestamptz default now()
);

-- Admin Notifications table
create table if not exists admin_notifications (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  message text not null,
  type text default 'info',
  is_read bool default false,
  created_at timestamptz default now()
);

-- Organizations table
create table if not exists organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  owner_id uuid references users(id) on delete set null,
  created_at timestamptz default now()
);

-- User notifications table
create table if not exists notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  title text not null,
  message text not null,
  type text default 'info',
  is_read bool default false,
  created_at timestamptz default now()
);

-- Auto-create user row when someone signs up via Supabase Auth
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.users (id, email, name, avatar_url)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'name', new.raw_user_meta_data->>'full_name', new.email),
    new.raw_user_meta_data->>'avatar_url'
  )
  on conflict (id) do nothing;
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
