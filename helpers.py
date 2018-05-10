import os
import requests
from urllib.request import urlopen, Request
from random import randint
from bs4 import BeautifulSoup

bot_id = os.environ['BOT_ID']
alphanum = list('01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ')

def get_new_word():
    word = []
    no_words = randint(1,4)
    for i in range(no_words):
        url = Request('https://randomword.com/', headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        rand_word = soup.find('div',id='random_word')
        rand_word = rand_word.text.upper()
        word += list(rand_word)+[' ']
    word.pop()
    return word

def new_game():
    word = get_new_word()
    if word == None:
        return (False, None, None, None)
    current_word = ['_' for i in range(len(word))]
    for i in range(len(word)):
        if not word[i].isalnum():
            current_word[i] = word[i]
    tries = min(len(word)//3, 7)
    return (True, word, current_word, tries)

def guess(word, current_word, attempted, tries, letter):
    letter = letter.upper()
    status = False
    print(attempted)
    for i in range(len(word)):
        if word[i] == letter:
            status = True
            current_word[i] = letter
    if not status:
        tries -=1
    attempted[alphanum.index(letter)] = '1'
    return (status, current_word, attempted, tries)

def display(current_word):
    os.system('clear')
    print("\n\nCurrent Word = ", end = '')
    for i in current_word:
        print(i,end = '')
    print()

def get_letter():
    return input('Enter a character to guess:').upper()

def if_won(word, current_word):
    for i in range(len(word)):
        if word[i] != current_word[i]:
            return False
    print("Yay! You've Won!!!")
    return True

def if_lost(tries):
    if tries == 0:
        print("Shucks, seems like you've lost")
        return True
    return False

def reply(message, chat_id):
    url = 'https://api.telegram.org/bot' + str(bot_id) + '/sendMessage'
    request = {'chat_id' : chat_id, 'text' : message}
    response = requests.post(url, json = request)

def __init__():
    word = []
    current_word = []
    tries = []
    attempted = ['0' for i in range(36)]
    (status, word, current_word, tries) = new_game()
    if not status:
        print("Initialization failed")
        return -1
    done = False
    display(current_word)
    while not done:
        letter = get_letter()
        if attempted[alphanum.index(letter)] == '0':
            print(attempted)
            (result, current_word, attempted, tries) = guess(word, current_word, attempted, tries, letter)
        display(current_word)
        if result:
            print('Well done')
        else:
            print(letter + ' was not in the word')
            print('remaining tries = ' + str(tries))
        done = if_won(word, current_word) or if_lost(tries)

if __name__ == '__main__':
    __init__()