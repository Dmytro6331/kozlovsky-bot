import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters, ConversationHandler
import os
import json
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8165148442:AAHz3JwL6VlKk-n9yrKe5i1ZU7-89IWwgEk")

# Payment links
PAYMENT_LINK = "https://artemtraining.wayforpay.link/"
PRO_PAYMENT_LINK = "https://secure.wayforpay.com/button/bd9b9ffbb15af"

# Admin IDs
ADMIN_IDS = [609094231, 5153484824, 254322794]

# Файл для хранения данных пользователей
USERS_DATA_FILE = "interested_users.json"

# Для работы с состояниями разговора и броадкаста
PHONE, PROCESSING, BROADCAST_TARGET, BROADCAST_CONTENT_TYPE, BROADCAST_TEXT, BROADCAST_PHOTO, BROADCAST_VIDEO, BROADCAST_CONFIRM, BROADCAST_CANCEL_CONFIRM = range(9)

# Определение ID файлов из инструкции
VIDEO_FILE_IDS = {
    "intro": "DQACAgIAAxkDAAIHM2fhRrRivkQWj4EqXRG60qnwYOjmAALBawACGrDwSnwzTaa6iXcONgQ",
    "more_info": "BAACAgIAAxkDAAIHP2fhWP0dZ8hfIBM5iGRcd8y2V_H8AAJIbAACGrDwSqqJk01KATMBNgQ",
    "training_info": "BAACAgIAAxkBAAINvmfoNgjnyesZybpfPCm_M6TkLNT5AAJLbAACGrDwSjmELCKJaJSlNgQ",
    "separate_testimonial": "BAACAgIAAxkBAAILE2flay-QCrsOKkuM-_BQZOYOztcZAAKNbgACFssIS7BMtu3oly_hNgQ",
    "course_completed": "DQACAgIAAxkBAAIO1WfpQQ_01JGQf2xv2DCzDhZ4O_NRAAIOZwACZvhAS_n9NqLItgg8NgQ"
}

DOCUMENT_FILE_IDS = [
    "BQACAgIAAxkDAAIHSmfhsDP9yNvalTqbv_yahB8qg70DAAKoOAACIyr5SPF0JlVT-_KTNgQ",
    "BQACAgIAAxkDAAIHS2fhsDMeV3NdGyAN41T13gs0Ez_fAAKqOAACIyr5SFW-Yqpy5UJ-NgQ",
    "BQACAgIAAxkDAAIHTGfhsDNV32a6M-err6FDujr0PKPpAAIjOQACIyr5SEKR7yUVbteoNgQ"
]

TESTIMONIAL_FILE_IDS = [
    "BAACAgIAAxkBAAIHWGfimLuI5nveS9A6qIGZ_yUg9yNjAAJgbQACpkAISxOBJPtS2rasNgQ",
    "BAACAgIAAxkDAAIHKmfhRoxkHbET16Q2mgN4Rc0p8ZydAAIBigACSB3QSjYVrKeUJHeCNgQ",
    "DQACAgIAAxkDAAIHT2fhsDn-fiMKvScGiLhjgWxjrBr5AALZZQACQDLISqIU-Nfd0z42NgQ",
    "BAACAgIAAxkDAAIHO2fhWPNfRh-Q3SFovoTLQ1O_arrEAAKFbgAClDjgSspPuuTGWSK_NgQ",
    "DQACAgIAAxkDAAIHLmfhRrA8alrwMWc8eFediqUV_-dRAAKsXwACnszISqQcU06eoadsNgQ"
]

TESTIMONIAL_DOUBLE_FILE_IDS = [
    "DQACAgIAAxkDAAIHMGfhRrK_8DlNhM2YiX1CvpiIBbroAAIJZwACwIbZSjDJUh6dGn4ZNgQ",
    "DQACAgIAAxkDAAIHMWfhRrJ82ZjT5hENGs2_OcZ4ho1cAALWawACVarwSgjASsIMjRh1NgQ"
]

TESTIMONIAL_TRIPLE_FILE_IDS = [
    "DQACAgIAAxkBAAISQWfq7Ta78Zh_8rm08qNIaBlzdl2VAAKZcwAC-W0JSxSwDHYFHMNoNgQ",
    "DQACAgIAAxkBAAISQ2fq7Xv5l8iy0-x8YrkXYl3rFVzvAALYcwAC-W0JS0HCK9sYxp08NgQ",
    "DQACAgIAAxkBAAISRWfq7b34Gv37xlDHYIbeTw5-2bDCAAIMdAAC-W0JS-PZwMZAnlESNgQ"
]

AGENT_VIDEO_IDS = [
    "DQACAgIAAxkBAAIH_GfkLfrlIbR0K_ohh7jZfhT8lYCVAAJ7ZAAC__cIS41AF8pr7dCnNgQ",
    "DQACAgIAAxkBAAIJmGflM_5OWzi32UkjhLaF7YjlwLSHAAKDZAAC__cIS5gP4vSrYqYLNgQ",
    "DQACAgIAAxkBAAIJmWflM_6PBymrXmh122qyUVmDJCIQAAKRZAAC__cIS3Rye3pphwABkDYE",
    "DQACAgIAAxkBAAIJmmflM_71YDr49u84_KKlGBak8UiMAAKXZAAC__cIS07rF5wdaU6XNgQ",
    "DQACAgIAAxkBAAIJnGflM_4LA8hThVMBeMNsdFZLHqwnAAJLZQAC__cISytJ4FdaBtuvNgQ",
    "DQACAgIAAxkBAAIJm2flM_6ME9J-vwgla9m8IZQBNnUtAAIqZQAC__cISwLqWAkokY6TNgQ",
    "DQACAgIAAxkBAAIJnWflM_7vKUx3_4UmTMutJFRLYWyxAAJaZQAC__cIS0RvcpZXvKvUNgQ",
    "DQACAgIAAxkBAAIJnmflM_7j3AvErwjZQEYaL_bnU4cwAAJlZQAC__cIS48bt-SP_5SZNgQ",
    "DQACAgIAAxkBAAIJn2flM_5rwGYvZHVRey3pBrCYDhbbAAJuZQAC__cISxA-_nK7KCGzNgQ",
    "DQACAgIAAxkBAAIJoGflM_7RsoD5XX9h2TXHaoZwrQvGAAJzZQAC__cISwABT3xwkpajsjYE",
    "DQACAgIAAxkBAAIJoWflM_5RWTnAXBiZ3UxRd3kmI-NgAAJ3ZQAC__cISzr6TJiSQ7m0NgQ"
]

AGENT_DESCRIPTIONS = [
    "🔹 Ділимось досвідом:\n"
    "💸 Ми пройшли шлях через помилки та втратили $200 000+,\n"
    "щоб зрозуміти, як усе працює.\n\n"
    "🎓 Тепер цей досвід — для вас,\n"
    "щоб не повторювати чужих помилок, а одразу рости!",
    
    "🔹 Туроператори + Маркетинг:\n"
    "🌍 Доступ до українських та європейських туроператорів\n"
    "✈️ Бронювання по всьому світу\n"
    "🤝 Робота з європейськими туристами на вигідних умовах\n"
    "📚 Уроки маркетингу — як залучати клієнтів і продавати більше",
    
    "🔹 Робота без вкладень:\n"
    "🧠 Навчаємо формувати свою аудиторію\n"
    "🛠 Використовувати всі можливості — без витрат\n"
    "🎯 Цінна частина курсу включена в базову програму",
    
    "🔹 Юридичні питання + Тренди:\n"
    "⚖️ Покроково розберемо юридичні аспекти\n"
    "✅ Як вести бізнес легально та ефективно\n"
    "📈 Враховуємо актуальні тренди та зміни на ринку",
    
    "🔹 Офлайн рекламні тури:\n"
    "🧳 Для активних агентів — участь в турах\n"
    "🏨 До 80 готелів за одну поїздку\n"
    "🛠 Отримаєш всі інструменти для ефективної роботи",
    
    "🔹 Готелі + Навчання:\n"
    "🏨 Доступ до готельної бази (економ / стандарт / преміум)\n"
    "🤝 Група агентів для обміну досвідом\n"
    "🎥 Відеоуроки + домовленості щодо онлайн рекламних турів\n"
    "🗺 Повний доступ до всіх напрямків",
    
    "🔹 Розширені можливості:\n"
    "🏨 Доступ до готельєрів\n"
    "📧 Робоча пошта та підтримка\n"
    "🚖 Пріоритетне поселення, трансфери, авіа та транспорт\n"
    "🔝 Все для зручної й професійної роботи агента",
    
    "🔹 Стартуй зараз:\n"
    "💶 Всього 9 євро — і ти отримуєш\n"
    "📚 Повний доступ до навчальної бази\n\n"
    "🚀 Почни свій шлях уже сьогодні!",
    
    "🔹 Гнучкий формат навчання:\n"
    "⏰ Проходь курс у зручний час\n"
    "🌍 Працює в будь-якому часовому поясі\n"
    "📩 Нові уроки — регулярно та безкоштовно",
    
    "🔹 Професійна спільнота:\n"
    "👥 700+ агентів вже в команді з повним доступом\n"
    "🤝 Завжди на зв'язку — особисто підтримую кожного\n"
    "❤️ Я живу цією справою — і ти станеш частиною чогось більшого",
    
    "🔹 Єдина у світі система:\n"
    "🌍 Жодна країна не дає агентам доступ до операторів сусідів\n"
    "🚀 Тільки у нас — унікальний функціонал і реальна перевага"
]

COURSE_CIRCLE_VIDEO_IDS = [
    "DQACAgIAAxkBAAIIVGfkfSw9DRCLhuYDlyaD_B2paQOgAAKLbAACt4kgSxAFrzCBlGhRNgQ",
    "DQACAgIAAxkBAAIJkmflMKduFuZADf3SAAG3lTtyMeN4-wACm2wAAreJIEsSi8dcI9VS5DYE",
    "DQACAgIAAxkBAAIJYWflI39WeiGlWVUT0HXyv7o8qTLBAAKcbAACt4kgSwu47maxutHqNgQ",
    "DQACAgIAAxkBAAIJlWflMotlTylNMuJc-k3FP0zcN_V1AAKmbAACt4kgS9LRJlVLOomfNgQ",
    "DQACAgIAAxkBAAIH92fkKwzpiOgD0sMKP8QwmE9bzalcAAKfbAACt4kgS73Aqchf7HvuNgQ"
]

