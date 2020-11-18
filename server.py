import socket
import threading
import os

HEADER = 100
host = ""
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, PORT))
messages = []
connections = {}

#uploaded_files = []



def send(conn, msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)


def updateStream(msg, specific_conn = None):
    if specific_conn == None:
        for conn in connections.keys():
            try:
                send(conn, msg)
            except Exception as e:
                print(e)
    else:
        try:
            send(specific_conn, msg)
        except Exception as e:
            print(e)
            

def getFile(conn, addr):
    FilePort = 9999
    fileServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fileServer.bind(("", FilePort))
    Fileconn = None
    try:
        fileServer.listen()
        Fileconn, Fileaddr = fileServer.accept()
        print("[FILE TRANSFER CONNECTION ESTABLISHED]",
              "From", addr, "side at", Fileaddr)
        fileLength = Fileconn.recv(1000)
        fileLength = int(fileLength.decode())

        Fileconn.send("//Length Recieved//".encode())

        filename = Fileconn.recv(1000).decode()
        fileName = "cache/" + filename

        Fileconn.send("//Name Recieved//".encode())

        print("[ACCEIPTING FILE]", addr, "is sending file",
              filename, "of size", fileLength, "bytes")

        data = b''
        while len(data) < fileLength:
            data += Fileconn.recv(10000000)

        Fileconn.send("//File Recieved//".encode())

        ofile = open(fileName, 'wb')
        ofile.write(data)
        ofile.close()

        print('[FILE UPLOAD SUCCESSFULL]', filename,
              "was successfully retrieved")
        
        head_msg = "(Daddy)" + "//Divider//" + "---[SYSTEM]---"
        body = connections[conn]  + " uploaded file named " + filename
        pack_msg = head_msg + '//Divider//' + body
        updateStream(pack_msg)

    except Exception as e:
        print(e)
    

def sendFile(addr):
    FilePort = 6969
    FileServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    FileServer.bind(("", FilePort))
    FileServer.listen()
    Fileconn , Fileaddr = FileServer.accept()
    print("[FILE TRANSFER CONNECTION ESTABLISHED]",
              "From", addr, "side at", Fileaddr)
    filename = Fileconn.recv(1000).decode()
    filepath = "./cache/" + filename
    ifile = None
    try:
        ifile = open(filepath,'rb')
        Fileconn.send("//FILE FOUND//".encode())
    except:
        Fileconn.send("//FILE NOT FOUND//".encode())
        return
    print("[SENDING] sending", filename, "to", addr)
    msg = Fileconn.recv(1000).decode()
    if msg != "//SEND LENGTH//":
        return
    bytestream = ifile.read()

    Fileconn.send(str(len(bytestream)).encode())

    msg = Fileconn.recv(1000).decode()
    if msg != "//LENGTH RECIEVED//":
        print("failed-1")
        return
    
    Fileconn.send(bytestream)

    msg = Fileconn.recv(1000).decode()

    if msg != "//FILE RECIEVED//":
        print('[FAILED] unable to send file')
    else:
        print('[SUCCESS] file successfully sent')




def listFiles(conn):
    file_names = ""
    uploaded_files = os.listdir('./cache')
    if uploaded_files == []:
        file_names = "\t\tNo Files\n"
    else:
        for names in uploaded_files:
            file_names += "\t\t" + names + "\n"
    head_msg = "Files on server:\n"
    pack_msg = "(Daddy)" + "//Divider//" + "---[SYSTEM]---" + "//Divider//" + head_msg + file_names
    updateStream(pack_msg, specific_conn=conn)

def handle_client(conn, addr):
    UPLOAD = '//FILE UPLOAD//'
    LIST_FILES = '//LIST FILES//'
    DOWNLOAD_FILE = "//FILE DOWNLOAD//"
    print(f"[NEW CONNECTION] {addr} connected.\n")
    connected = True
    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if(len(msg_length) == 0):
                continue
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == UPLOAD:
                filethread = threading.Thread(target=getFile, args=(conn,addr))
                filethread.daemon = True
                filethread.start()
            elif msg == LIST_FILES:
                listfilethread = threading.Thread(target=listFiles, args=(conn,))
                listfilethread.daemon = True
                listfilethread.start()
            elif msg == DOWNLOAD_FILE:
                filethread = threading.Thread(target=sendFile, args=(addr,))
                filethread.daemon = True
                filethread.start()
            else:
                print(connections[conn])
                pack_msg = "(" + str(addr[0]) + " , " + str(addr[1]) + ")" + \
                    "//Divider//" + connections[conn] + "//Divider//" + msg
                messages.append(pack_msg)
                updateStream(pack_msg)
                print(f"[{addr}] {msg}")
                if msg == DISCONNECT_MESSAGE:
                    connected = False
        except ConnectionResetError:
            connected = False

    print(f"[DISCONNECTED] {addr} disconnected!")
    conn.close()

def acceptClients():
    server.listen()
    print(f"[LISTENING] Server is listening on port: {PORT}")
    while True:
        # print(connections)
        conn, addr = server.accept()
        name = conn.recv(20480).decode()
        connections[conn] = name
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.daemon = True
        thread.start()

        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
def start_server():
    
    accepthread = threading.Thread(target=acceptClients)
    accepthread.daemon = True
    accepthread.start()
    while True:
        x = input()
        if(x=='quit'):
            break

    '''updatethread = threading.Thread(
        target=updateStream, args=(connections, messages, counting))
    updatethread.daemon = True
    updatethread.start()'''

    


print("[STARTING] Server is starting..")
start_server()
