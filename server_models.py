import struct
from classes import Message_unit,Character_unit,Room_unit,Monster_unit

from struct import unpack,unpack_from,pack

from  monster import *
from random import randint
from socket import error as SocketError
import errno
import socket as Socket
import threading
from threading import Thread, Lock

global mutex
mutex = threading.Lock()

prepare_rooms ={
		0: ["Golden Finger","Title as you see, golden finger will be set in the room up on what we dont know, stay turn~"], 
		1: ["Big Green","Green grass is under your feet, enjoy the fresh air!"],
		2: ["Apple Juice","Wanna an apple juice? Here you go, dont be shy and enjoy it. The monstor is not a monstor or I dont know."],
		3: ["Issac","Have you ever heard anything about Issac. Search the game Issac on Steam for more detail."],
		4: ["Heaven","A~~~~~~~ We are in the heaven, god is god, and god is god."],
		5: ["Ice Burger","This is ...., you know, for eat or for what, I dont really know it!"],
		6: ["Rainbow RainBow","Rainbow Rainbow, Rainbow, Rainbo, Raabow, Rain bowoo"],
		7: ["Rule 34","Rule 34? There is also rule 21, rule 13, and more...."],
		8: ["Boss Matt","Girls and boys, dont be shy, I am here, fight me if you wanna."],
		9: ["Riven","Riven. Some people like, some doesnt, whats your choice?"],
		10: ["Kitchen","Are you hungry, take some material, and cook yourself. Do what ever you wanna, and feel it at home."],
		11: ["Waiting Room", "Take a rest, you haven't start the game yet, or get ready for your next battle."]
		}
global rooms
rooms = {}
for i in range(len(prepare_rooms)):
	rooms[i] = Room_unit(
			9,
			i,
			prepare_rooms[i][0],
			len(prepare_rooms[i][1]),
			prepare_rooms[i][1]
			)

global live_player_list
live_player_list = {}

global rooms_lockers 
rooms_lockers = {}


global message_array
message_array = []

global live_monster_list
live_monster_list = {}
room_number_used_list = {}
for i in range(len(prepare_monsters)):
	
	room_number = randint(0,10)
	rooms[room_number].addPlayer(prepare_monsters[i]["name"])
	name = prepare_monsters[i]["name"]
	flags = prepare_monsters[i]["flags"]
	attack = prepare_monsters[i]["attack"]
	defense = prepare_monsters[i]["defense"]
	regen = prepare_monsters[i]["regen"]
	health = prepare_monsters[i]["health"]
	gold = prepare_monsters[i]["gold"]
	room_number = room_number
	description = prepare_monsters[i]["description"]
	description_length = len(description)
	live_monster_list[name] = Monster_unit(10,name,flags,attack,defense,regen,health,gold,room_number,description_length,description)


def Game(data):## type 11
    i = 0
    StartPoint = str(struct.unpack("H",data[:i+2])[0])
    StatLimit = str(struct.unpack("H",data[i+2:i+4])[0])
    DescriptionLength = str(struct.unpack("H",data[i+4:])[0])
    size = int(DescriptionLength)
    line = [
        # "Type: " + Type + " (Game)",
        "Initial Point: " + StartPoint,
        "Stat limit: " + StatLimit,
        "Description Length: " + DescriptionLength,
    ]
    return line,size


def GameDescription(data):
    # length = len(data)
    GameDescription = ""
    for i in range(len(data[:])):
        GameDescription +=  str(chr(data[i]))
    line = "Game Description: " + GameDescription
    return line

def recvProcess(data, client_socket, characters,
		leave
		):
	print(data)
	if int(data[0]) == 1: # message
		Message(client_socket)
	if int(data[0]) == 2: # change room
		Change_Room(client_socket,characters,rooms)
	elif int(data[0]) == 3: # fight
		Fight(client_socket,characters)
	elif int(data[0]) == 4: # pvp
		PVP(client_socket)
	elif int(data[0]) == 5: # loot
		Loot(client_socket,characters)
	elif int(data[0]) == 6: # start
		Start(client_socket,characters)
		print("Receive Process data: " +str(data) + "Name: " + live_player_list[client_socket])

	elif int(data[0]) == 10: # character (Half Done)
		Server_Character(client_socket,characters)
		return leave
	elif int(data[0]) == 12: # leave (Done)
		# client_socket.close()
		return True
def PVP(client_socket):
	data = client_socket.recv(32)
	Error(client_socket,8)
	return

