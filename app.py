from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)


# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite


import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi


import random

import queries

from datetime import datetime


app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])


# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/reset-database', methods=['POST'])
def reset_database():
    '''
    A helper function for testing purposes
    that let's us reset the database.
    '''
    queries.create_tables()
    queries.insert_mock_data()

    flash('Database reset successfully!')
    return redirect(url_for('index'))

@app.route('/')
def index():
    '''
    Home page with links to examples
    along with link to create a post.
    '''
    return render_template('main.html',page_title='About')

@app.route('/create_post/', methods=['GET', 'POST'])
def create_post():
    '''
    On GET, renders create_post.html page which allows user to create a post. 
    On POST, creates a post (which creates a post-id) and allows users to 
    add items to the post (items associated with that given post-id).
    '''
    if request.method == 'GET':
        return render_template('create_post.html',page_title='Create Post')
    else: # request.method == 'POST'
        conn = dbi.connect()
        # get form data
        user_id = request.form.get('user_id')
        post_kind = request.form.get('post_kind')
        post_description = request.form.get('post_description')
        post_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # create a post in post table and get the post-id
        post_id = queries.upload_post(conn, user_id, post_kind, 
                                      post_description, post_datetime)
        flash(f'Post with ID {post_id} successfully created!')

        # uses the post_id from this upload as an input when adding items to the post
        return redirect(url_for('insert_item', post_id=post_id))
    
@app.route('/insert_item/<post_id>', methods=["GET", "POST"])
def insert_item(post_id):
    '''
    On GET, renders the form that allows users to enter item information.
    On POST, uses form data to add an item to the item table and re-renders the 
    empty form to allow users to add another item to the post.
    '''
    # check if post with post_id exists before inserting items in it
    conn = dbi.connect()
    post = queries.return_post_if_exists(conn, post_id)
    if not post:
        flash("Post with ID: " + str(post_id) + " doesn't exist. \
                Cannot add items to a post if that post doesn't exist.")
        return render_template('main.html', page_title='About')

    if request.method == 'GET':
        return render_template('insert_item.html',
                               page_title='Insert Item',
                               post_id=post_id)
    else: # request.method == 'POST'
        # get form data
        item_name = request.form.get('item_name')
        item_description = request.form.get('item_description')
        price = request.form.get('price')
        category = request.form.get('category')


        # create a item in item table and get the item_id
        item_id = queries.upload_item(conn, 
                                    post_id,
                                    item_name,
                                    item_description, 
                                    price,
                                    category)
        flash(f'{item_name} with item ID {item_id} added to post {post_id}!')

        # allow user to add another item to this post
        return render_template('insert_item.html',
                               page_title='Insert Item',
                               post_id=post_id)
    

@app.route('/update/<post_id>', methods=["GET", "POST"])
def update_post(post_id):
    '''
    Update/delete a post's descriptions, images, etc.
    '''
    conn = dbi.connect()
    # get info about the post if post_id exists otherwise flash msg
    post = queries.return_post_if_exists(conn, post_id)
    if not post:
        flash("No post with id: " + str(post_id))
        return render_template('main.html', page_title='About')
   
    # else if post exists, get its items
    items = queries.get_post_items(conn, post_id)
    poster = queries.get_poster_name(conn, post['user_id'])

    if request.method == 'GET':
        return render_template('update_post.html', post = post, items = items, 
                                poster = poster['name'], page_title='Update Post')
    
    else: # POST method
        # get submit button value: update or delete
        button = request.form.get('submit')
        kind = request.form.get('post-kind')
        description = request.form.get('post-description')


        if button == 'update':
            # update post with either or both new kind & description
            queries.update_post(conn, post_id, kind, description)
            new_post = queries.return_post_if_exists(conn, post_id)
            flash('Post with id (' + str(post_id) + ') was updated successfully')
            return render_template('update_post.html', post = new_post, items = items, 
                                    poster = poster['name'], page_title='Update Post')
       
        elif button == 'delete':
            # NOTE: deleting post deletes all items under it
            queries.delete_post(conn, post_id)
            flash('Post with id (' + str(post_id) + ') was deleted successfully')
            return render_template('main.html', page_title='About')



