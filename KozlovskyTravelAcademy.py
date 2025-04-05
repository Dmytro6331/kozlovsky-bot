import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters, ConversationHandler
import os
import json
import datetime
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

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

# File for storing user data
USERS_DATA_FILE = "interested_users.json"

# For working with conversation states and broadcast
PHONE, PROCESSING = range(2)
BROADCAST_TARGET, BROADCAST_CONTENT_TYPE, BROADCAST_TEXT, BROADCAST_PHOTO, BROADCAST_VIDEO, BROADCAST_CONFIRM, BROADCAST_CANCEL_CONFIRM = range(7)

# Defining file IDs from the instruction
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
    "ЕКСКЛЮЗИВНО НА РИНКУ УКРАЇНИ! 🇺🇦\n\n"
    "🔹 ТурАгентам — швидко та вигідно!\n\n"
    "🏨 Прямий доступ до \"Hotelston\"\n"
    "💸 Оплата в гривні на розрахунковий рахунок\n"
    "❌ Без SWIFT, комісій та зайвих витрат\n"
    "🔁 Можливість створити 2-й кабінет і перенести заявки\n"
    "💱 Доступні рахунки в € / $ / £ / zł\n\n"
    "📲 Пиши — підключимо за 5 хв! 🚀",
    
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
    # First testimonial - two videos
    ["DQACAgIAAxkBAAIRCmfqorDyfxKVU5rHmlBHv3tpjfztAALVZQACQDLISvAffcB02YGPNgQ", 
     "DQACAgIAAxkDAAINvWfoNTMjJkZXyqkHNN0HUWSxTj57AALZZQACQDLISqIU-Nfd0z42NgQ"],
    
    # Second testimonial - three videos
    ["DQACAgIAAxkDAAIQCmfpto4RMJYMIcDsZw6cxBsrMhcDAAIJZwACwIbZSjDJUh6dGn4ZNgQ", 
     "DQACAgIAAxkDAAIQC2fpto4shW4776XKBAv8FXEbOsdgAALWawACVarwSgjASsIMjRh1NgQ", 
     "DQACAgIAAxkBAAIRFWfqpgABHsfGzJSEuY32tXSH_huC8QAC22sAAlWq8EpCPa475G6r8zYE"],
    
    # Third testimonial - one video
    ["DQACAgIAAxkBAAIRFmfqqJZOv-VA2M6ItMvrVS5xKBTcAALbawAC9k8AAUvoIb_OvatZsjYE"],
    
    # Fourth testimonial - one video
    ["BAACAgIAAxkBAAIRF2fqqPV-O-nK1y9ijXhmPTwBZEKpAAKnaQACTSxQS1OWiyqmkGIrNgQ"],
    
    # Fifth testimonial - one video
    ["BAACAgIAAxkDAAINlmfnzkEE9WJLxBNWBr5KwzgfFJ6RAAJgbQACpkAISxOBJPtS2rasNgQ"],
    
    # Sixth testimonial - one video
    ["BAACAgIAAxkDAAINvGfoNTIO_5wuJ41BlKXJ0gMje3CNAAIBigACSB3QSjYVrKeUJHeCNgQ"],
    
    # Seventh testimonial - one video
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
    "https://youtube.com/live/5KY-Hi6hkhQ",
    "https://youtube.com/live/M3yN2OYT-DA"  # Добавлено 12-е видео
]

# Function to save user data to JSON file with improved reliability
def save_user_data(user_id, username, phone, timestamp, action_type=None, course_type=None):
    """Saves user data to a JSON file with improved reliability.
    
    Args:
        user_id: User ID
        username: Username
        phone: Phone number
        timestamp: Timestamp
        action_type: Action type ("hotel_selection", "request_contact" or None)
        course_type: Course type ("basic", "pro" or None)
    """
    try:
        # Create backup directory if it doesn't exist
        backup_dir = "database_backup"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Check if the file exists and create it if not
        if not os.path.exists(USERS_DATA_FILE):
            with open(USERS_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        # Make a backup of the current file before modifying it
        backup_filename = f"{backup_dir}/users_data_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if os.path.exists(USERS_DATA_FILE) and os.path.getsize(USERS_DATA_FILE) > 0:
            try:
                import shutil
                shutil.copy2(USERS_DATA_FILE, backup_filename)
            except Exception as e:
                logger.error(f"Error creating backup: {e}")
        
        # Load existing data with enhanced error handling
        users_data = []
        try:
            with open(USERS_DATA_FILE, 'r', encoding='utf-8') as f:
                file_content = f.read()
                if file_content.strip():  # Check if file is not empty
                    users_data = json.loads(file_content)
                else:
                    users_data = []
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {USERS_DATA_FILE}, creating new data")
            # Try to recover from the latest backup
            latest_backup = None
            try:
                backup_files = [f for f in os.listdir(backup_dir) if f.startswith("users_data_backup_")]
                if backup_files:
                    latest_backup = sorted(backup_files)[-1]
                    with open(f"{backup_dir}/{latest_backup}", 'r', encoding='utf-8') as f:
                        users_data = json.load(f)
                    logger.info(f"Recovered data from backup: {latest_backup}")
                else:
                    users_data = []
            except Exception as e:
                logger.error(f"Error recovering from backup: {e}")
                users_data = []
        
        # Validate users_data is a list
        if not isinstance(users_data, list):
            logger.error(f"users_data is not a list: {type(users_data)}")
            users_data = []
        
        # Prepare user data
        user_data = {
            "id": user_id,
            "username": username if username else "No username",
            "phone": phone,
            "timestamp": timestamp,
            "action_type": action_type,
            "course_type": course_type
        }
        
        # Check if user already exists
        user_exists = False
        for user in users_data:
            if isinstance(user, dict) and user.get("id") == user_id:
                user_exists = True
                # Update only the necessary fields
                if action_type is not None:
                    user["action_type"] = action_type
                if course_type is not None:
                    user["course_type"] = course_type
                if phone != "Не указан":
                    user["phone"] = phone
                user["timestamp"] = timestamp
                break
        
        # If user doesn't exist, add them
        if not user_exists:
            users_data.append(user_data)
        
        # Save updated data with pretty-printing for readability
        with open(USERS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=4, ensure_ascii=False)
        
        # Manage backup files - keep only 20 most recent backups
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith("users_data_backup_")]
        if len(backup_files) > 20:  # Keep only 20 most recent backups
            backup_files = sorted(backup_files)
            for old_file in backup_files[:-20]:
                try:
                    os.remove(f"{backup_dir}/{old_file}")
                except Exception as e:
                    logger.error(f"Error removing old backup {old_file}: {e}")
            
        return True
    except Exception as e:
        logger.error(f"Error saving user data: {e}")
        return False

# Function to load user data from file
def load_users_data():
    try:
        if not os.path.exists(USERS_DATA_FILE):
            return []
        
        with open(USERS_DATA_FILE, 'r', encoding='utf-8') as f:
            file_content = f.read()
            if not file_content.strip():
                return []
            
            return json.loads(file_content)
    except Exception as e:
        logger.error(f"Error loading users data: {e}")
        
        # Try to recover from the latest backup if main file is corrupted
        backup_dir = "database_backup"
        if os.path.exists(backup_dir):
            try:
                backup_files = [f for f in os.listdir(backup_dir) if f.startswith("users_data_backup_")]
                if backup_files:
                    latest_backup = sorted(backup_files)[-1]
                    with open(f"{backup_dir}/{latest_backup}", 'r', encoding='utf-8') as f:
                        users_data = json.load(f)
                    logger.info(f"Recovered data from backup: {latest_backup}")
                    return users_data
            except Exception as recovery_error:
                logger.error(f"Error recovering from backup: {recovery_error}")
        
        return []

# Function to check if a user is an administrator
def is_admin(user_id):
    return user_id in ADMIN_IDS

