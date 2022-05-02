from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sys

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///hungry.db'
app.config['SECRET_KEY'] = 'lw2022sql'
db = SQLAlchemy(app)

food_meal = db.Table('food_meal',
    db.Column('meal_id', db.Integer, db.ForeignKey('meal.id')),
    db.Column('food_id', db.Integer, db.ForeignKey('food.id'))
)

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.relationship('Food', secondary=food_meal, backref="meals")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    allergens = db.Column(db.String)
    calories = db.Column(db.INT)

@app.route("/")
def index():
    return redirect("/foods")

@app.route("/createFood", methods=["POST", "GET"])
def createFood():
    if request.method == "POST":
        name = request.form["name"]
        allergens = "Something"

        allergens_list = request.form.getlist('check-allergen')
        allergens = ' '.join([str(item) for item in allergens_list])
        print(allergens, file=sys.stderr)
        calories = request.form["calories"]
        new_food = Food(name=name, allergens=allergens, calories=calories)

        try:
            db.session.add(new_food)
            db.session.commit()
            return redirect("/foods")
        except:
            return "Error Adding Food"
    else:
        return render_template("create_food.html")

@app.route("/editFood/<int:id>", methods=["POST", "GET"])
def editFood(id):
    food = Food.query.get(id)
    if request.method == "POST":
        food.name = request.form["name"]

        allergens_list = request.form.getlist('check-allergen')
        food.allergens = ' '.join([str(item) for item in allergens_list])

        food.calories = request.form["calories"]

        try:
            db.session.commit()
            return redirect("/foods")
        except:
            return "Error Updating Food"
    else:
        print(food.allergens, sys.stderr)
        return render_template("edit_food.html", food=food,
            lactose = "lactose" in food.allergens,
            gluten = "gluten" in food.allergens,
            nuts = "nuts" in food.allergens,
        )

@app.route("/deleteFood/<int:id>", methods=["POST", "GET"])
def deleteFood(id):
    food = Food.query.get(id)
    db.session.delete(food)
    db.session.commit()
    return redirect("/foods")

@app.route("/createMeal", methods=["POST", "GET"])
def createMeal():
    if request.method == "POST":
        meal_name = request.form["name"]
        selected_foods = request.form.getlist('selected-food')
        print(selected_foods, sys.stderr)
        new_meal = Meal(name=meal_name)

        for id in selected_foods:
            new_meal.ingredients.append(Food.query.get(id))
        
        db.session.commit()
        return redirect("/meals")
    else:
        food_items = Food.query.all()
        return render_template('create_meal.html', food_items=food_items)

@app.route("/foods", methods=["GET"])
def foods():
    food_items = Food.query.all()
    print(food_items, sys.stderr)
    return render_template('view_foods.html', food_items=food_items)

@app.route("/meals", methods=["GET"])
def meals():
    meal_items = Meal.query.all()
    print(meal_items, sys.stderr)
    return render_template('view_meals.html', meal_items=meal_items)


if __name__ == "__main__":
    app.run(debug=True, port=5001)



