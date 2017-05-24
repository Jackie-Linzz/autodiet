create table category(
  id      integer not null primary key,
  name    text not null,
  ord     integer not null,
  desc    text,
  picture text
);

create table diet(
  id      integer not null primary key,
  name    text not null,
  price   real not null,
  cid     integer not null references category(id),
  ord     integer not null,
  picture text,
  base    real not null,
  desc    text
);

create table faculty (
  id      text not null primary key,
  name    text not null,
  role    text not null,
  password  text not null
);

create table order_history (
  autoid  integer not null primary key autoincrement,
  one_uid     text not null,
  guid    text not null unique,
  name    text not null,
  num     real not null,
  stamp   real not null
);

create table customer_history (
  autoid  integer not null primary key autoincrement,
  session_id text  not null ,
  one_uid     text not null,
  name    text not null,
  num     real not null,
  guid   text not null ,
  stamp   real not null
);


