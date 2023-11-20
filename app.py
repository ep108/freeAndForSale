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

@app.route('/')
def index():
    return render_template('main.html',title='About')

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
    if request.method == 'GET':
        return render_template('insert_item.html',
                               page_title='Insert Item',
                               post_id=post_id)
    else: # request.method == 'POST'
        conn = dbi.connect()
        # get form data
        item_name = request.form.get('item_name')
        item_description = request.form.get('item_description')
        price = request.form.get('price')
        category = request.form.get('category')

        # create a post in post table and get the post-id
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
        return render_template('main.html', title='About')
    
    # else if post exists, get its items
    items = queries.get_post_items(conn, post_id)
    #TODO: get post's user_id's name to display on update.html
    #TODO: need to display list of links to items under posts in update.html

    if request.method == 'GET':
        return render_template('update.html', post = post, items = items) 
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
            return render_template('update.html', post = new_post, items = items)
        
        elif button == 'delete':
            #TODO: deleting post deletes all items under it
            queries.delete_post(conn, post_id)
            flash('Post with id (' + str(post_id) + ') was deleted successfully')
            return render_template('main.html', title='About')


@app.route('/update/<post_id>/<item_id>', methods=["GET", "POST"])
def update_item(post_id, item_id):
    '''
    Update/delete an item's descriptions, images, etc.
    '''
    pass


@app.route('/post/', methods=["GET", "POST"])
def post():
    '''
    On GET, renders a form that allows the user to add an item to a post.
    '''
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('post.html', title='Post')
    else: # request.method == 'POST'
        pass


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