COURSE_CIRCLE_DESCRIPTIONS = [
    "🔹 ТурАгентам — швидко та вигідно:\n"
    "🏨 Прямий доступ до \"Hotelston\"\n"
    "💸 Оплата в гривні по курсу ПриватБанку\n"
    "❌ Без SWIFT / комісій / витрат\n"
    "🔁 Можна створити 2-й кабінет і перенести заявки\n"
    "💱 Є рахунки в € / $ / £ / zł\n\n"
    "📲 Пиши — підключимо за 5 хв!",
    
    "🔹 Ексклюзив для агентів:\n"
    "📑 Договір = доступ до:\n"
    "🇲🇩 Молдовських операторів (кабінети + висока комісія)\n"
    "📞 Пряма комунікація з менеджерами\n"
    "✈️ Миттєве бронювання — одразу в готель і на рейс\n"
    "🎁 Рекламні тури за продажами\n"
    "⭐️ Додатково:\n"
    "🇵🇱 MerlinX (Польща)\n"
    "🇨🇿🇩🇪🇱🇹🇱🇻🇪🇪 Оператори Чехії, Німеччини, Балтії\n"
    "🛫 Пряма система бронювання авіа + оплата на рахунок",
    
    "🔹 Повна підтримка для агентів:\n"
    "💳 Оплата навіть лоукостів з кредитного ліміту\n"
    "🕐 Підтримка 24/7\n"
    "🏨 Доступ до готельєрів, трансферів, транспорту\n"
    "📚 15 років напрацювань — відкритий доступ\n"
    "📢 Безкоштовно:\n"
    "– Матеріали для соцмереж\n"
    "– Уроки маркетингу\n"
    "– Актуальні тренди та як отримувати заявки",
    
    "🔹 Кабінети + свобода вибору:\n"
    "🧾 Прямі кабінети в українських операторах з підвищеною комісією\n"
    "🔁 Ваші поточні кабінети залишаються активними\n"
    "💼 Можна мати 2 активні кабінети — бронюйте там, де вигідно\n"
    "❌ Жодних зобов'язань чи планів\n"
    "⚡️ Договір онлайн — доступи за 5 хвилин\n"
    "📞 Завжди на зв'язку, готові допомогти",
    
    "🔹 Основні факти про нас:\n"
    "👥 700+ активних агентів\n"
    "Кожен щотижня створює мінімум 1 заявку\n"
    "👨‍💼 Засновник — Артем Козловський\n"
    "Оператор \"Клуб Датур\":\n"
    "європейські туроператори, міжнародні системи бронювання та авіаквитки\n"
    "📄 Документи та відгуки\n"
    "Доступні для перегляду — все відкрито\n"
    "📲 Підтримка 24/7\n"
    "Особисті консультації від Артема — завжди на зв'язку"
]

AGENT_TESTIMONIAL_VIDEO_IDS = [
    # Первый отзыв - два видео
    ["DQACAgIAAxkBAAIRCmfqorDyfxKVU5rHmlBHv3tpjfztAALVZQACQDLISvAffcB02YGPNgQ", 
     "DQACAgIAAxkDAAINvWfoNTMjJkZXyqkHNN0HUWSxTj57AALZZQACQDLISqIU-Nfd0z42NgQ"],
    
    # Второй отзыв - три видео
    ["DQACAgIAAxkDAAIQCmfpto4RMJYMIcDsZw6cxBsrMhcDAAIJZwACwIbZSjDJUh6dGn4ZNgQ", 
     "DQACAgIAAxkDAAIQC2fpto4shW4776XKBAv8FXEbOsdgAALWawACVarwSgjASsIMjRh1NgQ", 
     "DQACAgIAAxkBAAIRFWfqpgABHsfGzJSEuY32tXSH_huC8QAC22sAAlWq8EpCPa475G6r8zYE"],
    
    # Третий отзыв - одно видео
    ["DQACAgIAAxkBAAIRFmfqqJZOv-VA2M6ItMvrVS5xKBTcAALbawAC9k8AAUvoIb_OvatZsjYE"],
    
    # Четвертый отзыв - одно видео
    ["BAACAgIAAxkBAAIRF2fqqPV-O-nK1y9ijXhmPTwBZEKpAAKnaQACTSxQS1OWiyqmkGIrNgQ"],
    
    # Пятый отзыв - одно видео
    ["BAACAgIAAxkDAAINlmfnzkEE9WJLxBNWBr5KwzgfFJ6RAAJgbQACpkAISxOBJPtS2rasNgQ"],
    
    # Шестой отзыв - одно видео
    ["BAACAgIAAxkDAAINvGfoNTIO_5wuJ41BlKXJ0gMje3CNAAIBigACSB3QSjYVrKeUJHeCNgQ"],
    
    # Седьмой отзыв - одно видео
    ["BAACAgIAAxkBAAIRGmfqqcHig8eV_D7ROzgqwx07c_ZqAAI2igACSB3QSofQW4dqRDluNgQ"]
]

CONTRACT_DOCUMENT_IDS = [
    "BQACAgIAAxkBAAIRHWfqqy9hrywWrhCcfibLSwkbBq6xAAK6agACgd_oSazbOVn09RIeNgQ",
    "BQACAgIAAxkBAAIRHmfqq13sfpPKd5Drg-FFwpKLBVOwAAK8agACgd_oSXsIEqtxtkeMNgQ"
]

COURSE_VIDEOS = [
    "https://youtu.be/1DyL0Txsh8k",
    "https://youtu.be/uE6cQdWZ01c",
    "https://youtube.com/live/OiXIEahO0po",
    "https://youtube.com/live/Avgd3udJHhg",
    "https://youtu.be/qaxO-fpTt64"
]

PRO_COURSE_VIDEOS = [
    "https://youtu.be/FBUkIORHqn8",
    "https://youtube.com/live/6AiZyPOuGHs",
    "https://youtube.com/live/ngpa0FRKMtE?feature=share",
    "https://youtu.be/DaEmrv2nZkg",
    "https://youtu.be/sXKcLj2Zf1A?si=osyIP_tA5tkDhKN6",
    "https://www.youtube.com/live/ap3oqMGCtz4?si=CVw2xN2z4lr5Izd3",
    "https://youtube.com/live/xxmkf_UCq2M?feature=share",
    "https://youtube.com/live/V1DBEc1hIZI?feature=share",
    "https://youtu.be/URKJAFGZ950",
    "https://www.youtube.com/watch?v=TP1g25v6XK4",
    "https://youtube.com/live/5KY-Hi6hkhQ"
]

# Функция для сохранения данных пользователей в файл
def save_user_data(user_id, username, phone, timestamp, action_type=None, course_type=None):
    """Сохраняет данные пользователя в JSON-файл.
    
    Args:
        user_id: ID пользователя
        username: Имя пользователя
        phone: Номер телефона
        timestamp: Метка времени
        action_type: Тип действия ("hotel_selection", "request_contact" или None)
        course_type: Тип курса ("basic", "pro" или None)
    """
    try:
        # Проверяем существует ли файл и создаем его, если нет
        if not os.path.exists(USERS_DATA_FILE):
            with open(USERS_DATA_FILE, 'w') as f:
                json.dump([], f)
        
        # Загружаем существующие данные
        with open(USERS_DATA_FILE, 'r') as f:
            users_data = json.load(f)
        
        # Добавляем нового пользователя
        user_data = {
            "id": user_id,
            "username": username if username else "No username",
            "phone": phone,
            "timestamp": timestamp,
            "action_type": action_type,  # "hotel_selection", "request_contact" или None
            "course_type": course_type   # "basic", "pro" или None
        }
        
        # Проверяем, есть ли уже такой пользователь
        user_exists = False
        for user in users_data:
            if user["id"] == user_id:
                user_exists = True
                # Обновляем данные пользователя, сохраняя существующие значения если новых нет
                if action_type is not None:
                    user["action_type"] = action_type
                if course_type is not None:
                    user["course_type"] = course_type
                if phone != "Не указан":
                    user["phone"] = phone
                user["timestamp"] = timestamp
                break
        
        # Если пользователя нет, добавляем его
        if not user_exists:
            users_data.append(user_data)
        
        # Сохраняем обновленные данные
        with open(USERS_DATA_FILE, 'w') as f:
            json.dump(users_data, f, indent=4)
            
        return True
    except Exception as e:
        logger.error(f"Error saving user data: {e}")
        return False

