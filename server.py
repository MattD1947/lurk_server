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

#    send_message[str(client_socket)] = threading.Thread(target=sendMessage, args=[client_socket, address])
#    send_message[str(client_socket)].start()

#   update_message[str(client_socket)] = threading.Thread(target=updateMessage, args=[client_socket,address])
#    update_message[str(client_socket)].start()


    # checking server update (other clients may send message to the others, in that case, the server will need to
    # response between this two clients)




    # send game description

    # Type = client_socket.recv(1)[0]
def ServerInput(characters):

	while(True):
		data = input("note: \n15 for add monster)\n16 live player list\ntype: ")
		EnterCenter(data,characters)

def main():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
	address = sys.argv[1]
	port = int(sys.argv[2])

	# server_socket.bind((socket.gethostname(), port)) 
	# assign this above if you are running this locally
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


# def receive_message(client_socket):
#     try:
#         receive_type = client_socket.recv(1)

#         if not len(receive_type):
#             return False

#         the_type(receive_type)

#         message_length = int(message_header.decode('ascii'.strip()))
#         return {"header": message_header, "data": client_socket.recv(message_length)}
#     except:
#         return False

# while True:
#     read_sockets, _, exception_sockets = select.select(sockets_list,[],sockets_list)
#     for notified_socket in read_sockets:
#         if notified_socket == server_socket:
#             client_socket, client_address = server_socket.accept()

#             print(f"Accepted new connection from {client_address[0]}:{client_address[1]}")
	    # user = receive_message(client_socket)
	    # if user is False:
	    #     continue
	    # sockets_list.append(client_socket)

	    # sent server info
	    # info = pack("<"+"5B",14,2,2,0,0)
	    # client_socket.sendall(info)

	    #sent game
	    # Type = 11
	    # initialPoints = 100
	    # statLimit = 65535
	    # description = "Welcome to Matt's server"
	    # descriptionLength = len(description)
	    # Format = '<'+'B'+'3H'
	    # game = pack(Format,Type,initialPoints,statLimit,descriptionLength)
	    # client_socket.sendall(game)

	    #send game description
	    # client_socket.sendall(bytes(description,"ascii"))

	    # Type = client_socket.recv(1)[0]

	    #test message
	    # if Type == 1:
	    #     data = client_socket.recv(66)
	    #     lines,size = Message(data)
	    #     message_description = client_socket.recv(size)
	    #     message_description_line = MessageDescription(message_description)
	    #     lines.append(message_description_line)
	    #     for i in lines:
	    #         print(i)
	    # client_socket.sendall(data)
	    # client_socket.sendall(message_description)

	    #send error







	    # clients[client_socket] = user
	    # username: {user['data'].decode("ascii")

	# else:
	    # message = receive_message(notified_socket)
	    # print(f"Connection lost from {notified_socket.decode('ascii')}")
	    # sockets_list.remove(notified_socket)
	    # print(f"Closed connection from {clients[notified_socket].decode('ascii')}")

	    # if message is False:
	    #     sockets_list.remove(notified_socket)
	    #     del clients[notified_socket]
	    #     continue
	    # user = clients[notified_socket]

	    # print(f"Received message from {user['data'].decode('ascii')} ")

	    # for client_socket in clients:
	    #     if client_socket != notified_socket:
	    #         client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # for notified_socket in exception_sockets:
    #     print(f"Closed connection from {notified_socket}")
    #     sockets_list.remove(notified_socket)
    #     del clients[notified_socket]
    # if len(sockets_list) >= 65535:
    #     print()

# while True:
#     read_sockets, _, exception_sockets = select.select(sockets_list,[],sockets_list)
#     for notified_socket in read_sockets:
#         notified_socket.connect()
#         client_socket.send(bytes("Welcome to the server!", "ascii"))
#         time.sleep(5)


# def main():
#     t1 = threading.Thread(target = TopWin)
#     t2 = threading.Thread(target = BottomWin)
#     threads = []
#     t1.start()
#     t2.start()
#     threads.append(t1)
#     threads.append(t2)
#     for thread in threads:
#         thread.join()
# main()




