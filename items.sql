use ejk100_db;

drop table if exists item;
create table item (
    item_id int,
    post_id int,
    item_name varchar(100),
    item_description varchar(500),
    price int,
    status enum('sold','on-hold','available'),
    category enum('Home', 'Beauty', 'Electronics'),
    primary key (post_id, item_id)
);