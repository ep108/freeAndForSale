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
        return render_template('update_post.html', post = post, items = items)
    
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
            return render_template('update_post.html', post = new_post, items = items)
       
        elif button == 'delete':
            # NOTE: deleting post deletes all items under it
            queries.delete_post(conn, post_id)
            flash('Post with id (' + str(post_id) + ') was deleted successfully')
            return render_template('main.html', title='About')



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
        return render_template('main.html', title='About')
   
    if request.method == 'GET':
        return render_template('update_item.html', item = item)

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
            return render_template('update_item.html', item = new_item)
       
        elif button == 'delete':
            queries.delete_item(conn, post_id, item_id)
            flash('Post with id (' + str(post_id) + ') was deleted successfully')
            return render_template('main.html', title='About')


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
