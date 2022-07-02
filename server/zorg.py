from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import json
import psycopg2 as psql
from app import basic_auth

zorg = Blueprint("zorg", __name__)



class SessionConflict(Exception):
    pass


def _connect():
    if os.getenv("FLASK_ENV") == "docker":
        return psql.connect(host="postgres",
                            dbname=os.getenv("POSTGRES_DB"),
                            user=os.getenv("POSTGRES_USER"),
                            password=os.getenv("POSTGRES_PASSWORD"),)
    else:
        return psql.connect("dbname=heffalump")

@zorg.route("trunk", methods=['OPTIONS'])
@cross_origin()
def options_trunk():
    raise Exception("dude")
    return 200

@zorg.route("trunk", methods=['GET'])
@basic_auth.required
@cross_origin()
def get_trunk():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM trunk")
    ret = cursor.fetchone()
    if not ret:
        return 500

    return jsonify({"trunk":ret[0]}) 

@zorg.route("trunk", methods=['POST'])
@basic_auth.required
@cross_origin()
def put_trunk():
    json_data = request.get_json()
    trunk = json_data["trunk"]
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE trunk SET value=%(trunk)s", {"trunk":json.dumps(trunk)})
    conn.commit()
    conn.close()
    return "success", 200

