from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters)

from conf import TOKEN, DB_NAME
from db_helper import DBHelper

BTN_TODAY, BTN_TOMORROW, BTN_MONTH, BTN_REGION, BTN_DUA, BTN_TASBEH, BTN_ADMIN, BTN_QOLLANMA = (
    '⌛️ Bugun', '⏳ Ertaga', '📅 To`liq taqvim', '🇺🇿 Mintaqa', '🤲 Duo', "ТАРОВЕҲ ТАСБЕҲИ", "ADMIN👨‍💻", "📖Qo`llanma📖")
main_buttons = ReplyKeyboardMarkup([
    [BTN_TODAY], [BTN_TOMORROW, BTN_MONTH], [BTN_REGION], [BTN_DUA, BTN_TASBEH],[BTN_ADMIN, BTN_QOLLANMA]
], resize_keyboard=True)

STATE_REGION = 1
STATE_CALENDAR = 2

user_region = dict()
db = DBHelper(DB_NAME)


def region_buttons():
    regions = db.get_regions()
    buttons = []
    tmp_b = []
    for region in regions:
        tmp_b.append(InlineKeyboardButton(region['name'], callback_data=region['id']))
        if len(tmp_b) == 2:
            buttons.append(tmp_b)
            tmp_b = []
    return buttons


def start(update, context):
    user = update.message.from_user
    user_region[user.id] = None
    buttons = region_buttons()

    update.message.reply_html(
        'Assalomu alaykum <b>{}!</b>\n \n<b>Ramazon oyingiz muborak bo`lsin</b>\nHozircha shu mintaqalar(viloyatlar bor sekin sekin qolganlarini qo`shamiz)\n\nSiz qaysi mintaqa bo`yicha ma`lumot olmoqchisiz?'.
            format(user.first_name), reply_markup=InlineKeyboardMarkup(buttons))

    return STATE_REGION


def inline_callback(update, context):
    try:
        query = update.callback_query
        user_id = query.from_user.id
        user_region[user_id] = int(query.data)
        query.message.delete()
        query.message.reply_html(text='<b>Ramazon taqvimi</b> 2️⃣0️⃣2️⃣2️⃣\n \nQuyidagilardan birini tanlang 👇',
                                 reply_markup=main_buttons)

        return STATE_CALENDAR
    except Exception as e:
        print('error ', str(e))


def calendar_today(update, context):
    try:
        user_id = update.message.from_user.id
        if not user_region[user_id]:
            return STATE_REGION
        region_id = user_region[user_id]
        region = db.get_region(region_id)
        today = str(datetime.now().date())

        calendar = db.get_calendar_by_region(region_id, today)
        photo_path = 'images/{}.jpg'.format(calendar['id'])
        update.message.reply_html('<b>Ramazon</b> 2️⃣0️⃣2️⃣2️⃣\n<b>{}</b> vaqti\nBugungi kun👇🏻\n \nSaharlik: <b>{}</b>\nIftorlik: <b>{}</b>'.format(
            region['name'], calendar['fajr'][:5], calendar['maghrib'][:5]), reply_markup=main_buttons)

        # update.message.reply_photo(photo=open(photo_path, 'rb'), caption=message, parse_mode='HTML',
        #                            reply_markup=main_buttons)
    except Exception as e:
        print('Error ', str(e))


def calendar_tomorrow(update, context):
    try:
        user_id = update.message.from_user.id
        if not user_region[user_id]:
            return STATE_REGION
        region_id = user_region[user_id]
        region = db.get_region(region_id)
        dt = str(datetime.now().date() + timedelta(days=1))

        calendar = db.get_calendar_by_region(region_id, dt)
        photo_path = 'images/{}.jpg'.format(calendar['id'])
        update.message.reply_html('<b>Ramazon</b> 2️⃣0️⃣2️⃣2️⃣\n<b>{}</b> vaqti\nErtagalik kun👇🏻\n \nSaharlik: <b>{}</b>\nIftorlik: <b>{}</b>'.format(
            region['name'], calendar['fajr'][:5], calendar['maghrib'][:5]), reply_markup=main_buttons)

        # update.message.reply_photo(photo=open(photo_path, 'rb'), caption=message, parse_mode='HTML',
        #                            reply_markup=main_buttons)
    except Exception as e:
        print('Error ', str(e))


def calendar_month(update, context):
    try:
        user_id = update.message.from_user.id
        if not user_region[user_id]:
            return STATE_REGION
        region_id = user_region[user_id]
        region = db.get_region(region_id)

        photo_path = 'images/table/region_{}.jpg'.format(region['id'])
        message = '<b>Ramazon</b> 2️⃣0️⃣2️⃣2️⃣\n<b>{}</b> vaqti\nBir oylik taqvim👆🏻'.format(region['name'])

        update.message.reply_photo(photo=open(photo_path, 'rb'), caption=message, parse_mode='HTML',
                                   reply_markup=main_buttons)
    except Exception as e:
        print('Error ', str(e))


