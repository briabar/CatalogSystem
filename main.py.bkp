from flask import (flash,
                   Flask,
                   jsonify,
                   make_response,
                   redirect,
                   render_template,
                   request,
                   session as login_session,
                   url_for)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import (Base,
                      Catagories,
                      Items,
                      User)
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import datetime
import json
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog of Amazing Things"

engine = create_engine('sqlite:///catalogdb.db')
Base.metadata.bing = engine

DBsession = sessionmaker(bind=engine)
session = DBsession()
# protect_items_by_user, if true controls
# delete and edit of items based on user
protect_items_by_user = True


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as e:
        print e
        return None


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/catalog/')
def showCatalog():
    '''Renders catalogmain.html, the main page of the webapp.  Shows all
    catagories, and a selection of recently added or edited items.'''
    view_limit = 5  # controls the number of items displayed ordered by time.
    catagories = session.query(Catagories)
    items = session.query(Items).order_by(Items.time.desc()).limit(view_limit)
    if 'username' not in login_session:
            return render_template('catalogmain.html',
                                   catagories=catagories, items=items)
    if 'username' in login_session:
        return render_template('catalogmainprivate.html',
                               catagories=catagories, items=items)


@app.route('/catalog/JSON/')
def showCatalogJSON():
    '''API endpoint. Returns a jsonified list of all catagories and items.'''
    catagories = session.query(Catagories)
    items = session.query(Items)
    return jsonify(catagories=[i.serialize for i in catagories],
                   items=[i.serialize for i in items])


@app.route('/catalog/<int:cat_id>/')
def showCatagory(cat_id):
    '''Takes in string catagory_name, finds items based on cat_id, and then
    renders catagory.html, which lists all items in a given catagory.'''
    try:
        catagory = session.query(Catagories).filter_by(id=cat_id).first()
        items = session.query(Items).filter_by(cat_id=cat_id)
        if 'username' not in login_session:
                return render_template('catagory.html',
                                       catagory=catagory, items=items)
        if 'username' in login_session:
            return render_template('catagoryprivate.html',
                                   catagory=catagory, items=items)
    except Exception as e:
        print e
        flash("404: Catagory or item not found.")
        return redirect(url_for('showCatalog'))


@app.route('/catalog/<int:cat_id>/JSON/')
def showCatagoryJSON(cat_id):
    '''API endpoint. Takes in integer cat_id and uses it to find all Items
    in catagory. Returns a jsonified list of all items in catagory'''
    items = session.query(Items).filter_by(cat_id=cat_id)
    return jsonify(items_in_catagory=[i.serialize for i in items])


@app.route('/catalog/<int:cat_id>/<int:item_id>/')
def showItem(cat_id, item_id):
    '''Takes in parameters cat_id and item_id. Returns render template
    of showitemdetails.html. This page shows details about a single item.'''
    try:
        catagory = session.query(Catagories).filter_by(id=cat_id).one()
        item = session.query(Items).filter_by(id=item_id).one()
        return render_template('showitemdetails.html',
                               item=item, catagory=catagory)
    except Exception as e:
        print e
        flash("404: Catagory or item not found.")
        return redirect(url_for('showCatalog'))


@app.route('/catalog/<int:cat_id>/<int:item_id>/JSON/')
def showItemJSON(cat_id, item_id):
    '''API endpoint. Takes parameters integer cat_id and integer item_id,
    searches for the matching item in sql, and returns jsonified details'''
    item = session.query(Items).filter_by(id=item_id).one()
    return jsonify(item=item.serialize)


@app.route('/catalog/new/', methods=['POST', 'GET'])
def newCatagory():
    '''if posted to, gets form data and creates a new catagory based on it,
    flashes success message, and redirects to showCatagory of new catagory.
    If GET requested returns render template newCatagory.html '''
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        catagory = Catagories(name=request.form['name'],
                              description=request.form['description'])
        session.add(catagory)
        session.commit()
        flash("New catagory " + catagory.name + " successfully created!")
        return redirect(url_for('showCatagory', cat_id=catagory.id))
    else:
        return render_template('newCatagory.html')


@app.route('/catalog/<int:cat_id>/edit/',
           methods=['GET', 'POST'])
def editCatagory(cat_id):
    '''Takes parameter integer cat_id. Sets catagory to
    sqlalchemy object with id matching cat_id. If method is POST catagory data
    is changed based on form request data and commited to DB. Success message
    is flashed and redirect to showCatagory is then returned. If method is
    GET render template editCatagory.html is returned.'''
    if 'username' not in login_session:
        return redirect('/login')
    try:
        catagory = session.query(Catagories).filter_by(id=cat_id).one()
    except Exception as e:
        print e
        flash("404: Catagory or item not found.")
        return redirect(url_for('showCatalog'))
    if protect_items_by_user:
        if login_session['user_id'] != catagory.user_id:
            return """<script>function myFunction()
                   {alert('You are not authorized to edit catagories.');
                   }</script><body onload='myFunction()'>"""
    if request.method == 'POST':
        catagory.name = request.form['name']
        catagory.description = request.form['description']
        session.add(catagory)
        session.commit()
        flash("Catagory details successfully updated.")
        return redirect(url_for('showCatagory', cat_id=cat_id))
    else:
        return render_template('editCatagory.html', catagory=catagory)


