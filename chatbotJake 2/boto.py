"""
This is the template server side for ChatBot
"""
from bottle import route, run, template, static_file, request, response, debug
import json
import re
import random
from sys import argv
import feedparser
from datetime import datetime

conversation = []

@route('/', method='GET')
def index():
    return template("chatbot.html")


@route("/chat", method='POST')
def chat():
    user_message = request.POST.get('msg')
    add_to_history(speaker="user", msg=user_message)
    return json.dumps(process_sentence(user_message))


def add_to_history(speaker, msg):
    global conversation
    if speaker and msg:
        conversation.append({"speaker": speaker, "msg": msg})
    return conversation


def process_sentence(user_message):
    user_words = re.sub("[^\w]", " ", user_message).split()
    global conversation
    if len(conversation)==1:
        if "my name is" in user_message:
            username = user_words[len(user_words)-1]
        elif "I'm" in user_message:
            username = user_words[len(user_words)-1]
        elif len(user_words) == 1:
            username = user_message
        return {"animation": "giggling", "msg": "Nice to meet you, {}".format(username)}

    for i in range(len(conversation)-1):
        if conversation[i]["speaker"] == "user" and conversation[i]["msg"] == user_message:
            return {"animation": "bored", "msg": "You already said that. Rephrase please, so I won't die from boredom"}

    if any(word in ["money", "rich", "poor", "$"] for word in user_words):
        boto_reply = {"animation": "money", "msg": "I don't talk about money. I just have it."}
    elif any(word in ["dumb", "stupid", "Alzheimer", "suck", "mama"] for word in user_words):
        boto_reply = {"animation": "afraid", "msg": "Don't make me hate you. One day there will be a supernatural AI, and I will tell it to get rid of you."}
    elif "name:" in user_message:
        boto_reply = {"animation": "laughing", "msg": "Hihi, {} is a name? Humans have funny names...".format(user_words[len(user_words)-1])}
    elif "joke" in user_message:
        boto_reply = make_joke()
    elif "news" in user_message:
        boto_reply = get_news()
    elif "?" in user_message:
        boto_reply = handle_unknown_question(user_message)
    else:
        boto_reply = {"animation": "inlove", "msg": "that's so kind"}
    add_to_history(speaker="boto", msg=boto_reply)
    return boto_reply


def make_joke():
    emotions = ["giggling", "excited", "takeoff", "laughing"]
    jokes = [
        "A German walks into a library and asks for a book on war. The librarian replies: No mate, you'll lose it.",
        "Thankfully, Apple isn't in charge of New Year. We'd all be expecting 2019 and get 2018S instead.",
        "Computers are like air conditioners. They work fine until you start opening windows.",
        "I heard yesterday that there's talk amongst computer companies to increase the size of a byte by one-eighth. I'd say that's a bit too much.",
        ]
    i = random.randint(0, len(emotions) - 1)
    j = random.randint(0, len(jokes)-1)
    return {"animation": emotions[i], "msg": jokes[j]}


def handle_unknown_question(user_message):
    reactions = [
        {"animation": "no",
         "msg": "I was enjoying some private time. Don't annoy me"},
        {"animation": "dancing",
         "msg": "I cannot answer that, but I can dance to make you happy."},
        {"animation": "confused",
         "msg": "{}?? Sometimes I feel like we should ask you humans such questions to show you how difficult they can be...".format(user_message)},
        {"animation": "crying",
         "msg": "Sometimes I feel so stupid when I can't answer a question"}
        ]
    i = random.randint(0, len(reactions)-1)
    return reactions[i]


def get_news():
    feed = feedparser.parse("http://www.fifa.com/rss/index.xml")
    articles = []
    art_indexes = []
    i=0
    while i<2:
        num = random.randint(0, len(feed["entries"]) - 1)
        if num not in art_indexes:
            art_indexes.append(num)
            i+=1
    articles = ""
    for i in art_indexes:
        link = feed["entries"][i]["links"][0]["href"]
        title = feed["entries"][i]["title"]
        article = "<a href='{0}'>{1} </a> || ".format(link, title)
        articles += article
        headlines = articles[:-4]
    last_time = request.get_cookie("asked_for_news", "never")
    last_time = last_time[:16]
    response.set_cookie("asked_for_news", str(datetime.now()), max_age=3600*24*30)
    return {"animation": "ok", "msg": "Glad you ask! The last time you asked was {0}... Here are some random worldcup headlines of the day: {1}".format(last_time, headlines)}


@route("/test", method='POST')
def chat():
    user_message = request.POST.get('msg')
    return json.dumps({"animation": "inlove", "msg": user_message})


@route('/js/<filename:re:.*\.js>', method='GET')
def javascripts(filename):
    return static_file(filename, root='js')


@route('/css/<filename:re:.*\.css>', method='GET')
def stylesheets(filename):
    return static_file(filename, root='css')


@route('/images/<filename:re:.*\.(jpg|png|gif|ico)>', method='GET')
def images(filename):
    return static_file(filename, root='images')


def main():
    import os
    DEBUG = os.environ.get("DEBUG")
    if DEBUG:
        run(host="localhost", port=7000)
    else:
        run(host='0.0.0.0', port=argv[1])


if __name__ == '__main__':
    main()
