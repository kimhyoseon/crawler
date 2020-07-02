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
    },
    'lowdeal': {
        'token': '478859546:AAHyBspDwCBJ8abuPRKn9d7Gjk6ryuExjVE',
        'chat_id': '@lowdeal' # 최저가 알리미 채널의 id
    },
    'instagram': {
        'token': '962167832:AAGGSaPbqnG5pmKy7WswO5sohjrqCnYQ1P0',
        'chat_id': '49249214' # 봇 -> 나한테
    },
    'kuhit': {
        'token': '849472688:AAFUFMwcs_KAhiyMZl2LvF6r_38jVnB3bwE',
        'chat_id': '49249214' # 봇 -> 나한테 (쿠힛 배송)
    },
    'kuhit_review': {
        'token': '906837133:AAH2CvSKqdcI_Jqq6eOFedFQRirQU79GYwQ',
        'chat_id': '49249214' # 봇 -> 나한테 (쿠힛 리뷰)
    },
    'jshk': {
        'token': '889211522:AAGnvkAM1o-_R22LM5zOPClj9i9HS9yYmcA',
        'chat_id': '49249214' # 봇 -> 나한테 (정성한끼 배송)
    },
    'yoona_azzi': {
        'token': '1011849541:AAEGm-k-Abp1uiW6w_FG-fI1wB0jFap1koQ',
        'chat_id': '49249214' # 봇 -> 나한테 (아찌알리미)
    },
    'keyword': {
        'token': '902900662:AAEi_jfuxE7aqxxI4xRBHit1XfcU1ImCARE',
        'chat_id': '49249214' # 봇 -> 나한테 (아찌알리미)
    }
}
# 메세지 전송
def send_message(message=None, bot_name=None):

    # 테스트
    #bot_name = 'dev'

    if message and BOT_LIST[bot_name]:
        # 봇 생성
        bot = telegram.Bot(BOT_LIST[bot_name]['token'])
        # 메세지 전송
        bot.sendMessage(chat_id=BOT_LIST[bot_name]['chat_id'], text=message)
        return True
    else:
        return False