import base64
import datetime
import hashlib
import flask
from Crypto.Cipher import AES
from diskcache import Cache
from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from pymongo import MongoClient


application = Flask(__name__)


mongo = PyMongo(application)
mongo_server = "localhost"
mongo_port = "27017"
AUTH_KEY = "14314314314314314314314314314314"  # 32 char's Authentication key

str = "mongodb://" + mongo_server + ":" + mongo_port

connection = MongoClient(str)  # connection to DB
db = connection.DFS
servers = db.servers
SERVER_HOST = None
SERVER_PORT = None

cache = Cache('/tmp/mycachedir')  # directory path is used to store cache


def decrypt_data(key, hashed_val):
    decrypted_data = AES.new(key, AES.MODE_ECB).decrypt(base64.b64decode(hashed_val))
    return decrypted_data


def server_inst():
    with application.app_context():
        return db.servers.find_one({"host": SERVER_HOST, "port": SERVER_PORT})



#  to upload
@application.route('/upload_f', methods=['POST'])
def upload_f():
    data = request.get_data()
    headers = request.headers
    encryp_filename = headers['filename']
    encryp_dir = headers['directory']
    access_key = headers['access_key']

    session_id = decrypt_data(AUTH_KEY, access_key).strip()
    decry_dir = decrypt_data(session_id, encryp_dir)
    decry_filename = decrypt_data(session_id, encryp_filename)

    hash_key = hashlib.md5() 
    hash_key.update(decry_dir)

    # Check if the directory exits or not
    if not db.directories.find_one(
            {"name": decry_dir, "identifier": hash_key.hexdigest(),
             "server": server_inst()["identifier"]}):
        hash_key = hashlib.md5()
        hash_key.update(decry_dir)
        db.directories.insert({"name": decry_dir
                                  , "identifier": hash_key.hexdigest()
                                  , "server": server_inst()["identifier"]})
        file_directory = db.directories.find_one(
            {"name": decry_dir, "identifier": hash_key.hexdigest(),
             "server": server_inst()["identifier"]})
    else:
        file_directory = db.directories.find_one(
            {"name": decry_dir, "identifier": hash_key.hexdigest(),
             "server": server_inst()["identifier"]})

    # Check if the files exists in the server
    if not db.files.find_one(
            {"name": decry_filename, "directory": file_directory['identifier'],
             "server": server_inst()["identifier"]}):
        hash_key = hashlib.md5()
        hash_key.update(file_directory['identifier'] + "/" + file_directory['name'] + "/" + server_inst()['identifier'])
        db.files.insert({"name": decry_filename
                                   , "directory": file_directory['identifier']
                                   , "server": server_inst()["identifier"]
                                   , "identifier": hash_key.hexdigest()
                                   , "updated_at": datetime.datetime.utcnow()})

        file = db.files.find_one({'identifier': hash_key.hexdigest()})
        cache_hash = file['identifier'] + "/" + file_directory['identifier'] + "/" + server_inst()["identifier"]
        cache.set(cache_hash, data)
        with open(file['identifier'], "wb") as f:
            f.write(file['identifier'] + "/" + file_directory['identifier'] + "/" + server_inst()["identifier"])

        file = db.files.find_one(
            {"name": decry_filename, "directory": file_directory['identifier'],
             "server": server_inst()["identifier"]})
    else:
        file = db.files.find_one(
            {"name": decry_filename, "directory": file_directory['identifier'],
             "server": server_inst()["identifier"]})

    return jsonify({'success': True})


#
# # to delete
# @application.route('/file/delete', methods=['POST'])
# def delete():
#     print "\nDELETING ...\n"
#     headers = request.headers
#     encryp_dir = headers['directory']
#     encryp_filename = headers['filename']
#     access_key = headers['access_key']
#
#     session_id = decrypt_data(AUTH_KEY, access_key).strip()
#     decry_dir = decrypt_data(session_id, encryp_dir)
#     decry_filename = decrypt_data(session_id, encryp_filename)
#
#     hash_key = hashlib.md5()
#     hash_key.update(decry_dir)
#
#     if not db.directories.find_one(
#             {"name": decry_dir, "identifier": hash_key.hexdigest(),
#              "server": server_inst()["identifier"]}):
#         print("No directory found")
#         return jsonify({"success": False})
#     else:
#         directory = db.directories.find_one(
#             {"name": decry_dir, "identifier": hash_key.hexdigest(),
#              "server": server_inst()["identifier"]})
#     file = db.files.find_one(
#         {"name": decry_filename, "directory": directory['identifier'], "server": server_inst()["identifier"]})
#     if not file:
#         print("No file found")
#         return jsonify({"success": False})
#
#     if (server_inst()["master_server"]):
#         thr = threading.Thread(target=asynchronous_delete, args=(file['identifier'], directory['identifier'], headers),
#                                kwargs={})
#         thr.start()
#     return jsonify({'success': True})


# to Download
@application.route('/file/download', methods=['POST'])
def download():
    print "\nDOWNLOADING ...\n"
    # data = request.get_json(force=True)
    headers = request.headers
    encryp_filename = headers['filename']
    encryp_dir = headers['directory']
    access_key = headers['access_key']

    session_id = decrypt_data(AUTH_KEY, access_key).strip()
    decry_dir = decrypt_data(session_id, encryp_dir)
    decry_filename = decrypt_data(session_id, encryp_filename)

    hash_key = hashlib.md5()
    hash_key.update(decry_dir)

    # finding the file directory
    directory = db.directories.find_one(
        {"name": decry_dir, "identifier": hash_key.hexdigest(), "server": server_inst()["identifier"]})
    if not directory:
        return jsonify({"success": False})

    # find the details of file
    file = db.files.find_one(
        {"name": decry_filename, "directory": directory['identifier'], "server": server_inst()["identifier"]})
    if not file:
        return jsonify({"success": False})

    # caching
    cache_hash = file['identifier'] + "/" + directory['identifier'] + "/" + server_inst()["identifier"]
    if cache.get(cache_hash):
        return cache.get(cache_hash)
    else:
        return flask.send_file(file['identifier'])



#
if __name__ == '__main__':
    with application.app_context():
        for curr_serv in db.servers.find():
            print(curr_serv)
            if (curr_serv['in_use'] == False):
                curr_serv['in_use'] = True
                SERVER_PORT = curr_serv['port']
                SERVER_HOST = curr_serv['host']
                db.servers.update({'identifier': curr_serv['identifier']}, curr_serv, upsert=True)
                application.run(host=curr_serv['host'], port=int(curr_serv['port']))
