
create table article (
    id int not null,
    name varchar(255) not null,
    content text,
    controversy bigint,
    wordbag text,
    num_refs int,
    primary key (id)
);

create table revision (
    id int not null,
    article_id int not null,
    createdat datetime not null,
    user varchar(127),
    anon boolean not null,
    hash varchar(40) not null,
    primary key (id),
    foreign key (article_id) references article(id)
);
