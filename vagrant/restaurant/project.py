from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Making an API Endpoint (GET Request)
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id,menu_id):
    itemedited = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItems=[itemedited.serialize])

@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id).all()
    return render_template('menu.html',restaurant=restaurant, items=items)
# Task 1: Create route for newMenuItem function here


@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):

    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'], description=request.form[
                           'description'], price=request.form['price'], course=request.form['course'], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash("New item Created!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

# Task 2: Create route for editMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    if request.method == 'POST':
        newname = request.form['name']
        itemedited = session.query(MenuItem).filter_by(id=menu_id).one()
        itemedited.name=newname 
       
        session.add(itemedited)
        session.commit()
        flash("Item Edited!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        itemedited = session.query(MenuItem).filter_by(id=menu_id).one()
        return render_template('editmenuitem.html', restaurant_id=restaurant_id,menu_id=menu_id,itemedited=itemedited)

    

# Task 3: Create a route for deleteMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if request.method == 'POST':
        
        itemtodelete = session.query(MenuItem).filter_by(id=menu_id).one()
        session.delete(itemtodelete)
        session.commit()
        flash("Item Deleted!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        itemtodelete = session.query(MenuItem).filter_by(id=menu_id).one()
        return render_template('deletemenuitem.html', restaurant_id=restaurant_id,menu_id=menu_id,itemtodelete = itemtodelete)






if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)