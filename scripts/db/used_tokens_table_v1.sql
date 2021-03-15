-- auto-generated definition
create table used_tokens
(
    token            varchar(100)                       not null,
    create_dt        datetime default CURRENT_TIMESTAMP null,
    constraint token_UNIQUE
        unique (token)
);

alter table used_tokens
    add primary key (token);
