create database bot_tg;
grant all privileges on database bot_tg to postgres;

create user db_repl_user with replication encrypted password '${DB_REPL_PASSWORD}';
grant all privileges on database bot_tg to db_repl_user;
SELECT pg_create_physical_replication_slot('replication_slot');

\c bot_tg;

create table if not exists phone_number_table (
  id serial primary key,
  phone_number varchar (30) not null
);

create table if not exists emails_table (
  id serial primary key,
  email varchar (40) not null
);

insert into phone_number_table(phone_number) values ('meow23@mail.ru'),('meow766@gmail.com');
insert into emails_table(email) values ('80000000000'),('81111111111');