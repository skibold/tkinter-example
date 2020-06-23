drop database if exists library;
create database library;

use library;

SET SQL_MODE='ALLOW_INVALID_DATES';

drop table if exists book;
create table book (
	isbn char(10) not null,
	title varchar(100) not null,
	constraint pk_book primary key (isbn)
);

drop table if exists authors;
create table authors (
	author_id int not null auto_increment,
	name varchar(25) not null,
	constraint pk_author primary key (author_id),
	constraint uk_author unique (name)
)
auto_increment = 1;

drop table if exists book_authors;
create table book_authors (
	author_id int not null,
	isbn char(10) not null,
	constraint pk_book_authors primary key (author_id, isbn),
	constraint fk_book_authors_book foreign key (isbn) references book(isbn),
	constraint fk_book_authors_author foreign key (author_id) references authors(author_id)
);

drop table if exists borrower;
create table borrower (
	card_id int not null auto_increment,
	ssn char(9) not null,
	bname varchar(25) not null,
	address varchar(50) not null,
	phone varchar(14),
	constraint pk_borrower primary key (card_id),
	constraint uk_borrower unique (ssn)
);

drop table if exists book_loans;
create table book_loans (
	loan_id int not null auto_increment,
	isbn char(10) not null,
	card_id int not null,
	date_out timestamp not null,
	due_date timestamp not null,
	date_in timestamp null,
	constraint pk_book_loans primary key (loan_id),
	constraint fk_book_loans_book foreign key (isbn) references book(isbn),
	constraint fk_book_loans_borrower foreign key (card_id) references borrower(card_id)
)
auto_increment = 1;

drop table if exists fines;
create table fines (
	loan_id int not null,
	fine_amt float,
	paid char(1) not null default 'N',
	constraint pk_fines primary key (loan_id),
	constraint fk_fines_loans foreign key (loan_id) references book_loans(loan_id)
);

drop view if exists full_catalog;
create view full_catalog as (
	select b.isbn as isbn, b.title as title, a.name as author, not exists (select * from book_loans where isbn=b.isbn and date_in is NULL) as available
	from book b, authors a, book_authors ba 
	where a.author_id = ba.author_id and ba.isbn = b.isbn
);

-- inserts
source book_inserts.sql;
source auth_inserts.sql;
source book_auth_inserts.sql;
source borrower_inserts.sql;
-- after all inserts
alter table borrower auto_increment = 1001;
select now();

