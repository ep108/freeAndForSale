import cs304dbi as dbi


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

    Returns new post dict.
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

def delete_post(conn, post_id):
    '''
    Deletes post with given id IF NO ITEMS 
    UNDER IT!!
    '''
    curs = dbi.dict_cursor(conn)

    # check if there are any items related to the post
    curs.execute('select item_id from item where post_id = %s', [post_id])
    items = curs.fetchall()

    if len(items) == 0:
        # no items found, safe to delete the post
        curs.execute('''
        delete from post 
        where post_id = %s
        ''', [post_id])
        print("deleted post")
        conn.commit()
    else:
        # TODO: maybe delete all items then the post (user deleting post automatically 
        # deletes items under it?)
        print("Cannot delete post. Items are associated with it.")



if __name__ == '__main__':
    dbi.conf('ejk100_db')
    conn = dbi.connect()

    # testing return_post_if_exists()
    # print("\nTesting return_post_if_exists()")
    # return_post_if_exists(conn, 1)
    # returns: 
    # check exists post:  {'post_id': 1, 'user_id': 1, 
    # 'post_kind': 'sale', 'post_description': 'selling stuff 
    # before move out!', 'post_datetime': datetime.datetime(2023, 11, 
    # 20, 14, 45)}

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