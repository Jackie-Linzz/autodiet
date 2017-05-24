
create table if not exists category (
  id      int unsigned not null  primary key,
  name    char(50) not null,
  ord     int unsigned not null,
  description    varchar(1000),
  picture char(100)
);

create table if not exists diet(
  id      int unsigned not null primary key,
  name    char(50) not null,
  price   float(8,2) not null,
  cid     int unsigned not null ,
  ord     int unsigned not null,
  picture char(100),
  base    float(8,2) not null,
  description    varchar(1000)
);

create table if not exists faculty (
  id      char(100) not null primary key,
  name    char(50) not null,
  role    char(50) not null,
  password  char(50) not null
);


create table if not exists order_history (
  th      int unsigned not null  primary key auto_increment,
  one_uid    char(50) not null,
  id      int unsigned not null,
  desk_uid char(50) not null,
  num     float(8,2) not null,
  stamp   double(20,5) not null
);



create table if not exists customer_history (
  th  bigint unsigned not null primary key auto_increment,
  session char(50)  not null ,
  desk     char(50) not null,
  desk_uid  char(50) not null,
  stamp   double(20,5) not null
);


create table if not exists cook_history (
  th bigint unsigned not null primary key auto_increment,
  fid char(50) not null,
  uid char(50) not null,
  id  int unsigned not null,
  stamp double(20,5) not null
);



create table if not exists comment(
  th int unsigned not null key auto_increment,
  session char(50) not null,
  comment char(200) not null,
  stamp double(20,5) not null
);

create table if not exists diet_stat (
  th   int unsigned not null primary key auto_increment,
  id   int unsigned not null,
  name char(50) not null,
  price float(8,2) not null,
  num  float(10,2) not null,
  stamp_from char(20) not null,
  stamp_to char(20) not null
);
create table if not exists cook_stat (
 th int unsigned not null primary key auto_increment,
 fid char(50) not null,
 name char(50) not null,
 num  float(10,2) not null,
 val  float(10,2) not null,
 stamp_from char(20) not null,
 stamp_to   char(20) not null
);

create table if not exists desks (
 desk char(20) not null primary key
);
