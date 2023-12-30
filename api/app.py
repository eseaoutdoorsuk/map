import os
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS

from utils import *
from update_location_database import update_location_database

app = Flask(__name__)
CORS(app)
api = Api(app)

spreadsheet = get_spreadsheet()
records = read_spreadsheet(spreadsheet, sheet="Form responses 2")
locations = read_spreadsheet(spreadsheet, sheet="locations")

class UsersResource(Resource):
    def get(self):
        password = request.args.get('password')

        if password == os.getenv("PASSWORD"):
            auth_level = AUTH_LEVEL.MEMBERS
        elif password == os.getenv("DEV_PASSWORD"):
            auth_level = AUTH_LEVEL.DEV
        elif password == "":
            auth_level = AUTH_LEVEL.PUBLIC
        else:
            auth_level = AUTH_LEVEL.DENIED
        
        try:
            users = {
                "auth_level": auth_level.name,
                "users": get_users_from_records(records, locations, auth_level=auth_level)
                }
            return jsonify(users)
        except Exception as e:
            return {"error": f"Unknown error: {str(e)}"}, 500

class LocationResource(Resource):
    def get(self):
        try:
            status = update_location_database()
            return jsonify({'message': status})
        except Exception as e:
            return {"error": f"Unknown error: {str(e)}"}, 500

api.add_resource(UsersResource, '/getUsers')
api.add_resource(LocationResource, '/updateLocationDatabase')

if __name__ == '__main__':
    app.run(debug=True)
