# lurk_server

lurk_server is a text-based MMORPG style game, including 14 types of message.

Protocol message begin with an 8-bit type, followed by 0 or more bytes of further information.
The amount of bytes to be read can be determined by the type, and in some cases a message length field further into the message. 
Messages are listed below by type. Notes:
  Variable-length text fields are sent without a null terminator.
  All numbers are sent little-endian. This makes things easy for x86 users at the expense of being unusual.
  Except as noted (health), all integer fields are unsigned.
  
Type: 1 (Message) -- send message to the other players
Type: 2 (Change room) -- change room from one to another
Type: 3 (Fight) -- start a fight in the room
Type: 4 (PVPFIGHT)(not supported yet) -- request a fight to a player or monster
Type: 5 (Loot) -- loot a body in the room
Type: 6 (Start) -- start playing game
Type: 7 (Error) -- send error message if any action wrongly happened
Type: 8 (Accept) -- send player accept message for action success
Type: 9 (Room) -- send player room info
Type: 10 (Character) -- send player character info like stat, health, gold, etc.
Type: 11 (Game) -- send game info to player
Type: 12 (Leave) -- receive from player and disconnect the player
Type: 13 (Connection) -- for next available room for the room the play is in
Type: 14 (Version) -- send lurk protocl version info

*To play the game may need a lurk protocl client