def Loot(client_socket,characters):
	data = client_socket.recv(32)
	target_player = data[:].decode('ascii').rstrip('\x00').lstrip('\x00')
	
	if live_player_list.get(client_socket,None) == None:
		Error(client_socket,17)
		return
	elif characters[live_player_list[client_socket]].death == True:
		Error(client_socket,22)
		return

	name = live_player_list[client_socket]
	monster = target_player

	# if the target is a monster
	if live_monster_list.get(monster,None) != None:
		if live_monster_list[monster].reward == "":
			Error(client_socket,32)
			return
		if live_monster_list[monster].reward != name:
			Error(client_socket,24)
			return
		characters[name].gold += live_monster_list[monster].gold
		sender_content = "You have looted " + str(live_monster_list[monster].gold) + " from the monster " + monster +"."
		message_length = len(sender_content)
		sender_name = "Server"
		recipient_name = live_player_list[client_socket]
		message_detail = Message_unit(1,message_length,recipient_name,sender_name,sender_content)
		SendMessage(client_socket,message_detail)
		Character(client_socket,characters,name)
		room_number = live_monster_list[monster].room_number
		rooms[room_number].players.remove(monster)
		live_monster_list[monster].gold = 0
		live_monster_list[monster].flags = int(b'01111000',2)

		# speak to everyone in the room
		room_number = live_monster_list[monster].room_number
		players = rooms[room_number].players
		for player in players:
			socket = Find_socket(player)
			if socket != None:
				Monster(socket,monster)

		del live_monster_list[monster]
		return
			
	room_number = characters[live_player_list[client_socket]].room_number
	if target_player == name:
		description = "Joke, are you trying loot yourself?"
		length = len(description)
		recipient = name
		sender = "Server"
		message_detail = Message_unit(1,length,recipient,sender,description)
		SendMessage(client_socket,message_detail)
		return

	# if the target is a player
	if characters.get(target_player,None) != None:
		if characters[target_player].death == False:
			socket = Find_socket(target_player)
			description = "Someone is trying to looking or spanking you, careful! "
			length = len(description)
			recipient = target_player
			sender = "Server"
			message_detail = Message_unit(1,length,recipient,sender,description)
			SendMessage(socket,message_detail)
			Error(client_socket, 33)
			return
		elif characters[target_player].room_number != room_number:
			Error(client_socket,34)
			return
		elif characters[target_player].gold <= 0:
			sender_content = "You got nothing to Loot"
			message_length = len(sender_content)
			sender_name = "Server"
			recipient_name = live_player_list[client_socket]
			message_detail = Message_unit(1,message_length,recipient_name,sender_name,sender_content)
			SendMessage(client_socket,message_detail)
			# Error(client_socket,35)
			return

		gold_looted = {**characters[target_player].gold}
		characters[target_player].gold = 0
		characters[live_player_list[client_socket]].gold += gold_looted
		sender_content = "You have looted " + str(gold_looted) + " from " + target_name +"." 
		message_length = len(sender_content)
		sender_name = "Server"
		recipient_name = live_player_list[client_socket]
		message_detail = Message_unit(1,message_length,recipient_name,sender_name,sender_content)
		SendMessage(client_socket,message_detail)
		Character(client_socket,characters,target_player)
		socket = Find_socket(target_player)
		characters.remove(target_player)

		return
	description = "No target found!"
	length = len(description)
	recipient = name
	sender = "Server"
	message_detail = Message_unit(1,length,recipient,sender,description)
	SendMessage(client_socket,message_detail)
	return

def Find_socket(name):
	for socket in live_player_list:
		if live_player_list.get(socket,None) == name:
			return socket
		else:
			return None

