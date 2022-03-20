from flask import Flask, request, render_template
import json

app = Flask(__name__)
# name=y
customers = [{'id': 1, 'name': 'danny', 'address': 'tel-aviv'},
             {'id': 2, 'name': 'marina', 'address': 'beer sheav'},
             {'id': 3, 'name': 'david', 'address': 'herzeliya'}]


# localhost:5000/
# static page
# dynamic page
@app.route("/")
def home():
    print('hi')
    return '''
        <html>
            Ready!
        </html>
    '''


# url/<resource> <--- GET POST
@app.route('/customers', methods=['GET', 'POST'])
def get_or_post_customer():
    if request.method == 'GET':
        # pseudo - select * from Customers
        # parsing
        # turn to json
        print(request.args.to_dict())
        search_args = request.args.to_dict()
        if len(search_args) == 0:
            return json.dumps(customers)
        results = []
        for c in customers:
            if "name" in search_args.keys():
                if c["name"].find(search_args["name"]) < 0:
                    continue
            if "address" in search_args.keys() and \
                    c["address"].find(search_args["address"]) < 0:
                continue
            results.append(c)
        return json.dumps(results)

    if request.method == 'POST':
        #  {'id': 4 [not be sent with DB], 'name': 'david', 'address': 'herzeliya'}
        new_customer = request.get_json()
        customers.append(new_customer)
        return '{"status": "success"}'

@app.route('/customers/<int:id>', methods=['GET', 'PUT', 'DELETE', 'PATCH'])
def get_customer_by_id(id):
    global customers
    if request.method == 'GET':
        # pseudo - select * from Customers where Customer.id == id
        # parsing
        # turn to json
        for c in customers:
            if c["id"] == id:
                return json.dumps(c)
        return '{}'
    if request.method == 'PUT':
        #  {'id': 4 [not be sent with DB], 'name': 'david', 'address': 'herzeliya'}
        # 1. if not exist --> add
        # 2. if exist, update fields with given data
        # 3.           missing fields will have None value
        updated_new_customer = request.get_json()
        for c in customers:
            if c["id"] == id:
                c["id"] = updated_new_customer["id"] if "id" in updated_new_customer.keys() else None
                c["name"] = updated_new_customer["name"] if "name" in updated_new_customer.keys() else None
                c["address"] = updated_new_customer["address"] if "address" in updated_new_customer.keys() else None
                return json.dumps(updated_new_customer)
        customers.append(updated_new_customer)
        return json.dumps(updated_new_customer)
    if request.method == 'PATCH':
        #  {'id': 4 [not be sent with DB], 'name': 'david', 'address': 'herzeliya'}
        # 1. if not exist --> return
        # 2. if exist, update fields with given data
        # 3.           missing fields will remain the same
        updated_customer = request.get_json()
        for c in customers:
            if c["id"] == id:
                c["id"] = updated_customer["id"] if "id" in updated_customer.keys() else c["id"]
                c["name"] = updated_customer["name"] if "name" in updated_customer.keys() else c["name"]
                c["address"] = updated_customer["address"] if "address" in updated_customer.keys() else c["address"]
                return json.dumps(updated_customer)
        return '{"status": "not found"}'
    if request.method == 'DELETE':
        customers = [c for c in customers if c["id"] != id]
        return json.dumps(customers)

app.run()

# download post-man
# activate:
# GET, GET/ID, POST, PUT, PATCH, DELETE -- check if they work
# connect the project to a DB (sqlite, postgresql, w/o alchemy)