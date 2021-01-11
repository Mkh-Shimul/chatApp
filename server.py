import socket, threading
from tkinter import *
from tkinter import messagebox


HOST = socket.gethostname()
PORT = 4000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
clients = {}
addresses = {}
print(HOST)
print("Server is ready...")


def data_read():
    print("Word from text file........................................")
    file = open('word_list.txt', 'r')
    data = file.read()
    content = data.rstrip()
    global final_list
    final_list = content.split()
    file.close()


serverRunning = True


# def popupError(s):
#     popupRoot = Tk()
#     popupRoot.after(2000, exit)
#     popupButton = Button(popupRoot, text = s, font = ("Verdana", 12), bg = "red", command = exit)
#     popupButton.pack()
#     popupRoot.geometry('400x50+700+500')
#     popupRoot.mainloop()


def handle_client(conn):
    try:
        data = conn.recv(1024).decode('utf8')
        welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % data
        conn.send(bytes(welcome, "utf8"))
        msg = "%s has joined the chat" % data
        broadcast(bytes(msg, "utf8"))
        clients[conn] = data
        while True:
            found = False
            response = 'Number of People Online\n'
            msg1 = conn.recv(1024)
            if msg1 != bytes("{quit}", "utf8"):
                broadcast(msg1, data + ": ")

            else:
                conn.send(bytes("{quit}", "utf8"))
                conn.close()
                del clients[conn]
                broadcast(bytes("%s has left the chat." % data, "utf8"))
                break
    except:
        print("%s has left the chat." % data)


def broadcast(msg, prefix=""):
    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)
    new_msg = msg.decode("utf8")
    # # hide main window
    root = Tk()
    root.withdraw()
    for i in range(len(final_list)):
        if new_msg == final_list[i]:
            # messagebox.askyesno("Warning Box", "You have a slang words: " + new_msg)
            messagebox.showinfo('MONEY', 'MORE MONEY')
        break


while True:
    data_read()
    conn, addr = s.accept()
    conn.send("".encode("utf8"))
    print("%s:%s has connected." % addr)
    addresses[conn] = addr
    threading.Thread(target=handle_client, args=(conn,)).start()
