#!/usr/bin/python2
#coding=utf-8
import sys
import socket  
import time
import os
import json
hot_point_socket = socket.socket()
hot_point_host = '127.0.0.1'
hot_point_port = 23333
addr = (hot_point_host, hot_point_port)
hot_point_socket.bind(addr)        
 
hot_point_socket.listen(5)
 
to_client, addr = hot_point_socket.accept()
print ('...connected from :', addr)

while True:
    data = to_client.recv(800)
    print(data)
    to_client.send(data)
   
 
hot_point_socket.close()
to_client.close()
        