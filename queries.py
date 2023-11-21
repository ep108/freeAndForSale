import cs304dbi as dbi
import os
import subprocess

import cs304dbi as dbi

def search(conn, name):
    '''
    Returns the pid of all the posts that contain an item whose name matches the search word.
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select post_id, item_name from item 
    where item_name LIKE %s
    ''', ['%'+name+'%'])
    return curs.fetchall() 

def filter_by_category(conn, category):
    '''
    Return the pid of all the posts that contain items whose category matches the given category.
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select post_id, item_name from item 
    where category = %s
    ''', [category])
    return curs.fetchall() 

def filter_by_category_and_item(conn, name, category):
    '''
    Return the pid of all the posts that contain the item name and the items whose category matches the given category.
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select post_id, item_name from item 
    where category = %s and item_name LIKE %s
    ''', [category, name])
    return curs.fetchall() 


def filter_by_location(conn, location, onCampus: bool):
    '''
    Return the pid of all the posts where zipcode == location (if onCampus is False) or residential hall == location (if onCampus is True)
    '''
    curs = dbi.dict_cursor(conn)

    if onCampus is True: 
        curs.execute('''
        select item.post_id, item.item_name from area 
        inner join item
        where residence = %s
        ''', [location])
        return curs.fetchall() 
    else: 
        curs.execute('''
        select item.post_id, item.item_name from area 
        inner join item
        where offcampus_zipcode = %s
        ''', [location])

def filter_by_location_and_item(conn, name, location, onCampus: bool):
    '''
    Return the pid of all the posts with item name, where zipcode == location (if onCampus is False) or residential hall == location (if onCampus is True)
    '''
    curs = dbi.dict_cursor(conn)

    if onCampus is True: 
        curs.execute('''
        select item.post_id, item.item_name from area inner join item
        where residence = %s and item_name LIKE %s
        ''', [location, name])
        return curs.fetchall() 
    else: 
        curs.execute('''
        select item.post_id, item.item_name from area inner join item
        where offcampus_zipcode = %s and item_name LIKE %s
        ''', [location, name])
        return curs.fetchall() 

def filter_by_all(conn, name, category, location, onCampus: bool):
    curs = dbi.dict_cursor(conn)

    if onCampus is True: 
        curs.execute('''
        select item.post_id, item.item_name from area inner join item
        where residence = %s and item_name LIKE %s and category = %s
        ''', [location, name, category])
        return curs.fetchall() 
    else: 
        curs.execute('''
        select item.post_id, item.item_name from area inner join item
        where offcampus_zipcode = %s and item_name LIKE %s and category = %s
        ''', [location, name])
        return curs.fetchall()

def user_info(conn, user_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select * from user
    where user_id = %s
    ''',[user_id])
    return curs.fetchone()

def update_profile(conn, user_id, user_email, name, residence, offcampus_address):
    '''
    updates information in the profile table given a particular user_id
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    update user set email = %s, name = %s, residence = %s, offcampus_zipcode = %s
    where user_id = %s''',
    [user_email, name, residence, offcampus_address, user_id])
    conn.commit()

def delete_profile(conn, user_id):
    '''
    deletes specific user from database given their user_id
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    delete from user
    where user_id = %s''',
    [user_id])
    conn.commit()

def check_id(conn, user_id):
    '''
    before the user updates their user_id, this checks to see 
    if the user_id already exists
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute(''' select user_id from user_id where user_id = %s''', [user_id])
    return curs.fetchone()

def upload_post(conn,user_id,post_kind, post_description, post_datetime):
    '''
    Creates a new post with a new automatically created post ID, 
    kind (giveaway or sale), description (500 characters max), and 
    time that the post was created.

    Returns the post ID.
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
                 INSERT INTO post(user_id, post_kind, post_description, post_datetime) 
                 VALUES (%s,%s,%s,%s)
                 ''',
                 [user_id,post_kind, post_description, post_datetime])
    conn.commit()
    
    # Get and return the post ID
    curs.execute('SELECT last_insert_id()')
    row = curs.fetchone()
    return row['last_insert_id()']
    
