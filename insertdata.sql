use ejk100_db;


-- insert sample users (user_id is autoincremented)
-- user_id: 1
insert into user(email, `name`, residence, offcampus_zipcode, hashed) 
values ("dc103@wellesley.edu", "Joyce", "Freeman", NULL, NULL);

-- user_id: 2
insert into user(email, `name`, residence, offcampus_zipcode, hashed) 
values ("edith@wellesley.edu", "Edith", "Tower", NULL, NULL);

-- user_id: 3
insert into user(email, `name`, residence, offcampus_zipcode, hashed) 
values ("kim@wellesley.edu", "Kim", "off-campus", "02142", NULL);


-- insert sample posts (post_id is autoincremented)
-- post_id: 1
insert into post(user_id, post_kind, post_description, post_datetime) 
values (1, "sale", "selling stuff before move out!", '2023-11-20 14:45:00');


-- insert sample areas
insert into area(residence, offcampus_zipcode, post_id) 
values ("Freeman", NULL, 1);


-- insert sample items (item_id is autoincremented)
-- item_id: 1
insert into item(post_id, item_name, item_description, price, `status`, category) 
values (1, "lamp", "barely used; like new", 10.00, 'available', 'Home');

-- item_id: 2
insert into item(post_id, item_name, item_description, price, `status`, category) 
values (1, "Chem txbk", "never used", 5.50, 'available', 'Books');

