import socket, threading
from tkinter import *
from tkinter import messagebox
import nltk, random
from nltk.corpus import movie_reviews
from nltk.corpus import stopwords

""" Machine Learning Part """
# Create a Document
documents = [(list(movie_reviews.words(fileid)), category)
             for category in movie_reviews.categories()
             for fileid in movie_reviews.fileids(category)]
# Suffle the document for random data everytime
random.shuffle(documents)

all_words = []
stop_words = stopwords.words("english")

# Create Sample data for trainig the Server
for w in movie_reviews.words():
    if w.lower() not in stop_words:
        all_words.append(w.lower())
all_words = nltk.FreqDist(all_words)
word_features = list(all_words.keys())[:3000]

""" Feature Selection Part """


def find_features(document):
    words = set(document)
    features = {}
    for w in word_features:
        features[w] = (w in words)
    return features


# Checking the feature selection part from a given database from nltk library with the below "print" command
# print((find_features(movie_reviews.words('neg/cv000_29416.txt'))))
""" Get the features to create a tuple """
featuresets = [(find_features(rev), category) for (rev, category) in documents]
# set that we'll train our classifier with
training_set = featuresets[:1900]
# set that we'll test against.
testing_set = featuresets[1900:]
# Create the classifier (We use Naive Bayes)
classifier = nltk.NaiveBayesClassifier.train(training_set)
# Testing the accuracy of our classifier/algorithm
print("Classifier accuracy percent:", (nltk.classify.accuracy(classifier, testing_set)) * 100)
classifier.show_most_informative_features(20)

# SERVER Configuration
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
    """ Old Code """
    # print("Words from text file........................................")
    # file = open('word_list.txt', 'r')
    # data = file.read()
    # content = data.rstrip()
    # global final_list
    # final_list = content.split()
    # file.close()
    """ New Code """
    data = nltk.data.load('word_list.txt')
    global final_list
    final_list = nltk.word_tokenize(data)
    print("Words from text file........................................")


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
            result = messagebox.askyesno("Warning Box", "You have a slang words: " + new_msg)
            if result == True:
                print("Ok")
            # messagebox.askyesnocancel('Warn Box', 'You have a slang word.' + new_msg + '\nContinue?')
        break


while True:
    # data_read()
    conn, addr = s.accept()
    conn.send("".encode("utf8"))
    print("%s:%s has connected." % addr)
    addresses[conn] = addr
    threading.Thread(target=handle_client, args=(conn,)).start()
