'''
Created on May 13, 2014

@author:  Tea Kolevska
@contact: tea.kolevska@gmail.com
@organization: ICCLab, Zurich University of Applied Sciences
@summary: Module for creating the server side sockets

 Copyright 2014 Zuercher Hochschule fuer Angewandte Wissenschaften
 All Rights Reserved.

    Licensed under the Apache License, Version 2.0 (the "License"); you may
    not use this file except in compliance with the License. You may obtain
    a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.


'''
import socket
import sys,os
import struct
import periodic_web
import json
import threading
import json

def main(argv):  
    running_threads=[{}]   
    print ("In main before while, running threads: %s" %running_threads) 
    HOST = '127.0.0.1'   # Symbolic name meaning all available interfaces
    PORT = 9005 # Arbitrary non-privileged port 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created.")
    try:
        s.bind((HOST, PORT))
    except socket.error , msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    s.listen(10)
    while 1:
        conn, addr = s.accept()
        print("Connection accepted.")
        pid=os.fork()
        print("Forked with pid %s" %pid)
        if pid==-1:
            os._exit(0)
        elif pid==0:
            socket_connection(s,conn,running_threads)
            print (pid, running_threads)
        else:
            conn.close()
        print(pid, running_threads)
    return


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = ''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data
 
def socket_connection(s,conn,running_threads): 
    #s.close()
    data = conn.recv(1024)
    print("Received data.")
    li_var=[]

    if data=="check threads":
        conn.sendall("ok")
        t_name=conn.recv(1024)
        #with open("threads.json") as f:
        #    running_threads=json.load(f)
        print (running_threads)
        print(t_name)
        if t_name in running_threads[0]:

            conn.sendall("True")     
        else:   
            conn.sendall("False")  
            
    if data=="periodic_stop":
        conn.sendall("ok")
        t_name=conn.recv(1024)
        #with open('threads.json') as f:
        #    data = json.load(f)
        print(running_threads)
        for key,value in running_threads: 
            if key==t_name:
                value.cancel()
                conn.sendall("Stopping counter.")
                del data[t_name] 

             
    if data=="periodic_start":
        conn.sendall("ok")
        print("Sent ok.")
        while True:
                raw_msglen = recvall(conn, 4)
                
                if not raw_msglen:
                    return None
                msglen = struct.unpack('>I', raw_msglen)[0]
                # Read the message data
                rez=recvall(conn, msglen)
                #result = json.loads(rez)
                li_var.append(rez)
                print("Received message %s" %rez)
                if rez=="None":
                    print("entering if")
                    break
        conn.sendall("Starting periodic counter for the user.")
        conn.close()
        print("Closing server socket.")
        print("len %s" %len(li_var))
        if len(li_var)==10:
            user=li_var[2]
            thread_name="thread"+user
            print(thread_name)
            name=thread_name
            print("Thread created %s." %thread_name)
            #my_dict={thread_name:user}
            #with open("threads.json") as f:
            #    data = json.load(f)
            #data.update(my_dict)
            #with open('threads.json', 'w') as f:
            #    json.dump(data, f)
            
            thread_name=periodic_web.MyThread(li_var[0],li_var[1],li_var[2],li_var[3],li_var[4],li_var[5],li_var[6],li_var[7],li_var[8],thread_name)
            thread_name.start()
            #my_dict={thread_name:user}
            #.update(my_dict)
            #running_threads[name]=thread_name
            running_threads=add_threads(running_threads,name,thread_name)
            print("Thread started %s." %thread_name)
            print ("Running threads %s" %running_threads)

    return running_threads

def add_threads(running_threads,name,thread):
    dict=running_threads[0]
    new_dict=dict.update({name:thread})
    running_threads[0]=dict
    return running_threads



if __name__ == '__main__':
    main(sys.argv[1:])
