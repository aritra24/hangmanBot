from flask import Flask, session, request
from helpers import *

app = Flask(__name__)
app.secret_key = 'Super Secret Key'
bot_id = os.environ['BOT_ID']


@app.route('/', methods=['POST'])
def game():
    req = request.get_json(silent=True, force=True)
    message = req.get('message')
    print()
    session['id'] = message['from']['id']
    if message['text'].upper() == 'NEW GAME':
        (status, session['word'], session['current_word'], session['tries']) = new_game()
        if not status:
            reply(bot_id, 'Failed to start new game', session['id'])
        else:
            session['game started'] = True
            reply(bot_id, "Enter a character", session['id'])
    elif message['text'] == 'CANCEL' and session['game started']:
        session.clear()
    elif session['game started']:
        (status, current_word) = guess(session['word'], session['current_word'], session['tries'], message['text'])
        if status:
            reply(bot_id, 'perfect \nCurrent word is'+''.join(current_word), session['id'])
            reply(bot_id, 'Enter a character', session['id'])
    else:
        reply(bot_id, 'got nothing', session['id'])
    for i in session:
        print(i, session[i])
    print()


if __name__ == '__main__':
    app.run(debug=True)

