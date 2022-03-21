from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from Customer import Customer
from User import User
from Logger import Logger
from RestData import RestData
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from functools import wraps
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'

dao = RestData('rest_api_project_db.db')
logger = Logger.get_instance()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            token = token.removeprefix('Bearer ')

        if not token:
            logger.logger.info('Missing credentials: missing Authorization header, missing token, missing Bearer '
                               'prefix.')
            return jsonify({'message': 'Token not found'}), 401

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'])
            user = dao.get_user_by_public_id(payload['public_id'])
        except:
            logger.logger.warning('Expired credentials: expired token')
            return jsonify({'message': 'Invalid Token'}), 401

        return f(user, *args, **kwargs)

    return decorated


@app.route("/")
def home():
    return '''
        <html>
            Welcome!
        </html>
    '''


@app.route('/customers', methods=['GET', 'POST'])
@token_required
def get_or_post_customer(user):
    if request.method == 'GET':
        search_args = request.args.to_dict()
        customers = dao.get_all_customers(search_args)
        return jsonify(customers)
    if request.method == 'POST':
        customer_data = request.get_json()
        inserted_customer = Customer(id_=None, name=customer_data["name"], city=customer_data["city"])
        answer = dao.insert_new_customer(inserted_customer)
        if answer:
            logger.logger.info(f'New customer: "{inserted_customer}" has been created by the user "{user}"!')
            return make_response('Customer was created successfully', 201)
        else:
            logger.logger.error(f'The user: "{user}" tried to insert new customer but did not sent both "name" and '
                                f'"city"')
            return jsonify({'answer': 'failed'})


@app.route('/customers', methods=['GET', 'POST'])
@token_required
def get_or_post_customer(user):
    if request.method == 'GET':
        search_args = request.args.to_dict()
        customers = dao.get_all_customers(search_args)
        return jsonify(customers)
    if request.method == 'POST':
        customer_data = request.get_json()
        inserted_customer = Customer(id_=None, name=customer_data["name"], city=customer_data["city"])
        answer = dao.insert_new_customer(inserted_customer)
        if answer:
            logger.logger.info(f'New customer: "{inserted_customer}" has been created by the user "{user}"!')
            return make_response('Customer was created successfully', 201)
        else:
            logger.logger.error(f'The user: "{user}" tried to insert new customer but did not sent both "name" and '
                                f'"city"')
            return jsonify({'answer': 'failed'})


@app.route('/customers/<int:id_>', methods=['GET', 'PUT', 'DELETE', 'PATCH'])
@token_required
def get_customer_by_id(user, id_):
    if request.method == 'GET':
        customer = dao.get_customer_by_id(id_)
        return jsonify(customer)
    if request.method == 'PUT':
        values_dict = request.get_json()
        answer = dao.update_put_customer(id_, values_dict)
        if answer:
            logger.logger.info(f'The customer with the id: {id_} has been updated by the user "{user}"!')
            return make_response('Put action was done!', 201)
        else:
            logger.logger.error(f'The user "{user}" tried to update a customer that his id: "{id_}" '
                                f'not exists in the db.')
            return jsonify({'answer': 'failed'})
    if request.method == 'DELETE':
        answer = dao.delete_customer(id_)
        if answer:
            logger.logger.info(f'The customer with the id: {id_} has been deleted by the user "{user}"!')
            return make_response('Delete action was done!', 201)
        else:
            logger.logger.error(f'The user "{user}" tried to delete a customer that his id: "{id_}" '
                                f'not exists in the db.')
            return jsonify({'answer': 'failed'})
    if request.method == 'PATCH':
        values_dict = request.get_json()
        answer = dao.update_patch_customer(id_, values_dict)
        if answer:
            logger.logger.info(f'The customer with the id: {id_} has been updated by the user "{user}"!')
            return make_response('Patch action was done!', 201)
        else:
            logger.logger.info(f'The user "{user}" tried to update a customer that his id: "{id_}" '
                               f'not exists in the db.')
            return jsonify({'answer': 'failed'})


@app.route('/signup', methods=['POST'])
def signup():
    form_data = request.form

    username = form_data.get('username')
    password = form_data.get('password')

    user = dao.get_user_by_username(username)

    if user:
        logger.logger.error(f'An anonymous tried to sign up with the username:{username} but this username already '
                            f'exists in the db')
        return make_response('Username already exists. Please select another username.', 202)

    else:
        inserted_user = User(id_=None, public_id=str(uuid.uuid4()), username=username,
                             password=generate_password_hash(password))
        dao.insert_new_user(inserted_user)
        logger.logger.info(f'New user: {inserted_user} has been created successfully!')
        return make_response('Successfully registered.', 201)


@app.route('/login', methods=['POST'])
def login():
    form_data = request.form

    if not form_data or not form_data.get('username') or not form_data.get('password'):
        logger.logger.info('A user tried to login without sending the required info(username, password)')
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required."'})

    user = dao.get_user_by_username(form_data.get('username'))
    if not user:
        logger.logger.warning(f'A user tried to login but the username:{form_data.get("username")} '
                              f'does not exist in the db')
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required."'})

    if not check_password_hash(user.password, form_data.get('password')):
        logger.logger.error(f'The user: {form_data.get("username")} tried to login with a wrong password.')
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required."'})

    logger.logger.debug(f'The user: {form_data.get("username")} logged in successfully!')
    token = jwt.encode({'public_id': user.public_id, 'exp': datetime.now() + timedelta(minutes=30)},
                       app.config['SECRET_KEY'])
    return make_response(jsonify({'token': token.decode('UTF-8')}), 201)


if __name__ == '__main__':
    app.run(debug=True)
