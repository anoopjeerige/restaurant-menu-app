"""
The restaurant application factory
"""
import os

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import db_session
from models import Restaurant, MenuItem


def create_app(test_config=None):
    """
    A application factory to create, set and return the restaurant flask app instance

    """
    # create and configure the application instance
    app = Flask(__name__, instance_relative_config=False)
    # set default configuration
    app.config.from_mapping(SECRET_KEY='dev')

    print(app.instance_path)
    # check for testing
    if test_config is None:
        # Override default configuration if config file exists
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load test configuration if it exists
        app.config.from_mapping(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    @app.route('/')
    @app.route('/restaurants/<int:restaurant_id>/')
    def restaurantMenu(restaurant_id):
        restaurant = db_session.query(
            Restaurant).filter_by(id=restaurant_id).one()
        menu_items = db_session.query(MenuItem).filter_by(
            restaurant_id=restaurant.id).all()

        return render_template('/menu.html', restaurant=restaurant, items=menu_items)

    @app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'POST'])
    def newMenuItem(restaurant_id):
        if request.method == 'POST':
            newMenu = MenuItem(name=request.form[
                               'name'], restaurant_id=restaurant_id)
            db_session.add(newMenu)
            db_session.commit()
            flash("New menu item: {} created".format(newMenu.name))
            return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
        else:
            return render_template('/newmenuitem.html', restaurant_id=restaurant_id)

    @app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET', 'POST'])
    def editMenuItem(restaurant_id, menu_id):
        editedItem = db_session.query(MenuItem).filter_by(id=menu_id).one()
        oldName = editedItem.name
        if request.method == 'POST':
            newName = request.form['name']
            editedItem.name = newName
            db_session.add(editedItem)
            db_session.commit()
            flash("Menu item changed from {0} to {1}".format(
                oldName, newName))
            return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
        else:
            return render_template('/editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, editedItem=editedItem)

    @app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET', 'POST'])
    def deleteMenuItem(restaurant_id, menu_id):
        toDelete = db_session.query(MenuItem).filter_by(id=menu_id).one()
        if request.method == 'POST':
            db_session.delete(toDelete)
            db_session.commit()
            flash("Menu item: {} deleted".format(toDelete.name))
            return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
        else:
            return render_template('/deletemenuitem.html', item=toDelete)

    # Making a API endpoint (GET request) to list of menu items of a restaurant
    @app.route('/restaurants/<int:restaurant_id>/menu/JSON')
    def restaurantMenuJSON(restaurant_id):
        restaurant = db_session.query(
            Restaurant).filter_by(id=restaurant_id).one()
        menu_items = db_session.query(MenuItem).filter_by(
            restaurant_id=restaurant_id).all()
        return jsonify(MenuItems=[item.serialize for item in menu_items])

    @app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
    def restaurantMenuItemJSON(restaurant_id, menu_id):
        menu_item = db_session.query(MenuItem).filter_by(id=menu_id).one()
        return jsonify(MenuItem=menu_item.serialize)

    return app

if __name__ == '__main__':
    app = create_app()
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