def upload_item(conn, post_id, item_name, item_description, price, category):
    '''
    Uploads an item to the item table that has an automatic item ID, the item's 
    associated post ID, the item name (100 characters max), the description 
    (500 characters max), the price (decimal), and the category ('Home','Beauty',
    'Electronics','Collectibles','Sports','Arts','Books','Other').

    Automatically sets item status to 'available.
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
                INSERT INTO item(post_id, item_name, item_description, price, status, category) 
                VALUES (%s,%s,%s,%s,'available',%s)
                ''',
                [post_id, item_name, item_description, price, category])
    conn.commit()

    # Get and return the item ID
    curs.execute('SELECT last_insert_id()')
    row = curs.fetchone()
    return row['last_insert_id()']

def return_item_if_exists(conn, post_id, item_id):
    '''
    Checks if item with given id exists in database.

    Returns item row with given id (dictionary).
    (empty if isn't in db).
    '''
    curs = dbi.dict_cursor(conn)
    # check if post_id is already in db
    curs.execute('''
    select * from item
    where post_id = %s and item_id = %s
    ''', [post_id, item_id])
    item = curs.fetchone()
    print("check exists item: ", item)
    return item


def update_item(conn, post_id, item_id, name, description, 
    price, status, category):
    '''
    Updates item with new info
    (if new info is submitted via form).
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    update item
    set item_name = %s,
    item_description = %s,
    price = %s,
    status = %s,
    category = %s
    where post_id = %s and item_id = %s
    ''', [name, description, price, status, category,
        post_id, item_id])
    print("updated item")
    conn.commit()

def delete_item(conn, post_id, item_id):
    '''
    Deletes specified item under a specified post.
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    delete from item
    where post_id = %s and item_id = %s
    ''', [post_id, item_id])
    print("deleted item")
    conn.commit()

def return_post_if_exists(conn, post_id):
    '''
    Checks if post with given id exists in database.

    Returns post row with given id (dictionary).
    (empty if isn't in db).
    '''
    curs = dbi.dict_cursor(conn)
    # check if post_id is already in db
    curs.execute('''
    select * from post
    where post_id = %s
    ''', [post_id])
    post = curs.fetchone()
    print("check exists post: ", post)
    return post


def get_post_items(conn, post_id):
    '''
    Get the items of a post given that this post exists.

    Returns a list of dicts of items.
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select * from item
    where post_id = %s
    ''', [post_id])
    items = curs.fetchall()
    print("items in given post ", items)
    return items
   


def update_post(conn, post_id, kind, description):
    '''
    Updates post with new kind and description
    (if new submitted via form).
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    update post
    set  post_kind = %s,
    post_description = %s
    where post_id = %s
    ''', [kind, description, post_id])
    print("updated post")
    conn.commit()

def delete_post_from_area(conn, post_id):
    '''
    Helper function of delete_post().

    Deletes post_id foreign key from area
    table - to be used before deleting a post
    to avoid foreign key contraint issues.
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    delete from area
    where post_id = %s
    ''', [post_id])
    conn.commit()


def delete_post(conn, post_id):
    '''
    Deletes post with given id IF NO ITEMS
    UNDER IT!!
    '''
    curs = dbi.dict_cursor(conn)

    # check if there are any items related to the post
    curs.execute('''
    select item_id from item 
    where post_id = %s''', 
    [post_id])
    items = curs.fetchall()

    print("items to delete: ", items) 
    # items to delete:  [{'item_id': 1}, {'item_id': 2}]

    # if there are items under the post delete all then delete post
    if len(items) > 0:
        for item in items:
            delete_item(conn, post_id, item['item_id'])
        print("Deleted all items under the post")
    
    # delete post_id in area table
    delete_post_from_area(conn, post_id)

    curs.execute('''
    delete from post
    where post_id = %s
    ''', [post_id])
    print("deleted post")
    conn.commit()

