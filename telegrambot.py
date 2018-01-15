#-*- coding: utf-8 -*-

import telegram

# 핫딜봇 - t.me/khs7515_hotdeal_bot
TOKEN = '478859546:AAHyBspDwCBJ8abuPRKn9d7Gjk6ryuExjVE'

# 채널ID
CHAT_ID = '@khs7515_hotdeal'

# 메세지 전송
def send_message(message):
    if not message:
        # 봇 생성
        bot = telegram.Bot(TOKEN)
        # 메세지 전송
        bot.sendMessage(chat_id=CHAT_ID, text=message)
        return True
    else:
        return False