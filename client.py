from os import stat
import socket
import threading
from colorama import init
from termcolor import colored


HEADER = 100
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
#IP = "koolkunal-31091.portmap.io"
IP = "192.168.56.1"
#PORT = 31091
PORT = 5050

messages = []

colors = {
    0: "green",
    1: "magenta",
    2: "blue",
    3: "yellow",
    4: "cyan"
}

iptocolor = {}


def getColor(addr):
    addr = addr[1:-1]
    if addr == "Daddy":
        return "red"
    addr = addr.split(",")[1]

    if addr not in iptocolor:
        ind = int(addr) % len(colors)
        while(ind in iptocolor.values()):
            ind = (ind+1) % len(colors)
        iptocolor[addr] = ind

    return colors[iptocolor[addr]]


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


def recieve(conn, messages):
    while True:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if len(msg_length) == 0:
                continue

            msg = conn.recv(int(msg_length)).decode(FORMAT)
            messages.append(msg)
            unpack_msg = msg.split("//Divider//")
            col = getColor(unpack_msg[0])
            print('', end='\r')
            print(colored(unpack_msg[1], col), end=' ')
            print(unpack_msg[2], end="\n")
            print(">>>", end=' ')
        except:
            break


def uploadFile(path):
    filename = path.split('/')[-1]

    # requesting server to accept file upload
    send("//FILE UPLOAD//")

    # waiting for the confirmation
    FilePort = 9999
    Fileconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        Fileconn.connect((IP, FilePort))
    except:
        return "Server denied to Upload File."
    # reading file
    try:
        file = open(path, 'rb')
        bytestream = file.read()
    except:
        Fileconn.close()
        return "No Such File!"

    # sending the length of file
    # print(len(bytestream))
    Fileconn.send(str(len(bytestream)).encode())

    # waiting for confirmation
    msg = Fileconn.recv(1000).decode()
    if msg != "//Length Recieved//":
        Fileconn.close()
        return "Server denied to Upload File."
    #print("length sent")

    # sending filename to the client
    Fileconn.send(filename.encode())

    # waiting for the confirmation from the sever for the filename recieved
    msg = Fileconn.recv(1000).decode()
    if msg != "//Name Recieved//":
        Fileconn.close()
        return "Server denied to Upload File."
    #print("name sent")

    # sending file to the client
    Fileconn.send(bytestream)

    # waiting for the confirmation from the server for the file recieved
    msg = Fileconn.recv(1000).decode()
    if msg != "//File Recieved//":
        Fileconn.close()
        return "Server denied to Upload File."

    return "File uploaded Successfully."


def downloadFile(filename):
    send("//FILE DOWNLOAD//")
    FilePort = 6969
    Fileconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        Fileconn.connect((IP, FilePort))
    except:
        return "Unable to connect"

    Fileconn.send(filename.encode())

    msg = Fileconn.recv(1000).decode()

    if msg != "//FILE FOUND//":
        Fileconn.close()
        return "No such File"

    Fileconn.send("//SEND LENGTH//".encode())
    msg = Fileconn.recv(1000).decode()
    Length = int(msg)

    Fileconn.send("//LENGTH RECIEVED//".encode())

    data = b''
    while len(data) < Length:
        data += Fileconn.recv(10000000)

    Fileconn.send("//FILE RECIEVED//".encode())

    ofile = open(filename, 'wb')
    ofile.write(data)
    ofile.close()
    return "File Downloaded Successfully"


UPLOAD_FILE = 'up'
LIST_FILES = 'ls'
DOWNLOAD_FILE = 'down'


def start():
    init()
    global client

    while True:
        name = input("enter your name:")
        if not len(name):
            print(colored('---[SYSTEM]---', 'red'), end=' ')
            print("Invalid name")
        else:
            break

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))
    client.send(name.encode())
    connected = True
    thread = threading.Thread(target=recieve, args=(client, messages))
    thread.daemon = True
    thread.start()
    print(">>>", end=' ')
    while connected:
        x = input()
        if not thread.isAlive():
            print(colored('---[SYSTEM]---', 'red'), end=' ')
            print("Connection lost!")
            break

        if len(x) == 0:
            print(">>>", end=' ')

        elif(x[0] == '!'):
            cmd = x[1:]
            cmd = cmd.split()
            # print(cmd)
            if len(cmd) == 2 and cmd[0] == UPLOAD_FILE:
                status = uploadFile(cmd[1])
                print('', end='\r')
                print(colored('---[SYSTEM]---', 'red'), end=' ')
                print(status)
                print(">>>", end=' ')

            elif len(cmd) == 1 and cmd[0] == LIST_FILES:
                send("//LIST FILES//")

            elif len(cmd) == 2 and cmd[0] == DOWNLOAD_FILE:
                status = downloadFile(cmd[1])
                print(colored('---[SYSTEM]---', 'red'), end=' ')
                print(status)
                print(">>>", end=' ')
            else:
                send(x)

        else:
            send(x)


start()