def Fight(client_socket,characters):
	name = live_player_list[client_socket]
	print(name+"<- You started a fight!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")	
	
	current_room_number = characters[name].room_number
	
	players = rooms[current_room_number].players
	monsters_in_room ={}
	players_in_room = {}
	init_fight_player = live_player_list[client_socket]
	# player and monster available to fight
	for player in players:
		if live_monster_list.get(player,None) != None:
			if live_monster_list[player].reward == "":
				monsters_in_room[player] = live_monster_list[player]
		elif characters.get(player,None) != None:
			characters[player].lock = True
			flags = characters[player].flags
			# print(len(bin(flags)))
			if characters[player].death == False:
				players_in_room[player] = characters[player]
	if len(monsters_in_room) == 0:
		Error(client_socket,20)
		return
	# if len(players_in_room) == 0:
	#	Error(client_socket,21)
	send_updated_character_message_list = players_in_room
	count = 0
	print("You are at line 276.")
	while True:
		if count > 100:
			break
		# player attack monster
		monsters_delete_list = []
		print("You are at line 283")
		for player in players_in_room:
			for monster in monsters_in_room:
				damage = characters[player].attack - live_monster_list[monster].defense
				death = False
				if damage > 0:
					live_monster_list[monster].health -= damage
					live_monster_list[monster].health += live_monster_list[monster].regen
					if live_monster_list[monster].health <= 0:
						live_monster_list[monster].health = 0
						live_monster_list[monster].flags = int('01111000',2)
						live_monster_list[monster].reward = player
						death = True
						monsters_delete_list.append(monster)
						monster_name = live_monster_list[monster].name
						tmp_list = {**live_player_list}
						for player in players_in_room:
							for socket in tmp_list:
								if tmp_list.get(socket,None) == player:
									Monster(socket,monster_name)
									break
				if damage <= 0:
					damage = 0
				if death == True:
					sender_content = "You killed " + monster +"!Don't forget to loot your reward!"
					sender_name = "Server" 
					recipient_name = init_fight_player
					message_length = len(sender_content)
					message_detail = Message_unit(1,message_length,recipient_name,sender_name,sender_content)
					for the_socket in live_player_list:
						if live_player_list[the_socket] == player:
							SendMessage(the_socket,message_detail)
							break
					continue
				print("Line: 317")
				sender_content = monster+" has been damaged by you: " +str(damage) + "."
				sender_name = "Server" 
				recipient_name = init_fight_player
				message_length = len(sender_content)
				message_detail = Message_unit(1,message_length,recipient_name,sender_name,sender_content)
				SendMessage(client_socket,message_detail)
			for delete_monster in monsters_delete_list:
				del monsters_in_room[delete_monster]
			monsters_delete_list = []
		print("Line: 326")	
		# monster attack player
		players_delete_list = []
		for monster in monsters_in_room: # this is a tmp room for monster
			death = False
			for player in players_in_room:
				damage = live_monster_list[monster].attack - characters[player].defense
				if damage > 0:
					characters[player].health -= damage
					characters[player].health += characters[player].regen
					if characters[player].health <= 0:
						
						death = True
						characters[player].health = 0
						characters[player].flags = int('01011000',2)
						characters[player].death = True
						players_delete_list.append(player)
						tmp_list = {**live_player_list}
						for socket in tmp_list:
							Character(socket,characters,player)
						print("Died body health:"+str(characters[player].health))
						break
				if damage <= 0:
					damage = 0
				if death == True:
					# i may need a logic for died body cleanup function, work on this later
					# characters[player].flags -= 128
					sender_content = "Monster " + monster +" killed you! Your gold is dropped if there is any! The body will be cleaned at any time."
					sender_name = "Server" 
					recipient_name = init_fight_player
					message_length = len(sender_content)
					message_detail = Message_unit(1,message_length,recipient_name,sender_name,sender_content)
					for the_socket in live_player_list:
						if live_player_list[the_socket] == player:
							SendMessage(the_socket,message_detail)
							Character(the_socket,characters,player)
							
							break
					continue
				sender_content = monster+" has damaged you about: " +str(damage) + "."
				sender_name = "Server" 
				recipient_name = init_fight_player
				message_length = len(sender_content)
				message_detail = Message_unit(1,message_length,recipient_name,sender_name,sender_content)
				SendMessage(client_socket,message_detail)
			for delete_player in players_delete_list:
				if characters[delete_player].gold == 0: # if there is no gold, the server will auto clean the body
					
					del characters[delete_player]
					for the_socket in live_player_list:# find the player matched socket, break , therefore it will not have the dictionary changed size durring iteration error
						if live_player_list[the_socket] == delete_player:
							del live_player_list[the_socket]
							print(delete_player+" was killed")
							sender_content = "You are died with no gold, therefore you body has been cleaned by server. Create a new CHARACTER to join the battle."
							length = len(sender_content)
							sender_name = "Server"
							recipient_name = delete_player
							message_detail = Message_unit(1,length,recipient_name,sender_name,sender_content)
							SendMessage(the_socket,message_detail)
							break
				del players_in_room[delete_player]
			players_delete_list = []
		if len(monsters_in_room) == 0 or len(players_in_room) == 0:
			for player_name in send_updated_character_message_list:
				for the_socket in live_player_list:
					if live_player_list[the_socket] == player_name:
						if the_socket != client_socket:

							sender_content = "A fight was happening in the room."
							message_length = len(sender_content)
							sender_name = "Server"
							recipient_name = live_player_list[the_socket]
							message_detail = Message_unit(1,message_length,recipient_name,sender_name,sender_content)
							SendMessage(the_socket,message_detail)
						Character(the_socket,characters,player_name)
			break
		print("line: 401")
		count+=1


	if count >= 100:
		sender_content = "It looks like you guys can not kill each other, see you next time!"
		message_length = len(sender_content)
		recipient_name  = live_player_list[client_socket]
		sender_name = "Server"
		message_detail = Message_unit(1,message_length,recipient_name,sender_name,sender_content)
		SendMessage(client_socket,message_detail)
		return




def Change_Room(client_socket,characters,rooms):
	if live_player_list.get(client_socket,None) == None:
		Error(client_socket,5)
		print("Line: 422")
		return
	mutex = threading.Lock()
	mutex.acquire()
	data = client_socket.recv(2,Socket.MSG_WAITALL)
	to_room_number = unpack('H',data)[0]
	name = live_player_list[client_socket]
	if live_player_list.get(client_socket,None) == None:
		Error(client_socket,17)
		mutex.release()
		return
	elif rooms.get(to_room_number,None) == None:
		Error(client_socket,16)
		mutex.release()
		return

	print("you are going to change room to :" + str(data))
	if data == None:
		Error(client_socket,1)
		mutex.release()
		return
	
	print("Room number is: "+str(to_room_number))
	if to_room_number >= 11 or to_room_number < 0:
		Error(client_socket,1)
		Character(colient_socket,characters,live_player_list[client_socket])
		mutex.release()
		return

	name = live_player_list.get(client_socket,"NONE")
	print(name+" was tring to change room to # "+str(to_room_number)+".")
	print("\n")
	name = live_player_list[client_socket]
	if to_room_number == characters[name].room_number:
		Error(client_socket,26)
		mutex.release()
		return
	old_room_number = characters[name].room_number

	# move player from one room to another
	characters[name].room_number = to_room_number
	Character(client_socket,characters,name)
	rooms[to_room_number].addPlayer(name)
	rooms[characters[name].room_number].players.remove(name)

	# notice player and server end
	Room(client_socket,characters)
	Check_Room_Player_List(client_socket,rooms,name,to_room_number,characters)

	# Character(client_socket,characters,name)
	# Connection(client_socket,current_room_number)
	Connection(client_socket,to_room_number)
