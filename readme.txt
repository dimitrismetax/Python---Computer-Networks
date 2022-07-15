client:

$ python client.py -r relay_nodes.txt -e end_servers.txt

Give end-server alias and number of pings to send:
(choose one of the available end_servers, google, mit etc + an integer for number of pings)
google 5
Relays file:   relay_nodes.txt
End-servers file:   end_servers.txt
RELAYS:  [['limnos', '147.52.206.52', '49999\n'], ['anafi', '147.52.206.53', '49199\n'], ['leros', '147.52.206.55', '49200\n']]
==============
Hops for anafi 11
Hops for leros 11
Hops for limnos 11
Ping for limnos 67.992
Ping for anafi 72.180
Ping for leros 75.153
All threads finished
Ping list
direct 70.811
limnos 69.256
anafi 73.201
leros 76.374

Traceroute list
anafi 16
leros 16
limnos 16
direct 11
limnos will be the one to download the file
Do you want to download the file from google ?(y/n)
(Here you choose if you want to download the selected file and then the connection closes)
y
Time it took to download:  0.434032201767



===========================================================================================
relay.py:
$ python relay.py

What is the port? :49999 (Here you enter the port which refered in relay_nodes.txt for the specific relay_node)
binded to port:  49999
I started listening
Connected to :  147.52.19.28 : 52781
ping www.google.com 5
traceroute www.google.com
I will send hops 11
I will send ping 67.992
Success https://www.google.com/images/branding/googlelogo/1x/googlelogo_white_background_color_272x92dp.png googlelogo_white_background_color_272x92dp.png
No data, exiting (Here the connection closes)
