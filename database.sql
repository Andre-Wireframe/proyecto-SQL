create database if not exists proyecto;
use proyecto;

create table if not exists admins (
	id int not null auto_increment,
    nombre varchar(150) not null unique,
    password varchar(255) not null,
    edad int not null,
    puesto varchar(150) not null,
    primary key(id),
    
    index (nombre)
);

create table if not exists usuarios (
	id int not null auto_increment,
    nombre varchar(150) not null unique,
    password varchar(255) not null,
    edad int not null,
    phone bigint,
    primary key(id),
    
    index (nombre)
);

create table if not exists servicios (
	id int not null auto_increment,
    nombre varchar(50) not null,
    costo double not null,
    periodo varchar(20) default "mensual",
    type varchar(30) not null, -- Primera, segunda o tercera necesidad
    primary key(id),
    
    index (nombre)
);

create table if not exists reportes (
	id int not null auto_increment,
    usuario int not null,
    servicio int not null,
    direccion varchar(200) not null,
    urgencia varchar(50) not null,
    descripcion varchar(250) not null,
    primary key(id),
	constraint service_fk_report foreign key(servicio) references servicios(id),
    constraint user_fk_report foreign key(usuario) references usuarios(id),
	
    index (urgencia, servicio)
);

alter table reportes
drop constraint service_fk_report,
drop constraint user_fk_report,
add constraint service_fk_report2 foreign key(servicio) references servicios(id) on delete cascade,
add constraint user_fk_report2 foreign key(usuario) references usuarios(id) on delete cascade;

select * from servicios;
select * from usuarios;
select * from reportes;