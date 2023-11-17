use ejk100_db;

-- Note: 
-- mysql < sql file name --> to run sql files
-- use ejk100_db --> change db we're using
-- describe table_name; --> shows table fields
-- show tables; --> shows all tables in current db
-- select * from table_name limit 5; --> to see first 5 items in a table 

drop table if exists interest;
drop table if exists item;
drop table if exists area;
drop table if exists post;
drop table if exists user;

create table user (
    user_id int auto_increment not null primary key,
    email varchar(30),
    `name` varchar(30),
    residence enum('Freeman', 'Bates',
    'McAfee', 'Tower', 'Claflin', 'Severence',
    'Stone-Davis', 'Lake House', 'Pomeroy', 'Munger',
    'Beebe', 'Shafer', 'Cazenove', 'French House',
    'off-campus', 'Casa Cervantes'),
    offcampus_zipcode varchar(5)
)
ENGINE = InnoDB;

create table post (
    post_id int auto_increment not null primary key,
    user_id int,
    post_kind enum('giveaway', 'sale'),
    post_description varchar(500),
    post_datetime datetime,
    foreign key (user_id) references user(user_id)
        on update restrict
        on delete restrict
)
ENGINE = InnoDB;

create table area (
    residence enum('Freeman', 'Bates',
    'McAfee', 'Tower', 'Claflin', 'Severence',
    'Stone-Davis', 'Lake House', 'Pomeroy', 'Munger',
    'Beebe', 'Shafer', 'Cazenove', 'French House',
    'Casa Cervantes', 'off-campus'),
    offcampus_zipcode varchar(5),
    post_id int,
    foreign key (post_id) references post(post_id)
        on update restrict
        on delete restrict
)
ENGINE = InnoDB;

create table item (
    item_id int auto_increment not null primary key,
    post_id int,
    item_name varchar(100),
    item_description varchar(500),
    price decimal(10, 2), -- 10 total digits, 2 after the decimal point
    `status` enum('sold','on-hold','available'),
    category enum('Home', 'Beauty', 'Electronics', 'Collectibles', 'Sports', 
                    'Arts', 'Books', 'Other'),
    foreign key (post_id) references post(post_id)
        on update restrict
        on delete restrict
)
ENGINE = InnoDB;

create table interest (
    user_id int,
    item_id int,
    foreign key (user_id) references user(user_id)
        on update restrict
        on delete restrict,
    foreign key (item_id) references item(item_id)
        on update restrict
        on delete restrict
)
ENGINE = InnoDB;
