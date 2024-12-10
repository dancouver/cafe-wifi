from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

app = Flask(__name__)

# Configure the SQLAlchemy part of the app instance
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cafes.db')
print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Define the Cafe model
class Cafe(db.Model):
    __tablename__ = 'cafe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

# Ensure the database is created and initialized
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
def post_new_cafe():
    if request.method == "POST":
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})
    return render_template("add_cafe.html")

@app.route("/report-closed", methods=["GET", "POST"])
def delete_cafe():
    if request.method == "POST":
        api_key = request.form.get('api-key')
        cafe_id = request.form.get('id1')
        cafe1 = Cafe.query.get(cafe_id)
        print(api_key)
        if cafe1 is not None and api_key == 'TopSecretAPIKey':
            db.session.delete(cafe1)
            db.session.commit()
            return jsonify({"success": "Successfully deleted the cafe."})
        elif cafe1 is not None:
            return jsonify({"error": "Sorry, that's not allowed. Make sure you have the correct API key."})
        else:
            return jsonify({"error": {"Not found": "Sorry, a cafe with that ID was not found."}}), 404
    return render_template("report_closed.html")

@app.route("/all")
def get_all_cafes():
    cafes = Cafe.query.all()
    print(f"Number of cafes found: {len(cafes)}")
    if cafes:
        for cafe in cafes:
            print(cafe.to_dict())
    else:
        print("No cafes found in the database.")
    return render_template("cafes.html", cafes=cafes)

@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    all_cafes = result.scalars().all()
    if all_cafes:
        return render_template("search_results.html", cafes=all_cafes)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404

if __name__ == "__main__":
    app.run(debug=True)
