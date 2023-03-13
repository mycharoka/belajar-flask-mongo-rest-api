from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from dotenv import load_dotenv
from error_handler import handler
import json
import os

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

app.config['MONGO_URI'] = os.getenv("MONGO_CONNECTION")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")

jwt = JWTManager(app)

mongo = PyMongo(app)

@app.route('/add', methods=['POST'])
def add_user():
  print('request >> ', request)
  _json = request.json
  print('json req >> ', _json)
  _name = _json['name']
  _email = _json['email']
  _password = _json['password']

  user_exist = mongo.db.user.find_one({
    'name': _name,
    'email': _email
  })
  print('user exist >> ', user_exist) 

  if user_exist:
    print('duplicate')
    return handler.Handler.already_exist()
  else:
    print('create new')
    pass_condition = _name and _email and _password and request.method == 'POST'
    print('is condition pass ? ', pass_condition)

    if pass_condition:
      _hashed_password = generate_password_hash(_password)
      print('hash password >> ', _hashed_password)

      id = mongo.db.user.insert_one({'name': _name, 'email': _email, 'password': _hashed_password})
      print("id mongo >> ", id)
      message = {
        'status': 200,
        'message': 'Success Added!'
      }
      response = jsonify(message)
      response.status_code = 200

      return response

    else:
      return handler.Handler.not_found()

@app.route('/login', methods=['POST'])
def user_login():
  print('request json >> ', request.json)
  user = request.json
  print('user >> ', user['email'])
  validate_user = mongo.db.user.find_one({'email': user['email']})
  print('validate user >> ', validate_user['password'])
  if validate_user:
    # hashed_password = generate_password_hash(user['password'])
    # print('hashed password >> ', hashed_password)

    check_password = check_password_hash(validate_user['password'], user['password'])
    print('validate password >> ', check_password)

    if check_password:
      token = create_access_token(identity=user['email'])
      message = {
        'status': 200,
        'message': 'Login Success',
        'token': 'Bearer '+ token
      }

      return jsonify(message)
    
    else:
      print('kesini dong harusnya')
      print(handler.Handler)
      return handler.Handler.not_match()
    
  else:
    return handler.Handler.not_found()



@app.route('/users')
@jwt_required()
def get_users():
  accessed_user = get_jwt_identity()
  print('this one >> ', accessed_user)
  users = mongo.db.user.find()
  response = dumps(users)
  print('type response >> ', type(response))

  obj = {'data': json.loads(response)}
  print(obj)
  # RETURN RESPONSE NYA HARUS JSON
  return obj


@app.route('/users/<id>')
def user(id):
  user = mongo.db.user.find_one({'_id': ObjectId(id)})
  response = dumps(user)

  obj = {'data': json.loads(response)}

  return obj


@app.route('/users/delete/<id>', methods=['DELETE'])
def delete_user(id):
  mongo.db.user.delete_one({'_id': ObjectId(id)})

  response = jsonify("Deleted!")
  response.status_code = 200

  return response


@app.route('/users/update/<id>', methods=['PUT'])
def update_user(id):
  print('le ID >> ', id)
  _id = id
  _json = request.json
  _name = _json['name']
  _email = _json['email']
  _password = _json['password']

  condition_passes = _name and _email and _password and _id and request.method == 'PUT'
  print('update condition pass >> ', condition_passes)

  if condition_passes:
    _hashed_password = generate_password_hash(_password)

    mongo.db.user.update_one({'_id': ObjectId(id['$oid']) if '$oid' in id else ObjectId(id)}, {'$set': {'name': _name, 'email': _email, 'password': _hashed_password}})

    response = jsonify('Update Success!')
    response.status_code = 200

    return response

  else:
    return handler.Handler.not_found()

@app.route('/')
def index():
  return {
    'status': 200,
    'message': "OK"
  }


if __name__ == "__main__":
  app.run(debug=True)


