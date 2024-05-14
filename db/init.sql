create table if not exists phone_number_table (
  id serial primary key,
  phone_number varchar (30) not null
);

create table if not exists emails_table (
  id serial primary key,
  email varchar (40) not null
);
