import os
# import requests

def get_new_word():
	return ['A','B','C','D',' ','E','F','G','A']

def new_game():
	word = get_new_word()
	if word == None:
		return (False, None, None, None)
	current_word = ['_' for i in range(len(word))]
	for i in range(len(word)):
		if not word[i].isalnum():
			current_word[i] = word[i]
	tries = 3
	return (True, word, current_word, tries)

def guess(word, current_word, tries, letter):
	letter = letter.upper()
	if letter not in word:
		tries -= 1
		return (False, current_word)
	else:
		for i in range(len(word)):
			if word[i] == letter:
				current_word[i] = letter
	return (True, current_word)

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

def reply(bot_id, message, chat_id):
	url = 'https://api.telegram.org/bot' + str(bot_id) + '/sendMessage'
	request = {'chat_id' : chat_id, 'text' : message}
	response = requests.post(url, json = request)
	print(request)

def __init__():
	word = []
	current_word = []
	tries = []
	(status, word, current_word, tries) = new_game(word, current_word, tries)
	if not status:
		print("Initialization failed")
		return -1
	done = False
	display(current_word)
	while not done:
		letter = get_letter()
		(result, current_word) = guess(word, current_word, tries, letter)
		display(current_word)
		if result:
			print('Well done')
		else:
			print(letter + ' was not in the word')
			print('remaining tries = ' + str(tries))
		done = if_won(word, current_word) or if_lost(tries)

if __name__ == '__main__':
	__init__()