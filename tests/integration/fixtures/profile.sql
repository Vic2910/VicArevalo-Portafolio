-- Test-only fixture: run inside a transaction on an EMPTY isolated database.
create table if not exists private.profile_test_drafts (id uuid primary key, summary text, contact text);
revoke all on private.profile_test_drafts from public, anon, authenticated;
insert into private.profile_test_drafts values ('11111111-1111-4111-8111-111111111111','PRIVATE_DRAFT_SENTINEL','PRIVATE_CONTACT_SENTINEL');
insert into public.public_profiles(id,full_name,degree,summary,published_at)
values ('11111111-1111-4111-8111-111111111111','Persona sintética','Carrera sintética','Instantánea aprobada',now());