#	client_socket.sendall(b'\x00')
	print("Connection sent!")

	# send notice to the others
	for player_name in rooms[to_room_number].players:
		if player_name != name:
			if live_monster_list.get(player_name, None) == None:
				Character(client_socket,characters,player_name)
				for the_socket in live_player_list:
					if live_player_list[the_socket] == player_name:
						content = "Player "+ name + " has entered this room."
						message_length = len(content)
						sender_name ="Server"
						recipient_name = live_player_list[the_socket]
						message_detail = Message_unit(1,message_length,recipient_name,sender_name,content)
						# SendMessage(the_socket,message_detail)
						Character(the_socket,characters,name)
			elif live_monster_list.get(player_name,None) != None:

				Monster(client_socket,player_name)
	for player_name in rooms[old_room_number].players:
		if player_name != name:
			if live_monster_list.get(player_name, None) == None:
				Character(client_socket,characters,player_name)
				for the_socket in live_player_list:
					if live_player_list[the_socket] == player_name:
						content = "Player "+ name + " has left this room."
						message_length = len(content)
						sender_name ="Server"
						recipient_name = live_player_list[the_socket]
						message_detail = Message_unit(1,message_length,recipient_name,sender_name,content)
						# SendMessage(the_socket,message_detail)
						Character(the_socket,characters,name)
						# Character(client_socket,characters,name)
	mutex.release()

def Monster(client_socket,monster_name):
    name = monster_name
    flags = live_monster_list[name].flags
    attack = live_monster_list[name].attack
    defense = live_monster_list[name].defense
    regen = live_monster_list[name].regen
    health = live_monster_list[name].health
    gold = live_monster_list[name].gold
    current_room_number = live_monster_list[name].room_number
    description_length = live_monster_list[name].description_length
    description = live_monster_list[name].description

    lines = []
    lines.append("Type: 10 (ChHARACTER)")
    lines.append("Name: "+str(name))
    lines.append("Flags: "+str(flags))
    lines.append("Attack: "+str(attack))
    lines.append("Defense: "+str(defense))
    lines.append("Regen: "+str(regen))
    lines.append("Health: "+str(health))
    lines.append("Gold: "+str(gold))
    lines.append("Room number: "+str(current_room_number))

    lines.append("Description length: "+str(description_length))
    lines.append("Description: "+str(description))
    send_name = name+'\x00'*(32-len(name))
    for i in lines:
        print(i)
    print("\n")
    header =pack('<B'+ '32s'+'B'+'H'*3+'H'+'H'*3,10,bytes(send_name,'ascii'),flags,attack,defense,regen,health,gold,current_room_number,description_length) 
    body = description.encode('ascii')
    # need try and except?
    client_socket.sendall(header)
    client_socket.sendall(body)

def Character(client_socket,characters,player_name):
    name = player_name   
    if characters.get(name,None) == None:
	    # Error(client_socket,1)
	    return
    attack = characters[name].attack
    defense = characters[name].defense
    regen = characters[name].regen
    health = characters[name].health
    gold = characters[name].gold
    current_room_number = characters[name].room_number
    description_length = characters[name].description_length
    description = characters[name].description
    
    flags = characters[name].flags
    
    lines = []
    lines.append("Name: "+str(name))
    lines.append("Flags: "+str(flags))
    lines.append("Attack: "+str(attack))
    lines.append("Defense: "+str(defense))
    lines.append("Regen: "+str(regen))
    lines.append("Health: "+str(health))
    lines.append("Gold: "+str(gold))
    lines.append("Room number: "+str(current_room_number))

    lines.append("Description length: "+str(description_length))
    lines.append("Description: "+str(description))
    send_name = name+'\x00'*(32-len(name))
    print(send_name)
    print(flags)
    print(attack)
    print(defense)
    print(defense)
    print(regen)
    print(health)
    print(gold)
    print(current_room_number)
    print(description_length)
    header =pack('<b'+ '32s'+'B'+'H'*3+'h'+'H'*3,10,bytes(send_name,'ascii'),flags,attack,defense,regen,health,gold,current_room_number,description_length) 
    body = description.encode('ascii')
    print("Header:")
    print("Header: "+str(header))
    print(header)
    print("Size")
    print(len(header))
    print(body)
    SendHeaderBody(client_socket,header,body)
    for i in lines:
        print(i)
    print("\n")


def SendHeaderBody(socket,header,body):
	try:
		socket.sendall(header)
	except SocketError as e:
		if e.errno == errno.ECONNRESET:
			raise
		elif e.errno == errno.EPIPE:
			raise
	try:
		socket.sendall(body)
	except SocketError as e:
		if e.errno == errno.ECONNRESET:
			raise
		elif e.errno == errno.EPIPE:
			raise

