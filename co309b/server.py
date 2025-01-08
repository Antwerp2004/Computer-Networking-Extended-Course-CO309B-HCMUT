import socket
from _thread import *
import pickle
from game import Game
from helper import HOST, PORT
from threading import Lock

lock = Lock()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse the address

try:
    s.bind((HOST, PORT))
    s.listen(2)  # Listen for up to 2 simultaneous connections
    print(f"Server started on {HOST}:{PORT}")
except socket.error as e:
    print(f"Socket error: {e}")
    exit(1)
print("Waiting for a connection, Server Started")

connected = set()
games = {}
idCount = 0

def threaded_client(conn, p, gameId):
    global idCount
    conn.send(str.encode(str(p)))

    while True:
        try:
            data = conn.recv(4096).decode()
        
            if gameId in games:
                game = games[gameId]
                
                if not data:
                    break
                else:
                    if data == "reset":
                        game.resetWent()
                    elif data != "get":
                        game.play(p, data)
                        
                    conn.sendall(pickle.dumps(game))
            else:
                break
        except:
            break

    print("Lost Connection")
    try:
        del games[gameId]
        print("Closing game", gameId)
    except:
        pass
    idCount -= 1
    conn.close()
                    

while True:
    conn, addr = s.accept()
    print("Connect to: ", addr)
    
    idCount += 1
    p = 0
    gameId = (idCount - 1)//2
    if idCount % 2 == 1:
        games[gameId] = Game(gameId)
        print("Creating a new game...")
    else:
        games[gameId].ready = True
        p = 1
        
    start_new_thread(threaded_client, (conn, p, gameId))