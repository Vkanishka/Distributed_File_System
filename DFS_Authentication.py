import base64
import hashlib
import json
import random
import string

from Crypto.Cipher import AES
from flask import Flask
from flask import request
from flask import jsonify
from pymongo import MongoClient


mongo_server = "localhost"
mongo_port = "27017"

connect_string = "mongodb://" + mongo_server + ":" + mongo_port

conn = MongoClient(connect_string)
db = conn.project
db.users.drop()
db.servers.drop()
db.directories.drop()
db.files.drop()
db.transactions.drop()
hash_key = hashlib.md5()

#b
database = conn.DFS

database.users.drop()
database.servers.drop()
database.directories.drop()
database.files.drop()
database.transactions.drop()

#a
m_server = "localhost"
m_port = "27017"

conn = MongoClient("mongodb://" + m_server + ":" + m_port)



#c
app = Flask(__name__)
AUTH_KEY = "14314314314314314314314314314314"


#e
@app.route('/user/c_user_aut', methods=['POST'])
def u_authentication():
    d_req = request.get_json(force=True)
    u_password = d_req.get('u_password')
    u_id = d_req.get('u_id')
    u_details = database.users.find_one({'u_id': u_id})
    encry_password = u_details['u_password']
    pub_key = u_details['pub_key']
    decrypted_u_password = AES.new(pub_key, AES.MODE_ECB).decrypt(base64.b64decode(encry_password)).strip()

    if decrypted_u_password == u_password:
        id_session = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))
        u_details['id_session'] = id_session
        if database.users.update({'u_id': u_id}, u_details, upsert=True):
            c_user = u_details
        else:
            return jsonify({'success': False
                            })
    else:
        return jsonify({'success': False
                        })
    if c_user:
        Session_keyhashed = c_user['id_session'] + b" " * (
                AES.block_size - len(c_user['id_session']) % AES.block_size)
        enc_hash_Session_key = base64.b64encode(AES.new(AUTH_KEY, AES.MODE_ECB).encrypt(Session_keyhashed))

        u_ticket = json.dumps(
            {'id_session': c_user['id_session'], 'server_host': "localhost", 'server_port': "9001",
             'access_key': enc_hash_Session_key})

        u_ticket_hash_format = u_ticket + b" " * (AES.block_size - len(u_ticket) % AES.block_size)
        enc_h_ticket = base64.b64encode(
            AES.new(c_user['pub_key'], AES.MODE_ECB).encrypt(u_ticket_hash_format))

        print "\nUser Authorized Successful\n"
        return jsonify({'success': True, 'u_ticket': enc_h_ticket})
    else:
        return jsonify({'success': False
                        })


#d
@app.route('/user/c_user', methods=['POST'])
def user_creation():
 
    print "-- Creating a new user --"

    req_d_req = request.get_json(force=True)
    u_id = req_d_req.get('u_id')
    u_password = req_d_req.get('u_password')

    pub_key = "y3y39yi2319jn2432b3c3oh23g8g38od"

    encrypted_u_password = base64.b64encode(AES.new(pub_key, AES.MODE_ECB).encrypt(u_password))

    s_id = "1q2w3e4r5t6y7u8i9o0p1q2w3e4r5"

    database.users.insert(
        {"u_id": u_id, "s_id": s_id, "pub_key": pub_key,
         "u_password": encrypted_u_password}
    )

    return jsonify({"msg": "User sucessfully Created",
                    "User ID": u_id})




if __name__ == '__main__':
    app.run()