def Version(data):
    # Type = str(data[0])
    i = 0
    majorVersion = str(data[i])
    minorVersion = str(data[i+1])
    size = str(struct.unpack("H", data[i+2:i+4])[0])
    exts= str(struct.unpack("b", data[-1:])[0])
    line = [
        # "Type: " + Type,
        "Lurk Version: " + majorVersion + "." + minorVersion,
        "Size of the list of extensions:" + size,
        "List of extensions: "+ exts
        ]
    return line

def Error(client_socket, data):
    i = 0
    code = data
    options = {
         0:"Other (not covered by any below error code)",
         1:"Bad room. Attempt to change to an inappropriate room",
         2:"Player Exists. Attempt to create a player that already exists.",
         3:"Bad Monster. Attempt to loot a nonexistent or not present monster.",
         4:"Stat error. Caused by setting inappropriate player stats.",
         5:"Not Ready. Caused by attempting an action too early, for example changing rooms before sending START or CHARACTER.",
         6:"No target. Sent in response to attempts to loot nonexistent players, fight players in different rooms, etc.",
         7:"No fight. Sent if the requested fight cannot happen for other reasons (i.e. no live monsters in room)",
         8:"No player vs. player combat on the server. Servers do not have to support player-vs-player combat.",
	10: "Character Setting Up Error, you can only have 100 stat points to use",
	15: "You have already logged in.",
	16: "No connection, call the manager if like to set up a new room.",
	17: "You haven't logged in yet.",
	18: "Wrong sender.",
	19: "The player you are looking for is either offline or not exist.",
	20: "There is no monster in this room.",
	21: "Are you sure you in the room or anyother in this room?",
	22: "The character is already dead. Please setup a new one!",
	23: "This player is still alive, go away!",
	24: "Reward should give to the player who killed the monster.",
	25: "Your health is too high! Not Allowed!",
	26: "You are already in the room.",
	27: "Would like to send yourself a message?",
	29: "Player is not in this room or non-exist.",
	30: "The body is either claimed by somebody else, or player is not exist.",
	31: "You already cliamed the monster or the reward is for somebody else.",
	32: "Careful! Maybe, just maybe, the monster is still alive, be careful.",
	33: "The player is still alive.",
	34: "The body you are trying to look is not in the room, turn around.",
	35: "There is no gold on this body, body will be cleaned up later."
	
         }
    description = options[data]
    length = len(description)
    lines = []
    lines.append("Code: "+ str(code))
    lines.append("Error Message Length: "+str(length))
    lines.append("Error Description: "+ description)
    print("Reminder for "+str(live_player_list.get(client_socket,"I have not logge in I think")))
    print("Type: 7 (ERROR)")
    for i in lines:
        print(i)
    print("\n")
    header = pack('bbh',7,code,length)
    body = description.encode('ascii')
    SendHeaderBody(client_socket,header,body)
    # client_socket.sendall(header)
    # client_socket.sendall(body)
    return 

def RecvElement(client_socket):
	word = b''
	while True:
		char = client_socket.recv(1)
		if (char == b'\x00' or char == b'') and word == b'':
			continue
		elif char == b'\x00' or char == b'':
			break
		word += char
	print("break word: "+str(word))
	return word

def DefineLongString(socket,length):
	data = socket.recv(length,Socket.MSG_WAITALL)
	print("Data(LongString): "+str(data))
	new_data = ""
	for i in data:
		print(type(i))
		if i <= 0 or i >= 128:
			break
		new_data += chr(i)
	print("Word: "+str(new_data))
	return new_data # this gonna return a string
	
def DefineInt(socket,length):
	data = socket.recv(length,Socket.MSG_WAITALL)
	print("Data(int): "+str(data))
	integer = 0
	if length == 1:
		integer = int(str(unpack("B",data[:1])[0]))
		print("I am one byte with: "+str(integer))
	elif length == 2:
		integer = int(str(unpack("H",data[:2])[0]))
		print("I am two bytes with: "+str(integer))
	print("Integer: "+str(integer)+"From: "+str(socket))
	return integer

