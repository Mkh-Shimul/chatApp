import tkinter
import socket
import threading
from tkinter.messagebox import askyesno

# """ Machine Learning Part """
# # Create a Document

from nltk import ngrams
from nltk.corpus import stopwords
import string

stopwords_english = stopwords.words('english')


# clean words, i.e. remove stopwords and punctuation
def clean_words(words, stopwords_english):
    words_clean = []
    for word in words:
        word = word.lower()
        if word not in stopwords_english and word not in string.punctuation:
            words_clean.append(word)
    return words_clean


# feature extractor function for unigram
def bag_of_words(words):
    words_dictionary = dict([word, True] for word in words)
    return words_dictionary


# feature extractor function for ngrams (bigram)
def bag_of_ngrams(words, n=2):
    words_ng = []
    for item in iter(ngrams(words, n)):
        words_ng.append(item)
    words_dictionary = dict([word, True] for word in words_ng)
    return words_dictionary


from nltk.tokenize import word_tokenize

text = "It was a very good movie."
words = word_tokenize(text.lower())

# print("Words: ", words)

# print ("Bag of nGrams: ", bag_of_ngrams(words))
words_clean = clean_words(words, stopwords_english)
# print ("Clean Words: ", words_clean)

important_words = ['above', 'below', 'off', 'over', 'under', 'more', 'most', 'such', 'no', 'nor', 'not', 'only', 'so',
                   'than', 'too', 'very', 'just', 'but']

stopwords_english_for_bigrams = set(stopwords_english) - set(important_words)

words_clean_for_bigrams = clean_words(words, stopwords_english_for_bigrams)
# print("Clean Bigram Words: ", words_clean_for_bigrams)

unigram_features = bag_of_words(words_clean)
# print("Unigram Features: ", unigram_features)

bigram_features = bag_of_ngrams(words_clean_for_bigrams)
# print("Bigram Features: ", bigram_features)

all_features = unigram_features.copy()
all_features.update(bigram_features)
# print ("All Features: ", all_features)


def bag_of_all_words(words, n=2):
    words_clean = clean_words(words, stopwords_english)
    words_clean_for_bigrams = clean_words(words, stopwords_english_for_bigrams)

    unigram_features = bag_of_words(words_clean)
    bigram_features = bag_of_ngrams(words_clean_for_bigrams)

    all_features = unigram_features.copy()
    all_features.update(bigram_features)

    return all_features


# print("All words bag: ", bag_of_all_words(words))

from nltk.corpus import movie_reviews

pos_reviews = []
for fileid in movie_reviews.fileids('pos'):
    words = movie_reviews.words(fileid)
    pos_reviews.append(words)

neg_reviews = []
for fileid in movie_reviews.fileids('neg'):
    words = movie_reviews.words(fileid)
    neg_reviews.append(words)

# positive reviews feature set
pos_reviews_set = []
for words in pos_reviews:
    pos_reviews_set.append((bag_of_all_words(words), 'pos'))

# negative reviews feature set
neg_reviews_set = []
for words in neg_reviews:
    neg_reviews_set.append((bag_of_all_words(words), 'neg'))

# print(len(pos_reviews_set), len(neg_reviews_set))  # Output: (1000, 1000)

# radomize pos_reviews_set and neg_reviews_set
# doing so will output different accuracy result everytime we run the program
from random import shuffle

shuffle(pos_reviews_set)
shuffle(neg_reviews_set)

test_set = pos_reviews_set[:200] + neg_reviews_set[:200]
train_set = pos_reviews_set[200:] + neg_reviews_set[200:]

# print(len(test_set), len(train_set))  # Output: (400, 1600)

from nltk import classify
from nltk import NaiveBayesClassifier

classifier = NaiveBayesClassifier.train(train_set)

accuracy = classify.accuracy(classifier, test_set)
print("Accuracy is: ", accuracy*100)  # Output: 0.8025

# print(classifier.show_most_informative_features(10))




HOST = socket.gethostname()
PORT = 4000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = (HOST, PORT)


def echo_data(sock):
    while True:
        try:
            msg = sock.recv(1024).decode('utf8')

            from nltk.tokenize import word_tokenize
            from bnbphoneticparser import BengaliToBanglish, BanglishToBengali
            from textblob import TextBlob

            detect_lang = TextBlob(msg)

            if detect_lang.detect_language() == "bn":
                banglishTobengali = BanglishToBengali()
                bengaliTobanglish = BengaliToBanglish()
                if banglishTobengali:
                    new_data = banglishTobengali.parse(msg)
                else:
                    new_data = bengaliTobanglish.parse(msg)
                # msg_list.insert(tkinter.END, new_data)
                c = TextBlob(new_data)
                custom_review_new = c.translate(to='en')
                custom_review_tokens = word_tokenize(str(custom_review_new))
                custom_review_set = bag_of_all_words(custom_review_tokens)
                print(classifier.classify(custom_review_set))  # Output: neg
                # Negative review correctly classified as negative
                if classifier.classify(custom_review_set) == 'neg':
                    ans = askyesno("Warning Box", msg)
                    # print(ans)
                    if ans:
                        msg_list.insert(tkinter.END, msg)
                else:
                    msg_list.insert(tkinter.END, msg)
                # print("Bengali")
            else:
                custom_review = msg
                custom_review_tokens = word_tokenize(custom_review)
                custom_review_set = bag_of_all_words(custom_review_tokens)
                print(classifier.classify(custom_review_set))  # Output: neg
                # Negative review correctly classified as negative
                if classifier.classify(custom_review_set) == 'neg':
                    ans = askyesno("Warning Box", msg)
                    # print(ans)
                    if ans:
                        msg_list.insert(tkinter.END, msg)
                else:
                    msg_list.insert(tkinter.END, msg)
        except OSError:
            break


def send(event=None):
    msg = my_msg.get()
    my_msg.set("")
    s.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        s.close()
        top.quit()


def on_closing(event=None):
    my_msg.set("{quit}")
    send()


top = tkinter.Tk()
top.title("JnU Chat Room")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()
my_msg.set("Clear & Enter Name")
scrollbar = tkinter.Scrollbar(messages_frame)
msg_list = tkinter.Listbox(messages_frame, height=15, width=100, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

address = (HOST, PORT)
s.connect(address)

threading.Thread(target=echo_data, args=(s,)).start()

tkinter.mainloop()