def select_region(update, context):
    buttons = region_buttons()
    update.message.reply_text('Sizga qaysi mintaqa bo`yicha ma`lumot olmoqchisiz?',
                              reply_markup=InlineKeyboardMarkup(buttons))
    return STATE_REGION


def select_dua(update, context):
    saharlik = "<b>Saxarlik (og`iz yopish) duosi:</b>\nНавайту ан асума совма шаҳри Рамазона минал фажри илал мағриби, холисан лиллаҳи таъала."
    iftorlik = "<b>Iftorlik (og`iz ochish) duosi:</b>\nАллоҳумма лака сумту ва бика аманту ва аъалайка таваккалту ва ъала ризқика афтарту, фағфирли, йа Ғоффару, ма қоддамту вама аххорту."
    update.message.reply_photo(photo=open('images/ramadan_dua.png', 'rb'),
                               caption="{}\n \n{}".format(saharlik, iftorlik), parse_mode='HTML',
                               reply_markup=main_buttons)

def select_tasbeh(update, context):
    taroveh = "<b>ТАРОВЕҲ ТАСБЕҲИ</b>\n- - - - - - - - - - - - - - - - - -\n📖 - Субҳаана зил мулки вал малакут. Субҳаана зил ъиззати вал ъазомати вал қудроти вал кибрияи вал жабарут. Субҳаанал маликил ҳаййиллазий лаа янааму ва лаа ямут. Суббуҳун қуддусур Роббунаа ва Роббул малааикати вар Руҳ. Лаа илааҳа иллаллоҳу настағфируллоҳ. Нас‘алукал жанната ва наъузу бика минан нар."
    update.message.reply_photo(photo=open('images/names.jpg', 'rb'), caption="{}".format(taroveh), parse_mode='HTML', reply_markup=main_buttons)

def select_admin(update, context):
    update.message.reply_html('<b>ADMIN</b>: @khurboev_3 | Coder |\n<b>Our Team</b>: @coder_boys')

def select_qollanma(update, context):
    update.message.reply_html('''Assalomu alaykum va Rahmatullohi Va Barakatuh.\nBotimizga xush kelibsiz😊\nUshbu bot sizlarga foydali bo'lsin uchun yaratildi.👉Admin mehnatini qadrlang. Zero sizga foydali ma'lumotlar boshqalarga ham foyda keltirsin Insha Alloh.\nAgar bot ishlamay qolsa /start funksiyasini boshqattan ishlating🔄(botni qaytadan ishga tushiring.\n\nAgar botdan foydalanishda xato va kamchiliklar yuzaga kelsa admin bilan bog'lanishingiz mumkin.''')



def main():
    # Updater o`rnatib olamiz
    updater = Updater(TOKEN, use_context=True)

    # Dispatcher eventlarni aniqlash uchun
    dispatcher = updater.dispatcher

    # start kommandasini ushlab qolish
    # dispatcher.add_handler(CommandHandler('start', start))

    # inline button query
    # dispatcher.add_handler(CallbackQueryHandler(inline_callback))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STATE_REGION: [
                CallbackQueryHandler(inline_callback),
                MessageHandler(Filters.regex('^(' + BTN_TODAY + ')$'), calendar_today),
                MessageHandler(Filters.regex('^(' + BTN_TOMORROW + ')$'), calendar_tomorrow),
                MessageHandler(Filters.regex('^(' + BTN_MONTH + ')$'), calendar_month),
                MessageHandler(Filters.regex('^(' + BTN_REGION + ')$'), select_region),
                MessageHandler(Filters.regex('^(' + BTN_DUA + ')$'), select_dua),
                MessageHandler(Filters.regex('^(' + BTN_TASBEH + ')$'), select_tasbeh),
                MessageHandler(Filters.regex('^(' + BTN_ADMIN + ')$'), select_admin),
                MessageHandler(Filters.regex('^(' + BTN_QOLLANMA + ')$'), select_qollanma)
            ],
            STATE_CALENDAR: [
                MessageHandler(Filters.regex('^(' + BTN_TODAY + ')$'), calendar_today),
                MessageHandler(Filters.regex('^(' + BTN_TOMORROW + ')$'), calendar_tomorrow),
                MessageHandler(Filters.regex('^(' + BTN_MONTH + ')$'), calendar_month),
                MessageHandler(Filters.regex('^(' + BTN_REGION + ')$'), select_region),
                MessageHandler(Filters.regex('^(' + BTN_DUA + ')$'), select_dua),
                MessageHandler(Filters.regex('^(' + BTN_TASBEH + ')$'), select_tasbeh),
                MessageHandler(Filters.regex('^(' + BTN_ADMIN + ')$'), select_admin),
                MessageHandler(Filters.regex('^(' + BTN_QOLLANMA + ')$'), select_qollanma)
            ],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


main()