def Server_Character(client_socket,characters):
#	    Error(client_socket,15)
#	    return True
    # format = "b"*32+"B"+"H"*3+"h"+"H"*3
	mutex = threading.Lock()
	mutex.acquire()
	name = DefineLongString(client_socket,32)
	if name == "":
		name = "Unknown, name is not given."
	flags =DefineInt(client_socket,1)
	print(flags)
	flags = int('10001000',2) # reset flags
	attack =DefineInt(client_socket,2)
	defense =DefineInt(client_socket,2)
	regen =DefineInt(client_socket,2)
	health =DefineInt(client_socket,2)
	gold =DefineInt(client_socket,2)
	gold = 0
	current_room_number =DefineInt(client_socket,2)
	description_length =DefineInt(client_socket,2)
	print("Description length(type): "+str(type(description_length)))
	print("Description length: "+ str(description_length))
	description = DefineLongString(client_socket,description_length)
	print("description")
	print(description)
	description_length = len(description)
	if current_room_number < 0 or current_room_number > 10:
		current_room_number = 0
	exist = False
	if (characters.get(name,None) != None and characters != None):
		flags = characters[name].flags
		print(flags)
		print("Name: "+name)
		for socket in live_player_list:
			if live_player_list[socket] == name:
				if socket == client_socket:
				#	Error(socket,15) # can switch to message type to notice the client or just being mute
					break
				description = "Someone is trying to take your characters, you are protected!"
				length = len(description)
				recipient = name
				sender = "Server"
				message_detail = Message_unit(1,length,recipient,sender,description)
				
				SendMessage(socket,message_detail)
				Error(client_socket,2)
				mutex.release()
				return
		attack = characters[name].attack
		defense = characters[name].defense
		regen = characters[name].regen
		health = characters[name].health
		gold = characters[name].gold
		current_room_number = characters[name].room_number
		description_length = characters[name].description_length
		description = characters[name].description
		exist = True
		characters[name].login = True
		print("Welcome back!"+str(type(name))+ " "+ str(name))

	initPointsfromclient = attack + defense + regen	
	if(initPointsfromclient > 100):
		Error(client_socket, 4) # 4 is the error code
		mutex.release()
		return
	elif(health > 100 or health <= 0):
		# Error(client_socket,25)
		health = 100
	for i in range(len(rooms)):
		if rooms[i].room_number == current_room_number:
			rooms[i].addPlayer(name)
			print("You are now in room "+str(i))
			found = 1
			break
	Accept(client_socket,10)
	if current_room_number >=11 or current_room_number < 0:
		Error(client_socket,1)
		description = "You still in, you have been seated in the default room."
		current_room_number = 0
		recipient = name
		sender = "Server"
		message_detail = Message_unit(1,length,recipient,sender,description)
		SendMessage(client_socket,message_detail)
		
	if exist == False:
		characters[name] = Character_unit(10,name,flags,attack,defense, regen, health, gold, current_room_number, description_length, description)
		characters[name].login = True
		
	# unique login add player to live player plist
	live_player_list[client_socket] = name
	check_message = False
	for i in range(len(message_array)):
		if message_array[i].recipient_name == name:
			if message_array[i].sender_name == "Server":
				continue
			SendMessage(client_socket,message_array[i])
			check_message = True
		if check_message == True:
			print(name + ": checked the mailbox(send mesage checked)")
			print("\n")
	flags = characters[name].flags
	lines = []
	lines.append("Type: 10 (CHARACTER)")
	lines.append("Name: "+str(name))
	lines.append("Flags: "+str(flags))
	lines.append("Attack: "+str(attack))
	lines.append("Defense: "+str(defense))
	lines.append("Regen: "+str(regen))
	lines.append("Health: "+str(health))
	lines.append("Gold: "+str(gold))
	lines.append("Room number: "+str(current_room_number))
	
	lines.append("Description length: "+str(description_length))
	lines.append("Description: "+str(description))
	send_name = name+'\x00'*(32-len(name))
	header =pack('<B'+ '32s'+'B'+'H'*3+'h'+'H'*3,10,bytes(
				send_name,'ascii'),
				flags,
				attack,
				defense,
				regen,
				health,
				gold,
				current_room_number,
				description_length
				) 
	body = description.encode('ascii')
	client_socket.sendall(header)
	client_socket.sendall(body)
	print("Server Character: Header and body sent!")
	for i in lines:
		print(i)
		print("\n")
	message = name+" has joinged the game."
	message_length = len(message)
	message_detail = Message_unit(1,message_length,name,"Server",message)
#	SendMessage(client_socket,message_detail)
	print("live_player_list size: "+str(len(live_player_list)))
	tmp_list = {**live_player_list}
	for socket in tmp_list:
		print("Name: "+str(live_player_list.get(socket,None)))
		print(characters[name].login)
	tmp_list = {}
	tmp_list = {**live_player_list}
	for socket in tmp_list:
		name1 = live_player_list.get(socket,None)
		name2 = live_player_list.get(client_socket,None)
		print("Name to everyone in the room except me: "+name1)
		if name1 == None:
			continue
		if name1 == name and name2 != None:
			continue
		print("Name in the room: "+str(live_player_list.get(socket,None)))
		if characters.get(live_player_list.get(socket,None)) == None:
			continue
		print("Character: "+str(characters[live_player_list.get(socket,None)]))
		print("Socket: "+str(socket))
		print("Message Detail: "+ str(message_detail))
		print("Message Content: "+str(message_detail.sender_content))
#		SendMessage(socket,message_detail)
		Character(socket,characters,name)
	print("End of Server Character")
	mutex.release()