@app.route('/catalog/<int:cat_id>/delete/', methods=['GET', 'POST'])
def deleteCatagory(cat_id):
    '''Takes in parameter integer cat_id.  Get's confirm from form
     checkbox.  If method is POST and confirm is not None than catagory
     catagory_name is deleted from database.  ALL ITEMS IN CATAGORY ARE ALSO
     DELETED. Success message is flashed, and redirect to showCatalog is
      returned.  If methos is POST and confirm is None then error message is
      flashed and redirect to showCatalog is returned.  If method is GET
       then render template deleteCatagory.html is returned.'''
    if 'username' not in login_session:
        return redirect('/login')
    confirm = request.form.get('confirm')
    try:
        catagory = session.query(
            Catagories).filter_by(id=cat_id).one()
    except Exception as e:
        print e
        flash("404: Catagory or item not found.")
        return redirect(url_for('showCatalog'))
    if protect_items_by_user:
        if login_session['user_id'] != catagory.user_id:
            return """<script>function myFunction()
                   {alert('You are not authorized to delete catagories.');
                   }</script><body onload='myFunction()'>"""
    if request.method == 'POST' and confirm is not None:
        items = session.query(Items).filter_by(cat_id=cat_id).all()
        session.delete(catagory)
        session.commit()
        for item in items:
            session.delete(item)
            session.commit()
        flash("Successfully deleted " + catagory.name)
        return redirect(url_for('showCatalog'))
    elif request.method == 'POST' and confirm is None:
        flash('Confirm not clicked. Catagory not deleted!')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteCatagory.html',
                               catagory=catagory)


@app.route('/catalog/<int:cat_id>/new/', methods=['GET', 'POST'])
def newItem(cat_id):
    '''Take in parameter cat_id. If method is POST adds new item to DB
    based on form data, flashes success message, and returns redirect for
    showCatalog.  If method is GET returns render template newItem.html.'''
    if 'username' not in login_session:
        return redirect('/login')
    try:
        catagory = session.query(
            Catagories).filter_by(id=cat_id).first()
    except Exception as e:
        print e
        flash("404: Catagory or item not found.")
        return redirect(url_for('showCatalog'))

    if request.method == 'POST':
        item = Items(name=request.form['name'],
                     description=request.form['description'],
                     cat_name=catagory.name,
                     time=datetime.datetime.now(),
                     cat_id=catagory.id)
        session.add(item)
        session.commit()
        flash("New item " + item.name + " successfully created!")
        return redirect(url_for('showCatagory', cat_id=cat_id))
    else:
        return render_template('newItem.html',
                               cat_id=cat_id, catagory=catagory)


@app.route('/catalog/<int:cat_id>/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteItem(cat_id, item_id):
    '''Takes in parameter integer cat_id and integer item_id. Sets confirm
    based on form checklist request. Sets catagory by catagory_name. If method
    is POST and confirm is not None then item is deleted from DB. Success
    message is flashed and redirect to showCatagory is returned. If method is
    POST and confirm is None error message is flashed and redirect to
    showCatagory is returned.  If method is GET render template deleteItem
    is returned.'''
    if 'username' not in login_session:
        return redirect('/login')
    confirm = request.form.get('confirm')
    try:
        catagory = session.query(Catagories).filter_by(
            id=cat_id).first()
        # This is a list of items in this catagory
        items = session.query(Items).filter_by(cat_id=catagory.id).all()
        # This is the item for deletion
        item = session.query(Items).filter_by(id=item_id).one()
    except Exception as e:
        print e
        flash("404: Catagory or item not found.")
        return redirect(url_for('showCatalog'))
    if protect_items_by_user:
        if login_session['user_id'] != item.user_id:
            return """<script>function myFunction()
                {alert('You are not authorized to delete this item.');
                }</script><body onload='myFunction()'>"""
    if request.method == 'POST' and confirm is not None:
        session.delete(item)
        session.commit()
        flash("Item " + item.name + " Successfully deleted!")
        return redirect(url_for('showCatagory', cat_id=item.cat_id))
    elif request.method == 'POST' and confirm is None:
        flash('Confirm not clicked. Item not deleted!')
        return redirect(url_for('showCatagory',
                                cat_id=catagory.id, items=items))
    else:
        return render_template('deleteItem.html', catagory=catagory, item=item)


@app.route('/catalog/<int:cat_id>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(cat_id, item_id):
    '''Takes parameter integer cat_id and integer item_id. Sets item to
    sqlalchemy object with id matching item_id. If method is POST item data
    is changed based on form request data and commited to DB. Success message
    is flashed and redirect to showCatagory is then returned. If method is
    GET render template editItem.html is returned.'''
    if 'username' not in login_session:
        return redirect('/login')
    try:
        item = session.query(Items).filter_by(id=item_id).one()
    except Exception as e:
        print e
        flash("404: Catagory or item not found.")
        return redirect(url_for('showCatalog'))
    if protect_items_by_user:
        if login_session['user_id'] != item.user_id:
            return """<script>function myFunction()
                {alert('You are not authorized to edit this item.');
                }</script><body onload='myFunction()'>"""
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.time = datetime.datetime.now()
        session.add(item)
        session.commit()
        flash("Item details successfully updated.")
        return redirect(url_for('showItem', cat_id=cat_id, item_id=item.id))
    else:
        return render_template('editItem.html', item=item)


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
# add other providers in if statement here
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        print login_session.__contains__
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port=5000)
