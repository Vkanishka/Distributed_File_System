import hashlib  # secure hashes and message digests
import os
import threading
import requests
from diskcache import Cache
from flask import Flask
from flask_pymongo import PyMongo
from pymongo import MongoClient


thread_lock = threading.Lock()
SERVER_RESPONSE_POS = 200 # response from server
application = Flask(__name__)
mongo = PyMongo(application)  # mongo setup
mongo_server = "localhost"
mongo_port = "27017"
str = "mongodb://" + mongo_server + ":" + mongo_port
connection = MongoClient(str)   # conn to Database
db = connection.project
AUTH_KEY = "14314314314314314314314314314314"   # 32 char's Authentication key
ser_host = None
ser_port = None

# Set the cache instance
cache = Cache('/tmp/mycachedir')


def get_current_server(host, port): 
    with application.app_context():
        return db.servers.find_one({"host": host, "port": port})


class Ser_transs:
    def asynchronous_upload_trans(self, file, directory, headers):

        with application.app_context():
            servers = db.servers.find()
            for server in servers:
                host = server["host"]
                port = server["port"]
                trans = trans(thread_lock, file, directory)
                trans.start()

                cache_hash = file + "/" + directory + "/" + server['identifier']
                # None is tacked on at the end here - needs further investigation
                data = cache.get(cache_hash)
                #print data

                if get_current_server(host, port)['master_server']:
                    continue

                if (host == ser_host and port == ser_port):
                    continue

                with open(file, "wb") as f:
                    f.write(data)
                print(headers)

                headers = {'access_key': headers['access_key'],
                           'directory': headers['directory'],
                           'filename': headers['filename']}
                r = requests.post("http://" + host + ":" + port + "/file/upload", data=data, headers=headers)

                if r.status_code == SERVER_RESPONSE_POS:
                    transStatus.create(file + directory, server, "SUCCESS")
                else:
                    transStatus.create(file + directory, server, "FAILURE")

            if (transStatus.total_success_count()
                    >= transStatus.total_failure_count()
                    + transStatus.total_unknown_count()):
                requests.post("http://" + host + ":" + port + "/file/delete", data='', headers=headers)

    def asynchronous_del_trans(self, file, directory, headers):

        with application.app_context():
            servers = db.servers.find()
            for server in servers:
                host = server["host"]
                port = server["port"]
                del_trans = Deletetrans(thread_lock, file, directory, host, port)
                del_trans.start()

                if get_current_server(host, port)['master_server']:
                    continue

                if (host == ser_host and port == ser_port):
                    continue
                print(headers)
                headers = {'access_key': headers['access_key'],
                           'directory': headers['directory'],
                           'filename': headers['filename']}
                r = requests.post("http://" + host + ":" + port + "/file/delete", data='', headers=headers)

                if r.status_code == SERVER_RESPONSE_POS:
                    transStatus.create(file + directory, server, "SUCCESS")
                else:
                    transStatus.create(file + directory, server, "FAILURE")
            if (transStatus.total_success_count()
                    >= transStatus.total_failure_count()
                    + transStatus.total_unknown_count()):
                requests.post("http://" + host + ":" + port + "/file/delete", data='', headers=headers)


class trans(threading.Thread):
    def __init__(self, lock, filename, directory):
        threading.Thread.__init__(self)
        self.lock = lock
        self.filename = filename
        self.directory = directory

    def run(self):
        self.lock.acquire()
        return
        self.lock.release()


class Deletetrans(threading.Thread):
    def __init__(self, lock, filename, directory, host, port):
        threading.Thread.__init__(self)
        self.lock = lock
        self.filename = filename
        self.directory = directory
        self.host = host
        self.port = port

    def run(self):
        self.lock.acquire()
        if db.files.find_one({"identifier": self.filename, "directory": self.directory,
                              "server": get_current_server(self.host, self.port)}):
            db.files.remove({"identifier": self.filename, "directory": self.directory,
                             "server": get_current_server(self.host, self.port)})
            os.remove(self.filename)
        self.lock.release()


# This will be used to monitor the "health" of any active servers
class transStatus:
    def __init__(self):
        pass

    @staticmethod
    def create(name, server, status):
        hash_key = hashlib.md5()
        hash_key.update(name)
        trans = db.transs.find_one({"identifier": hash_key.hexdigest()})
        if trans:
            trans["ledger"] = status
        else:
            db.transs.insert(
                {"identifier": hash_key.hexdigest(), "ledger": status, "server-identifier": server['identifier']})


    @staticmethod
    def get(name):
        hash_key = hashlib.md5()
        hash_key.update(name)
        return db.transs.find_one({"identifier": hash_key.hexdigest()})


    @staticmethod
    def total_success_count():
        count = 0
        for trans in db.transs.find():
            if trans['ledger'] == "SUCCESS":
                count += 1
        return count


    @staticmethod
    def total_failure_count():
        count = 0
        for trans in db.transs.find():
            if trans['ledger'] == "FAILURE":
                count += 1
        return count


    @staticmethod
    def total_unknown_count():
        count = 0
        for trans in db.transs.find():
            if trans['ledger'] == "UNKNOWN":
                count += 1
        return count