# pick up start here################
def Start(client_socket,characters):

	mutex = threading.Lock()
	mutex.acquire()
	name = live_player_list.get(client_socket,None)
	if name == None:
		Error(client_socket,17)
		mutex.release()
		return
		#prevent start since it is already started
	if characters[name].start_status == True:
		mutex.release()
		return

	if bin(characters[name].flags)[-5] == "0" and bin(characters[name].flags)[-7] == "0":
		characters[name].flags += int('1010000',2)
	print("Name: " +str(name))
	Character(client_socket,characters,name)
	Room(client_socket,characters)
	current_room_number = characters[name].room_number # for notice players in the room
	Check_Room_Player_List(client_socket,rooms,name,current_room_number,characters)
	print("Room Checkted!")
	characters[name].start_status = True
	# send notice to the other players in this room
	for player_name in rooms[characters[name].room_number].players:
		if player_name != name:
			if live_monster_list.get(player_name, None) == None:
				Character(client_socket,characters,player_name)
				tmp_list = {** live_player_list}
				for the_socket in tmp_list:
					if tmp_list[the_socket] == player_name and live_player_list.get(the_socket,None) != None:
						content = "Player "+ name + " has left this room."
						message_length = len(content)
						sender_name ="Server"
						recipient_name = live_player_list[the_socket]
						message_detail = Message_unit(1,message_length,recipient_name,sender_name,content)
						# SendMessage(the_socket,message_detail)
						Character(the_socket,characters,name)
						# Character(client_socket,characters,name)
	Connection(client_socket,current_room_number)
	mutex.release()


def Check_Room_Player_List(client_socket,rooms,character_name,current_room_number,characters):
	mutex = threading.Lock()
	mutex.acquire()
	room_player_list = []
	room_player_list = rooms[current_room_number].players
	for player_name in room_player_list:
		print("Player: "+str(player_name))
		if live_monster_list.get(player_name,None)!=None:
			monster_name = live_monster_list[player_name].name
			Monster(client_socket,monster_name)
		elif player_name != character_name and characters.get(player_name,None) != None:
			name = player_name
			# add if check later if needed
			if characters.get(name,None) == None:
				# Error(client_socket,29)
				continue
			flags = characters[player_name].flags 
			attack = characters[player_name].attack
			defense = characters[player_name].defense
			regen = characters[player_name].regen
			health = characters[player_name].health
			gold = characters[player_name].gold
			current_room_number = characters[player_name].room_number
			description_length = characters[player_name].description_length
			description = characters[player_name].description
			send_name = name+'\x00'*(32-len(name))
			header =pack('<b'+ '32s'+'B'+'H'*3+'h'+'H'*3,10,bytes(send_name,'ascii'),flags,attack,defense,regen,health,gold,current_room_number,description_length) 
			body = description.encode('ascii')
			client_socket.sendall(header)
			client_socket.sendall(body)
	mutex.release()
		
def PlayerSocket(player_name):
	for socket in live_player_socket:
		if live_player_socket.get(socket,None) == player_name:
			return socket
	return None


def EnterCenter(data,characters):
	if int(data) == 15:
		Old_Character()
	elif int(data) == 16:
		LivePlayerList(characters)
	elif int(data) == 17:
		MonsterList()
	# elif int(data) == 3:
	# dont know about the init a fight	

def MonsterList():
	for monster in live_monster_list:
		print("Monster name: " + monster + "Room number: " + str(live_monster_list[monster].room_number))

def LivePlayerList(characters):
	for socket in live_player_list:
		name = live_player_list[socket]
		room_number = characters[name].room_number
		print("Player: "+name+" Room number: "+ str(room_number) +" socket: "+str(socket))


def Old_Character():
    Type = 10 ## 1byte
    Name = "Name:"
    name = str(input("Name: "))

    # flags
    Flags = "Flags:"
    flags = int('11111000',2)

    # attack
    Attack = "Attack:"
    attack = int(input("Attack: "))
    # defense
    Defense = "Defense:"
    defense = int(input("Defense: "))
    
    #regen
    Regen = "Regen:"
    regen = int(input("Regen: "))
    # health
    Health = "Health:"
    health = int(input("Health: "))
    
    # gold
    Glod = "Gold:"
    glod = int(input("Gold: "))
    
    # currentRoomNumber
    Room_number = "Room Number:"
    room_number = int(input("0-10\nRoom number: "))
    
    # playerDescription
    Description = "Description:"
    description = str(input("Description: "))
    
    # playerDescription = str(unpack('b'*length,data)[0])


    #set player descirption length
    descriptionLength = len(description)

    # name = name.encode('ascii')
    live_monster_list[name] = Monster_unit(10,name,flags,attack,defense,regen,health,gold,room_number,descriptionLength,description)
    rooms[room_number].addPlayer(name)

def Accept(client_socket,accept_type):
    lines = []
    lines.append("Type: 8 (ACCEPT)")
    lines.append("Accepted message: "+str(accept_type))
    for i in lines:
	    print(i)
    print("\n")
    message = pack('2b',8,accept_type)
    client_socket.sendall(message)
    return lines


def Room(client_socket,characters):
    lines = []
    character = characters[live_player_list[client_socket]]
    send_type = 9
    current_room_number = character.room_number
    client_room_number = current_room_number
    client_room_name = rooms[current_room_number].room_name 
    client_room_name_tosend = rooms[current_room_number].room_name
    # '\x00'*(32-len(rooms[current_room_number].room_name)) 
    room_description_length = rooms[current_room_number].room_description_length
    room_description = rooms[current_room_number].room_description
    header = pack('<b'+'H'+'32s'+'H',send_type,client_room_number,bytes(client_room_name_tosend,'ascii') + b'\x00'*(32 - len(rooms[current_room_number].room_name)) ,room_description_length)
    body = room_description.encode('ascii')
    # SendHeaderBody(client_socket,header,body)
    client_socket.sendall(header)
    client_socket.sendall(body)
    lines.append("Type: 9 (ROOM)")
    lines.append("Room number: "+str(client_room_number))
    lines.append("Room name: "+str(client_room_name))
    lines.append("Room description length: " + str(room_description_length))
    lines.append("Room description: "+str(room_description))
    for i in lines:
        print (i)
    print("\n")


