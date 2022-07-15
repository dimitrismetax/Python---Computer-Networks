import itertools
import sys
import os
import socket
import threading
import thread
import functools
import operator
import subprocess
import commands
import requests
from struct import pack
import time
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random

def generate_pair():
	seed = Random.new().read
	pair = RSA.generate(2048, random_generator) #size of the generated key is 2048 bits
	return pair


def convertTuple(tup):
    str = functools.reduce(operator.add, (tup))
    return str

def handler(conn, addr, data):
	print data
	commands = data.split()
	if commands[0] == "ping":
                addr = commands[1]
                ping_count = commands[2]
		try:
                        response = subprocess.check_output(
                                ['ping', '-c', ping_count, addr],
                                stderr=subprocess.STDOUT,  # get all output
                                universal_newlines=True  # return string not bytes
                        )
                except subprocess.CalledProcessError:
                        response = None
        #       command = ['ping', '-c' , ping , server ]
        #       if subprocess.call(command) == 0:
                t1 = 1

                try:
                        temp = response.split(" = ")
                except AttributeError:
                        t1 = 0

                if t1 !=0:
                        temp2 = temp[1].split("/")
                        averageRTT = temp2[1]
			data = "ping ", str(averageRTT)
			data = convertTuple(data)
			print "I will send", str(data)
			conn.send(data)

        elif commands[0] == "traceroute":
		addr = commands[1]
		proc = subprocess.Popen(["traceroute " + addr], stdout=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()
                tempout = out.split("\n")
                hops = len(tempout) -2
		data = "hops ", str(hops)
		data = convertTuple(data)
		print "I will send", str(data)
		conn.send(data)
        elif commands[0] == "Success":
		url = commands[1]
		filename = commands[2]
		start = time.time()
		r = requests.get(url, allow_redirects=True)
		roundtrip = time.time() - start
               	open(filename, 'wb').write(r.content)
		with open(filename, 'r') as fp:
        		image_data = fp.read()
		roundtrip = pack('>d', roundtrip)
		length = pack('>Q', len(image_data))
		conn.sendall(roundtrip)
		conn.sendall(length)
		conn.sendall(image_data)

def main():
	port = raw_input('\nWhat is the port? :')
	host=""
	port = int(port)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((host, port))
	print('binded to port: '), port
	s.listen(10)
	print 'I started listening'
	conn, addr = s.accept()
	print('Connected to : '), addr[0],':', addr[1]
	
	while 1:
		data = conn.recv(240)
		if not data:
			print "No data, exiting"
			conn.close()
			break
		thread.start_new_thread(handler, (conn,addr,data))
	s.close()

if __name__ == '__main__':
	main()

