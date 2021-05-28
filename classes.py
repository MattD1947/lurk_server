class Character_unit:
    def __init__(self, init_type, name, flags, attack, defense, regen, health, gold, room_number, description_length, description,*start_status):

	    self.init_type = init_type
	    self.name = name
	    self. flags = flags
	    self.attack = attack
	    self.defense = defense
	    self. regen = regen
	    self.health = health
	    self.gold = gold
	    self.room_number = room_number
	    self.description_length = description_length
	    self.description = description
	    self.start_status = False
	    self.death = False
	    self.login = True
	    self.lock = False
    def getName():
	    return name


class Room_unit:
    def __init__(self,init_type,room_number,room_name,room_description_length,room_description,*player):
        self.init_type = init_type
        self.room_number = room_number
        self.room_name = room_name
        self.room_description_length = room_description_length
        self.room_description = room_description
        self.players = []
    def addPlayer(self,player):
        self.players.append(player)

class Message_unit:
    def __init__(self, init_type, message_length, recipient_name, sender_name, sender_content):
        self.init_type = init_type
        self.message_length = message_length
        self.recipient_name = recipient_name
        self.sender_name = sender_name
        self.sender_content = sender_content


class Monster_unit:
    def __init__(self, init_type, name, flags, attack, defense, regen, health, gold, room_number, description_length, description,*start_status):

	    self.init_type = init_type
	    self.name = name
	    self. flags = flags
	    self.attack = attack
	    self.defense = defense
	    self. regen = regen
	    self.health = health
	    self.gold = gold
	    self.room_number = room_number
	    self.description_length = description_length
	    self.description = description
	    self.start_status = False
	    self.reward = ""
    def getName():
	    return name


	


