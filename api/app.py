import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from utils import *
from update_location_database import update_location_database

app = Flask(__name__)
CORS(app)

spreadsheet = get_spreadsheet()
records = read_spreadsheet(spreadsheet, sheet="Form responses 2")
locations = read_spreadsheet(spreadsheet, sheet="locations")

@app.route('/getUsers', methods=['GET'])
def get_users():
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
        return jsonify(users), 200, {
            "Cache-Control": "s-maxage=604800, stale-while-revalidate=86400"
        }
    except Exception as e:
        return jsonify({"error": f"Unknown error: {str(e)}"}), 500

@app.route('/updateLocationDatabase', methods=['GET'])
def update_location():
    try:
        status = update_location_database()
        return jsonify()
    except Exception as e:
        return jsonify({"error": f"Unknown error: {str(e)}"}), 500

@app.route('/', methods=['GET'])
def hello():
    return jsonify()

if __name__ == '__main__':
    app.run(debug=True)
