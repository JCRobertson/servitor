from fbchat import Client
from fbchat.models import *
import time
import json
import requests
import re


def getWikiText(searchTerm):
    print("+++++ Beginning Search for " + searchTerm + " +++++")

    searchTerm = re.sub(" ", "%20", searchTerm)
    response = requests.get(
        "http://wh40k.lexicanum.com/mediawiki/api.php?action=opensearch&search=" + searchTerm + "&limit=10&format=json")
    data = json.loads(response.text)
    searchTerm = data[1][0]

    wikiText = getSummaryText(searchTerm)

    while "redirect" in wikiText:
        print("+++++ Redirecting +++++")
        searchTerm = wikiText[12:]
        searchTerm = searchTerm[:(len(searchTerm) - 2)]
        wikiText = getSummaryText(searchTerm)
    while "REDIRECT" in wikiText:
        print("+++++ Redirecting +++++")
        searchTerm = wikiText[12:]
        searchTerm = searchTerm[:(len(searchTerm) - 2)]
        wikiText = getSummaryText(searchTerm)
    return wikiText


def getSummaryText(searchTerm):
    print("+++++ Getting Summary for " + searchTerm + " +++++")

    response = requests.get(
        "http://wh40k.lexicanum.com/mediawiki/api.php?action=parse&page=" + searchTerm + "&format=json&prop=wikitext&section=0")
    data = json.loads(response.text)
    data = data.get('parse')
    wikiText = data.get('wikitext')
    wikiText = wikiText.get('*')
    return wikiText


def formatWikiText(wikiText):
    print("+++++ Formatting Response +++++")

    while "{{" in wikiText:
        part1 = wikiText.partition('{{')
        part2 = part1[2].partition("}}")
        wikiText = part1[0] + part2[2]

    while "[[Image" in wikiText:
        part1 = wikiText.partition('[[Image')
        part2 = part1[2].partition("]]")
        wikiText = part1[0] + part2[2]

    wikiText = re.sub('\\[', '', wikiText)
    wikiText = re.sub(']', '', wikiText)
    wikiText = re.sub('\\\'', '', wikiText)
    wikiText = re.sub('}', '', wikiText)
    wikiText = re.sub('\\|', '', wikiText)
    wikiText = re.sub('\\\n', '', wikiText)
    return wikiText


def search(searchTerm):
    return formatWikiText(getWikiText(searchTerm))


class ServitorClient(Client):
    def onMessage(self, mid, author_id, message_object, thread_id, thread_type, ts, metadata, msg, **kwargs):
        print("Received message, processing")
        print("AUTHOR ID: " + author_id)
        # if thread_id == '1684891288218201' and thread_type == ThreadType.GROUP:
        if "emperor" in message_object.text.lower():
            self.send(Message(text="+++ Praise the Omnissiah +++"), thread_id=thread_id, thread_type=thread_type)
        if "tau" in message_object.text.lower():
            self.send(Message(text="+++ Seize the Xenotech +++"), thread_id=thread_id, thread_type=thread_type)
        if "servitor tell me about " in message_object.text.lower():
            searchTerm = message_object.text[23:]
            print("+++++ Found Search Term " + searchTerm + " +++++")
            self.send(Message(text="+++ Accessing the Archives on " + searchTerm + " +++"), thread_id=thread_id, thread_type=thread_type)
            self.send(Message(text=search(searchTerm)), thread_id=thread_id, thread_type=thread_type)


client = ServitorClient('email', 'pass')

client.listen()



#
# while True:
#     client.send(Message(text='Also! Fuck the Tau!'), thread_id='1684891288218201', thread_type=ThreadType.GROUP)
#     time.sleep(60)
