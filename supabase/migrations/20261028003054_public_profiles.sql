begin;
create schema if not exists private;
revoke all on schema private from public, anon, authenticated;
alter default privileges in schema private revoke all on tables from public, anon, authenticated;

-- Validators are invoker functions, contain no data access, and fix search_path.
create function public.public_text_valid(value text, max_length integer default null)
returns boolean language sql immutable set search_path = '' as $$
  select value is not null and value = btrim(value) and length(value) > 0
    and (max_length is null or length(value) <= max_length)
    and value !~ '\[[^]]+\]'
    and lower(value) not in ('pendiente','por definir','tbd','todo','información pendiente');
$$;
create function public.public_contacts_valid(items jsonb)
returns boolean language plpgsql immutable set search_path = '' as $$
declare item jsonb; raw text; kind text;
begin
  if jsonb_typeof(items) <> 'array' or jsonb_array_length(items) > 10 then return false; end if;
  for item in select * from jsonb_array_elements(items) loop
    if jsonb_typeof(item) <> 'object' then return false; end if;
    if (select count(*) from jsonb_object_keys(item)) <> 3
      or not (item ?& array['kind','label','value']) then return false; end if;
    if jsonb_typeof(item->'kind') <> 'string' or jsonb_typeof(item->'label') <> 'string'
      or jsonb_typeof(item->'value') <> 'string' then return false; end if;
    raw := item->>'value'; kind := item->>'kind';
    if not public.public_text_valid(item->>'label',200) or not public.public_text_valid(raw,2048)
      or raw ~ '[<>[:cntrl:]]' then return false; end if;
    if kind = 'email' then
      if raw !~ '^[A-Za-z0-9.!#$%&''*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$' then return false; end if;
    elsif kind = 'phone' then
      if raw !~ '^\+?[0-9 ()-]{7,30}$' then return false; end if;
    elsif kind = 'https' then
      if raw !~ '^https://[A-Za-z0-9.-]+(:[0-9]+)?([/?#][^[:space:]<>]*)?$' or position(chr(92) in raw)>0 then return false; end if;
    else return false;
    end if;
  end loop;
  return true;
end;
$$;
revoke all on function public.public_text_valid(text,integer) from public;
revoke all on function public.public_contacts_valid(jsonb) from public;

create table public.public_profiles (
  id uuid primary key default gen_random_uuid(),
  singleton boolean not null default true unique check (singleton),
  full_name text not null,
  degree text not null,
  summary text,
  public_contacts jsonb not null default '[]'::jsonb,
  published_at timestamptz,
  check (public.public_text_valid(full_name,200)),
  check (public.public_text_valid(degree,200)),
  check (summary is null or public.public_text_valid(summary,2000)),
  check (public.public_contacts_valid(public_contacts))
);
alter table public.public_profiles enable row level security;
revoke all on public.public_profiles from public, anon, authenticated;
grant select on public.public_profiles to anon, authenticated;
create policy published_profile on public.public_profiles for select to anon, authenticated
using (published_at is not null);
commit;