def get_poster_name(conn, user_id):
    '''
    Given the post's user id, get 
    the name of the user who posted
    the post.

    Returns one dict like this:
    {'name': 'Joyce'}
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select name from user
    where user_id = %s
    ''', [user_id])
    name = curs.fetchone()
    print("name of user: ", name)
    return name

def create_tables():
    '''
    Helper function to 
    reset database.

    Creates tables: area, post, item,
    user, interest in db
    '''
    # NOTE: info from https://docs.python.org/3/library/subprocess.html 
    create_sql_path = os.path.join(os.path.dirname(__file__), 'create.sql')
    command = f'mysql < {create_sql_path}'
    # execute command
    subprocess.run(command, shell=True)

def insert_mock_data():
    '''
    Insert mock data for the created tables
    in the db for testing purposes.
    '''
    insert_sql_path = os.path.join(os.path.dirname(__file__), 'insertdata.sql')
    command = f'mysql < {insert_sql_path}'
    # execute command
    subprocess.run(command, shell=True)


if __name__ == '__main__':
    dbi.conf('ejk100_db')
    conn = dbi.connect()

    # resets db!
    # create_tables()
    # insert_mock_data()

    # testing return_post_if_exists()
    # print("\nTesting return_post_if_exists()")
    # return_post_if_exists(conn, 1)
    # returns: 
    # check exists post:  {'post_id': 1, 'user_id': 1, 
    # 'post_kind': 'sale', 'post_description': 'selling stuff 
    # before move out!', 'post_datetime': datetime.datetime(2023, 11, 

    # testing get_post_items()
    # print("\nTesting get_post_items()")
    # get_post_items(conn, 1) # get all items with post_id of 1
    # returns:
    # items in given post  [{'item_id': 1, 'post_id': 1, 'item_name':
    # 'lamp', 'item_description': 'barely used; like new', 'price': Decimal('10.00'),
    # 'status': 'available', 'category': 'Home'}, {'item_id': 2, 'post_id': 1, 'item_name':
    # 'Chem txbk', 'item_description': 'never used', 'price': Decimal('5.50'), 'status':
    # 'available', 'category': 'Books'}]

    # testing update_post() - to test make sure to drop & reset tables
    # print("\nTesting update_post()")
    # update_post(conn, 1, "sale", "new description")
    # return_post_if_exists(conn, 1)

    # testing delete_post() - after testing, reset database!!
    # print("\nTesting delete_post()")
    # delete_post(conn, 1)

    # testing upload_post()
    # print("\nTesting upload_post()")
    # upload_post(conn,2, 'giveaway','Thanksgiving giveaway!','2023-11-18 00:15:00')
    # post_id = upload_post(conn,2, 'sale','closet cleanout','2023-11-18 01:15:00')
    # print(f'Automatically generated post ID: {post_id}')

    # testing upload_item()
    # print("\nTesting upload_item()")
    # upload_item(conn, 2, 'utensils','lightly used, one fork missing',0.00,'Home')
    # upload_item(conn, 2, 'plates','set of 8, fall decorations',0.00,'Home')
    # item_id = upload_item(conn, 2, 'linens','white and beige',0.00,'Home')
    # print(f'Automatically generated item ID: {item_id}')
    # testing return_item_if_exists()
    # print("\nTesting return_item_if_exists()")
    # return_item_if_exists(conn, 1, 2)

    # testing update_item() - after testing, reset database!!
    # print("\nTesting update_item()")
    # update_item(conn, 1, 2, "cs textbook", "updated item description", 
    # 6.50, "on-hold", "Books")
    # return_item_if_exists(conn, 1, 2)

    # testing delete_item() - after testing, reset DB!!
    # print("\nTesting delete_item()")
    # delete_item(conn, 1, 1)

    # testing get_poster_name()
    # print("\nTesting user name")
    # get_poster_name(conn, 1)

