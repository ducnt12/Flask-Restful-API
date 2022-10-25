from os import abort
from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# -----------APP INIT--------------------------------------------
app = Flask(__name__)
auth = HTTPBasicAuth()

# -----------App configuration -----------------------------------
app.config['SECRET_KEY'] = "thisissecret"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///user.db'
db = SQLAlchemy(app)

# -----------Database initilization ------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

# -----------Method declaration------------------------------------
# Get all user
@app.route("/api/users", methods=["GET"])
def get_all_users():
    users = User.query.all()

    output = [{
        "public_id": user.public_id,
        "username": user.username,
        "password": user.password,
        "admin": user.admin
        } for user in users]
    return jsonify({"users": output}) 

# Get user by public id
@app.route("/api/users/<public_id>", methods=["GET"])
def get_one_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "No user found!"})
    user_data = {
        "public_id": user.public_id,
        "username": user.username,
        "password": user.password,
        "admin": user.admin
    }

    return jsonify({"user": user_data})

@app.route("/api/users/register", methods=["POST"])
def create_user():
    data = request.get_json()

    if(User.query.filter_by(username=data["username"]).first() is not None):
        return jsonify({"message": "Username has been taken!"})

    hashed_password = generate_password_hash(data["password"], method="sha256")

    new_user = User(public_id=str(uuid.uuid4()), username=data["username"], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "New user created!"})

@app.route("/api/users/<public_id>", methods=["PUT"])
def promote_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "No user found!"})

    user.admin = True
    db.session.commit()

    return jsonify({"message": "The user has been promoted!"})

@app.route("/api/users/<public_id>", methods=["DELETE"])
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "No user found!"})
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "The user has been deleted!"})

if __name__ == "__main__":
    app.run(debug=True)