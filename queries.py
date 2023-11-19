import cs304dbi as dbi


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

if __name__ == '__main__':
    dbi.conf('ejk100_db')
    conn = dbi.connect()


    # testing return_post_if_exists()
    print("\nTesting return_post_if_exists()")
    return_post_if_exists(conn, 1)
    # returns:
    # check exists post:  {'post_id': 1, 'user_id': 1,
    # 'post_kind': 'sale', 'post_description': 'selling stuff
    # before move out!', 'post_datetime': datetime.datetime(2023, 11,
    # 20, 14, 45)}


    # testing get_post_items()
    print("\nTesting get_post_items()")
    get_post_items(conn, 1) # get all items with post_id of 1
    # returns:
    # items in given post  [{'item_id': 1, 'post_id': 1, 'item_name':
    # 'lamp', 'item_description': 'barely used; like new', 'price': Decimal('10.00'),
    # 'status': 'available', 'category': 'Home'}, {'item_id': 2, 'post_id': 1, 'item_name':
    # 'Chem txbk', 'item_description': 'never used', 'price': Decimal('5.50'), 'status':
    # 'available', 'category': 'Books'}]


    # testing update_post() - after testing, reset database!!
    # print("\nTesting update_post()")
    # update_post(conn, 1, "sale", "new description")
    # return_post_if_exists(conn, 1)


    # testing delete_post() - after testing, reset database!!
    # print("\nTesting delete_post()")
    # delete_post(conn, 1)

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

