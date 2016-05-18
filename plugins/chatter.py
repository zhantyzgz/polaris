from core.utils import *

commands = [
    ('^' + bot.username, [])
]
description = 'Chat with the bot.'
hidden = True

def run(m):
    input = m.content.replace(bot.username + ' ', '')

    
    if m.receiver.id < 0:
        chat = m.receiver.id
    else:
        chat = m.sender.id
    
    url = 'http://api.program-o.com/v2/chatbot/'
    params = {
        'bot_id': config.keys.chatbot,
        'say': input,
        'convo_id': chat,
        'format': 'json'
    }
    
    res = requests.get(url, params=params, timeout=config.timeout)
    
    if res.status_code != 200:
        send_alert('%s\n%s' % (lang.errors.connection, res.text))
        return send_message(m, lang.errors.connection)
	
    try:
        chatting = DictObject(json.loads(res.text))
        message = chatting.botsay

        send_message(m, message)
    except:
        send_alert(res.text)

def process(m):
    if m.reply and m.type == 'text':
        if (m.reply.sender.id == bot.id and
                not m.content.startswith(config.start)):
            m.content = bot.username + ' ' + m.content

    if (m.type == 'text' and
        m.receiver.id > 0 and
        not m.content.startswith(config.start)):
        m.content = bot.username + ' ' + m.content
