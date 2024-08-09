import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def handle_users():
    users_query = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users_query))

    return jsonify(all_users), 200

@app.route('/users/favorites/', methods=['GET'])
@jwt_required()
def handle_user_favorites(current_user_id):
    current_user_id = get_jwt_identity()
    user_favorites_query = User.query.get(current_user_id)
    user_favorites = user_favorites_query.serialize()

    return jsonify(user_favorites), 200

@app.route('/planets', methods=['GET'])
def handle_planets():
    planets_query = Planet.query.all()
    all_planets = list(map(lambda x: x.serialize(), planets_query))

    return jsonify(all_planets), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def handle_specific_planet(planet_id):
    planet_query = Planet.query.get(planet_id)
    specific_user = planet_query.serialize()

    return jsonify(specific_user), 200

@app.route('/people', methods=['GET'])
def handle_people():
    people_query = People.query.all()
    all_people = list(map(lambda x: x.serialize(), people_query))

    return jsonify(all_people), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def handle_specific_people(people_id):
    specific_people_query = specific_people.query.get(people_id)
    specific_people = specific_people_query.serialize()

    return jsonify(specific_people), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
@jwt_required()
def handle_favorite_planet(planet_id, current_user_id):
    current_user_id = get_jwt_identity()
    favorite_planet_query = Planet.query.get(planet_id)
    user_query = User.query.get(current_user_id)
    user_query.favorite_planets.append(favorite_planet_query)
    print("planet fav añadido")

    return jsonify(user_query.serialize()), 200

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
@jwt_required()
def handle_favorite_people(people_id):
    current_user_id = get_jwt_identity()
    favorite_people_query = People.query.get(people_id)
    user_query = User.query.get(current_user_id)
    user_query.favorite_peoples.append(favorite_people_query)
    print("personaje fav añadido")

    return jsonify(user_query.serialize()), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_people(people_id, ):
    current_user_id = get_jwt_identity()
    favorite_people_query = People.query.get(people_id)
    user_query = User.query.get(current_user_id)
    user_query.favorite_peoples.remove(favorite_people_query)
    print("personaje favorito eliminado")

    return jsonify(user_query.serialize()), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_planet(planet_id, current_user_id):
    current_user_id = get_jwt_identity()
    favorite_planet_query = Planet.query.get(planet_id)
    user_query = User.query.get(current_user_id)
    user_query.favorite_planets.remove(favorite_planet_query)
    print("planeta favorito eliminado")

    return jsonify(user_query.serialize()), 200

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    print("\n\n\n")
    print(email)
    print(password)

    if email is None or password is None:
        return jsonify({"msg": "Bad username or password"}), 401

    user_query = User.query.filter_by(email=email)
    user = user_query.first()
    print(user)

    if user is None:
        return jsonify({"msg": "Bad username or password"}), 401
    if user.email != email or user.password != password:
        return jsonify({"msg": "Bad username or password"}), 401

    print("\n\n\n")
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/current-user", methods=["GET"])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    print(current_user_id)

    if current_user_id is None:
        return jsonify({"msg": "User not found"}), 401
    
    user_query = User.query.get(current_user_id)
    print(user_query)

    if user_query is None:
        return jsonify({"msg": "User not found"}), 401

    user = user_query.serialize()
    return jsonify(current_user=user), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
