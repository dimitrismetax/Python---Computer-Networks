import random
import itertools
import sys
import os
import subprocess
import commands
import requests
import socket
import threading
import thread
import functools
import operator
from struct import unpack
import time
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random

def sign(msg, prkey):
	msg = msg.encode()
	hash = SHA256.new(msg).digest()
	signature = prkey.sign(hash,'')
	return signature

def verify(msg, pckey, signature):
	msg = msg.encode()
        hash = SHA256.new(msg).digest()
	if pckey.verify(hash, signature):
		return True
	else:
		return False

def generate_pair():
	seed = Random.new().read
	pair = RSA.generate(2048, seed) #size of the generated key is 2048 bytes
	return pair

def exchange(conn, relay_name, pckey, prkey):
	pckey = pckey.exportKey()
	sig = sign (key, prkey)
	sig 	
	conn.send()
	return key	

def downloader(alias, conn, mode):
	url = " " 
	if alias == 'google':
        	url = 'https://www.google.com/images/branding/googlelogo/1x/googlelogo_white_background_color_272x92dp.png'
                filename = 'googlelogo_white_background_color_272x92dp.png'
        elif alias == 'mit':
        	url = 'http://www.mit.edu/~gil/images/mit_logo.gif'
                filename = 'mit_logo.gif'
        elif alias == 'grnet':
          	url = 'https://grnet.gr/wp-content/uploads/sites/13/2016/04/GRNET_Logo_Transparent-e1431694322566-1.png'
             	filename = 'GRNET_Logo_Transparent-e1431694322566-1.png'
  	elif alias == 'bbc-uk':
      		filename = 'bbc_news_logo.png'
             	url = 'http://www.bbc.co.uk/news/special/2015/newsspec_10857/bbc_news_logo.png'
  	elif alias == 'caida':
             	url = 'https://www.caida.org/images/logo_caida_large.gif'
           	filename = 'logo_caida_large.gif'
    	elif alias == 'anu':
            	url = 'http://style.anu.edu.au/_anu/4/images/logos/2x_anu_logo_small.png'
             	filename = '2x_anu_logo_small.png'
     	elif alias == 'inspire':
             	filename = 'hy335b.png'
             	url = 'http://www.inspire.edu.gr/wp-content/uploads/2015/01/hy335b.png'
    	elif alias == 'japan-go':
              	filename = 'logo_japangov.png'
         	url = 'https://www.japan.go.jp/_userdata/gnavi/_userdata/navigation/img/logo_japangov.png'

	if mode == "direct": 
		start = time.time()
		r = requests.get(url, allow_redirects=True)
		roundtrip = time.time() - start
		open(filename,'wb').write(r.content)
	else:
		data = "Success ", url, " ", filename
		data = convertTuple(data)
		conn.send(data)
		
		rec = conn.recv(8)
		(roundtrip,) = unpack('>d', rec)
		rec = conn.recv(8)
		(length,) = unpack('>Q', rec)
		img_data = b''
		while length > len(img_data):
			remain = length - len(img_data)
			img_data+=conn.recv(240 if remain > 240 else remain)
			
		
		open(filename, 'wb').write(img_data)

	
	conn.close()
        print "Time it took to download: ", roundtrip

def convertTuple(tup):
	str = functools.reduce(operator.add, (tup))
	return str

def relay_handler(relay_name, conn, addr, pings):
	if pings == -1:
		data = "traceroute ", addr
	elif int(pings) < 50:
		data = "ping ", addr, " ", pings
	else:
		data = " "

	data = convertTuple(data)
	conn.send(data)

	rec = conn.recv(240)
	rec = rec.split()
	if not rec:
		print "Nothing received from relay: ", relay_name
	else:
		if rec[0] == "ping":
			print "Ping for", relay_name, rec[1]
			float_ping = float(rec[1])
			temp_ping_lst = [relay_name, float_ping]
			ping_list.append(temp_ping_lst)
		elif rec[0] == "hops":
			hops = int(rec[1])
			if hops < 30:
				print "Hops for", relay_name, rec[1]
				temp_tracert_lst = [relay_name, hops]
				traceroute_list.append(temp_tracert_lst)
			else:
				print "Reached max number of hops for relay: " , relay_name, rec



