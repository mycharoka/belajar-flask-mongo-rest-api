from error_handler import app
from flask import jsonify, request

class Handler:
  @app.errorhandler(400)
  def already_exist(error=None):
    msg = {
      'status': 400,
      'message': 'Already Exist'
    }

    res = jsonify(msg)
    res.status_code = 400

    return res
  
  @app.errorhandler(400)
  def not_match(error=None):
    msg = {
      'status': 400,
      'message': 'Password Not Match!'
    }

    res = jsonify(msg)
    res.status_code(400)

    return res
  
  @app.errorhandler(404)
  def not_found(error=None):
    msg = {
      'status': 404,
      'message': 'Not Found ' + request.url
    }

    res = jsonify(msg)
    res.status_code(404)

    return res