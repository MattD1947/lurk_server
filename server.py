import socket
import struct
from struct import *
import threading
from threading import Thread, Lock
mutex = Lock()
import time
from time import sleep
import curses
from curses import wrapper
import pickle
import select
from server_models import *

from socket import error as SocketError
import errno
import sys



# port = 5101

# classes settings
message_array = []
rooms = {}


# threading setup
recv_message = {}
send_message = {}
update_message = {}
leave = False

number = 0


def recvMessage(client_socket,characters,address):
	leave = False
	login_status = False
	while(True):
		try:
			message_type_byte = client_socket.recv(1)
		except SocketError as e:
			if e.errno != errno.ECONNRESET:
				raise
			# elif e.errno != errno.EPIPE:
			#	raise
			pass

		if len(message_type_byte) == 0:
			print(str(message_type_byte)+"OK")
			if live_player_list.get(client_socket,None) == None:
				print("Player has left the server with no available character.56")
				print("Socket(leaving by accident): "+str(client_socket))
				print("Socket(leaving by accident): "+str(live_player_list.get(client_socket,"Leaving without login or body cleaned.")))
				print("Connection lost from {0}:{1}.53\n".format(address[0],address[1]))
				client_socket.close()
				break
			else:
				if characters.get(live_player_list[client_socket],None) != None:
					characters[live_player_list[client_socket]].login = False
					characters[live_player_list[client_socket]].start_status = False
					print("Player login status has been set up FALSE.60")
					print("Player start_status has been set up FALSE.61")
				print("Socket(leaving by accident): "+str(client_socket))
				print("Socket(leaving by accident): "+str(live_player_list.get(client_socket,None)))
				print("Connection lost from {0}:{1}.59\n".format(address[0],address[1]))
				del live_player_list[client_socket]

				client_socket.close()
				break

			if characters.get(live_player_list[client_socket],None) != None:
				print(live_player_list[client_socket])

				characters[live_player_list[client_socket]].login = False
				characters[live_player_list[client_socket]].start_status = False
				print("Notice: "+liver_player_list[client_socket])
				print("Player login status has been set up FALSE.")
				print("Player start_status has been set up FALSE.")
				del live_player_list[client_socket]
				print("Player has been removed from live_player_list.")
			client_socket.close()
			print("Connection lost from {0}:{1}.65\n".format(address[0],address[1]))
			break

		leave = recvProcess(message_type_byte, client_socket, 
				# message_array,
				characters,
				leave
				)
		if(leave):
			if live_player_list.get(client_socket,None) == None: # this means the player is died and has been removed from characters and live_player_list
				print("Connection lost from {0}:{1}.74\n".format(address[0],address[1]))
				client_socket.close()
				break
			if characters.get(live_player_list[client_socket],None) != None:
				characters[live_player_list[client_socket]].login = False
				characters[live_player_list[client_socket]].start_status = False
				print("Player login status has been set up FALSE.")
				print("Player start_status has been set up FALSE.")
			# name = live_player_list[client_socket]
			print("Player "+str(live_player_list[client_socket]) + " has left the server. 79")
			del live_player_list[client_socket]
			client_socket.close()
			break

def runningThreading(client_socket, address,characters):
	# beginning of the connection
    # sent server info
    info = pack("<"+"5B",14,2,2,0,0)
    client_socket.sendall(info)

    # sent game

    Type = 11
    initialPoints = 100
    statLimit = 65535
    description = "Welcome to Matt's server"
    descriptionLength = len(description)
    Format = '<'+'B'+'3H'
    game = pack(Format,Type,initialPoints,statLimit,descriptionLength)
    client_socket.sendall(game)
    client_socket.sendall(bytes(description,'ascii'))

    # waiting for client send byte to server

    recvMessage(client_socket, characters,address)

def ServerInput(characters):

	while(True):
		data = input("note: \n15 for add monster)\n16 live player list\ntype: ")
		EnterCenter(data,characters)

def main():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
	address = sys.argv[1]
	port = int(sys.argv[2])
	server_socket.bind((address, port))
	server_socket.listen(65535)
	sockets_list = [server_socket]
	global number
	global leave
	global characters
	clients = {}
	characters = {}
	number = 0
	threading.Thread(target=ServerInput,args=[characters]).start()
	while True:
		try:
			clients[number], address = server_socket.accept()
			threading.Thread(target=runningThreading, args=[clients[number], address,characters]).start()
			number += 1
			print("Connection from {0}:{1} has been established.\n".format(address[0],address[1]))
		except SocketError as e:
			if e.errno != errno.ECONNREST:
				raise
			pass

main()
