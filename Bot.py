from flask import Flask, session, request
from helpers import *
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'Super Secret Key'
bot_id = os.environ['BOT_ID']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    chat_id = db.Column(db.Integer, primary_key = True)
    word = db.Column(db.String(50))
    current_word = db.Column(db.String(50))
    tries = db.Column(db.Integer)

    def __init__(self, chat_id, word, current_word, tries):
        self.chat_id = chat_id
        self.word = word
        self.current_word = current_word
        self.tries = tries

@app.route('/', methods=['POST'])
def game():
    req = request.get_json(silent=True, force=True)
    message = req.get('message')
    print()
    chat_id = message['from']['id']
    if message['text'].upper() == 'NEW GAME':
        (status, word, current_word,tries) = new_game()
        if not status:
            reply(bot_id, 'Failed to start new game', chat_id)
        else:
            word = ''.join(word)
            current_word = ''.join(current_word)
            if not db.session.query(User).filter(User.chat_id == chat_id).count():
                user = User(chat_id, word, current_word, tries)
                db.session.add(user)
            else:
                user = db.session.query(User).filter(User.chat_id == chat_id).first()
                user.word = word
                user.current_word = current_word
                user.tries = tries
            reply(bot_id, "New Game started",chat_id)
            reply(bot_id, "current word is "+current_word,chat_id)
            reply(bot_id, "Enter a character", chat_id)
    elif message['text'].upper() == 'CANCEL':
        if db.session.query(User).filter(User.chat_id == chat_id).count():
            user = db.session.query(User).filter(User.chat_id == chat_id).first()
            user.word = None
            user.current_word = None
            user.tries = 0
    else:
        if not db.session.query(User).filter(User.chat_id == chat_id).count():
            reply(bot_id, "Start a new game first", chat_id)
        else:
            user = db.session.query(User).filter(User.chat_id == chat_id).first()
            if user.word != None:
                (status, user.current_word, user.tries) = guess(list(user.word), list(user.current_word), user.tries, message['text'])
                user.current_word = ''.join(user.current_word)
                if status:
                    reply(bot_id, 'Perfect \nCurrent word is ' + user.current_word, user.chat_id)
                else:
                    reply(bot_id, 'Nope \nCurrent word is ' + user.current_word + ', ' + str(user.tries) + ' tries left', user.chat_id)
                if not if_won(list(user.word), list(user.current_word)) and not if_lost(user.tries):
                    reply(bot_id, 'Enter another character', user.chat_id)
                else:
                    if if_lost(user.tries):
                        reply(bot_id, "Sorry, you've lost", user.chat_id)
                        reply(bot_id, "The answer was "+ user.word, user.chat_id)
                    else:
                        reply(bot_id, "Yay, you've won", user.chat_id)
                    user.word = None
                    user.current_word = None
                    user.tries = 0
            else:
                reply(bot_id, "Start a new game first", chat_id)
    db.session.commit()
    return "Done"


if __name__ == '__main__':
    app.run(debug=True)

