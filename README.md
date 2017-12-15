# Distributed_File_System

DFS is a Distributed file system, which is implemented in python 

* Each Section in this is independent, as we can write this in any languasge without disturbing the other sections of the program.

*

* IDE- Pycharm

--> Dependencies

--> python 2.7 is used for this program

packages : * base64 - for decode and encode 
           * json   - data interchange format inspired by JavaScript
           * haslib - Secure hashes and message digests
           * random - used to generate pseudo-random numbers
           * string - contains common string operations
           * AES    - Crypto.Cipher
           * Flask  - whinch is an Rest API
           * MongoClient 
           
POSTMAN - it is one of the most used REST client allover and it is complete set of toolchain for the API Development.

1st - Authentication server is initialised
2nd - creation of Directory_Service.py and it is runned
3rd - Run users.py

        DFS -- Authentication
        
* details of Mongo DB connection
* Creating conn with Mongo Data base
* drop the tables
* inserting the details of master & worker into Data base
* 32 char's unique Authentication key
* creating new users
* seeking data from request
* encrypting the password using public key and AES
* random session id is generated
* inserting details into Data base
* response back to client 

       DFS -- Directory_Service

* run the direcvtory_service     
* packages used : * datetime
                  * cache from diskcache
                  * jsonify
                  * request
                  * pyMongo
            
* Details of Mongo DB server and connection
* enter 32 char's Authentication key
* Connection to data base
* directory path is used to store cache data
              
             /tmp/mycachedir
* host - Server_Host
  port - Server_Port
  
* In the process of uploading check if the directory exist or not and also check if the files exist in the server.
* In the Process of Downloading, find the file directory, details of the file and then caching.


* for the Testing of Distributed File System, run the servers as per mentioned process.