def Message(client_socket):
	mutex = threading.Lock()
	mutex.acquire()
	print("Begining of Message###########################")
	lines = []
	line_0_recv_type = "Type: 1 (Message)"
	lines.append(line_0_recv_type)
	length_size = DefineInt(client_socket,2)
	line_1_length_size = "Message Length: " + str(length_size)
	lines.append(line_1_length_size)

	recipient_name = DefineLongString(client_socket,32)

	print("recipient name: "+ str(recipient_name))
	print("length of the name: " + str(len(recipient_name)))
	if len(recipient_name) == 0:
		recipient_name = "Server"
	line_2_recipient_name = "Recipient name: " + recipient_name
	lines.append(line_2_recipient_name)

	sender_name = DefineLongString(client_socket,32)
	line_3_sender_name = "Sender name: " + sender_name
	lines.append(line_3_sender_name)

	message_description = DefineLongString(client_socket,length_size)
	print("Message from "+ str(sender_name) + ": "+str(message_description))
#	reset the size of message_description
	length_size = len(message_description)
	lines.append("Message: "+message_description)
	message_detail = Message_unit(1,length_size,recipient_name,sender_name,message_description)
	print("Server record:"+live_player_list[client_socket])
	for line in lines:
		print( line)
		print("\n")
	if live_player_list.get(client_socket,None) == None:
		Error(client_socket,17)
		mutex.release()
		return
	send_status = False
	for the_socket in live_player_list:
		if recipient_name == sender_name:
			Error(client_socket,27)
			mutex.release()
			return


 
		elif live_player_list[the_socket] == recipient_name:
			print("Befor check: "+sender_name)
			print(recipient_name)
			SendMessage(the_socket,message_detail)
			send_status = True
			message_array.append(message_detail)
			break
	if send_status == False:
		if recipient_name == "Server":
			Accept(client_socket,1)
			tmp_list = {**live_player_list}
			for socket in tmp_list:
				if tmp_list.get(socket,None) == None:
					continue
				if tmp_list.get(socket,None) == sender_name:
					continue
				SendMessage(socket,message_detail)
			mutex.release()
				
			return
		print("Message Sent Failed.")
		Error(client_socket,19)
		mutex.release()
		return

def SendMessage(socket,message_detail):
	message_length = message_detail.message_length
	recipient_name = message_detail.recipient_name
	sender_name = message_detail.sender_name
	message = message_detail.sender_content
	header = pack("<bH"+"32s"+"32s",1,message_length,bytes(recipient_name+"\x00"*(32-len(recipient_name)),'ascii'),bytes(sender_name+"\x00"*(32-len(sender_name)),'ascii'))
	body = message.encode('ascii')
	# print(str(message_length)+"\n"+str(recipient_name)+"\n"+str(sender_name)+"\n"+str(message)+"\n")
	print("Header: "+str(header))
	print("Body: "+str(body))
	print("Message send!")
	print("\n")
	try:
		socket.sendall(header)
	except SocketError as e:
		if e.errno == errno.ECONNRESET:
			raise
		elif e.errno != errno.EPIPE:
			riase
		pass
	try:
		socket.sendall(body)
	except SocketError as e:
		if e.errno == errno.ECONNRESET:
			print("Error message received!")
			raise
def MessageDescription(data):
    actu_message = data.decode('ascii').rstrip('\x00').lstrip('\x00')
    return actu_message




def Leave():
    Type = 12
    signal = pack('b',Type)
    return signal

def Connection(client_socket, current_room_number):
    
    lines = []
    nextroom = current_room_number + 1
    if current_room_number >= 10:
	    name = str(live_player_list[client_socket])
	    print("Last room reached: "+ name)
	    description = "You are at the top floor which is the last room."
	    length = len(description)
	    recipient = name
	    sender = "Server"
	    message_detail = Message_unit(1,length,recipient,sender,description)
	    SendMessage(client_socket,message_detail)
	    nextroom = 0

    lines.append("Type: 13 (CONNECTION)")
    lines.append("Room number: "+str(nextroom))
    lines.append("Room name: "+str(rooms[nextroom].room_name))
    description = ("You are now in room "+ str(rooms[nextroom].room_name) +". This room is great!")
    lines.append("Room description length: "+str(len(description)))
    lines.append("Room description: "+description)
    for line in lines:
	    print(line)
    print("\n")
    
    lines = []
    client_room_number = nextroom
    client_room_name_tosend = rooms[nextroom].room_name+"\x00"*(32-len(rooms[nextroom].room_name)) 
    room_description_length = len(description)
    room_description = description

    print(room_description_length)

    header = pack("<b"+"H"+"32s"+ "H",13,nextroom,bytes(client_room_name_tosend,'ascii'),room_description_length)
    body = room_description.encode('ascii')
    print(header)
    client_socket.sendall(header)
    client_socket.sendall(body)
    
