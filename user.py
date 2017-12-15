import base64
import json

import requests
from Crypto.Cipher import AES
from pymongo import MongoClient

# mongo setup stuff
mongo_server = "localhost"
mongo_port = "27017"
connect_str = "mongodb://" + mongo_server + ":" + mongo_port
conn = MongoClient(connect_str)
db = conn.project

# user info - this file is essentially the first user
user_id = "1"
pub_key = "4ThisIsARandomlyGenAESpublicKey4"
user_pwd = "notsoez2HackThis"

# required encyption pre-requiste variables
secret_hash = AES.new(pub_key, AES.MODE_ECB)

u_headers = {'Content-type': 'application/json'}
payload = {'u_id': user_id
    , 'u_password': user_pwd
    , 'pub_key': pub_key}
request = requests.post("http://localhost:5000/user/c_user", data=json.dumps(payload))

u_headers = {'Content-type': 'application/json'}
payload = {'u_id': user_id
    , 'u_password': user_pwd}
request = requests.post("http://localhost:5000/user/c_user_aut", data=json.dumps(payload))


if (request != None):
    print "\nCONTINUE WITH NEXT STEPS HERE - FILE MANAGEMENT\n"

    server_resp = request.text
    print server_resp
    enco_hashed_ticket = json.loads(server_resp)["u_ticket"]
    deco_hashed_ticket = secret_hash.decrypt(base64.b64decode(enco_hashed_ticket))
    data = json.loads(deco_hashed_ticket.strip())

    session_id = data["id_session"]
    server_host = data["server_host"]
    server_port = data["server_port"]
    access_key = data["access_key"]
    virtual_structure_hash = AES.new(session_id, AES.MODE_ECB)

    print ""
    print data
    print ""

    print("\nDATA DECRYPTION SUCCESS\n")

    directory = "/fileserver/location"
    filename = "test-files/test.txt"
    encryp_dir = base64.b64encode(
        virtual_structure_hash.encrypt(directory + b" " * (AES.block_size - len(directory) % AES.block_size)))
    encryp_filename = base64.b64encode(
        virtual_structure_hash.encrypt(filename + b" " * (AES.block_size - len(filename) % AES.block_size)))

    data = open('test-files/test.txt', 'rb').read()
    u_headers = {'access_key': access_key
        , 'directory': encryp_dir
        , 'filename': encryp_filename}

    request = requests.post("http://" + server_host + ":" + server_port + "/upload_f", data=data, headers=u_headers)
    print request.text