# Функция для загрузки данных пользователей из файла
def load_users_data():
    try:
        if not os.path.exists(USERS_DATA_FILE):
            return []
        
        with open(USERS_DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading users data: {e}")
        return []

# Функция для проверки, является ли пользователь администратором
def is_admin(user_id):
    return user_id in ADMIN_IDS

# 1. Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback=False) -> None:
    """Send a message when the command /start is issued."""
    
    # Check if this is a payment confirmation with start=money
    if hasattr(context, 'args') and context.args and context.args[0] == "money":
        await payment_confirmation(update, context)
        return
    
    # Check if this is a Pro payment confirmation with start=money1
    if hasattr(context, 'args') and context.args and context.args[0] == "money1":
        await pro_payment_confirmation(update, context)
        return
    
    # 1.1 Приветствие - отправка приветственного видео
    try:
        if is_callback:
            # Если это callback, используем reply_video с query.message
            await update.callback_query.message.reply_video(
                video=VIDEO_FILE_IDS["intro"]
            )
        else:
            # Если это команда, используем обычный reply_video
            await update.message.reply_video(
                video=VIDEO_FILE_IDS["intro"]
            )
    except Exception as e:
        logger.error(f"Error sending intro video: {e}")
        if is_callback:
            await update.callback_query.message.reply_text("Не вдалося відправити відео. Спробуйте пізніше.")
        else:
            await update.message.reply_text("Не вдалося відправити відео. Спробуйте пізніше.")
    
    # 1.2 Приветственное сообщение с кнопками
    keyboard = [
        [InlineKeyboardButton("ℹ️ Хочу дізнатись більше", callback_data="more_info")],
        [InlineKeyboardButton("📝 Відгуки", callback_data="testimonials"),
         InlineKeyboardButton("📄 Документи", callback_data="documents")],
        [InlineKeyboardButton("❓ Про що цей курс", callback_data="about_course")],
        [InlineKeyboardButton("🎁 Ексклюзив для турагентів✨", callback_data="i_am_agent")],
        [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Текст приветственного сообщения
    welcome_text = (
        "✨ Привіт, друзі! ✨\n"
        "🚀 Створили найефективніше навчання на ринку, яке дозволить за 3 дні почати бронювати і заробляти від 500 €! 🌟\n\n"
        "🙌 Радий вітати вас тут!\n"
        "👤 Мене звати Артем Козловський — засновник однієї з найбільших туристичних компаній в Україні — Enjoy the World (юридично — Клуб Датур).\n\n"
        "🌟 Що ми даємо агентам:\n"
        "✅ Доступи до європейських туроператорів і міжнародних систем 🌐\n"
        "✅ Миттєві валютні платежі 💶\n"
        "✅ Прямі кабінети для роботи 📝\n"
        "✅ Найвигідніші % на ринку 💸\n\n"
        "📂 Всі документи компанії — нижче\n"
        "💬 Відгуки партнерів та знайомство з командою — також під цим відео\n\n"
        "💪 Дякую за довіру та до зустрічі у світі туризму! 💼✈️"
    )
    
    # Отправка приветственного сообщения
    if is_callback:
        await update.callback_query.message.reply_text(welcome_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# 2. Кнопка "Хочу дізнатись більше"
async def more_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle more info button press."""
    query = update.callback_query
    await query.answer()
    
    # Создаем клавиатуру с кнопками 2.1
    keyboard = [
        [InlineKeyboardButton("👨‍💼 Цікавить навчання", callback_data="training_info")],
        [InlineKeyboardButton("📝 Відгуки", callback_data="testimonials")],
        [InlineKeyboardButton("📱 Соціальні мережі", callback_data="social_media")],
        [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")],
        [InlineKeyboardButton("💰 Оплатити курс WayForPay", url=PAYMENT_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем видео с описанием
    try:
        await query.message.reply_video(
            video=VIDEO_FILE_IDS["more_info"],
            caption=(
                "🛫 Злетай до мрії разом з нами!\n\n"
                "🔥 Що тебе чекає в курсі:\n"
                "💎 Всього 9€ — і ти вже на старті\n"
                "💎 Реальний досвід з 15+ років практики\n"
                "💎 Доступ до всіх систем бронювання та операторів\n"
                "💎 Особисті кабінети + підтримка команди\n"
                "💎 Чат-бот з AI, який допомагає 24/7\n"
                "💎 Можливість подорожувати, знімати контент і дарувати емоції ✨\n\n"
                "🚀 Почни прямо зараз — зроби перший крок до нової реальності!"
            ),
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error sending more_info video: {e}")
        await query.message.reply_text(
            "🛫 Злетай до мрії разом з нами!\n\n"
            "🔥 Що тебе чекає в курсі:\n"
            "💎 Всього 9€ — і ти вже на старті\n"
            "💎 Реальний досвід з 15+ років практики\n"
            "💎 Доступ до всіх систем бронювання та операторів\n"
            "💎 Особисті кабінети + підтримка команди\n"
            "💎 Чат-бот з AI, який допомагає 24/7\n"
            "💎 Можливість подорожувати, знімати контент і дарувати емоції ✨\n\n"
            "🚀 Почни прямо зараз — зроби перший крок до нової реальності!",
            reply_markup=reply_markup
        )

# 3. Кнопка "Про що цей курс"
async def about_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle about course button press."""
    query = update.callback_query
    await query.answer()
    
    # Сбрасываем индекс видео для агента
    context.user_data["agent_video_index"] = 0
    
    # Отправляем первое видео для агентов
    await send_agent_video(update, context)

# Функция отправки видео для агентов
async def send_agent_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send agent video based on the current index."""
    query = update.callback_query
    index = context.user_data.get("agent_video_index", 0)
    
    # Проверяем, что индекс в пределах массива
    if index >= len(AGENT_VIDEO_IDS):
        await query.message.reply_text("Всі відео вже переглянуті.")
        return
    
    # Отправляем видео без описания
    try:
        await query.message.reply_video(video=AGENT_VIDEO_IDS[index])
        
        # Отправляем описание ОТДЕЛЬНЫМ сообщением
        description = AGENT_DESCRIPTIONS[index]
        
        keyboard = [
            [InlineKeyboardButton("▶️ Наступне відео", callback_data="next_agent_video")],
            [InlineKeyboardButton("👨‍💼 Хочу дізнатись більше", callback_data="more_info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(description, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error sending agent video: {e}")
        await query.message.reply_text(
            f"Не вдалося відправити відео. Спробуйте ще раз або зв'яжіться з підтримкою."
        )

# Обработка кнопки "Следующее видео" для агентов
async def next_agent_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle next agent video button press."""
    query = update.callback_query
    await query.answer()
    
    # Увеличиваем индекс видео
    current_index = context.user_data.get("agent_video_index", 0)
    next_index = current_index + 1
    
    # Сохраняем новый индекс
    context.user_data["agent_video_index"] = next_index
    
    # Отправляем следующее видео
    await send_agent_video(update, context)

# 4. Кнопка "Документи"
async def documents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle documents button press."""
    query = update.callback_query
    await query.answer()
    
    # Отправляем документы
    for doc_id in DOCUMENT_FILE_IDS:
        try:
            await query.message.reply_document(document=doc_id)
        except Exception as e:
            logger.error(f"Error sending document: {e}")
            await query.message.reply_text("Не вдалося відправити документ. Спробуйте пізніше.")
    
    # Отправляем сообщение с кнопкой навчання -> more_info (2.1)
    keyboard = [
        [InlineKeyboardButton("👨‍💼 Навчання", callback_data="more_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "Усі документи компанії. Для повернення в меню натисніть кнопку нижче:",
        reply_markup=reply_markup
    )

# 5. Кнопка "Відгуки"
async def testimonials(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle testimonials button press."""
    query = update.callback_query
    await query.answer()
    
    # Сбрасываем индекс отзыва
    context.user_data["testimonial_index"] = 0
    
    # Отправляем заголовок
    await query.message.reply_text("💙 Цінуємо всіх наших учнів! 💛")
    
    # Отправляем первый отзыв
    await send_testimonial(update, context)

# Функция отправки отзыва
async def send_testimonial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a testimonial based on the current index."""
    query = update.callback_query
    index = context.user_data.get("testimonial_index", 0)
    
    # Подготавливаем кнопки в зависимости от индекса отзыва
    if index < 7:  # Не последний отзыв (для первых 7 отзывов)
        keyboard = [
            [InlineKeyboardButton("😊 Більше відгуків", callback_data=f"testimonial_{index+1}")],
            [InlineKeyboardButton("👨‍💼 Навчання", callback_data="more_info"),
             InlineKeyboardButton("💰 Оплатити", callback_data="training_info")]
        ]
    else:  # Последний отзыв
        keyboard = [
            [InlineKeyboardButton("👨‍💼 Навчання", callback_data="more_info"),
             InlineKeyboardButton("💰 Оплатити", callback_data="training_info")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        # Отправка обычных отзывов (индексы 0-4)
        if index < 5:
            await query.message.reply_video(
                video=TESTIMONIAL_FILE_IDS[index],
                reply_markup=reply_markup
            )
            
        # Отправка 6-го отзыва (специального)
        elif index == 5:
            await query.message.reply_video(
                video=VIDEO_FILE_IDS["separate_testimonial"],
                reply_markup=reply_markup
            )
            
        # Отправка 7-го отзыва (двойного)
        elif index == 6:
            # Отправляем первое видео без кнопок
            await query.message.reply_video(
                video=TESTIMONIAL_DOUBLE_FILE_IDS[0]
            )
            
            # Отправляем второе видео с кнопками
            await query.message.reply_video(
                video=TESTIMONIAL_DOUBLE_FILE_IDS[1],
                reply_markup=reply_markup
            )
            
        # Отправка 8-го отзыва (тройного)
        elif index == 7:
            # Отправляем первое видео без кнопок
            await query.message.reply_video(
                video=TESTIMONIAL_TRIPLE_FILE_IDS[0]
            )
            
            # Отправляем второе видео без кнопок
            await query.message.reply_video(
                video=TESTIMONIAL_TRIPLE_FILE_IDS[1]
            )
            
            # Отправляем третье видео с кнопками
            await query.message.reply_video(
                video=TESTIMONIAL_TRIPLE_FILE_IDS[2],
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error sending testimonial: {e}")
        await query.message.reply_text(
            "Не вдалося відправити відео. Спробуйте пізніше.",
            reply_markup=reply_markup
        )

# Обработчики для уникальных callback данных отзывов
async def testimonial_1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle testimonial_1 button press."""
    query = update.callback_query
    await query.answer()
    context.user_data["testimonial_index"] = 1
    await send_testimonial(update, context)

async def testimonial_2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle testimonial_2 button press."""
    query = update.callback_query
    await query.answer()
    context.user_data["testimonial_index"] = 2
    await send_testimonial(update, context)

async def testimonial_3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle testimonial_3 button press."""
    query = update.callback_query
    await query.answer()
    context.user_data["testimonial_index"] = 3
    await send_testimonial(update, context)

async def testimonial_4(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle testimonial_4 button press."""
    query = update.callback_query
    await query.answer()
    context.user_data["testimonial_index"] = 4
    await send_testimonial(update, context)

async def testimonial_5(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle testimonial_5 button press."""
    query = update.callback_query
    await query.answer()
    context.user_data["testimonial_index"] = 5
    await send_testimonial(update, context)

async def testimonial_6(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle testimonial_6 button press."""
    query = update.callback_query
    await query.answer()
    context.user_data["testimonial_index"] = 6
    await send_testimonial(update, context)

async def testimonial_7(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle testimonial_7 button press."""
    query = update.callback_query
    await query.answer()
    context.user_data["testimonial_index"] = 7
    await send_testimonial(update, context)

# 6. Кнопка "Задати питання"
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle ask question button press."""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(
        "Ви можете задати питання про курс або туристичний бізнес.\n"
        "Просто напишіть ваше питання в чат, і ми відповімо якнайшвидше."
    )

# 7. Кнопка "Цікавить навчання"
async def training_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle training info button press."""
    query = update.callback_query
    await query.answer()
    
    # Клавиатура с кнопками
    keyboard = [
        [InlineKeyboardButton("💰 Оплатити курс WayForPay", url=PAYMENT_LINK)],
        [InlineKeyboardButton("📝 Відгуки", callback_data="testimonials"), 
         InlineKeyboardButton("📄 Документи", callback_data="documents")],
        [InlineKeyboardButton("❓ Про що цей курс", callback_data="about_course")],
        [InlineKeyboardButton("🎁 Ексклюзив для турагентів✨", callback_data="i_am_agent")],
        [InlineKeyboardButton("📱 Соціальні мережі", callback_data="social_media")],
        [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Текст сообщения
    caption = (
        "🧳 Готові змінити своє життя через туризм?\n\n"
        "📌 Що ви отримаєте після оплати:\n"
        "💎 Зручна оплата: Apple Pay, Google Pay, PayPal, Wise, Revolut, криптовалюта\n"
        "💎 Миттєвий доступ до Telegram-каналу з практичними уроками\n"
        "💎 Навчання:\n"
        "   — Системи бронювання 🌐\n"
        "   — Маркетинг та контент 📱\n"
        "   — Досвід 15+ років в одній програмі\n"
        "💎 Доступ до міжнародних операторів та валютних рахунків\n"
        "💎 Понад 700 агентів по всьому світу вже з нами\n"
        "💎 Безкоштовні заявки від клієнтів та навички створення якісного контенту 📸\n\n"
        "💼 Це більше, ніж курс — це ваш новий старт!"
    )
    
    # Отправка видео с описанием
    try:
        await query.message.reply_video(
            video=VIDEO_FILE_IDS["training_info"],
            caption=caption,
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error sending training_info video: {e}")
        await query.message.reply_text(
            caption,
            reply_markup=reply_markup
        )

# 8.1 Подтверждение оплаты (через /start money)
async def payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle payment confirmation."""
    # Сохраняем информацию о покупке базового курса
    user_id = update.effective_user.id
    username = update.effective_user.username
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_data(user_id, username, "Не указан", timestamp, course_type="basic")
    
    # Клавиатура с кнопками выбора доступа к курсу
    keyboard = [
        [InlineKeyboardButton("📘 Отримати курс повністю", callback_data="full_course")],
        [InlineKeyboardButton("📗 Отримати поступово", callback_data="gradual_course")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Текст сообщения об успешной оплате
    await update.message.reply_text(
        "✅ Ваш платіж успішно підтверджено! 🚀\nВиберіть, як вам зручніше отримати матеріали:",
        reply_markup=reply_markup
    )

# 8.2 Подтверждение оплаты Pro курса (через /start money1)
async def pro_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Pro payment confirmation."""
    # Сохраняем информацию о покупке Pro курса
    user_id = update.effective_user.id
    username = update.effective_user.username
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_data(user_id, username, "Не указан", timestamp, course_type="pro")
    
    # Клавиатура с кнопками выбора доступа к Pro курсу
    keyboard = [
        [InlineKeyboardButton("📘 Отримати курс повністю", callback_data="pro_full_course")],
        [InlineKeyboardButton("📗 Отримати поступово", callback_data="pro_gradual_course")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправка сообщения об успешной оплате Pro курса
    await update.message.reply_text(
        "Вітаю, ви придбали курс Pro",
        reply_markup=reply_markup
    )

# 8.3 Подтверждение оплаты (через сообщение об успешной оплате)
async def payment_success(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle successful payment message."""
    # Сохраняем информацию о покупке базового курса
    user_id = update.effective_user.id
    username = update.effective_user.username
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_data(user_id, username, "Не указан", timestamp, course_type="basic")
    
    # Клавиатура с кнопками выбора доступа к курсу
    keyboard = [
        [InlineKeyboardButton("📘 Отримати курс повністю", callback_data="full_course")],
        [InlineKeyboardButton("📗 Отримати поступово", callback_data="gradual_course")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Текст сообщения об успешной оплате
    await update.message.reply_text(
        "✅ Ваш платіж успішно підтверджено! 🚀\nВиберіть, як вам зручніше отримати матеріали:",
        reply_markup=reply_markup
    )

# 9. Получение курса полностью
async def full_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle full course access button press."""
    query = update.callback_query
    await query.answer()
    
    # Сохраняем контекст для правильного возврата при переходе в отзывы турагентов
    context.user_data["return_to_full_course"] = True
    
    # Подготовка текста со всеми ссылками на видео
    course_text = (
        "Ось твій курс 📘\n"
        "Ці 5 відео допоможуть тобі розібратися в усьому кроці за кроком. "
        "Переглядай їх у зручному темпі — головне не поспішай і одразу застосовуй знання на практиці! ✏\n\n"
    )
    
    # Добавляем ссылки на все видео
    for i, video_url in enumerate(COURSE_VIDEOS, 1):
        course_text += f"📹 Відео {i}: {video_url}\n"
    
    # Клавиатура с кнопками
    keyboard = [
        [InlineKeyboardButton("✅ Я пройшов / пройшла курс", callback_data="course_completed")],
        [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")],
        [InlineKeyboardButton("📱 Соціальні мережі", callback_data="social_media")],
        [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправка сообщения со всеми видео
    await query.message.reply_text(course_text, reply_markup=reply_markup)

# 10. Получение курса постепенно
async def gradual_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle gradual course access button press."""
    query = update.callback_query
    await query.answer()
    
    # Сбрасываем индекс видео
    context.user_data["video_index"] = 0
    
    # Клавиатура с кнопкой "Следующее видео"
    keyboard = [
        [InlineKeyboardButton("▶️ Наступне відео", callback_data="next_video")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправка первого видео
    await query.message.reply_text(
        f"Чудово, давай розпочнемо курс поступово 📘\n"
        f"Ось твоє перше відео — переглянь уважно, і як тільки закінчиш, натисни кнопку \"▶️ Наступне відео\". "
        f"Усього буде 5 відео, тож рухаємося крок за кроком 🚶 🚶\n"
        f"📹 Відео 1: {COURSE_VIDEOS[0]}",
        reply_markup=reply_markup
    )

# Обработка кнопки "Следующее видео" для постепенного курса
async def next_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle next video button press."""
    query = update.callback_query
    await query.answer()
    
    # Увеличиваем индекс видео
    current_index = context.user_data.get("video_index", 0)
    next_index = current_index + 1
    
    # Проверяем, что индекс в пределах массива
    if next_index >= len(COURSE_VIDEOS):
        await query.message.reply_text("Всі відео переглянуті.")
        return
    
    # Сохраняем индекс
    context.user_data["video_index"] = next_index
    
    # Формируем текст для сообщения
    if next_index == 1:  # Для второго видео добавляем дополнительный текст
        text = (
            f"📹 Відео {next_index + 1}: {COURSE_VIDEOS[next_index]}\n\n"
            f"YouTube\n"
            f"Відео {next_index + 1}\n\n"
            f"#{next_index + 1}\n\n"
            f"😌 Втомився під час навчання? Ми підберемо для тебе ідеальний відпочинок! 🌴✨ Пиши нам – і допоможемо перезавантажитися! 💬"
        )
        
        # Кнопки для второго видео - добавляем подбор отеля
        keyboard = [
            [InlineKeyboardButton("▶️ Наступне відео", callback_data="next_video")],
            [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")]
        ]
    elif next_index == 3:  # Для четвертого видео (индекс 3)
        text = (
            f"📹 Відео {next_index + 1}: {COURSE_VIDEOS[next_index]}\n\n"
            f"YouTube\n"
            f"Відео {next_index + 1}\n\n"
            f"#{next_index + 1}"
        )
        
        # Сохраняем контекст для правильного возврата при переходе в отзывы турагентов
        context.user_data["return_to_basic_course"] = True
        
        # Кнопки для четвертого видео
        keyboard = [
            [InlineKeyboardButton("▶️ Наступне відео", callback_data="next_video")],
            [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")]
        ]
    else:
        text = (
            f"📹 Відео {next_index + 1}: {COURSE_VIDEOS[next_index]}\n\n"
            f"YouTube\n"
            f"Відео {next_index + 1}\n\n"
            f"#{next_index + 1}"
        )
        
        # Подготавливаем кнопки в зависимости от индекса
        if next_index < len(COURSE_VIDEOS) - 1:  # Не последнее видео
            keyboard = [
                [InlineKeyboardButton("▶️ Наступне відео", callback_data="next_video")]
            ]
        else:  # Последнее видео
            # Сохраняем контекст для правильного возврата при переходе в отзывы турагентов
            context.user_data["return_to_basic_course"] = True
            
            # Добавляем кнопки к последнему видео
            keyboard = [
                [InlineKeyboardButton("✅ Я пройшов / пройшла курс", callback_data="course_completed")],
                [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")],
                [InlineKeyboardButton("📱 Соціальні мережі", callback_data="social_media")],
                [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")]
            ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправка видео
    await query.message.reply_text(text, reply_markup=reply_markup)

# 11. Получение Pro курса полностью
async def pro_full_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Pro full course access button press."""
    query = update.callback_query
    await query.answer()
    
    # Сохраняем контекст для правильного возврата при переходе в отзывы турагентов
    context.user_data["return_to_pro_full_course"] = True
    
    # Подготовка текста со всеми ссылками на видео
    course_text = (
        "Ось ваш Pro курс 📘\n"
        "Ці 11 відео допоможуть тобі розібратися в усьому кроці за кроком. "
        "Переглядай їх у зручному темпі — головне не поспішай і одразу застосовуй знання на практиці! ✏\n\n"
    )
    
    # Добавляем ссылки на все видео
    for i, video_url in enumerate(PRO_COURSE_VIDEOS, 1):
        course_text += f"📹 Відео {i}: {video_url}\n"
    
    # Клавиатура с кнопками
    keyboard = [
        [InlineKeyboardButton("👨‍💼 Цікавить співпраця", callback_data="request_contact")],
        [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")],
        [InlineKeyboardButton("📱 Соціальні мережі", callback_data="social_media")],
        [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправка сообщения со всеми видео
    await query.message.reply_text(course_text, reply_markup=reply_markup)

# 12. Получение Pro курса постепенно
async def pro_gradual_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Pro gradual course access button press."""
    query = update.callback_query
    await query.answer()
    
    # Сбрасываем индекс видео
    context.user_data["pro_video_index"] = 0
    
    # Клавиатура с кнопкой "Следующее видео"
    keyboard = [
        [InlineKeyboardButton("▶️ Наступне відео", callback_data="next_pro_video")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправка первого видео
    await query.message.reply_text(
        f"Чудово, давай розпочнемо Pro курс поступово 📘\n"
        f"Ось твоє перше відео — переглянь уважно, і як тільки закінчиш, натисни кнопку \"▶️ Наступне відео\". \n"
        f"Усього буде 11 відео, тож рухаємося крок за кроком 🚶 🚶\n"
        f"📹 Відео 1: {PRO_COURSE_VIDEOS[0]}",
        reply_markup=reply_markup
    )

# Обработка кнопки "Следующее видео" для постепенного Pro курса
async def next_pro_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle next pro video button press."""
    query = update.callback_query
    await query.answer()
    
    # Увеличиваем индекс видео
    current_index = context.user_data.get("pro_video_index", 0)
    next_index = current_index + 1
    
    # Проверяем, что индекс в пределах массива
    if next_index >= len(PRO_COURSE_VIDEOS):
        await query.message.reply_text("Всі відео переглянуті.")
        return
    
    # Сохраняем индекс
    context.user_data["pro_video_index"] = next_index
    
    # Формируем текст для сообщения
    text = (
        f"📹 Відео {next_index + 1}: {PRO_COURSE_VIDEOS[next_index]}\n\n"
        f"YouTube\n"
        f"Відео {next_index + 1}\n\n"
        f"#{next_index + 1}"
    )
    
    # Подготавливаем кнопки в зависимости от индекса
    if next_index < len(PRO_COURSE_VIDEOS) - 1:  # Не последнее видео
        keyboard = [
            [InlineKeyboardButton("▶️ Наступне відео", callback_data="next_pro_video")],
            [InlineKeyboardButton("👨‍💼 Цікавить співпраця", callback_data="request_contact")]
        ]
    else:  # Последнее видео
        # Сохраняем контекст для правильного возврата при переходе в отзывы турагентов
        context.user_data["return_to_pro_course"] = True
        
        keyboard = [
            [InlineKeyboardButton("👨‍💼 Цікавить співпраця", callback_data="request_contact")],
            [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")],
            [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправка видео
    await query.message.reply_text(text, reply_markup=reply_markup)

# 13.1 Завершение основного курса
async def course_completed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle course completed button press."""
    query = update.callback_query
    await query.answer()
    
    # Сохраняем контекст для правильного возврата при переходе в отзывы турагентов
    context.user_data["return_to_basic_course"] = True
    
    try:
        # Сначала отправляем видео
        await query.message.reply_video(video=VIDEO_FILE_IDS["course_completed"])
        
        # Клавиатура с кнопкой для Pro курса и дополнительными кнопками
        keyboard = [
            [InlineKeyboardButton("💰 Оплатити Pro курс", url=PRO_PAYMENT_LINK)],
            [InlineKeyboardButton("📱 Соціальні мережі", callback_data="social_media")],
            [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")],
            [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Текст поздравления
        await query.message.reply_text(
            "🎯 Наступний крок — це курс \"Pro\", де ти отримаєш:\n"
            "🔑 Доступ до двох систем інтеграції туроператорів.\n"
            "📊 Прямі кабінети, підвищені комісії та правила роботи з сайтами операторів.\n"
            "🏨 Систему бронювання готелів (конкурентну з Booking).\n"
            "✈️ Систему бронювання авіаквитків.\n"
            "💻 Інструменти для швидкого підбору туру з будь-якої точки світу.\n"
            "🚀 Додатково:\n"
            "🌟 Розвиток бренду.\n"
            "📱 Заявки із соцмереж безкоштовно.\n"
            "🤝 Постійну підтримку нашої команди.",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in course_completed: {e}")
        
        # Если произошла ошибка с видео, все равно отправим текст
        keyboard = [
            [InlineKeyboardButton("💰 Оплатити Pro курс", url=PRO_PAYMENT_LINK)],
            [InlineKeyboardButton("📱 Соціальні мережі", callback_data="social_media")],
            [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")],
            [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            "🎯 Наступний крок — це курс \"Pro\", де ти отримаєш:\n"
            "🔑 Доступ до двох систем інтеграції туроператорів.\n"
            "📊 Прямі кабінети, підвищені комісії та правила роботи з сайтами операторів.\n"
            "🏨 Систему бронювання готелів (конкурентну з Booking).\n"
            "✈️ Систему бронювання авіаквитків.\n"
            "💻 Інструменти для швидкого підбору туру з будь-якої точки світу.\n"
            "🚀 Додатково:\n"
            "🌟 Розвиток бренду.\n"
            "📱 Заявки із соцмереж безкоштовно.\n"
            "🤝 Постійну підтримку нашої команди.",
            reply_markup=reply_markup
        )

# 13.2 Завершение Pro курса
async def pro_course_completed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Pro course completed button press."""
    query = update.callback_query
    await query.answer()
    
    # Сохраняем контекст для правильного возврата при переходе в отзывы турагентов
    context.user_data["return_to_pro_course"] = True
    
    # Клавиатура с кнопками
    keyboard = [
        [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправка поздравления с завершением Pro курса
    await query.message.reply_text(
        "🎉 Вітаємо з успішним завершенням Pro курсу!\n"
        "Тепер ви маєте всі необхідні знання та інструменти для успішної роботи в туристичному бізнесі.\n"
        "Бажаємо великих успіхів та високих комісій!",
        reply_markup=reply_markup
    )

# 14. Кнопка "🎁 Ексклюзив для турагентів✨"
async def i_am_agent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle exclusive for agents button press."""
    query = update.callback_query
    await query.answer()
    
    # Сбрасываем индекс видео и сохраняем контекст для правильного возврата
    context.user_data["course_video_index"] = 0
    context.user_data["return_to_agent_info"] = True
    
    # Отправляем первое видео
    await send_course_video(update, context)

# Функция отправки видео курса
async def send_course_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a course video based on the current index."""
    query = update.callback_query
    index = context.user_data.get("course_video_index", 0)
    
    # Проверяем, что индекс в пределах массива
    if index >= len(COURSE_CIRCLE_VIDEO_IDS):
        await query.message.reply_text("Всі відео переглянуті.")
        return
    
    # Сначала отправляем видео без кнопок
    try:
        await query.message.reply_video(
            video=COURSE_CIRCLE_VIDEO_IDS[index]
        )
        
        # Подготавливаем кнопки в зависимости от индекса
        if index < len(COURSE_CIRCLE_VIDEO_IDS) - 1:  # Не последнее видео
            keyboard = [
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"),
                 InlineKeyboardButton("▶️ Наступне відео", callback_data="next_course_video")],
                [InlineKeyboardButton("🌟 Наші продукти", url="https://datour.club/#partners")],
                [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")],
                [InlineKeyboardButton("📜 Договір", callback_data="contract")],
                [InlineKeyboardButton("👨‍💼 Цікавить співпраця", callback_data="request_contact")]
            ]
        else:  # Последнее видео - заменяем кнопку "Следующее видео" на "На початок"
            keyboard = [
                [InlineKeyboardButton("⏪ На початок ⏪", callback_data="back_to_main")],
                [InlineKeyboardButton("🌟 Наші продукти", url="https://datour.club/#partners")],
                [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")],
                [InlineKeyboardButton("📜 Договір", callback_data="contract")],
                [InlineKeyboardButton("👨‍💼 Цікавить співпраця", callback_data="request_contact")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем описание с кнопками
        await query.message.reply_text(
            COURSE_CIRCLE_DESCRIPTIONS[index],
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error sending course video: {e}")
        await query.message.reply_text(
            f"Не вдалося відправити відео курсу. Спробуйте ще раз або зв'яжіться з підтримкою."
        )

# Обработка кнопки "Следующее видео" в курсе для агентов
async def next_course_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle next course video button press."""
    query = update.callback_query
    await query.answer()
    
    # Увеличиваем индекс видео
    current_index = context.user_data.get("course_video_index", 0)
    next_index = current_index + 1
    
    if next_index < len(COURSE_CIRCLE_VIDEO_IDS):
        context.user_data["course_video_index"] = next_index
        await send_course_video(update, context)
    else:
        await query.message.reply_text("Всі відео переглянуті.")

# 15. Админ-панель
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать админ-панель для просмотра данных пользователей."""
    user_id = update.effective_user.id
    
    # Проверка, является ли пользователь администратором
    if not is_admin(user_id):
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return
    
    # Загружаем данные пользователей
    users_data = load_users_data()
    
    # Создаем клавиатуру с опциями админ-панели
    keyboard = [
        [InlineKeyboardButton("Співпраця", callback_data="admin_show_all")],
        [InlineKeyboardButton("📈 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("🔄 Оновити дані", callback_data="admin_refresh")],
        [InlineKeyboardButton("🏨 Підбір готелю", callback_data="admin_hotel_stats")],
        [InlineKeyboardButton("📣 Розсилка повідомлень", callback_data="admin_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🔐 Адмін-панель\n\n"
        f"Всього користувачів: {len(users_data)}\n"
        f"Виберіть опцію:",
        reply_markup=reply_markup
    )

# Обработка кнопок админ-панели
async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка кнопок админ-панели."""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Проверка, является ли пользователь администратором
    if not is_admin(user_id):
        await query.answer("У вас нет доступа к этой команде.", show_alert=True)
        return
    
    await query.answer()
    
    # Загружаем данные пользователей
    users_data = load_users_data()
    
    if query.data == "admin_show_all":
        # Показать всех пользователей
        if not users_data:
            await query.message.reply_text("Нет данных о пользователях.")
            return
        
        # Разбиваем данные пользователей на страницы по 10
        page = context.user_data.get("admin_page", 0)
        total_pages = (len(users_data) - 1) // 10 + 1
        
        # Подготавливаем текст для текущей страницы
        start_idx = page * 10
        end_idx = min(start_idx + 10, len(users_data))
        page_users = users_data[start_idx:end_idx]
        
        text = f"📊 Користувачі (Страница {page + 1}/{total_pages}):\n\n"
        for i, user in enumerate(page_users, start=1):
            text += (f"{start_idx + i}. @{user['username']} | "
                    f"{user['phone']} | ID: {user['id']} | "
                    f"{user['timestamp']}\n\n")
        
        # Кнопки навигации
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data="admin_prev_page"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("➡️ Вперед", callback_data="admin_next_page"))
        
        keyboard = [nav_buttons, [InlineKeyboardButton("🔙 Назад до меню", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(text, reply_markup=reply_markup)
    
    elif query.data == "admin_stats":
        # Показать статистику
        text = "📈 Статистика:\n\n"
        
        # Подсчет пользователей по типам курсов
        basic_users = sum(1 for user in users_data if user.get("course_type") == "basic")
        pro_users = sum(1 for user in users_data if user.get("course_type") == "pro")
        no_course_users = len(users_data) - basic_users - pro_users
        
        text += f"Всього користувачів: {len(users_data)}\n"
        text += f"Користувачів з базовим курсом: {basic_users}\n"
        text += f"Користувачів з Pro курсом: {pro_users}\n"
        text += f"Користувачів без курсів: {no_course_users}\n\n"
        
        # Подсчет пользователей по дням
        daily_stats = {}
        for user in users_data:
            date = user["timestamp"].split(" ")[0]
            daily_stats[date] = daily_stats.get(date, 0) + 1
        
        # Показываем статистику по дням
        text += "Користувачі по днях:\n"
        for date, count in sorted(daily_stats.items(), reverse=True):
            text += f"{date}: {count} користувачів\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад до меню", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(text, reply_markup=reply_markup)
    
    elif query.data == "admin_hotel_stats":
        # Показать пользователей, запросивших подбор отеля
        hotel_users = [user for user in users_data if user.get("action_type") == "hotel_selection"]
        
        if not hotel_users:
            text = "Немає користувачів, які запитували підбір готелю."
        else:
            text = f"📊 Користувачі, які запитували підбір готелю ({len(hotel_users)}):\n\n"
            for i, user in enumerate(hotel_users, start=1):
                text += (f"{i}. @{user['username']} | "
                        f"{user['phone']} | ID: {user['id']} | "
                        f"{user['timestamp']}\n\n")
        
        keyboard = [[InlineKeyboardButton("🔙 Назад до меню", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(text, reply_markup=reply_markup)
    
    elif query.data == "admin_refresh":
        # Обновить данные
        keyboard = [
            [InlineKeyboardButton("Співпраця", callback_data="admin_show_all")],
            [InlineKeyboardButton("📈 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("🔄 Оновити дані", callback_data="admin_refresh")],
            [InlineKeyboardButton("🏨 Підбір готелю", callback_data="admin_hotel_stats")],
            [InlineKeyboardButton("📣 Розсилка повідомлень", callback_data="admin_broadcast")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            f"🔐 Адмін-панель\n\n"
            f"Всього користувачів: {len(users_data)}\n"
            f"Данные обновлены: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Виберіть опцію:",
            reply_markup=reply_markup
        )
    
    elif query.data == "admin_prev_page":
        # Предыдущая страница
        context.user_data["admin_page"] = max(0, context.user_data.get("admin_page", 0) - 1)
        # Вызываем показ всех пользователей снова
        query.data = "admin_show_all"
        await admin_buttons(update, context)
    
    elif query.data == "admin_next_page":
        # Следующая страница
        total_pages = (len(users_data) - 1) // 10 + 1
        context.user_data["admin_page"] = min(total_pages - 1, context.user_data.get("admin_page", 0) + 1)
        # Вызываем показ всех пользователей снова
        query.data = "admin_show_all"
        await admin_buttons(update, context)
    
    elif query.data == "admin_back":
        # Возврат в главное меню админ-панели
        context.user_data["admin_page"] = 0
        keyboard = [
            [InlineKeyboardButton("Співпраця", callback_data="admin_show_all")],
            [InlineKeyboardButton("📈 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("🔄 Оновити дані", callback_data="admin_refresh")],
            [InlineKeyboardButton("🏨 Підбір готелю", callback_data="admin_hotel_stats")],
            [InlineKeyboardButton("📣 Розсилка повідомлень", callback_data="admin_broadcast")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            f"🔐 Адмін-панель\n\n"
            f"Всього користувачів: {len(users_data)}\n"
            f"Виберіть опцію:",
            reply_markup=reply_markup
        )
    
    elif query.data == "admin_broadcast":
        # Запуск процесса рассылки
        await start_broadcast(update, context)

# Рассылка сообщений администратором
async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает процесс рассылки сообщений."""
    query = update.callback_query
    if query:
        await query.answer()
    
    # Загружаем данные пользователей для статистики
    users_data = load_users_data()
    
    # Подсчет пользователей по типам курсов
    basic_users = sum(1 for user in users_data if user.get("course_type") == "basic")
    pro_users = sum(1 for user in users_data if user.get("course_type") == "pro")
    no_course_users = len(users_data) - basic_users - pro_users
    
    # Создаем клавиатуру для выбора целевой аудитории
    keyboard = [
        [InlineKeyboardButton(f"Базовий курс ({basic_users})", callback_data="target_basic")],
        [InlineKeyboardButton(f"Pro курс ({pro_users})", callback_data="target_pro")],
        [InlineKeyboardButton(f"Без курсів ({no_course_users})", callback_data="target_none")],
        [InlineKeyboardButton(f"Всі користувачі ({len(users_data)})", callback_data="target_all")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="broadcast_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Если это вызов из callback, изменяем существующее сообщение
    if query:
        await query.message.edit_text(
            "Виберіть цільову аудиторію для розсилки:",
            reply_markup=reply_markup
        )
    else:  # Иначе отправляем новое сообщение (вызов из командной строки)
        await update.message.reply_text(
            "Виберіть цільову аудиторію для розсилки:",
            reply_markup=reply_markup
        )
    
    return BROADCAST_TARGET

async def broadcast_target_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор целевой аудитории для рассылки."""
    query = update.callback_query
    await query.answer()
    
    target_data = query.data.replace("target_", "")
    context.user_data["broadcast_target"] = target_data
    
    # Определяем текст в зависимости от выбранной аудитории
    target_text = {
        "basic": "користувачів з базовим курсом",
        "pro": "користувачів з Pro курсом",
        "none": "користувачів без курсів",
        "all": "всіх користувачів"
    }.get(target_data, "обрану аудиторію")
    
    # Создаем клавиатуру для выбора типа контента
    keyboard = [
        [InlineKeyboardButton("📝 Текст", callback_data="content_type_text")],
        [InlineKeyboardButton("🖼 Фото", callback_data="content_type_photo")],
        [InlineKeyboardButton("🎬 Відео", callback_data="content_type_video")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="broadcast_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        f"Обрана аудиторія: {target_text}\n\n"
        "Виберіть тип контенту для розсилки:",
        reply_markup=reply_markup
    )
    
    return BROADCAST_CONTENT_TYPE

async def broadcast_content_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор типа контента для рассылки."""
    query = update.callback_query
    await query.answer()
    
    content_type = query.data.replace("content_type_", "")
    context.user_data["broadcast_content_type"] = content_type
    
    # В зависимости от выбранного типа контента
    if content_type == "text":
        await query.message.edit_text(
            "Введіть текст повідомлення для розсилки:\n\n"
            "Для скасування введіть /cancel"
        )
        return BROADCAST_TEXT
    
    elif content_type == "photo":
        await query.message.edit_text(
            "Надішліть фото з підписом для розсилки:\n\n"
            "Для скасування введіть /cancel"
        )
        return BROADCAST_PHOTO
    
    elif content_type == "video":
        await query.message.edit_text(
            "Надішліть відео з підписом для розсилки:\n\n"
            "Для скасування введіть /cancel"
        )
        return BROADCAST_VIDEO
    
    # Если выбран неизвестный тип контента, отменяем рассылку
    await query.message.edit_text("Невідомий тип контенту. Розсилку скасовано.")
    return ConversationHandler.END

async def broadcast_text_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает получение текста для рассылки."""
    message_text = update.message.text
    context.user_data["broadcast_text"] = message_text
    
    # Определяем текст в зависимости от выбранной аудитории
    target_data = context.user_data.get("broadcast_target", "all")
    target_text = {
        "basic": "користувачів з базовим курсом",
        "pro": "користувачів з Pro курсом",
        "none": "користувачів без курсів",
        "all": "всіх користувачів"
    }.get(target_data, "обрану аудиторію")
    
    # Создаем клавиатуру для подтверждения
    keyboard = [
        [InlineKeyboardButton("✅ Підтвердити", callback_data="broadcast_confirm")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="broadcast_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Повідомлення для розсилки для {target_text}:\n\n"
        f"{message_text}\n\n"
        "Підтвердіть відправку:",
        reply_markup=reply_markup
    )
    
    return BROADCAST_CONFIRM

async def broadcast_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает получение фото для рассылки."""
    photo = update.message.photo[-1]  # Получаем фото с максимальным размером
    caption = update.message.caption or ""
    
    # Сохраняем данные фото в контексте пользователя
    context.user_data["broadcast_photo_id"] = photo.file_id
    context.user_data["broadcast_caption"] = caption
    
    # Определяем текст в зависимости от выбранной аудитории
    target_data = context.user_data.get("broadcast_target", "all")
    target_text = {
        "basic": "користувачів з базовим курсом",
        "pro": "користувачів з Pro курсом",
        "none": "користувачів без курсів",
        "all": "всіх користувачів"
    }.get(target_data, "обрану аудиторію")
    
    # Создаем клавиатуру для подтверждения
    keyboard = [
        [InlineKeyboardButton("✅ Підтвердити", callback_data="broadcast_confirm")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="broadcast_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем фото с кнопками подтверждения
    await update.message.reply_photo(
        photo=photo.file_id,
        caption=f"Фото для розсилки для {target_text} з підписом:\n\n{caption}\n\nПідтвердіть відправку:",
        reply_markup=reply_markup
    )
    
    return BROADCAST_CONFIRM

async def broadcast_video_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает получение видео для рассылки."""
    video = update.message.video
    caption = update.message.caption or ""
    
    # Сохраняем данные видео в контексте пользователя
    context.user_data["broadcast_video_id"] = video.file_id
    context.user_data["broadcast_caption"] = caption
    
    # Определяем текст в зависимости от выбранной аудитории
    target_data = context.user_data.get("broadcast_target", "all")
    target_text = {
        "basic": "користувачів з базовим курсом",
        "pro": "користувачів з Pro курсом",
        "none": "користувачів без курсів",
        "all": "всіх користувачів"
    }.get(target_data, "обрану аудиторію")
    
    # Создаем клавиатуру для подтверждения
    keyboard = [
        [InlineKeyboardButton("✅ Підтвердити", callback_data="broadcast_confirm")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="broadcast_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем видео с кнопками подтверждения
    await update.message.reply_video(
        video=video.file_id,
        caption=f"Відео для розсилки для {target_text} з підписом:\n\n{caption}\n\nПідтвердіть відправку:",
        reply_markup=reply_markup
    )
    
    return BROADCAST_CONFIRM

async def broadcast_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Подтверждает и выполняет рассылку сообщений."""
    query = update.callback_query
    await query.answer()
    
    target_data = context.user_data.get("broadcast_target", "all")
    content_type = context.user_data.get("broadcast_content_type", "text")
    
    # Загружаем данные пользователей
    users_data = load_users_data()
    
    # Фильтруем пользователей в зависимости от целевой аудитории
    if target_data == "basic":
        recipients = [user for user in users_data if user.get("course_type") == "basic"]
    elif target_data == "pro":
        recipients = [user for user in users_data if user.get("course_type") == "pro"]
    elif target_data == "none":
        recipients = [user for user in users_data if not user.get("course_type")]
    else:  # all
        recipients = users_data
    
    # Создаем клавиатуру с кнопкой отмены
    keyboard = [
        [InlineKeyboardButton("❌ Відмінити розсилку", callback_data="broadcast_cancel_confirm")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Предупреждаем пользователя о начале рассылки
    await query.message.edit_text(
        f"Увага! Розсилка буде відправлена {len(recipients)} користувачам.\n\n"
        "Ви впевнені, що хочете продовжити?\n\n"
        "Ви зможете скасувати розсилку під час процесу, натиснувши кнопку 'Відмінити розсилку'.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Продовжити розсилку", callback_data="continue_broadcast")],
            [InlineKeyboardButton("❌ Відмінити розсилку", callback_data="broadcast_cancel_confirm")]
        ])
    )
    
    return BROADCAST_CONFIRM

async def continue_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Выполняет рассылку сообщений."""
    query = update.callback_query
    await query.answer()
    
    target_data = context.user_data.get("broadcast_target", "all")
    content_type = context.user_data.get("broadcast_content_type", "text")
    
    # Загружаем данные пользователей
    users_data = load_users_data()
    
    # Фильтруем пользователей в зависимости от целевой аудитории
    if target_data == "basic":
        recipients = [user for user in users_data if user.get("course_type") == "basic"]
    elif target_data == "pro":
        recipients = [user for user in users_data if user.get("course_type") == "pro"]
    elif target_data == "none":
        recipients = [user for user in users_data if not user.get("course_type")]
    else:  # all
        recipients = users_data
    
    # Создаем клавиатуру с кнопкой отмены
    keyboard = [
        [InlineKeyboardButton("❌ Відмінити розсилку", callback_data="broadcast_cancel_confirm")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Сообщение о начале рассылки
    status_message = await query.message.edit_text(
        "Розсилка в процесі...\n"
        "0% виконано (0/%d)\n\n"
        "✅ Успішно відправлено: 0\n"
        "❌ Не вдалося відправити: 0\n\n"
        "Ви можете скасувати розсилку, натиснувши кнопку нижче:" % len(recipients),
        reply_markup=reply_markup
    )
    
    # Флаг отмены рассылки
    context.user_data["broadcast_cancelled"] = False
    
    # Счетчики
    sent_count = 0
    failed_count = 0
    
    # Отправляем сообщения
    for i, user in enumerate(recipients):
        # Проверяем не отменена ли рассылка
        if context.user_data.get("broadcast_cancelled"):
            skipped_count = len(recipients) - i
            await status_message.edit_text(
                f"Розсилка скасована користувачем!\n\n"
                f"✅ Успішно відправлено: {sent_count}\n"
                f"❌ Не вдалося відправити: {failed_count}\n"
                f"⏸ Пропущено: {skipped_count}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад до меню", callback_data="admin_back")
                ]])
            )
            return ConversationHandler.END
        
        try:
            # Отправка в зависимости от типа контента
            if content_type == "text":
                broadcast_text = context.user_data.get("broadcast_text", "")
                await context.bot.send_message(
                    chat_id=user["id"],
                    text=broadcast_text
                )
            elif content_type == "photo":
                photo_id = context.user_data.get("broadcast_photo_id", "")
                caption = context.user_data.get("broadcast_caption", "")
                await context.bot.send_photo(
                    chat_id=user["id"],
                    photo=photo_id,
                    caption=caption
                )
            elif content_type == "video":
                video_id = context.user_data.get("broadcast_video_id", "")
                caption = context.user_data.get("broadcast_caption", "")
                await context.bot.send_video(
                    chat_id=user["id"],
                    video=video_id,
                    caption=caption
                )
            
            sent_count += 1
        except Exception as e:
            logger.error(f"Error sending broadcast to user {user['id']}: {e}")
            failed_count += 1
        
        # Обновляем статус каждые 5 отправленных сообщений или для последнего
        if (i + 1) % 5 == 0 or i + 1 == len(recipients):
            progress = ((i + 1) / len(recipients) * 100)
            await status_message.edit_text(
                f"Розсилка в процесі...\n"
                f"{progress:.1f}% виконано ({i+1}/{len(recipients)})\n\n"
                f"✅ Успішно відправлено: {sent_count}\n"
                f"❌ Не вдалося відправити: {failed_count}\n\n"
                f"Ви можете скасувати розсилку, натиснувши кнопку нижче:",
                reply_markup=reply_markup
            )
    
    # Сообщение о завершении рассылки
    await status_message.edit_text(
        f"Розсилка завершена!\n\n"
        f"✅ Успішно відправлено: {sent_count}\n"
        f"❌ Не вдалося відправити: {failed_count}",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Назад до меню", callback_data="admin_back")
        ]])
    )
    
    return ConversationHandler.END

async def broadcast_cancel_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет активную рассылку."""
    query = update.callback_query
    await query.answer()
    
    # Устанавливаем флаг отмены рассылки
    context.user_data["broadcast_cancelled"] = True
    
    await query.message.edit_text(
        "Розсилка буде скасована після завершення поточного повідомлення..."
    )
    
    return ConversationHandler.END

async def broadcast_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет процесс создания рассылки."""
    query = update.callback_query
    await query.answer()
    
    # Очищаем данные рассылки
    context.user_data.pop("broadcast_target", None)
    context.user_data.pop("broadcast_content_type", None)
    context.user_data.pop("broadcast_text", None)
    context.user_data.pop("broadcast_photo_id", None)
    context.user_data.pop("broadcast_video_id", None)
    context.user_data.pop("broadcast_caption", None)
    
    await query.message.edit_text(
        "Розсилку скасовано.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Назад до меню", callback_data="admin_back")
        ]])
    )
    
    return ConversationHandler.END

# Команда для запуска рассылки
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /broadcast для запуска рассылки."""
    user_id = update.effective_user.id
    
    # Проверка, является ли пользователь администратором
    if not is_admin(user_id):
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return ConversationHandler.END
    
    # Начинаем процесс рассылки
    return await start_broadcast(update, context)

# 16. Социальные сети
async def social_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle social media button press."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Instagram", url="instagram.com/kozlovsky_official"),
         InlineKeyboardButton("YouTube", url="https://www.youtube.com/@Enjoy-World")],
        [InlineKeyboardButton("Telegram", url="t.me/EnjoybyAK"),
         InlineKeyboardButton("Viber", url="https://invite.viber.com/?g2=AQAdFXxYRdaujUjJrDmLqBUV0euxHSLFrEj34LGtzWmFdIZ8fq7avy%2FjLrlTBiNv&lang=ru")],
        [InlineKeyboardButton("🔙 Назад", callback_data="more_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "📱 Наші соціальні мережі:\n"
        "Підписуйтесь, щоб бути в курсі всіх новин",
        reply_markup=reply_markup
    )

# 17. Запрос контактных данных
# Функция для запроса номера телефона
async def request_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запрос номера телефона пользователя."""
    query = update.callback_query
    await query.answer()
    
    # Сохраняем данные пользователя при нажатии кнопки
    user_id = query.from_user.id
    username = query.from_user.username
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_data(user_id, username, "Не указан", timestamp, "request_contact")
    
    # Сохраняем URL для дальнейшего перехода
    context.user_data["next_url"] = "https://t.me/kozlovsky_official2"
    
    # Создаем клавиатуру с кнопкой запроса контакта
    keyboard = [[KeyboardButton("📱 Поділитися номером телефону", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await query.message.reply_text(
        "Для зв'язку з нашим представником, будь ласка, поділіться вашим номером телефону. \n"
        "Натисніть кнопку нижче:",
        reply_markup=reply_markup
    )
    
    return PHONE

# Функция для запроса номера телефона для подбора отеля
async def hotel_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запрос номера телефона для подбора отеля."""
    query = update.callback_query
    await query.answer()
    
    # Сохраняем данные пользователя при нажатии кнопки
    user_id = query.from_user.id
    username = query.from_user.username
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_data(user_id, username, "Не указан", timestamp, "hotel_selection")
    
    # Сохраняем URL для дальнейшего перехода
    context.user_data["next_url"] = "https://t.me/kozlovsky_official"
    context.user_data["action_type"] = "hotel_selection"
    
    # Создаем клавиатуру с кнопкой запроса контакта
    keyboard = [[KeyboardButton("📱 Поділитися номером телефону", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await query.message.reply_text(
        "Для зв'язку з Артемом щодо підбору готелю, будь ласка, поділіться вашим номером телефону. \n"
        "Натисніть кнопку нижче:",
        reply_markup=reply_markup
    )
    
    return PHONE

# Обработка полученного контакта
async def process_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка полученного контакта и переход к следующему шагу."""
    user = update.message.from_user
    phone_number = update.message.contact.phone_number
    
    # Сохраняем данные пользователя с учетом типа действия
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    action_type = context.user_data.get("action_type", None)
    save_user_data(user.id, user.username, phone_number, timestamp, action_type)
    
    # Определяем текст в зависимости от типа действия
    if action_type == "hotel_selection":
        message_text = "Дякуємо! Ваш номер телефону збережено. Зараз ви будете перенаправлені до Артема Козловського"
        button_text = "📞 Зв'язок з Артемом"
    else:
        message_text = "Дякуємо! Ваш номер телефону збережено. Зараз ви будете перенаправлені до нашого представника."
        button_text = "👨‍💼 Перейти до представника"
    
    # Сообщаем пользователю о переходе
    await update.message.reply_text(
        message_text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(button_text, url=context.user_data.get("next_url", "https://t.me/kozlovsky_official"))
        ]])
    )
    
    return ConversationHandler.END

# Отмена процесса запроса контакта
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена запроса контакта."""
    await update.message.reply_text(
        "Процес збору контактних даних скасовано.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("👨‍💼 Перейти до представника", url=context.user_data.get("next_url", "https://t.me/kozlovsky_official"))
        ]])
    )
    
    return ConversationHandler.END

# 18. Отзывы турагентов
async def agent_testimonials(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle agent testimonials button press."""
    query = update.callback_query
    await query.answer()
    
    # Устанавливаем индекс отзывов в 0
    context.user_data["agent_testimonial_index"] = 0
    
    # Сохраняем источник перехода для правильного возврата
    if query.data == "agent_testimonials":
        # Определяем источник перехода из контекста пользователя
        if context.user_data.get("return_to_full_course"):
            context.user_data["source"] = "basic_course"
        elif context.user_data.get("return_to_pro_full_course") or context.user_data.get("return_to_pro_course"):
            context.user_data["source"] = "pro_course"
        elif context.user_data.get("return_to_agent_info"):
            context.user_data["source"] = "agent_info"
    
    # Отправляем заголовок
    await query.message.reply_text("💬 Відгуки від наших партнерів-турагентів:")
    
    # Отправляем первый отзыв
    await send_agent_testimonial(update, context)

# Функция отправки отзыва турагента
async def send_agent_testimonial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send agent testimonial video based on the current index."""
    query = update.callback_query
    index = context.user_data.get("agent_testimonial_index", 0)
    
    # Проверяем, что индекс в пределах массива
    if index >= len(AGENT_TESTIMONIAL_VIDEO_IDS):
        await query.message.reply_text(
            "Всі відгуки переглянуті.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Повернутись", callback_data="back_to_source")
            ]])
        )
        return
    
    videos = AGENT_TESTIMONIAL_VIDEO_IDS[index]
    
    # Отправляем все видео отзыва
    for i, video_id in enumerate(videos):
        try:
            # Последнее видео с кнопками
            if i == len(videos) - 1:
                # Кнопки для последнего видео отзыва
                if index < len(AGENT_TESTIMONIAL_VIDEO_IDS) - 1:  # Не последний отзыв
                    keyboard = [
                        [InlineKeyboardButton("▶️ Наступний відгук", callback_data="next_agent_testimonial")],
                        [InlineKeyboardButton("🔙 Повернутись", callback_data="back_to_source")]
                    ]
                else:  # Последний отзыв
                    keyboard = [
                        [InlineKeyboardButton("🔙 Повернутись", callback_data="back_to_source")]
                    ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_video(video=video_id, reply_markup=reply_markup)
            else:
                # Промежуточные видео без кнопок
                await query.message.reply_video(video=video_id)
        except Exception as e:
            logger.error(f"Error sending agent testimonial video: {e}")
            await query.message.reply_text(
                f"Не вдалося відправити відео відгуку. Спробуйте ще раз або зв'яжіться з підтримкою."
            )

# Обработка кнопки "Следующий отзыв турагента"
async def next_agent_testimonial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle next agent testimonial button press."""
    query = update.callback_query
    await query.answer()
    
    # Увеличиваем индекс отзыва
    current_index = context.user_data.get("agent_testimonial_index", 0)
    next_index = current_index + 1
    
    # Сохраняем новый индекс
    context.user_data["agent_testimonial_index"] = next_index
    
    # Отправляем следующий отзыв
    await send_agent_testimonial(update, context)

# Функция для возврата к источнику перехода
async def back_to_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Возвращает пользователя к источнику перехода."""
    query = update.callback_query
    await query.answer()
    
    # Получаем источник перехода из контекста
    source = context.user_data.get("source", "")
    
    # Определяем функцию для вызова в зависимости от источника
    if source == "basic_course" and context.user_data.get("return_to_full_course"):
        # Возврат к полному курсу
        await full_course(update, context)
    elif source == "pro_course" and context.user_data.get("return_to_pro_full_course"):
        # Возврат к полному Pro курсу
        await pro_full_course(update, context)
    elif source == "agent_info" and context.user_data.get("return_to_agent_info"):
        # Возврат к информации для агентов
        await i_am_agent(update, context)
    else:
        # Если источник не определен, возвращаемся на главный экран
        await back_to_main(update, context)

# 19. Кнопка "📜 Договір"
async def contract(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle contract button press."""
    query = update.callback_query
    await query.answer()
    
    # Отправляем два документа
    for doc_id in CONTRACT_DOCUMENT_IDS:
        try:
            await query.message.reply_document(document=doc_id)
        except Exception as e:
            logger.error(f"Error sending contract document: {e}")
            await query.message.reply_text("Не вдалося відправити документ. Спробуйте пізніше.")
    
    # Отправляем кнопку для возврата на i_am_agent
    keyboard = [[InlineKeyboardButton("🔙 Повернутись", callback_data="i_am_agent")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text("Вище представлені документи договору.", reply_markup=reply_markup)

# 20. Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages."""
    text = update.message.text.lower()
    
    # Проверяем, может ли быть это сообщением об успешной оплате
    if "оплата" in text and "успішн" in text:
        await payment_success(update, context)
    else:
        # Отвечаем на любые другие текстовые сообщения простым текстом без кнопок
        await update.message.reply_text("AI асистент у розробці")

# 21. Возврат к началу
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle back to main button press."""
    query = update.callback_query
    await query.answer()
    
    # Вызываем функцию start с обновлением
    await start(update, context, is_callback=True)

# Главная функция запуска бота
def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Добавление ConversationHandler для запроса контактных данных
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(request_contact, pattern="^request_contact$"),
            CallbackQueryHandler(hotel_selection, pattern="^hotel_selection$")
        ],
        states={
            PHONE: [MessageHandler(filters.CONTACT, process_contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Добавление ConversationHandler для рассылки сообщений
    broadcast_handler = ConversationHandler(
        entry_points=[
            CommandHandler("broadcast", broadcast_command),
            CallbackQueryHandler(start_broadcast, pattern="^admin_broadcast$")
        ],
        states={
            BROADCAST_TARGET: [
                CallbackQueryHandler(broadcast_target_selected, pattern="^target_"),
                CallbackQueryHandler(broadcast_cancel, pattern="^broadcast_cancel$")
            ],
            BROADCAST_CONTENT_TYPE: [
                CallbackQueryHandler(broadcast_content_type_selected, pattern="^content_type_"),
                CallbackQueryHandler(broadcast_cancel, pattern="^broadcast_cancel$")
            ],
            BROADCAST_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_text_received)
            ],
            BROADCAST_PHOTO: [
                MessageHandler(filters.PHOTO, broadcast_photo_received)
            ],
            BROADCAST_VIDEO: [
                MessageHandler(filters.VIDEO, broadcast_video_received)
            ],
            BROADCAST_CONFIRM: [
                CallbackQueryHandler(broadcast_confirm, pattern="^broadcast_confirm$"),
                CallbackQueryHandler(continue_broadcast, pattern="^continue_broadcast$"),
                CallbackQueryHandler(broadcast_cancel, pattern="^broadcast_cancel$"),
                CallbackQueryHandler(broadcast_cancel_confirmation, pattern="^broadcast_cancel_confirm$")
            ],
        },
        fallbacks=[CommandHandler("cancel", broadcast_cancel)],
    )
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    
    # Add callback query handlers
    application.add_handler(CallbackQueryHandler(more_info, pattern="^more_info$"))
    application.add_handler(CallbackQueryHandler(training_info, pattern="^training_info$"))
    application.add_handler(CallbackQueryHandler(documents, pattern="^documents$"))
    application.add_handler(CallbackQueryHandler(testimonials, pattern="^testimonials$"))
    application.add_handler(CallbackQueryHandler(social_media, pattern="^social_media$"))
    
    # Add handlers for agent testimonials and contract
    application.add_handler(CallbackQueryHandler(agent_testimonials, pattern="^agent_testimonials$"))
    application.add_handler(CallbackQueryHandler(next_agent_testimonial, pattern="^next_agent_testimonial$"))
    application.add_handler(CallbackQueryHandler(back_to_source, pattern="^back_to_source$"))
    application.add_handler(CallbackQueryHandler(contract, pattern="^contract$"))
    
    # Add handler for back to main
    application.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))
    
    # Обработчики для отзывов с уникальными callback_data
    application.add_handler(CallbackQueryHandler(testimonial_1, pattern="^testimonial_1$"))
    application.add_handler(CallbackQueryHandler(testimonial_2, pattern="^testimonial_2$"))
    application.add_handler(CallbackQueryHandler(testimonial_3, pattern="^testimonial_3$"))
    application.add_handler(CallbackQueryHandler(testimonial_4, pattern="^testimonial_4$"))
    application.add_handler(CallbackQueryHandler(testimonial_5, pattern="^testimonial_5$"))
    application.add_handler(CallbackQueryHandler(testimonial_6, pattern="^testimonial_6$"))
    application.add_handler(CallbackQueryHandler(testimonial_7, pattern="^testimonial_7$"))
    
    # Admin panel handlers
    application.add_handler(CallbackQueryHandler(admin_buttons, pattern="^admin_"))
    
    # Course handlers
    application.add_handler(CallbackQueryHandler(full_course, pattern="^full_course$"))
    application.add_handler(CallbackQueryHandler(pro_full_course, pattern="^pro_full_course$"))
    application.add_handler(CallbackQueryHandler(gradual_course, pattern="^gradual_course$"))
    application.add_handler(CallbackQueryHandler(pro_gradual_course, pattern="^pro_gradual_course$"))
    application.add_handler(CallbackQueryHandler(next_video, pattern="^next_video$"))
    application.add_handler(CallbackQueryHandler(next_pro_video, pattern="^next_pro_video$"))
    application.add_handler(CallbackQueryHandler(ask_question, pattern="^ask_question$"))
    application.add_handler(CallbackQueryHandler(course_completed, pattern="^course_completed$"))
    application.add_handler(CallbackQueryHandler(pro_course_completed, pattern="^pro_course_completed$"))
    application.add_handler(CallbackQueryHandler(i_am_agent, pattern="^i_am_agent$"))
    application.add_handler(CallbackQueryHandler(next_agent_video, pattern="^next_agent_video$"))
    application.add_handler(CallbackQueryHandler(about_course, pattern="^about_course$"))
    application.add_handler(CallbackQueryHandler(next_course_video, pattern="^next_course_video$"))
    
    # Добавляем обработчик для запроса контактных данных
    application.add_handler(conv_handler)
    
    # Добавляем обработчик для рассылки сообщений
    application.add_handler(broadcast_handler)
    
    # Добавляем обработчики для callback_data, связанных с рассылкой
    application.add_handler(CallbackQueryHandler(broadcast_target_selected, pattern="^target_"))
    application.add_handler(CallbackQueryHandler(broadcast_cancel, pattern="^broadcast_cancel$"))
    application.add_handler(CallbackQueryHandler(broadcast_content_type_selected, pattern="^content_type_"))
    application.add_handler(CallbackQueryHandler(broadcast_confirm, pattern="^broadcast_confirm$"))
    application.add_handler(CallbackQueryHandler(continue_broadcast, pattern="^continue_broadcast$"))
    application.add_handler(CallbackQueryHandler(broadcast_cancel_confirmation, pattern="^broadcast_cancel_confirm$"))
    
    # Add message handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()