# 1. Command /start
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
    
    # 1.1 Welcome - send intro video
    try:
        if is_callback:
            # If this is a callback, use reply_video with query.message
            await update.callback_query.message.reply_video(
                video=VIDEO_FILE_IDS["intro"]
            )
        else:
            # If this is a command, use regular reply_video
            await update.message.reply_video(
                video=VIDEO_FILE_IDS["intro"]
            )
    except Exception as e:
        logger.error(f"Error sending intro video: {e}")
        if is_callback:
            await update.callback_query.message.reply_text("Failed to send video. Please try again later.")
        else:
            await update.message.reply_text("Failed to send video. Please try again later.")
    
    # 1.2 Welcome message with buttons
    keyboard = [
        [InlineKeyboardButton("ℹ️ Хочу дізнатись більше", callback_data="more_info")],
        [InlineKeyboardButton("📝 Відгуки", callback_data="testimonials"),
         InlineKeyboardButton("📄 Документи", callback_data="documents")],
        [InlineKeyboardButton("❓ Про що цей курс", callback_data="about_course")],
        [InlineKeyboardButton("🎁 Ексклюзив для турагентів✨", callback_data="i_am_agent")],
        [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Welcome message text
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
    
    # Send welcome message
    if is_callback:
        await update.callback_query.message.reply_text(welcome_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# 2. Button "Want to know more"
async def more_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle more info button press."""
    query = update.callback_query
    await query.answer()
    
    # Create keyboard with buttons for 2.1
    keyboard = [
        [InlineKeyboardButton("👨‍💼 Цікавить навчання", callback_data="training_info")],
        [InlineKeyboardButton("📝 Відгуки", callback_data="testimonials")],
        [InlineKeyboardButton("📱 Соціальні мережі", callback_data="social_media")],
        [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")],
        [InlineKeyboardButton("💰 Оплатити курс WayForPay", url=PAYMENT_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send video with description
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

# 3. Button "About this course"
async def about_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle about course button press."""
    query = update.callback_query
    await query.answer()
    
    # Reset agent video index
    context.user_data["agent_video_index"] = 0
    
    # Send first agent video
    await send_agent_video(update, context)

# Function for sending agent videos
async def send_agent_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send agent video based on the current index."""
    query = update.callback_query
    index = context.user_data.get("agent_video_index", 0)
    
    # Check that index is within array bounds
    if index >= len(AGENT_VIDEO_IDS):
        await query.message.reply_text("All videos have been viewed.")
        return
    
    # Send video without description
    try:
        await query.message.reply_video(video=AGENT_VIDEO_IDS[index])
        
        # Send description as a SEPARATE message
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
            f"Failed to send video. Please try again or contact support."
        )

# Handle "Next video" button for agents
async def next_agent_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle next agent video button press."""
    query = update.callback_query
    await query.answer()
    
    # Increment video index
    current_index = context.user_data.get("agent_video_index", 0)
    next_index = current_index + 1
    
    # Save new index
    context.user_data["agent_video_index"] = next_index
    
    # Send next video
    await send_agent_video(update, context)

# 4. Button "Documents"
async def documents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle documents button press."""
    query = update.callback_query
    await query.answer()
    
    # Send documents
    for doc_id in DOCUMENT_FILE_IDS:
        try:
            await query.message.reply_document(document=doc_id)
        except Exception as e:
            logger.error(f"Error sending document: {e}")
            await query.message.reply_text("Failed to send document. Please try again later.")
    
    # Send message with button to training -> more_info (2.1)
    keyboard = [
        [InlineKeyboardButton("👨‍💼 Навчання", callback_data="more_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "Усі документи компанії. Для повернення в меню натисніть кнопку нижче:",
        reply_markup=reply_markup
    )

# 5. Button "Testimonials"
async def testimonials(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle testimonials button press."""
    query = update.callback_query
    await query.answer()
    
    # Reset testimonial index
    context.user_data["testimonial_index"] = 0
    
    # Send header
    await query.message.reply_text("💙 Цінуємо всіх наших учнів! 💛")
    
    # Send first testimonial
    await send_testimonial(update, context)

# Function for sending testimonials
async def send_testimonial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a testimonial based on the current index."""
    query = update.callback_query
    index = context.user_data.get("testimonial_index", 0)
    
    # Prepare buttons based on testimonial index
    if index < 7:  # Not the last testimonial (for first 7 testimonials)
        keyboard = [
            [InlineKeyboardButton("😊 Більше відгуків", callback_data=f"testimonial_{index+1}")],
            [InlineKeyboardButton("👨‍💼 Навчання", callback_data="more_info"),
             InlineKeyboardButton("💰 Оплатити", callback_data="training_info")]
        ]
    else:  # Last testimonial
        keyboard = [
            [InlineKeyboardButton("👨‍💼 Навчання", callback_data="more_info"),
             InlineKeyboardButton("💰 Оплатити", callback_data="training_info")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        # Sending regular testimonials (indices 0-4)
        if index < 5:
            await query.message.reply_video(
                video=TESTIMONIAL_FILE_IDS[index],
                reply_markup=reply_markup
            )
            
        # Sending 6th testimonial (special)
        elif index == 5:
            await query.message.reply_video(
                video=VIDEO_FILE_IDS["separate_testimonial"],
                reply_markup=reply_markup
            )
            
        # Sending 7th testimonial (double)
        elif index == 6:
            # Send first video without buttons
            await query.message.reply_video(
                video=TESTIMONIAL_DOUBLE_FILE_IDS[0]
            )
            
            # Send second video with buttons
            await query.message.reply_video(
                video=TESTIMONIAL_DOUBLE_FILE_IDS[1],
                reply_markup=reply_markup
            )
            
        # Sending 8th testimonial (triple)
        elif index == 7:
            # Send first video without buttons
            await query.message.reply_video(
                video=TESTIMONIAL_TRIPLE_FILE_IDS[0]
            )
            
            # Send second video without buttons
            await query.message.reply_video(
                video=TESTIMONIAL_TRIPLE_FILE_IDS[1]
            )
            
            # Send third video with buttons
            await query.message.reply_video(
                video=TESTIMONIAL_TRIPLE_FILE_IDS[2],
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error sending testimonial: {e}")
        await query.message.reply_text(
            "Failed to send video. Please try again later.",
            reply_markup=reply_markup
        )

# Handlers for unique testimonial callback data
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

# 6. Button "Ask a question"
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle ask question button press."""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(
        "Ви можете задати питання про курс або туристичний бізнес.\n"
        "Просто напишіть ваше питання в чат, і ми відповімо якнайшвидше."
    )

# 7. Button "Interested in training"
async def training_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle training info button press."""
    query = update.callback_query
    await query.answer()
    
    # Keyboard with buttons
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
    
    # Message text
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
    
    # Send video with description
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

# 8.1 Payment confirmation (via /start money)
async def payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle payment confirmation."""
    # Save information about basic course purchase
    user_id = update.effective_user.id
    username = update.effective_user.username
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_data(user_id, username, "Не указан", timestamp, course_type="basic")
    
    # Keyboard with course access option buttons
    keyboard = [
        [InlineKeyboardButton("📘 Отримати курс повністю", callback_data="full_course")],
        [InlineKeyboardButton("📗 Отримати поступово", callback_data="gradual_course")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Successful payment message text
    await update.message.reply_text(
        "✅ Ваш платіж успішно підтверджено! 🚀\nВиберіть, як вам зручніше отримати матеріали:",
        reply_markup=reply_markup
    )

# 8.2 Pro course payment confirmation (via /start money1)
async def pro_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Pro payment confirmation."""
    # Save information about Pro course purchase
    user_id = update.effective_user.id
    username = update.effective_user.username
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_data(user_id, username, "Не указан", timestamp, course_type="pro")
    
    # Keyboard with Pro course access option buttons
    keyboard = [
        [InlineKeyboardButton("📘 Отримати курс повністю", callback_data="pro_full_course")],
        [InlineKeyboardButton("📗 Отримати поступово", callback_data="pro_gradual_course")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send Pro course successful payment message
    await update.message.reply_text(
        "Вітаю, ви придбали курс Pro",
        reply_markup=reply_markup
    )

# 8.3 Payment confirmation (via successful payment message)
async def payment_success(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle successful payment message."""
    # Save information about basic course purchase
    user_id = update.effective_user.id
    username = update.effective_user.username
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_data(user_id, username, "Не указан", timestamp, course_type="basic")
    
    # Keyboard with course access option buttons
    keyboard = [
        [InlineKeyboardButton("📘 Отримати курс повністю", callback_data="full_course")],
        [InlineKeyboardButton("📗 Отримати поступово", callback_data="gradual_course")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Successful payment message text
    await update.message.reply_text(
        "✅ Ваш платіж успішно підтверджено! 🚀\nВиберіть, як вам зручніше отримати матеріали:",
        reply_markup=reply_markup
    )

# 9. Getting the full course
async def full_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle full course access button press."""
    query = update.callback_query
    await query.answer()
    
    # Save context for correct return when viewing agent testimonials
    context.user_data["return_to_full_course"] = True
    
    # Prepare text with all video links
    course_text = (
        "Ось твій курс 📘\n"
        "Ці 5 відео допоможуть тобі розібратися в усьому кроці за кроком. "
        "Переглядай їх у зручному темпі — головне не поспішай і одразу застосовуй знання на практиці! ✏\n\n"
    )
    
    # Add links to all videos
    for i, video_url in enumerate(COURSE_VIDEOS, 1):
        course_text += f"📹 Відео {i}: {video_url}\n"
    
    # Keyboard with buttons
    keyboard = [
        [InlineKeyboardButton("✅ Я пройшов / пройшла курс", callback_data="course_completed")],
        [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")],
        [InlineKeyboardButton("📱 Соціальні мережі", callback_data="social_media")],
        [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message with all videos
    await query.message.reply_text(course_text, reply_markup=reply_markup)

# 10. Getting the course gradually
async def gradual_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle gradual course access button press."""
    query = update.callback_query
    await query.answer()
    
    # Reset video index
    context.user_data["video_index"] = 0
    
    # Keyboard with "Next video" button
    keyboard = [
        [InlineKeyboardButton("▶️ Наступне відео", callback_data="next_video")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send first video
    await query.message.reply_text(
        f"Чудово, давай розпочнемо курс поступово 📘\n"
        f"Ось твоє перше відео — переглянь уважно, і як тільки закінчиш, натисни кнопку \"▶️ Наступне відео\". "
        f"Усього буде 5 відео, тож рухаємося крок за кроком 🚶 🚶\n"
        f"📹 Відео 1: {COURSE_VIDEOS[0]}",
        reply_markup=reply_markup
    )

# Handle "Next video" button for gradual course
async def next_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle next video button press."""
    query = update.callback_query
    await query.answer()
    
    # Increment video index
    current_index = context.user_data.get("video_index", 0)
    next_index = current_index + 1
    
    # Check that index is within array bounds
    if next_index >= len(COURSE_VIDEOS):
        await query.message.reply_text("All videos have been viewed.")
        return
    
    # Save index
    context.user_data["video_index"] = next_index
    
    # Format text for message
    if next_index == 1:  # For second video add additional text
        text = (
            f"📹 Відео {next_index + 1}: {COURSE_VIDEOS[next_index]}\n\n"
            f"YouTube\n"
            f"Відео {next_index + 1}\n\n"
            f"#{next_index + 1}\n\n"
            f"😌 Втомився під час навчання? Ми підберемо для тебе ідеальний відпочинок! 🌴✨ Пиши нам – і допоможемо перезавантажитися! 💬"
        )
        
        # Buttons for second video - add hotel selection
        keyboard = [
            [InlineKeyboardButton("▶️ Наступне відео", callback_data="next_video")],
            [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")]
        ]
    elif next_index == 3:  # For fourth video (index 3)
        text = (
            f"📹 Відео {next_index + 1}: {COURSE_VIDEOS[next_index]}\n\n"
            f"YouTube\n"
            f"Відео {next_index + 1}\n\n"
            f"#{next_index + 1}"
        )
        
        # Save context for correct return when viewing agent testimonials
        context.user_data["return_to_basic_course"] = True
        
        # Buttons for fourth video
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
        
        # Prepare buttons based on index
        if next_index < len(COURSE_VIDEOS) - 1:  # Not the last video
            keyboard = [
                [InlineKeyboardButton("▶️ Наступне відео", callback_data="next_video")]
            ]
        else:  # Last video
            # Save context for correct return when viewing agent testimonials
            context.user_data["return_to_basic_course"] = True
            
            # Add buttons to last video
            keyboard = [
                [InlineKeyboardButton("✅ Я пройшов / пройшла курс", callback_data="course_completed")],
                [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")],
                [InlineKeyboardButton("📱 Соціальні мережі", callback_data="social_media")],
                [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")]
            ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send video
    await query.message.reply_text(text, reply_markup=reply_markup)

# 11. Getting the full Pro course
async def pro_full_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Pro full course access button press."""
    query = update.callback_query
    await query.answer()
    
    # Save context for correct return when viewing agent testimonials
    context.user_data["return_to_pro_full_course"] = True
    
    # Prepare text with all video links
    course_text = (
        "Ось ваш Pro курс 📘\n"
        "Ці 12 відео допоможуть тобі розібратися в усьому кроці за кроком. "
        "Переглядай їх у зручному темпі — головне не поспішай і одразу застосовуй знання на практиці! ✏\n\n"
    )
    
    # Add links to all videos
    for i, video_url in enumerate(PRO_COURSE_VIDEOS, 1):
        course_text += f"📹 Відео {i}: {video_url}\n"
    
    # Keyboard with buttons
    keyboard = [
        [InlineKeyboardButton("👨‍💼 Цікавить співпраця", callback_data="request_contact")],
        [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")],
        [InlineKeyboardButton("📱 Соціальні мережі", callback_data="social_media")],
        [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message with all videos
    await query.message.reply_text(course_text, reply_markup=reply_markup)

# 12. Getting the Pro course gradually
async def pro_gradual_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Pro gradual course access button press."""
    query = update.callback_query
    await query.answer()
    
    # Reset video index
    context.user_data["pro_video_index"] = 0
    
    # Keyboard with "Next video" button
    keyboard = [
        [InlineKeyboardButton("▶️ Наступне відео", callback_data="next_pro_video")],
        [InlineKeyboardButton("👨‍💼 Цікавить співпраця", callback_data="request_contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send first video
    await query.message.reply_text(
        f"Чудово, давай розпочнемо Pro курс поступово 📘\n"
        f"Ось твоє перше відео — переглянь уважно, і як тільки закінчиш, натисни кнопку \"▶️ Наступне відео\". \n"
        f"Усього буде 12 відео, тож рухаємося крок за кроком 🚶 🚶\n"
        f"📹 Відео 1: {PRO_COURSE_VIDEOS[0]}",
        reply_markup=reply_markup
    )

# Handle "Next video" button for gradual Pro course
async def next_pro_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle next pro video button press."""
    query = update.callback_query
    await query.answer()
    
    # Increment video index
    current_index = context.user_data.get("pro_video_index", 0)
    next_index = current_index + 1
    
    # Check that index is within array bounds
    if next_index >= len(PRO_COURSE_VIDEOS):
        await query.message.reply_text("All videos have been viewed.")
        return
    
    # Save index
    context.user_data["pro_video_index"] = next_index
    
    # Format text for message
    text = (
        f"📹 Відео {next_index + 1}: {PRO_COURSE_VIDEOS[next_index]}\n\n"
        f"YouTube\n"
        f"Відео {next_index + 1}\n\n"
        f"#{next_index + 1}"
    )
    
    # Prepare buttons based on index
    if next_index < len(PRO_COURSE_VIDEOS) - 1:  # Not the last video
        keyboard = [
            [InlineKeyboardButton("▶️ Наступне відео", callback_data="next_pro_video")],
            [InlineKeyboardButton("👨‍💼 Цікавить співпраця", callback_data="request_contact")]
        ]
    else:  # Last video (12-е видео)
        # Save context for correct return when viewing agent testimonials
        context.user_data["return_to_pro_course"] = True
        
        keyboard = [
            [InlineKeyboardButton("👨‍💼 Цікавить співпраця", callback_data="request_contact")],
            [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")],
            [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send video
    await query.message.reply_text(text, reply_markup=reply_markup)

# 13.1 Completion of the basic course
async def course_completed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle course completed button press."""
    query = update.callback_query
    await query.answer()
    
    # Save context for correct return when viewing agent testimonials
    context.user_data["return_to_basic_course"] = True
    
    try:
        # First send the video
        await query.message.reply_video(video=VIDEO_FILE_IDS["course_completed"])
        
        # Keyboard with Pro course button and additional buttons
        keyboard = [
            [InlineKeyboardButton("💰 Оплатити Pro курс", url=PRO_PAYMENT_LINK)],
            [InlineKeyboardButton("📱 Соціальні мережі", callback_data="social_media")],
            [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")],
            [InlineKeyboardButton("🏨 Підбір готелю", callback_data="hotel_selection")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Congratulation text
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
        
        # If there was an error with the video, still send the text
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

# 13.2 Completion of the Pro course
async def pro_course_completed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Pro course completed button press."""
    query = update.callback_query
    await query.answer()
    
    # Save context for correct return when viewing agent testimonials
    context.user_data["return_to_pro_course"] = True
    
    # Keyboard with buttons
    keyboard = [
        [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send congratulations on completing the Pro course
    await query.message.reply_text(
        "🎉 Вітаємо з успішним завершенням Pro курсу!\n"
        "Тепер ви маєте всі необхідні знання та інструменти для успішної роботи в туристичному бізнесі.\n"
        "Бажаємо великих успіхів та високих комісій!",
        reply_markup=reply_markup
    )

# 14. Button "🎁 Exclusive for agents✨"
async def i_am_agent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle exclusive for agents button press."""
    query = update.callback_query
    await query.answer()
    
    # Reset video index and save context for correct return
    context.user_data["course_video_index"] = 0
    context.user_data["return_to_agent_info"] = True
    
    # Send first video
    await send_course_video(update, context)

# Function for sending course videos
async def send_course_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a course video based on the current index."""
    query = update.callback_query
    index = context.user_data.get("course_video_index", 0)
    
    # Check that index is within array bounds
    if index >= len(COURSE_CIRCLE_VIDEO_IDS):
        await query.message.reply_text("All videos have been viewed.")
        return
    
    # First send video without buttons
    try:
        await query.message.reply_video(
            video=COURSE_CIRCLE_VIDEO_IDS[index]
        )
        
        # Prepare buttons based on index
        if index < len(COURSE_CIRCLE_VIDEO_IDS) - 1:  # Not the last video
            keyboard = [
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"),
                 InlineKeyboardButton("▶️ Наступне відео", callback_data="next_course_video")],
                [InlineKeyboardButton("🌟 Наші продукти", url="https://datour.club/#partners")],
                [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")],
                [InlineKeyboardButton("📜 Договір", callback_data="contract")],
                [InlineKeyboardButton("👨‍💼 Цікавить співпраця", callback_data="request_contact")]
            ]
        else:  # Last video - replace "Next video" button with "Back to start"
            keyboard = [
                [InlineKeyboardButton("⏪ На початок ⏪", callback_data="back_to_main")],
                [InlineKeyboardButton("🌟 Наші продукти", url="https://datour.club/#partners")],
                [InlineKeyboardButton("💬 Відгуки турагентів", callback_data="agent_testimonials")],
                [InlineKeyboardButton("📜 Договір", callback_data="contract")],
                [InlineKeyboardButton("👨‍💼 Цікавить співпраця", callback_data="request_contact")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send description with buttons
        await query.message.reply_text(
            COURSE_CIRCLE_DESCRIPTIONS[index],
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error sending course video: {e}")
        await query.message.reply_text(
            f"Failed to send course video. Please try again or contact support."
        )

# Handle "Next video" button in agent course
async def next_course_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle next course video button press."""
    query = update.callback_query
    await query.answer()
    
    # Increment video index
    current_index = context.user_data.get("course_video_index", 0)
    next_index = current_index + 1
    
    if next_index < len(COURSE_CIRCLE_VIDEO_IDS):
        context.user_data["course_video_index"] = next_index
        await send_course_video(update, context)
    else:
        await query.message.reply_text("All videos have been viewed.")

# 15. Admin panel
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin panel for viewing user data."""
    user_id = update.effective_user.id
    
    # Check if user is an administrator
    if not is_admin(user_id):
        await update.message.reply_text("You don't have access to this command.")
        return
    
    # Load user data
    users_data = load_users_data()
    
    # Create keyboard with admin panel options
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

# Handle admin panel buttons
async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle admin panel buttons."""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Check if user is an administrator
    if not is_admin(user_id):
        await query.answer("You don't have access to this command.", show_alert=True)
        return
    
    await query.answer()
    
    # Load user data
    users_data = load_users_data()
    
    if query.data == "admin_show_all":
        # Show all users
        if not users_data:
            await query.message.reply_text("No user data available.")
            return
        
        # Split user data into pages of 10
        page = context.user_data.get("admin_page", 0)
        total_pages = (len(users_data) - 1) // 10 + 1
        
        # Prepare text for current page
        start_idx = page * 10
        end_idx = min(start_idx + 10, len(users_data))
        page_users = users_data[start_idx:end_idx]
        
        text = f"📊 Користувачі (Сторінка {page + 1}/{total_pages}):\n\n"
        for i, user in enumerate(page_users, start=1):
            text += (f"{start_idx + i}. @{user['username']} | "
                    f"{user['phone']} | ID: {user['id']} | "
                    f"{user['timestamp']}\n\n")
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data="admin_prev_page"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("➡️ Вперед", callback_data="admin_next_page"))
        
        keyboard = [nav_buttons, [InlineKeyboardButton("🔙 Назад до меню", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(text, reply_markup=reply_markup)
    
    elif query.data == "admin_stats":
        # Show statistics
        text = "📈 Статистика:\n\n"
        
        # Count users by course type
        basic_users = sum(1 for user in users_data if user.get("course_type") == "basic")
        pro_users = sum(1 for user in users_data if user.get("course_type") == "pro")
        no_course_users = len(users_data) - basic_users - pro_users
        
        text += f"Всього користувачів: {len(users_data)}\n"
        text += f"Користувачів з базовим курсом: {basic_users}\n"
        text += f"Користувачів з Pro курсом: {pro_users}\n"
        text += f"Користувачів без курсів: {no_course_users}\n\n"
        
        # Count users by day
        daily_stats = {}
        for user in users_data:
            date = user["timestamp"].split(" ")[0]
            daily_stats[date] = daily_stats.get(date, 0) + 1
        
        # Show statistics by day
        text += "Користувачі по днях:\n"
        for date, count in sorted(daily_stats.items(), reverse=True):
            text += f"{date}: {count} користувачів\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад до меню", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(text, reply_markup=reply_markup)
    
    elif query.data == "admin_hotel_stats":
        # Show users who requested hotel selection
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
        # Refresh data
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
            f"Дані оновлено: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Виберіть опцію:",
            reply_markup=reply_markup
        )
    
    elif query.data == "admin_prev_page":
        # Previous page
        context.user_data["admin_page"] = max(0, context.user_data.get("admin_page", 0) - 1)
        # Call show all users again
        query.data = "admin_show_all"
        await admin_buttons(update, context)
    
    elif query.data == "admin_next_page":
        # Next page
        total_pages = (len(users_data) - 1) // 10 + 1
        context.user_data["admin_page"] = min(total_pages - 1, context.user_data.get("admin_page", 0) + 1)
        # Call show all users again
        query.data = "admin_show_all"
        await admin_buttons(update, context)
    
    elif query.data == "admin_back":
        # Return to main admin panel menu
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
        # Start broadcast process
        await start_broadcast(update, context)

# 16. Social media
async def social_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle social media button press."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Instagram", url="instagram.com/kozlovsky_official"),
         InlineKeyboardButton("YouTube", url="https://www.youtube.com/@Enjoy-World")],
        [InlineKeyboardButton("Telegram", url="t.me/EnjoybyAK"),
         InlineKeyboardButton("Viber", url="https://invite.viber.com/?g2=AQAdFXxYRdaujUjJrDmLqBUV0euxHSLFrEj34LGtzWmFdIZ8fq7avy%2FjLrlTBiNv&lang=ru")],
        [InlineKeyboardButton("🔙 Назад", callback_data="social_media_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "📱 Наші соціальні мережі:\n"
        "Підписуйтесь, щоб бути в курсі всіх новин",
        reply_markup=reply_markup
    )

# New function to handle back button from social media with message deletion
async def social_media_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle back button press from social media and delete the message."""
    query = update.callback_query
    await query.answer()
    
    # Delete the message with social media links
    await query.message.delete()
    
    # Don't call more_info anymore to avoid sending new message
    # We just delete the message and do nothing else

    # 17. Request contact information
# 17.1 Function for requesting phone number
async def request_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Request user's phone number."""
    query = update.callback_query
    await query.answer()
    
    # Save user data when button is pressed
    user_id = query.from_user.id
    username = query.from_user.username
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_data(user_id, username, "Не указан", timestamp, "request_contact")
    
    # Save URL for further transition
    context.user_data["next_url"] = "https://t.me/kozlovsky_official2"
    context.user_data["action_type"] = "request_contact"
    
    # Create keyboard with contact request button
    keyboard = [[KeyboardButton("📱 Поділитися номером телефону", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await query.message.reply_text(
        "Для зв'язку з нашим представником, будь ласка, поділіться вашим номером телефону. \n"
        "Натисніть кнопку нижче:",
        reply_markup=reply_markup
    )
    
    return PHONE

# 17.2 Function for requesting phone number for hotel selection
async def hotel_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Request phone number for hotel selection."""
    query = update.callback_query
    await query.answer()
    
    # Save user data when button is pressed
    user_id = query.from_user.id
    username = query.from_user.username
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_data(user_id, username, "Не указан", timestamp, "hotel_selection")
    
    # Save URL for further transition
    context.user_data["next_url"] = "https://t.me/kozlovsky_official"
    context.user_data["action_type"] = "hotel_selection"
    
    # Create keyboard with contact request button
    keyboard = [[KeyboardButton("📱 Поділитися номером телефону", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await query.message.reply_text(
        "Для зв'язку з Артемом щодо підбору готелю, будь ласка, поділіться вашим номером телефону. \n"
        "Натисніть кнопку нижче:",
        reply_markup=reply_markup
    )
    
    return PHONE

# 17.3 Process received contact
async def process_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process received contact and move to next step."""
    user = update.message.from_user
    phone_number = update.message.contact.phone_number
    
    # Save user data with action type
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    action_type = context.user_data.get("action_type", "request_contact")
    save_user_data(user.id, user.username, phone_number, timestamp, action_type)
    
    # Determine text based on action type
    if action_type == "hotel_selection":
        message_text = "Дякуємо! Ваш номер телефону збережено. Зараз ви будете перенаправлені до Артема Козловського"
        button_text = "📞 Зв'язок з Артемом"
    else:
        message_text = "Дякуємо! Ваш номер телефону збережено. Зараз ви будете перенаправлені до нашого представника."
        button_text = "👨‍💼 Перейти до представника"
    
    # Notify user about transition
    await update.message.reply_text(
        message_text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(button_text, url=context.user_data.get("next_url", "https://t.me/kozlovsky_official"))
        ]])
    )
    
    # Separately remove keyboard with contact request button
    await context.bot.send_message(chat_id=update.effective_chat.id, text=".", reply_markup=ReplyKeyboardRemove())
    
    # Forward the phone number to admins (ID: 254322794 and 609094231)
    admin_message = ""
    if action_type == "hotel_selection":
        admin_message = f"🏨 Новий запит на підбір готелю. Користувач @{user.username} ({user.first_name}) залишив номер: {phone_number}"
    else:
        admin_message = f"👨‍💼 Новий запит на співпрацю. Користувач @{user.username} ({user.first_name}) залишив номер: {phone_number}"
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=admin_message)
        except Exception as e:
            logger.error(f"Failed to send message to admin {admin_id}: {e}")
    
    return ConversationHandler.END

# Cancel contact request process
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel contact request."""
    # Notify user about cancellation
    await update.message.reply_text(
        "Процес збору контактних даних скасовано.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("👨‍💼 Перейти до представника", url=context.user_data.get("next_url", "https://t.me/kozlovsky_official"))
        ]])
    )
    
    # Separately remove keyboard with contact request button
    await context.bot.send_message(chat_id=update.effective_chat.id, text=".", reply_markup=ReplyKeyboardRemove())
    
    return ConversationHandler.END

# 18. Agent testimonials
async def agent_testimonials(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle agent testimonials button press."""
    query = update.callback_query
    await query.answer()
    
    # Set testimonial index to 0
    context.user_data["agent_testimonial_index"] = 0
    
    # Save transition source for correct return
    if query.data == "agent_testimonials":
        # Сначала проверяем флаги Pro курса, чтобы они имели приоритет
        if context.user_data.get("return_to_pro_full_course") or context.user_data.get("return_to_pro_course"):
            context.user_data["source"] = "pro_course"
        # Затем проверяем остальные флаги
        elif context.user_data.get("return_to_full_course") or context.user_data.get("return_to_basic_course"):
            context.user_data["source"] = "basic_course"
        elif context.user_data.get("return_to_agent_info"):
            context.user_data["source"] = "agent_info"
    
    # Send header
    await query.message.reply_text("💬 Відгуки від наших партнерів-турагентів:")
    
    # Send first testimonial
    await send_agent_testimonial(update, context)

# 18.2 Function for sending agent testimonial
async def send_agent_testimonial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send agent testimonial video based on the current index."""
    query = update.callback_query
    index = context.user_data.get("agent_testimonial_index", 0)
    
    # Check that index is within array bounds
    if index >= len(AGENT_TESTIMONIAL_VIDEO_IDS):
        await query.message.reply_text(
            "Всі відгуки переглянуті.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Повернутись", callback_data="back_to_source")
            ]])
        )
        return
    
    videos = AGENT_TESTIMONIAL_VIDEO_IDS[index]
    
    # Send all testimonial videos
    for i, video_id in enumerate(videos):
        try:
            # Last video with buttons
            if i == len(videos) - 1:
                # Buttons for last testimonial video
                if index < len(AGENT_TESTIMONIAL_VIDEO_IDS) - 1:  # Not the last testimonial
                    keyboard = [
                        [InlineKeyboardButton("▶️ Наступний відгук", callback_data="next_agent_testimonial")],
                        [InlineKeyboardButton("🔙 Повернутись", callback_data="back_to_source")]
                    ]
                else:  # Last testimonial
                    keyboard = [
                        [InlineKeyboardButton("🔙 Повернутись", callback_data="back_to_source")]
                    ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_video(video=video_id, reply_markup=reply_markup)
            else:
                # Intermediate videos without buttons
                await query.message.reply_video(video=video_id)
        except Exception as e:
            logger.error(f"Error sending agent testimonial video: {e}")
            await query.message.reply_text(
                f"Failed to send testimonial video. Please try again or contact support."
            )

# Handle "Next agent testimonial" button
async def next_agent_testimonial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle next agent testimonial button press."""
    query = update.callback_query
    await query.answer()
    
    # Increment testimonial index
    current_index = context.user_data.get("agent_testimonial_index", 0)
    next_index = current_index + 1
    
    # Save new index
    context.user_data["agent_testimonial_index"] = next_index
    
    # Send next testimonial
    await send_agent_testimonial(update, context)

# 18.3 Function for returning to transition source
async def back_to_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return user to transition source."""
    query = update.callback_query
    await query.answer()
    
    # Get transition source from context
    source = context.user_data.get("source", "")
    
    # Улучшенная логика выбора направления возврата
    # Determine function to call based on source
    if source == "basic_course":
        # Приоритет возврата для флага full_course (полный курс)
        if context.user_data.get("return_to_full_course"):
            await full_course(update, context)
        # Затем проверяем флаг базового курса (пошаговый просмотр)
        elif context.user_data.get("return_to_basic_course"):
            # Если мы не знаем точный шаг, то возвращаемся к полному виду курса
            await full_course(update, context)
        else:
            # Если ни один из флагов не установлен, но источник basic_course
            await full_course(update, context)
    elif source == "pro_course":
        # Приоритет возврата в Pro курс - если установлен флаг return_to_pro_full_course
        if context.user_data.get("return_to_pro_full_course"):
            await pro_full_course(update, context)
        # Если установлен флаг return_to_pro_course
        elif context.user_data.get("return_to_pro_course"):
            # Возврат к Pro курсу (полному виду)
            await pro_full_course(update, context)
        else:
            # Если ни один из флагов не установлен, но источник pro_course
            await pro_full_course(update, context)
    elif source == "agent_info" and context.user_data.get("return_to_agent_info"):
        # Return to agent information
        await i_am_agent(update, context)
    else:
        # If source is not determined, return to main information
        await more_info(update, context)

# 19. Button "📜 Contract"
async def contract(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle contract button press."""
    query = update.callback_query
    await query.answer()
    
    # Send contract documents
    for doc_id in CONTRACT_DOCUMENT_IDS:
        try:
            await query.message.reply_document(document=doc_id)
        except Exception as e:
            logger.error(f"Error sending contract document: {e}")
            await query.message.reply_text("Failed to send document. Please try again later.")
    
    # Send button to return to i_am_agent
    keyboard = [[InlineKeyboardButton("🔙 Повернутись", callback_data="i_am_agent")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text("Вище представлені документи договору.", reply_markup=reply_markup)

# 20. Handle text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages."""
    # Check if user is in broadcast creation state
    # ConversationHandler has priority over this function
    # But for sure add a check
    if context.user_data.get("creating_broadcast"):
        # Skip processing to let ConversationHandler process the message
        return
    
    text = update.message.text.lower()
    
    # Check if this might be a successful payment message
    if "оплата" in text and "успішн" in text:
        await payment_success(update, context)
    else:
        # Respond to any other text messages
        await update.message.reply_text("AI асистент у розробці")

# 21. Return to main menu
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle back to main button press."""
    query = update.callback_query
    await query.answer()
    
    # Call start function with update
    await start(update, context, is_callback=True)

# 23. Extended broadcast system
# 23.1 Start broadcast process
async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start broadcast message process."""
    query = update.callback_query
    if query:
        await query.answer()
    
    # Mark that user is in broadcast creation process
    context.user_data["creating_broadcast"] = True
    
    # Load user data for statistics
    users_data = load_users_data()
    
    # Count users by course type and action type
    basic_users = sum(1 for user in users_data if user.get("course_type") == "basic")
    pro_users = sum(1 for user in users_data if user.get("course_type") == "pro")
    no_course_users = len(users_data) - basic_users - pro_users
    
    # New categories for users who clicked specific buttons
    cooperation_users = sum(1 for user in users_data if user.get("action_type") == "request_contact")
    hotel_users = sum(1 for user in users_data if user.get("action_type") == "hotel_selection")
    
    # Create keyboard for target audience selection with new categories
    keyboard = [
        [InlineKeyboardButton(f"Базовий курс ({basic_users})", callback_data="target_basic")],
        [InlineKeyboardButton(f"Pro курс ({pro_users})", callback_data="target_pro")],
        [InlineKeyboardButton(f"Без курсів ({no_course_users})", callback_data="target_none")],
        [InlineKeyboardButton(f"Запит співпраці ({cooperation_users})", callback_data="target_cooperation")],
        [InlineKeyboardButton(f"Запит готелю ({hotel_users})", callback_data="target_hotel")],
        [InlineKeyboardButton(f"Всі користувачі ({len(users_data)})", callback_data="target_all")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="broadcast_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = "Виберіть цільову аудиторію для розсилки:"
    
    # If called from callback, modify existing message
    if query:
        await query.message.edit_text(message_text, reply_markup=reply_markup)
    else:  # Otherwise send new message (called from command line)
        await update.message.reply_text(message_text, reply_markup=reply_markup)
    
    return BROADCAST_TARGET

# 23.2 Select content type for broadcast
async def broadcast_target_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle target audience selection for broadcast."""
    query = update.callback_query
    await query.answer()
    
    target_data = query.data.replace("target_", "")
    context.user_data["broadcast_target"] = target_data
    
    # Determine text based on selected audience
    target_text = {
        "basic": "користувачів з базовим курсом",
        "pro": "користувачів з Pro курсом",
        "none": "користувачів без курсів",
        "cooperation": "користувачів із запитом на співпрацю",  # New category
        "hotel": "користувачів із запитом на підбір готелю",    # New category
        "all": "всіх користувачів"
    }.get(target_data, "обрану аудиторію")
    
    # Create keyboard for content type selection
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

# 23.3-23.5 Select content type and get content for broadcast
async def broadcast_content_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle content type selection for broadcast."""
    query = update.callback_query
    await query.answer()
    
    content_type = query.data.replace("content_type_", "")
    context.user_data["broadcast_content_type"] = content_type
    
    # Based on selected content type
    if content_type == "text":
        await query.message.edit_text(
            "Введіть текст повідомлення для розсилки:\n\n"
            "Для скасування введіть /cancel"
        )
        return BROADCAST_TEXT
    
    elif content_type == "photo":
        # Clear previous data
        if "broadcast_photo_id" in context.user_data:
            del context.user_data["broadcast_photo_id"]
        if "broadcast_caption" in context.user_data:
            del context.user_data["broadcast_caption"]
            
        # Send new message instead of edit
        await query.message.reply_text(
            "Надішліть фото з підписом для розсилки:\n\n"
            "Для скасування введіть /cancel"
        )
        return BROADCAST_PHOTO
    
    elif content_type == "video":
        # Clear previous data
        if "broadcast_video_id" in context.user_data:
            del context.user_data["broadcast_video_id"]
        if "broadcast_caption" in context.user_data:
            del context.user_data["broadcast_caption"]
            
        # Send new message instead of edit
        await query.message.reply_text(
            "Надішліть відео з підписом для розсилки:\n\n"
            "Для скасування введіть /cancel"
        )
        return BROADCAST_VIDEO
    
    # If unknown content type selected, cancel broadcast
    await query.message.edit_text("Unknown content type. Broadcast cancelled.")
    return ConversationHandler.END

# Process received text for broadcast
async def broadcast_text_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process received text for broadcast."""
    message_text = update.message.text
    context.user_data["broadcast_text"] = message_text
    
    # Determine text based on selected audience
    target_data = context.user_data.get("broadcast_target", "all")
    target_text = {
        "basic": "користувачів з базовим курсом",
        "pro": "користувачів з Pro курсом",
        "none": "користувачів без курсів",
        "cooperation": "користувачів із запитом на співпрацю",  # New category
        "hotel": "користувачів із запитом на підбір готелю",    # New category
        "all": "всіх користувачів"
    }.get(target_data, "обрану аудиторію")
    
    # Create keyboard for confirmation
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

# Process received photo for broadcast - ИСПРАВЛЕНО
async def broadcast_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process received photo for broadcast."""
    photo = update.message.photo[-1]  # Get photo with maximum size
    caption = update.message.caption or ""
    
    # Save photo data in user context
    context.user_data["broadcast_photo_id"] = photo.file_id
    context.user_data["broadcast_caption"] = caption
    
    # Determine text based on selected audience
    target_data = context.user_data.get("broadcast_target", "all")
    target_text = {
        "basic": "користувачів з базовим курсом",
        "pro": "користувачів з Pro курсом",
        "none": "користувачів без курсів",
        "cooperation": "користувачів із запитом на співпрацю",
        "hotel": "користувачів із запитом на підбір готелю",
        "all": "всіх користувачів"
    }.get(target_data, "обрану аудиторію")
    
    # Send NEW message with photo and confirmation, instead of editing the previous one
    keyboard = [
        [InlineKeyboardButton("✅ Підтвердити", callback_data="broadcast_confirm")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="broadcast_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        # Send a new message with the photo and buttons
        await update.message.reply_photo(
            photo=photo.file_id,
            caption=f"Фото для розсилки для {target_text} з підписом:\n\n{caption}\n\nПідтвердіть відправку:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error sending photo confirmation: {e}")
        await update.message.reply_text(
            f"Помилка при відправці підтвердження фото. Спробуйте знову.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Скасувати", callback_data="broadcast_cancel")]])
        )
    
    return BROADCAST_CONFIRM

# Process received video for broadcast - ИСПРАВЛЕНО
async def broadcast_video_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process received video for broadcast."""
    video = update.message.video
    caption = update.message.caption or ""
    
    # Save video data in user context
    context.user_data["broadcast_video_id"] = video.file_id
    context.user_data["broadcast_caption"] = caption
    
    # Determine text based on selected audience
    target_data = context.user_data.get("broadcast_target", "all")
    target_text = {
        "basic": "користувачів з базовим курсом",
        "pro": "користувачів з Pro курсом",
        "none": "користувачів без курсів",
        "cooperation": "користувачів із запитом на співпрацю",
        "hotel": "користувачів із запитом на підбір готелю",
        "all": "всіх користувачів"
    }.get(target_data, "обрану аудиторію")
    
    # Send NEW message with video and confirmation, instead of editing the previous one
    keyboard = [
        [InlineKeyboardButton("✅ Підтвердити", callback_data="broadcast_confirm")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="broadcast_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        # Send a new message with the video and buttons
        await update.message.reply_video(
            video=video.file_id,
            caption=f"Відео для розсилки для {target_text} з підписом:\n\n{caption}\n\nПідтвердіть відправку:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error sending video confirmation: {e}")
        await update.message.reply_text(
            f"Помилка при відправці підтвердження відео. Спробуйте знову.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Скасувати", callback_data="broadcast_cancel")]])
        )
    
    return BROADCAST_CONFIRM

# 23.6 Confirm and perform broadcast
async def broadcast_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm and perform broadcast messages."""
    query = update.callback_query
    await query.answer()
    
    target_data = context.user_data.get("broadcast_target", "all")
    content_type = context.user_data.get("broadcast_content_type", "text")
    
    # Load user data
    users_data = load_users_data()
    
    # Filter users based on target audience
    if target_data == "basic":
        recipients = [user for user in users_data if user.get("course_type") == "basic"]
    elif target_data == "pro":
        recipients = [user for user in users_data if user.get("course_type") == "pro"]
    elif target_data == "none":
        recipients = [user for user in users_data if not user.get("course_type")]
    elif target_data == "cooperation":  # For "Цікавить співпраця" category
        recipients = [user for user in users_data if user.get("action_type") == "request_contact"]
    elif target_data == "hotel":  # For "Підбір готелю" category
        recipients = [user for user in users_data if user.get("action_type") == "hotel_selection"]
    else:  # all
        recipients = users_data
    
    # Save recipients list
    context.user_data["broadcast_recipients"] = recipients
    
    # Send text message with buttons, instead of editing previous message
    # This avoids the error when trying to edit a media message with text
    keyboard = [
        [InlineKeyboardButton("✅ Продовжити розсилку", callback_data="continue_broadcast")],
        [InlineKeyboardButton("❌ Відмінити розсилку", callback_data="broadcast_cancel_confirm")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    confirm_message = await query.message.reply_text(
        f"Увага! Розсилка буде відправлена {len(recipients)} користувачам.\n\n"
        "Ви впевнені, що хочете продовжити?\n\n"
        "Ви зможете скасувати розсилку під час процесу, натиснувши кнопку 'Відмінити розсилку'.",
        reply_markup=reply_markup
    )
    
    # Save message ID for updating
    context.user_data["confirm_message_id"] = confirm_message.message_id
    
    return BROADCAST_CONFIRM

# 23.6.2 Perform broadcast - Fixed implementation to ensure proper functioning
async def continue_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Perform broadcast messages."""
    query = update.callback_query
    await query.answer()
    
    # Get necessary data from context
    content_type = context.user_data.get("broadcast_content_type", "text")
    recipients = context.user_data.get("broadcast_recipients", [])
    
    # Create keyboard with cancel button
    keyboard = [
        [InlineKeyboardButton("❌ Відмінити розсилку", callback_data="broadcast_cancel_confirm")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Message about broadcast start - using reply_text to create a new message
    status_message = await query.message.reply_text(
        "Розсилка в процесі...\n"
        f"0% виконано (0/{len(recipients)})\n\n"
        "✅ Успішно відправлено: 0\n"
        "❌ Не вдалося відправити: 0\n\n"
        "Ви можете скасувати розсилку, натиснувши кнопку нижче:",
        reply_markup=reply_markup
    )
    
    # Save status message ID for updates
    context.user_data["status_message_id"] = status_message.message_id
    context.user_data["status_chat_id"] = status_message.chat_id
    
    # Broadcast cancellation flag
    context.user_data["broadcast_cancelled"] = False
    
    # Counters
    sent_count = 0
    failed_count = 0
    
    # Send messages
    for i, user in enumerate(recipients):
        # Check if broadcast is cancelled
        if context.user_data.get("broadcast_cancelled"):
            skipped_count = len(recipients) - (i + 1)
            await context.bot.edit_message_text(
                chat_id=context.user_data["status_chat_id"],
                message_id=context.user_data["status_message_id"],
                text=f"Розсилка скасована користувачем!\n\n"
                     f"✅ Успішно відправлено: {sent_count}\n"
                     f"❌ Не вдалося відправити: {failed_count}\n"
                     f"⏸ Пропущено: {skipped_count}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад до меню", callback_data="admin_back")
                ]])
            )
            # Clear flags
            context.user_data["creating_broadcast"] = False
            return ConversationHandler.END
        
        try:
            # Send based on content type
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
        
        # Add small delay between sends (20 messages per second)
        await asyncio.sleep(0.05)
        
        # Save progress for possible recovery
        context.user_data["broadcast_progress"] = i + 1
        
        # Update status every 5 sent messages or for the last one
        if (i + 1) % 5 == 0 or i + 1 == len(recipients):
            progress = ((i + 1) / len(recipients) * 100)
            try:
                await context.bot.edit_message_text(
                    chat_id=context.user_data["status_chat_id"],
                    message_id=context.user_data["status_message_id"],
                    text=f"Розсилка в процесі...\n"
                         f"{progress:.1f}% виконано ({i+1}/{len(recipients)})\n\n"
                         f"✅ Успішно відправлено: {sent_count}\n"
                         f"❌ Не вдалося відправити: {failed_count}\n\n"
                         f"Ви можете скасувати розсилку, натиснувши кнопку нижче:",
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Error updating status message: {e}")
    
    # Message about broadcast completion
    try:
        await context.bot.edit_message_text(
            chat_id=context.user_data["status_chat_id"],
            message_id=context.user_data["status_message_id"],
            text=f"Розсилка завершена!\n\n"
                 f"✅ Успішно відправлено: {sent_count}\n"
                 f"❌ Не вдалося відправити: {failed_count}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад до меню", callback_data="admin_back")
            ]])
        )
    except Exception as e:
        logger.error(f"Error updating final status message: {e}")
    
    # Clear flags
    context.user_data["creating_broadcast"] = False
    
    return ConversationHandler.END

# 23.7 Cancel broadcast
async def broadcast_cancel_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel active broadcast."""
    query = update.callback_query
    await query.answer()
    
    # Set broadcast cancellation flag
    context.user_data["broadcast_cancelled"] = True
    
    # Send as a new message instead of edit to avoid possible errors
    await query.message.reply_text(
        "Розсилка буде скасована після завершення поточного повідомлення..."
    )
    
    # Clear flags
    context.user_data["creating_broadcast"] = False
    
    return ConversationHandler.END

async def broadcast_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel broadcast creation process."""
    query = update.callback_query
    if query:
        await query.answer()
    
    # Clear broadcast data
    keys_to_remove = [
        "broadcast_target", "broadcast_content_type", "broadcast_text", 
        "broadcast_photo_id", "broadcast_video_id", "broadcast_caption", 
        "broadcast_recipients", "status_message_id", "status_chat_id", 
        "broadcast_cancelled", "creating_broadcast", "confirm_message_id"
    ]
    
    for key in keys_to_remove:
        context.user_data.pop(key, None)
    
    # Send as a new message instead of edit to avoid possible errors
    if query:
        await query.message.reply_text(
            "Розсилку скасовано.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад до меню", callback_data="admin_back")
            ]])
        )
    else:
        await update.message.reply_text(
            "Розсилку скасовано.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад до меню", callback_data="admin_back")
            ]])
        )
    
    return ConversationHandler.END

# Command to start broadcast
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler for /broadcast command to start broadcast."""
    user_id = update.effective_user.id
    
    # Check if user is an administrator
    if not is_admin(user_id):
        await update.message.reply_text("You don't have access to this command.")
        return ConversationHandler.END
    
    # Start broadcast process
    return await start_broadcast(update, context)

# Cancel broadcast via /cancel command
async def broadcast_command_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel broadcast creation process via /cancel command."""
    # Clear broadcast data
    keys_to_remove = [
        "broadcast_target", "broadcast_content_type", "broadcast_text", 
        "broadcast_photo_id", "broadcast_video_id", "broadcast_caption", 
        "broadcast_recipients", "status_message_id", "status_chat_id", 
        "broadcast_cancelled", "creating_broadcast", "confirm_message_id"
    ]
    
    for key in keys_to_remove:
        context.user_data.pop(key, None)
    
    await update.message.reply_text(
        "Розсилку скасовано.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Назад до меню", callback_data="admin_back")
        ]])
    )
    
    return ConversationHandler.END

# Main function to start the bot
def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add ConversationHandler for contact data request
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(request_contact, pattern="^request_contact$"),
            CallbackQueryHandler(hotel_selection, pattern="^hotel_selection$")
        ],
        states={
            PHONE: [MessageHandler(filters.CONTACT, process_contact)],
            PROCESSING: [MessageHandler(filters.TEXT, cancel)]  # Добавлен дополнительный стан для обработки отмены
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
        per_chat=True
    )
    
    # Обновлен ConversationHandler для рассылки сообщений
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
                MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_text_received),
                CommandHandler("cancel", broadcast_command_cancel)
            ],
            BROADCAST_PHOTO: [
                MessageHandler(filters.PHOTO, broadcast_photo_received),
                CommandHandler("cancel", broadcast_command_cancel)
            ],
            BROADCAST_VIDEO: [
                MessageHandler(filters.VIDEO, broadcast_video_received),
                CommandHandler("cancel", broadcast_command_cancel)
            ],
            BROADCAST_CONFIRM: [
                CallbackQueryHandler(broadcast_confirm, pattern="^broadcast_confirm$"),
                CallbackQueryHandler(continue_broadcast, pattern="^continue_broadcast$"),
                CallbackQueryHandler(broadcast_cancel, pattern="^broadcast_cancel$"),
                CallbackQueryHandler(broadcast_cancel_confirmation, pattern="^broadcast_cancel_confirm$")
            ],
        },
        fallbacks=[CommandHandler("cancel", broadcast_command_cancel)],
        allow_reentry=True
    )
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    
    # State handlers should have high priority (group 1)
    application.add_handler(broadcast_handler, group=1)
    application.add_handler(conv_handler, group=1)  # Contact data request handler
    
    # Add callback query handlers (group 5)
    application.add_handler(CallbackQueryHandler(more_info, pattern="^more_info$"), group=5)
    application.add_handler(CallbackQueryHandler(training_info, pattern="^training_info$"), group=5)
    application.add_handler(CallbackQueryHandler(documents, pattern="^documents$"), group=5)
    application.add_handler(CallbackQueryHandler(testimonials, pattern="^testimonials$"), group=5)
    application.add_handler(CallbackQueryHandler(ask_question, pattern="^ask_question$"), group=5)
    application.add_handler(CallbackQueryHandler(social_media, pattern="^social_media$"), group=5)
    application.add_handler(CallbackQueryHandler(social_media_back, pattern="^social_media_back$"), group=5)  # New handler for social media back button
    application.add_handler(CallbackQueryHandler(agent_testimonials, pattern="^agent_testimonials$"), group=5)
    application.add_handler(CallbackQueryHandler(next_agent_testimonial, pattern="^next_agent_testimonial$"), group=5)
    application.add_handler(CallbackQueryHandler(back_to_source, pattern="^back_to_source$"), group=5)
    application.add_handler(CallbackQueryHandler(contract, pattern="^contract$"), group=5)
    application.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"), group=5)
    
    # Handlers for testimonials with unique callback_data
    application.add_handler(CallbackQueryHandler(testimonial_1, pattern="^testimonial_1$"), group=5)
    application.add_handler(CallbackQueryHandler(testimonial_2, pattern="^testimonial_2$"), group=5)
    application.add_handler(CallbackQueryHandler(testimonial_3, pattern="^testimonial_3$"), group=5)
    application.add_handler(CallbackQueryHandler(testimonial_4, pattern="^testimonial_4$"), group=5)
    application.add_handler(CallbackQueryHandler(testimonial_5, pattern="^testimonial_5$"), group=5)
    application.add_handler(CallbackQueryHandler(testimonial_6, pattern="^testimonial_6$"), group=5)
    application.add_handler(CallbackQueryHandler(testimonial_7, pattern="^testimonial_7$"), group=5)
    
    # Admin panel handlers
    application.add_handler(CallbackQueryHandler(admin_buttons, pattern="^admin_"), group=5)
    
    # Course handlers
    application.add_handler(CallbackQueryHandler(full_course, pattern="^full_course$"), group=5)
    application.add_handler(CallbackQueryHandler(pro_full_course, pattern="^pro_full_course$"), group=5)
    application.add_handler(CallbackQueryHandler(gradual_course, pattern="^gradual_course$"), group=5)
    application.add_handler(CallbackQueryHandler(pro_gradual_course, pattern="^pro_gradual_course$"), group=5)
    application.add_handler(CallbackQueryHandler(next_video, pattern="^next_video$"), group=5)
    application.add_handler(CallbackQueryHandler(next_pro_video, pattern="^next_pro_video$"), group=5)
    application.add_handler(CallbackQueryHandler(course_completed, pattern="^course_completed$"), group=5)
    application.add_handler(CallbackQueryHandler(pro_course_completed, pattern="^pro_course_completed$"), group=5)
    application.add_handler(CallbackQueryHandler(i_am_agent, pattern="^i_am_agent$"), group=5)
    application.add_handler(CallbackQueryHandler(next_agent_video, pattern="^next_agent_video$"), group=5)
    application.add_handler(CallbackQueryHandler(about_course, pattern="^about_course$"), group=5)
    application.add_handler(CallbackQueryHandler(next_course_video, pattern="^next_course_video$"), group=5)
    
    # Text message handler should have low priority (group 10)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message), group=10)
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()