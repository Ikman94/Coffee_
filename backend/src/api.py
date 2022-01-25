import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

def check_drinks(ds):
    if ds is None:
        return False

    return True

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = None

    try:
        drinks = Drink.query.all()
    except Exception as e:
        print(e)
        abort(404)

    if check_drinks(drinks) is False:
        abort(404)

    ds = [d.short() for d in drinks]

    return jsonify({
        'success': True,
        'drinks': ds
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        drinks = Drink.query.all()
    except Exception as e:
        print(e)
        abort(404)

    if check_drinks(drinks) is False:
        abort(404)

    ds = [d.long() for d in drinks]

    return jsonify({
        'success': True,
        'drinks': ds
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt):
    req = request.get_json()
    title = req['title']
    recipe = json.dumps(req['recipe'])

    try:
        d = Drink(title=title, recipe=recipe)
        d.insert()
    except Exception as e:
        print(e)
        abort(422)

    return jsonify({
        "success": True,
        "drinks": d.long()
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, *args, **kwargs):
    id = kwargs["id"]
    print(id)

    req = request.get_json()

    try:
        d = Drink.query.filter_by(id=id).one_or_none()
    except Exception as e:
        print(e)
        abort(404)

    if check_drinks(d) is False:
        abort(404)

    bad_request = True

    if 'title' in req:
        d.title = req['title']
        bad_request = False

    if 'recipe' in req:
        d.recipe = req['recipe']
        bad_request = False

    if bad_request is True:
        abort(400)

    try:
        d.insert()
    except Exception as e:
        print(e)
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [d.long()]
    })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, *args, **kwargs):
    id = kwargs["id"]
    print(id)

    d = Drink.query.filter_by(id=id).one_or_none()

    if check_drinks(d) is False:
        abort(404)

    try:
        d.delete()
    except Exception as e:
        print(e)
        abort(500)

    return jsonify({
        'success': True,
        'delete': id
    })

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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''
'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not Found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable Entity"
    }), 422

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_auth_error(auth):
    response = jsonify(auth.error)
    response.status_code = auth.status_code
    return response