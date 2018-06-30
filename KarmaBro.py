import re
import redis
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

print('Bro initialized')
vk_session = vk_api.VkApi(login = '89132322121', password = open('password.txt').readlines())
print('Connecting...')
vk_session._auth_token()
print('Connected successfully!\nBro is running')


pattern = re.compile(r'\[id82762098\|Марина\].*')
patternPlus = re.compile(r'.*плюс.*\[id(\d+)\|.*\]', re.IGNORECASE)
r = redis.StrictRedis(host='localhost', port=6379, db=0)


def write_msg(peer_id, s):
    vk_session.method('messages.send', {'peer_id': 2000000000 + peer_id, 'message': s})

def get_name(user_id):
    full_name = r.hget("names", user_id)
    if full_name is None:
        full_name = vk_session.method('users.get', {'user_id': user_id})[0]["first_name"] +  " " + vk_session.method('users.get', {'user_id': user_id})[0]["last_name"]
        r.hset("names", user_id, full_name)
    else:
        full_name = full_name.decode('utf-8')
    return full_name
    
longpoll = VkLongPoll(vk_session)
last_message_id = 0

for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:
        if event.from_chat and event.chat_id == 143 and event.to_me and len(pattern.findall(event.text)) != 0:
            if len(patternPlus.findall(event.text)) != 0:
                user_id = re.search(patternPlus, event.text).group(1)
                r.hincrby("users", user_id, 1)
                write_msg (143, "Теперь карма " + get_name(user_id) + " = " + r.hget("users", user_id).decode('utf-8'))
    # if event.type == VkEventType.USER_TYPING_IN_CHAT and event.chat_id == 143:
    #     write_msg(143, "Заткнись=(")