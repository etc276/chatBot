from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, RegexHandler, ConversationHandler)

import logging
import time
import beauty
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = '455989974:AAG1_pt549X9YV64asFXixuaMl-lchzidgk'
PTT_URL = 'https://www.ptt.cc'

# 0: choose joke or guess
# 1: choose joke type
# 2: choose guess type
# 3: give score. (END)
CHOOSING, JOKE, GUESS, SCORE = range(4)


def start(bot, update):
    # reply and show keyboard choice
    reply_keyboard = [['joke', 'guess']]

    update.message.reply_text(
        "哈囉，我是機器人\n"
        "/cancel to stop conversation.\n"
        "你喜歡聽笑話還是猜謎 ??",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True)
    )

    current_page = beauty.get_web_page(PTT_URL + '/bbs/Beauty/index.html')
    if current_page:
        articles = []  # 全部的今日文章
        date = time.strftime("%m/%d").lstrip('0')  # 今天日期, 去掉開頭的 '0' 以符合 PTT 網站格式
        current_articles, prev_url = beauty.get_articles(current_page, date)  # 目前頁面的今日文章
        while current_articles:  # 若目前頁面有今日文章則加入 articles，並回到上一頁繼續尋找是否有今日文章
            articles += current_articles
            current_page = beauty.get_web_page(PTT_URL + prev_url)
            current_articles, prev_url = beauty.get_articles(current_page, date)

        # 已取得文章列表，開始進入各文章讀圖
        for article in articles:
            if (article['push_count'] <= 2):
                continue
            print('Processing', article)
            page = beauty.get_web_page(PTT_URL + article['href'])
            if page:
                img_urls = beauty.parse(page)
    chat_id = update.message.chat_id
    for img_url in img_urls:
        bot.send_photo(chat_id=chat_id, photo=img_url)

    # go to CHOOSING state
    return CHOOSING


def joke(bot, update):
    reply_keyboard = [['0', '5', '10']]
    update.message.reply_text(
    # haha
    "那天我到一間小店吃午餐\n"

    "跟老闆點了排骨飯\n"

    "但老闆卻上弄碗排骨麵\n"

    "端上來時，我看著老闆問\n"

    "「老闆，我剛點的是排骨飯耶」\n"

    "老闆抓抓頭，一臉尷尬\n"

    "「不然我幫你加點滷大腸好嗎?」\n"

    "「蛤？」我疑惑\n"

    "老闆：「沒有啦，我想說齁，那個加腸變飯啦...」")

    update.message.reply_text(
        "請給分",        
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=True)
    )
    return JOKE


def guess(bot, update):
    reply_keyboard = [['0', '5', '10']]
    update.message.reply_text("哪個殺手只會講英文 ?? (給你五秒唷)")
    time.sleep(5)
    update.message.reply_text("銀翼殺手")
    update.message.reply_text(
        "請給分",        
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=True)
    )
    return GUESS


def score(bot, update):
    reply_keyboard = [['0', '5', '10']]
    update.message.reply_text(
        "高一點嘛QQ",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=True)
    )
    return SCORE


def end(bot, update):
    text = update.message.text
    update.message.reply_text("好啦掰晡, 才%s分QQ" % text)
    return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        # initial state (recieve '/start', then go start())
        entry_points=[CommandHandler('start', start)],

        states={
            # now is CHOOSING state, if receive 'joke' then joke()
            CHOOSING: [RegexHandler('^joke$', joke),
                       RegexHandler('^guess$', guess)],

            # now is JOKE state, whatever receive then score() 
            JOKE:  [MessageHandler(Filters.text, score)],
            GUESS: [MessageHandler(Filters.text, score)],
            SCORE: [MessageHandler(Filters.text, end  )],
            },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__=='__main__':
    main()