def direct_ping_handler(addr, pings):
	try:
		response = subprocess.check_output(
				['ping', '-c', pings , addr ],
				stderr=subprocess.STDOUT,  # get all output
				universal_newlines=True  # return string not bytes
		)
	except subprocess.CalledProcessError:
		response = None

	t1 = 1

	try:
		temp = response.split(" = ")
	except AttributeError:
		print "ATTRIBUTE ERROR"
		t1 = 0

	if t1 !=0:
		temp2 = temp[1].split("/")
		averageRTT = temp2[1]
		temp_lst = ["direct", float(averageRTT)]
		ping_list.append(temp_lst)


def direct_tracert_handler(addr):
	proc = subprocess.Popen(["traceroute " + addr], stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()
	tempout = out.split("\n")
	hops = len(tempout) -2
	if hops < 30:
		temp_lst = ["direct", int(hops)]
		traceroute_list.append(temp_lst)
	else:
		print "Reached max number of hops for direct communication"

def client_to_relayRTT_handler(relay_name, addr, pings):
	try:
		response = subprocess.check_output(
				['ping', '-c', pings , addr ],
				stderr=subprocess.STDOUT,  # get all output
				universal_newlines=True  # return string not bytes
		)
	except subprocess.CalledProcessError:
		response = None

	t1 = 1

	try:
		temp = response.split(" = ")
	except AttributeError:
		print "ATTRIBUTE ERROR"
		t1 = 0

	if t1 !=0:
		temp2 = temp[1].split("/")
		averageRTT = temp2[1]
		temp_lst = [relay_name, float(averageRTT)]
		client_to_relayRTT.append(temp_lst)

def client_to_relayHops_handler(relay_name, addr):
	proc = subprocess.Popen(["traceroute " + addr], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        tempout = out.split("\n")
        hops = len(tempout) -2
        if hops < 30:
                temp_lst = [relay_name, int(hops)]
                client_to_relayHops.append(temp_lst)
        else:
                print "Reached max number of hops for direct communication"


def main():
	input = raw_input('\nGive end-server alias and number of pings to send:\n')
	req = input.split(" ")
	server = "x"
	alias = req[0]
	ping = req[1]

	if ping == '0':
		print "Invalid input"
		sys.exit()
	
	prog_mode = "direct"
	args_iter = iter(sys.argv)
	for x in args_iter:
		if x == '-e':
			endfile = args_iter.next()
			print "End-servers file:  ", endfile
		elif x == '-r':
			relayfile= args_iter.next()
			print "Relays file:  ", relayfile
			prog_mode = "relay"

	
	f = open(endfile,"r");
	lines = f.readlines();
	for i in lines:
		thisline = i.split(",")
		if alias in thisline[1]:
			server = thisline[0]
			continue
	if prog_mode == "relay":
		f = open(relayfile,"r");
		lines = f.readlines();
		relays = []
		for i in lines:
			thisline = i.split(", ")
			relays.append(thisline)
 
		print "RELAYS: ", relays

	if server == 'x':
		print "Input server isn't included in the end_servers file"
	else:
		print "=============="
		threads = []
#=================HERE THREADS START============================================
		t = threading.Thread(target = direct_ping_handler, args = (server, ping)) #ping from client to end
		threads.append(t)
		t.start()
		t = threading.Thread(target = direct_tracert_handler, args = (server, ))  #traceroute from client to end
		threads.append(t)
		t.start()

		if prog_mode == "relay": #code below will only execute if we have the -r parameter
			sockets = []
			global ping_list
	        	global traceroute_list
        	        global client_to_relayRTT
			global client_to_relayHops
			global relayKey_list
			relayKey_list = []
			client_to_relayHops = []
        	        client_to_relayRTT = []
        	        ping_list = []
			traceroute_list = []
			prkey = generate_pair() #generate pair of private and public keys
			pckey = prkey.publickey() #our client's public key
			pckey = pckey.exportKey()
			prkey = prkey.exportKey()
			
			print pckey
			print prkey

			for i in relays:
				sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				temp_port = int(i[2])
				temp_addr = i[1]
				sock.connect((temp_addr, temp_port))  #initital relay connection
				relay_alias = i[0]
				sockets.append([relay_alias, sock])

				#temp_key = exchange(sock, relay_alias, pckey) #inital exchange of keys (will return relay's key)
                                #relayKey_list.append([relay_alias,temp_key]) #put the key along with relay's name in a list

				t = threading.Thread(target = relay_handler, args = (relay_alias, sock, server, ping))  #ping from relay to end
				threads.append(t)
				t.start()
				t = threading.Thread(target = relay_handler, args = (relay_alias, sock, server, -1))  #traceroute from relay to end
				threads.append(t)
				t.start()
				t = threading.Thread(target = client_to_relayRTT_handler, args = (relay_alias, temp_addr, ping))  #ping from client to relay
				threads.append(t)
				t.start()
				t = threading.Thread(target = client_to_relayHops_handler, args = (relay_alias, temp_addr))  #traceroute from client to relay
				threads.append(t)
				t.start()

			for x in threads:
				x.join()
			print "All threads finished"
			
			for i in ping_list: #add RTT1 and RTT2 from client to relay(1) and from relay to end server(2)		
				for j in client_to_relayRTT:
					if i[0] == j[0]:
						i[1] += j[1]
			for i in traceroute_list: #add hops1 and hops2 from client to relay(1) and from relay to end server(2)
				for j in client_to_relayHops:
					if i[0] == j[0]:		
						i[1] += j[1]
	
			print "Ping list"
			for row in ping_list:
				print(" ".join([str(e) for e in row]))

		
			print "\nTraceroute list"
			for row in traceroute_list:
				print(" ".join([str(e) for e in row]))

		
			#MEASUREMENTS

			ping_list = sorted(ping_list,key=lambda l:l[1])
			traceroute_list = sorted(traceroute_list,key=lambda l:l[1])

			min = ping_list[0][1]
			chosen_list = []
			if min == ping_list[1][1]:
				for i in ping_list:
        		        	if min == i[1]:
	        	 	        	chosen_list.append([i[0],])

				print "Relays:", (" ".join([str(e) for e in chosen_list])), "\nhave the same ping, measuring hops"
        			for i in chosen_list:	
					for j in traceroute_list:
                	 			if j[0] == i[0]:
                	        		        i.append(j[1])
        			chosen_list = sorted(chosen_list,key=lambda l:l[1])
        			min_chosen = chosen_list[0][1]
       			 	for k in chosen_list[:]:
	        	        	if min_chosen < k[1]:
	        	        	        chosen_list.remove(k)
        			if len(chosen_list) == 1:
        			        print chosen_list[0][0], "will be the one to download the file"
					chosen_alias = chosen_list[0][0]
        			else:
                			print "Two or more relays has the same ping and hops, choosing randomly:"
					chosen_alias= chosen_list[randint(0, len(chosen_list))][0]
					print chosen_alias, "will be the one to download the file"
			else:
        			print ping_list[0][0], "will be the one to download the file"
				chosen_alias = ping_list[0][0]

		#code below will execute for direct and relay mode aswell
		mode = "direct"
		if chosen_alias != "direct":
			mode = "relay" 
		print "Do you want to download the file from", alias, "?(y/n)"
		input = raw_input()
		if input == "y":
			chosen_sock =  socket.socket(socket.AF_INET,socket.SOCK_STREAM)#base case for direct mode (doesn't need a socket so we just initialize as a random sock)
			for i in sockets:
				if i[0] == chosen_alias:
					chosen_sock.close()  #we need to close the base case's opened sock
					chosen_sock = i[1] #pick a connection unless its direct
				else:
					i[1].close() #close uneeded (if not all) connections
							
			downloader(alias, chosen_sock, mode)
		else:
			print "No download it is :("
			for i in sockets:
                        	i[1].close()
	
		


		
		
if __name__ == '__main__': 
	main()  

