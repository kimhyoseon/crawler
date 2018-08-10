#-*- coding: utf-8 -*-

import telegram

# 개인알림방법 https://www.forsomedefinition.com/automation/creating-telegram-bot-notifications/

BOT_LIST = {
    'dev': {
        'token': '478859546:AAHyBspDwCBJ8abuPRKn9d7Gjk6ryuExjVE',
        'chat_id': '49249214' # khs7515의 id
    },
    'hotdeal': {
        'token': '478859546:AAHyBspDwCBJ8abuPRKn9d7Gjk6ryuExjVE',
        'chat_id': '@khs7515_hotdeal' # 핫딜알리미 채널의 id
    },
    'aptrent': {
        'token': '478859546:AAHyBspDwCBJ8abuPRKn9d7Gjk6ryuExjVE',
        'chat_id': '@apt_rent' # 임대아파트알리미 채널의 id
    }
}

# 메세지 전송
def send_message(message=None, bot_name=None):

    # 테스트
    bot_name = 'dev'

    if message and BOT_LIST[bot_name]:
        # 봇 생성
        bot = telegram.Bot(BOT_LIST[bot_name]['token'])
        # 메세지 전송
        bot.sendMessage(chat_id=BOT_LIST[bot_name]['chat_id'], text=message)
        return True
    else:
        return False