from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)

app.secret_key = "b4pAk4U_B0d4t"

app.config['MONGO_URI'] = "mongodb://localhost:27023/Users"

mongo = PyMongo(app)

@app.route('/add', methods=['POST'])
def add_user():
  print('request >> ', request)
  _json = request.json
  print('json req >> ', _json)
  _name = _json['name']
  _email = _json['email']
  _password = _json['password']

  pass_condition = _name and _email and _password and request.method == 'POST'
  print('is condition pass ? ', pass_condition)

  if pass_condition:
    _hashed_password = generate_password_hash(_password)
    print('hash password >> ', _hashed_password)

    id = mongo.db.user.insert_one({'name': _name, 'email': _email, 'password': _hashed_password})
    print("id mongo >> ", id)
    response = jsonify("User added!")
    response.status_code = 200

    return response

  else:
    return not_found()


@app.route('/users')
def get_users():
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
    return not_found()

@app.errorhandler(404)
def not_found(error=None):
  message = {
    'status': 404,
    'message': 'Not Found ' + request.url
  }

  response = jsonify(message)
  response.status_code = 404

  return response

if __name__ == "__main__":
  app.run(debug=True)


