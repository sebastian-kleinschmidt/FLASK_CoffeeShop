import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from functools import wraps
from jose import jwt
from urllib.request import urlopen

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

AUTH0_DOMAIN = 'dev-b9cnr88e.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'CoffeeShop'

'''
@COMPLETED uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES
'''
@COMPLETED implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=['GET'])
def get_all_drinks():
    try:
        drinks = Drink.query.all()
    except BaseException:
        abort(400)
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200

'''
@COMPLETED implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail", methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(jwt):
    try:
        drinks = Drink.query.all()
    except BaseException:
        abort(400)
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]})

'''
@COMPLETED implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt):
    try:
        data = request.get_json()
        drink = Drink()
        drink.title = data['title']
        drink.recipe = json.dumps(data['recipe'])
        drink.insert()
    except BaseException:
        abort(400)
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200

'''
@COMPLETED implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:drink_id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def get_specific_drink(jwt, drink_id):
    try:
        data = request.get_json()
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if not drink:
            abort(404)

        try:
            if data['title']:
                drink.title = data['title']
            if data.get('recipe'):
                drink.recipe = json.dumps(data.get('recipe'))
            drink.update()
        except BaseException:
            abort(400)
    except BaseException:
        abort(400)
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200

'''
@COMPLETED implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where 
    id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:drink_id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def get_drink(jwt, drink_id):
    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        drink.delete()
    except BaseException:
        abort(400)
    return jsonify({
        'success': True,
    }), 200

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@COMPLETED implement error handlers using the @app.errorhandler(error)
decorator each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''

'''
@COMPLETED implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
        }), 404

'''
@COMPLETED implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(401)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
        }), 401


@app.errorhandler(403)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
        }), 403
