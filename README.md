Catalog System 1.0
===================

Description
---------------------

The Catalog System is a system for organizing items into categories built
in python using Flask and sqlalchemy.

Installation
----------------

In order to run the application you must have a valid database file.  One can
be created by running "python database.py"  If you want to populate the database
with some example items you can run "python testdata.py"

Features
------------------

### Google Login

The catalog system uses google API's Oauth2 system for authorizing users to use
CRUD functions.  By default any item or category can be changed by any authorized
user, but one can change this to user level authorization by changing the global
variable protect_items_by_user from False to True.  If this item is selected, only
the owner of a category or item has access to CRUD functionality.

>>Must have valid google API client id and client secrets. Must also have valid
>>client_secrets.json file.  

### Main Page

The root directory gives a list of categories on the left and the five most
recently created items on the right.  This number can be changed from the global
variable view_limit in the function showCatalog().

### Create Category

Login required.
New categories can be created from the main page at the bottom of listed existing
categories. This will only appear if you are an authenticated user.

### Edit Category

Login required.
Edit a Category's name and description by clicking on the edit button to the
right of the category name on the main page.

### Delete Category

Login required.
You can delete any category by clicking the delete button next to the category
name on the main page.  If you delete a category all associated items will be
deleted as well.  There is a confirmation button that must be clicked for the
operation to performed.

### Show Category

By clicking on the name of any category name on can view a list of all items
that belong to that category.

### Show Item Details

Any item's details can be viewed by clicking on an item's name. From there edit
and delete functionality is also accessible for authorized users.

### Create Items

Login required.
You can create a new item from any category page by clicking the button on the
top left.  Items should have a name and description.

### Edit Items

Login required.
Edit an item by clicking the edit button from either the main catalog page,
the category page, or the item details page to the right of the item you wish
to modify.

### Delete Items

Login required.
From the main page, the items catalog page, or the item details page clicking
delete to the right of the desired item name will give you access to delete
functionality.  In order to delete an item the confirmation button must be clicked.

JSON API Endpoints
----------------------

Item Catalog has three JSON API endpoints.

### showCatalogJSON ('/catalog/JSON/')

Returns JSON data for all categories and items.

### showCatalogJSON ('/catalog/<int:cat_id>/JSON/')

Returns JSON data on a given category.  

### showItemJSON ('/catalog/<int:cat_id>/<int:item_id>/JSON/')

Returns JSON data on a single item.
