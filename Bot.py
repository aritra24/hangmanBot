from flask import Flask, request
from helpers import *
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
bot_id = os.environ['BOT_ID']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

alphanum = list('01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ')

class User(db.Model):
    __tablename__ = 'users'
    chat_id = db.Column(db.Integer, primary_key = True)
    word = db.Column(db.String(50))
    current_word = db.Column(db.String(50))
    attempted = db.Column(db.String(36))
    tries = db.Column(db.Integer)

    def __init__(self, chat_id, word, current_word, attempted, tries):
        self.chat_id = chat_id
        self.word = word
        self.current_word = current_word
        self.attempted = attempted
        self.tries = tries

@app.route('/', methods=['POST'])
def game():
    req = request.get_json(silent=True, force=True)
    message = req.get('message')
    print()
    chat_id = message['from']['id']
    if message['text'].upper() == 'NEW GAME':
        (status, word, current_word,tries) = new_game()
        attempted = '0'*36
        if not status:
            reply('Failed to start new game', chat_id)
        else:
            word = ''.join(word)
            current_word = ''.join(current_word)
            if not db.session.query(User).filter(User.chat_id == chat_id).count():
                user = User(chat_id, word, current_word, attempted, tries)
                db.session.add(user)
            else:
                user = db.session.query(User).filter(User.chat_id == chat_id).first()
                user.word = word
                user.current_word = current_word
                user.attempted = attempted
                user.tries = tries
            reply("New Game started",chat_id)
            reply("current word is "+current_word,chat_id)
            reply("Enter a character", chat_id)
    elif message['text'].upper() == 'CANCEL':
        if db.session.query(User).filter(User.chat_id == chat_id).count():
            user = db.session.query(User).filter(User.chat_id == chat_id).first()
            user.word = None
            user.current_word = None
            user.tries = 0
            reply("Cancelled",chat_id)
    else:
        if not db.session.query(User).filter(User.chat_id == chat_id).count():
            reply("Start a new game first", chat_id)
        else:
            user = db.session.query(User).filter(User.chat_id == chat_id).first()
            if user.word != None:
                if message['text'] in alphanum:
                    if user.attempted[alphanum.index(message['text'].upper())] == '0':
                        (status, user.current_word, user.attempted, user.tries) = \
                        guess(list(user.word), list(user.current_word), list(user.attempted), \
                            user.tries, message['text'])
                        user.current_word = ''.join(user.current_word)
                        user.attempted = ''.join(user.attempted)
                        if status:
                            reply('Perfect \nCurrent word is ' + user.current_word, user.chat_id)
                        else:
                            reply('Nope \nCurrent word is ' + user.current_word + ', \n' \
                                + str(user.tries) + ' tries left', user.chat_id)
                    else:
                        reply('Already attempted', user.chat_id)
                else:
                    user.tries -= 1
                    reply('Nope \nCurrent word is ' + user.current_word + ', \n' \
                                + str(user.tries) + ' tries left', user.chat_id)
                if not if_won(list(user.word), list(user.current_word)) and not if_lost(user.tries):
                    reply('Enter another character', user.chat_id)
                else:
                    if if_lost(user.tries):
                        reply("Sorry, you've lost", user.chat_id)
                        reply("The answer was "+ user.word, user.chat_id)
                    else:
                        reply("Yay, you've won", user.chat_id)
                    user.word = None
                    user.current_word = None
                    user.attempted = '0'*36
                    user.tries = 0
            else:
                reply("Start a new game first", chat_id)
    db.session.commit()
    return "Done"


if __name__ == '__main__':
    app.run(debug=True)