@app.route('/update/<post_id>/<item_id>', methods=["GET", "POST"])
def update_item(post_id, item_id):
    '''
    Update/delete an item's descriptions, images, etc.
    '''
    conn = dbi.connect()

    # get info about the item if item_id exists otherwise flash msg
    item = queries.return_item_if_exists(conn, post_id, item_id)
    if not item:
        flash("No item with id: " + str(item_id))
        return render_template('main.html', page_title='About')
   
    if request.method == 'GET':
        return render_template('update_item.html', item = item, page_title='Update Item')

    else: # POST method
        # get submit button value: update or delete
        button = request.form.get('submit')
        name = request.form.get('item-name')
        description = request.form.get('item-description')
        price = request.form.get('item-price')
        status = request.form.get('item-status')
        category = request.form.get('item-category')

        if button == 'update':
            # update post with either or both new kind & description
            queries.update_item(conn, post_id, item_id, name, description, price, status, category)
            new_item = queries.return_item_if_exists(conn, post_id, item_id)
            flash('Item with id (' + str(item_id) + ') was updated successfully')
            return render_template('update_item.html', item = new_item, page_title='Update Item')
       
        elif button == 'delete':
            queries.delete_item(conn, post_id, item_id)
            flash('Post with id (' + str(post_id) + ') was deleted successfully')
            return render_template('main.html', page_title='About')

@app.route('/filter/', methods=["GET", "POST"])
def search():
    '''
    On GET, renders search.html page which allows user to enter a keyword. 
    On POST, it grabs what the user enters and sends them to filter.html,
    where they can see what posts match their queried word
    '''

    # cases: 
    # case 1: user enters text, the default is all
    # case 2: user enters text and specifies a location 
    # case 3: user enters text and specifies category
    # case 4: user enters text and specifies both 
    
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('search.html')
    else:
        name = request.form.get('item')
        category = request.form.get('category')
        location = request.form.get('location')

        # we want to check if the location is a zipcode or a res hall
        # we set onCampus to a bool value based off of the aforementioned
        if type(location) is int:
            onCampus = False 
        else:
            onCampus = True
        
        # the following cases have nested if else statements in the case
        # that there is no item that satisfies all requirements in the database

        # if the user only inputs text in, default for category and location is all
        if category == 'all' and location == 'all':
            posts = queries.search(conn, name)

        # if the user specifies item and location only, but category is default
        elif location and category == 'all':
            posts = queries.filter_by_location_and_item(conn, name, location, onCampus)
        
        # if the user specifies item and category only, but location is default
        elif category and location == 'all':
            posts = queries.filter_by_category_and_item(conn, name, category)
        
        # if the user specifies all 
        else:
            posts = queries.filter_by_all(conn, name, category, location, onCampus)
        
        if posts:
            return render_template('filter.html', name = name, posts = posts)
        else:
            flash("The item with the specified details were not found")
            return render_template('search.html')
        
@app.route('/profile/<user_id>', methods=["GET", "POST"])
def profile(user_id):
    '''
    :int user_id: unique identification of the user 
    this function updates the profile info or gets the info
    '''

    # things to consider in the next phase:
    # making it clear that users can only include either their 
    # res hall or their off-campus zip code 

    # the only reason why there's only update and delete and not add is because
    # we will be implementing sessions and a log-in page in the next phase 
    conn = dbi.connect()
    button = request.form.get('submit')
    if request.method == 'GET':
        person = queries.user_info(conn, user_id)
        return render_template('profile.html', person = person)
    else: 
       # the user can either update or delete their profile
        if button == 'update':
            name = request.form.get("name")
            id = request.form.get("user_id")
            email = request.form.get("email")
            residence = request.form.get("residence")
            offcampus_address = request.form.get("offcampus_zipcode")
            if user_id == id: 
                flash ("You updated your profile")
                # update the profile 
                queries.update_profile(conn, user_id, email, name, residence, offcampus_address)        
            else:
                # this will check if the updated_id already exists
                updated_id = queries.check_id(conn, user_id)
                if updated_id == None: 
                    flash ("You updated your profile")
                    # update the profile 
                    queries.update_profile(conn, id, email, name, residence, offcampus_address)        
                else:
                    flash (f"The user_id {id} already exists")
                    person = queries.user_info(conn, user_id)
                    return render_template('profile.html', person = person)

            # we want to grab their updated profile and display it
            person = queries.user_info(conn, id)
            return render_template('profile.html', person = person)

        elif button == 'delete':
            queries.delete_profile(conn, user_id)
            flash("You have deleted your profile")
            return render_template('main.html', page_title='About')

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = 'ejk100_db'
    print('will connect to {}'.format(db_to_use))
    dbi.conf(db_to_use)
    app.debug = True
    app.run('0.0.0.0',port)
