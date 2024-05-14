create database bot_tg;
grant all privileges on database bot_tg to postgres;

create role repl_user with replication encrypted password '123';

SELECT pg_create_physical_replication_slot('replication_slot');
create table if not exists phone_number_table (
  id serial primary key,
  phone_number varchar (30) not null
);

create table if not exists emails_table (
  id serial primary key,
  email varchar (40) not null
);