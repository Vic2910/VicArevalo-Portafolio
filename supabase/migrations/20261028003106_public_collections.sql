begin;
create table public.public_skills (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references public.public_profiles(id) on delete restrict,
  name text not null check (public.public_text_valid(name)),
  description text check (description is null or public.public_text_valid(description,4000)),
  display_order integer not null default 0,
  published_at timestamptz
);
create table public.public_academic_experiences (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references public.public_profiles(id) on delete restrict,
  activity text not null check (public.public_text_valid(activity,200)),
  institution text check (institution is null or public.public_text_valid(institution,200)),
  start_date date,
  end_date date,
  ongoing boolean not null default false,
  description text check (description is null or public.public_text_valid(description,4000)),
  display_order integer not null default 0,
  published_at timestamptz,
  check (end_date is null or start_date is null or end_date >= start_date),
  check (not ongoing or end_date is null)
);
create index public_skills_profile_order on public.public_skills(profile_id,display_order,id);
create index public_academic_profile_order on public.public_academic_experiences(profile_id,display_order,id);
alter table public.public_skills enable row level security;
alter table public.public_academic_experiences enable row level security;
revoke all on public.public_skills, public.public_academic_experiences from public, anon, authenticated;
grant select on public.public_skills, public.public_academic_experiences to anon, authenticated;
create policy published_skills on public.public_skills for select to anon, authenticated using (
  published_at is not null and exists (select 1 from public.public_profiles p where p.id=profile_id and p.published_at is not null)
);
create policy published_academic on public.public_academic_experiences for select to anon, authenticated using (
  published_at is not null and exists (select 1 from public.public_profiles p where p.id=profile_id and p.published_at is not null)
);
commit;
