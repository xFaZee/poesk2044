import os
import time
import threading
import concurrent.futures
from datetime import datetime
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
import whois
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    CallbackQueryHandler,
    filters
)

# Конфигурация
MAX_WORKERS = 30
TIMEOUT = 10
RESULTS_DIR = "Poisk2004_Results"
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
]

# Ссылки для кнопок
SUPPORT_LINK = "https://t.me/ваш_аккаунт"
DONATE_LINK = "https://pay.tg/ваш_кошелек"

# База сервисов
SERVICES = {
    'VK': 'https://vk.com/{}',
    'Telegram': 'https://t.me/{}',
    'GitHub': 'https://github.com/{}',
    'Reddit': 'https://www.reddit.com/user/{}',
    'TikTok': 'https://www.tiktok.com/@{}',
    'Pinterest': 'https://www.pinterest.com/{}',
    'Flickr': 'https://www.flickr.com/people/{}',
    'Vimeo': 'https://vimeo.com/{}',
    'Mixcloud': 'https://www.mixcloud.com/{}/',
    'Tumblr': 'https://{}.tumblr.com',
    'WeHeartIt': 'https://weheartit.com/{}',
    'DeviantArt': 'https://{}.deviantart.com',
    '500px': 'https://500px.com/p/{}',
    'VSCO': 'https://vsco.co/{}',
    'Behance': 'https://www.behance.net/{}',

    # Технологии и разработка
    'GitLab': 'https://gitlab.com/{}',
    'Bitbucket': 'https://bitbucket.org/{}',
    'StackOverflow': 'https://stackoverflow.com/users/{}',
    'StackExchange': 'https://stackexchange.com/users/{}',
    'HackerRank': 'https://www.hackerrank.com/{}',
    'LeetCode': 'https://leetcode.com/{}',
    'CodePen': 'https://codepen.io/{}',
    'Repl.it': 'https://repl.it/@{}',
    'Codecademy': 'https://www.codecademy.com/profiles/{}',
    'Kaggle': 'https://www.kaggle.com/{}',
    'Dev.to': 'https://dev.to/{}',
    'Codewars': 'https://www.codewars.com/users/{}',
    'Topcoder': 'https://www.topcoder.com/members/{}',
    'HackerEarth': 'https://www.hackerearth.com/@{}',
    'Exercism': 'https://exercism.io/profiles/{}',
    'FreeCodeCamp': 'https://www.freecodecamp.org/{}',
    'Glitch': 'https://glitch.com/@{}',
    'Scratch': 'https://scratch.mit.edu/users/{}',
    'JSFiddle': 'https://jsfiddle.net/user/{}/',
    'CodeSandbox': 'https://codesandbox.io/u/{}',

    # Медиа и развлечения
    'Last.fm': 'https://www.last.fm/user/{}',
    'Bandcamp': 'https://bandcamp.com/{}',
    'ReverbNation': 'https://www.reverbnation.com/{}',
    'Smule': 'https://www.smule.com/{}',
    'Unsplash': 'https://unsplash.com/@{}',
    'IMDb': 'https://www.imdb.com/user/ur{}',
    'Letterboxd': 'https://letterboxd.com/{}',
    'Trakt': 'https://www.trakt.tv/users/{}',
    'MyAnimeList': 'https://myanimelist.net/profile/{}',

    # Игры
    'Steam': 'https://steamcommunity.com/id/{}',
    'Epic Games': 'https://www.epicgames.com/account/personal?productName={}',
    'Roblox': 'https://www.roblox.com/user.aspx?username={}',
    'Fortnite Tracker': 'https://fortnitetracker.com/profile/all/{}',
    'Xbox': 'https://xboxgamertag.com/search/{}',
    'PlayStation': 'https://psnprofiles.com/{}',
    'Origin': 'https://www.origin.com/usa/en-us/profile/{}',
    'Battle.net': 'https://battle.net/account/management/',
    'GOG': 'https://www.gog.com/u/{}',
    'Ubisoft': 'https://club.ubisoft.com/en-US/profile/{}',
    'Chess.com': 'https://api.chess.com/pub/player/{}',
    'Speedrun.com': 'https://www.speedrun.com/user/{}',
    'Giant Bomb': 'https://www.giantbomb.com/profile/{}/',
    'Destiny Tracker': 'https://destinytracker.com/d2/profile/{}',

    # Форумы и обсуждения
    'HackerNews': 'https://news.ycombinator.com/user?id={}',
    'ProductHunt': 'https://www.producthunt.com/@{}',
    'Slashdot': 'https://slashdot.org/~{}',
    'Instructables': 'https://www.instructables.com/member/{}',
    'Hackaday': 'https://hackaday.io/{}',
    'Blender Artists': 'https://blenderartists.org/u/{}',
    'Unity Forum': 'https://forum.unity.com/members/{}/',

    # Профессиональные сервисы
    'Fiverr': 'https://www.fiverr.com/{}',
    'Upwork': 'https://www.upwork.com/freelancers/{}',
    'Freelancer': 'https://www.freelancer.com/u/{}',
    'Toptal': 'https://www.toptal.com/resume/{}',
    'AngelList': 'https://angel.co/{}',
    'Crunchbase': 'https://www.crunchbase.com/person/{}',
    'Dribbble': 'https://dribbble.com/{}',
    'Carbonmade': 'https://{}.carbonmade.com',

    # Электронная коммерция
    'Etsy': 'https://www.etsy.com/shop/{}',
    'eBay': 'https://www.ebay.com/usr/{}',
    'Amazon': 'https://www.amazon.com/gp/profile/amzn1.account.{}',
    'AliExpress': 'https://www.aliexpress.com/store/{}',
    'Wish': 'https://www.wish.com/{}',
    'Flippa': 'https://flippa.com/users/{}',
    'Shopify': 'https://{}.myshopify.com',
    'Big Cartel': 'https://{}.bigcartel.com',
    'Depop': 'https://www.depop.com/{}',
    'Redbubble': 'https://www.redbubble.com/people/{}',

    # Образование
    'KhanAcademy': 'https://www.khanacademy.org/profile/{}',
    'Duolingo': 'https://www.duolingo.com/profile/{}',
    'Skillshare': 'https://www.skillshare.com/profile/{}/',
    'Academia.edu': 'https://independent.academia.edu/{}',
    'ResearchGate': 'https://www.researchgate.net/profile/{}',
    'SlideShare': 'https://www.slideshare.net/{}',
    'SpeakerDeck': 'https://speakerdeck.com/{}',

    # Здоровье и фитнес
    'Strava': 'https://www.strava.com/athletes/{}',
    'MyFitnessPal': 'https://www.myfitnesspal.com/profile/{}',
    'Endomondo': 'https://www.endomondo.com/profile/{}',
    'Runkeeper': 'https://runkeeper.com/user/{}/profile',
    'MapMyRun': 'https://www.mapmyrun.com/profile/{}/',

    # Путешествия
    'TripAdvisor': 'https://www.tripadvisor.com/members/{}',
    'Airbnb': 'https://www.airbnb.com/users/show/{}',
    'Couchsurfing': 'https://www.couchsurfing.com/people/{}',
    'Foursquare': 'https://foursquare.com/{}',

    # Краудфандинг
    'Kickstarter': 'https://www.kickstarter.com/profile/{}',
    'Indiegogo': 'https://www.indiegogo.com/individuals/{}',
    'GoFundMe': 'https://www.gofundme.com/mvc.php?route=profile/{}',
    'BuyMeACoffee': 'https://www.buymeacoffee.com/{}',

    # Безопасность и приватность
    'Keybase': 'https://keybase.io/{}',
    'HaveIBeenPwned': 'https://haveibeenpwned.com/',
    'Privacy.com': 'https://privacy.com/',

    # Другие
    'Pastebin': 'https://pastebin.com/u/{}',
    'Wikipedia': 'https://en.wikipedia.org/wiki/User:{}',
    'Slack': 'https://{}.slack.com',
    'Discord': 'https://discord.com/users/{}',
    'TradingView': 'https://www.tradingview.com/u/{}/',
    'Houzz': 'https://www.houzz.com/user/{}',
    'Zillow': 'https://www.zillow.com/profile/{}',
    'Realtor.com': 'https://www.realtor.com/realestateagents/{}',
    'Yelp': 'https://www.yelp.com/user_details?userid={}'
}

class UsernameAnalyzer:
    def __init__(self, username):
        self.username = username
        self.registration_dates = {}
        self.name_history = {}
        self.social_links = {}

    def analyze_vk(self):
        try:
            url = f"https://vk.com/{self.username}"
            response = requests.get(url, headers={'User-Agent': USER_AGENTS[0]}, timeout=TIMEOUT)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Поиск даты регистрации
                profile_info = soup.find('div', class_='profile_info_row')
                if profile_info and "С нами с" in profile_info.text:
                    self.registration_dates['VK'] = profile_info.text.split("С нами с")[1].strip()
                
                # Поиск истории имен
                name_history = []
                for item in soup.find_all('div', class_='profile_info_row'):
                    if "был" in item.text or "была" in item.text:
                        name_history.append(item.text.strip())
                if name_history:
                    self.name_history['VK'] = name_history
                
                return url
        except Exception as e:
            print(f"Ошибка анализа VK: {e}")
            return None

    def analyze_github(self):
        try:
            url = f"https://api.github.com/users/{self.username}"
            response = requests.get(url, headers={'User-Agent': USER_AGENTS[0]}, timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                created_at = datetime.strptime(data['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                self.registration_dates['GitHub'] = created_at.strftime('%d.%m.%Y')
                return f"https://github.com/{self.username}"
        except Exception as e:
            print(f"Ошибка анализа GitHub: {e}")
            return None

    def analyze_domain(self):
        """Безопасный анализ домена с соблюдением правил WHOIS"""
        try:
            domain = f"{self.username}.com"
            
            # Сначала проверяем доступность сайта
            try:
                response = requests.get(f"http://{domain}", timeout=5)
                if response.status_code == 200:
                    self.social_links['Domain'] = f"http://{domain}"
                    return f"http://{domain}"
            except:
                pass
            
            # Если сайт недоступен, делаем ОДИН запрос WHOIS с задержкой
            time.sleep(2)  # Соблюдаем правила VeriSign
            
            try:
                w = whois.whois(domain)
                if w.creation_date:
                    if isinstance(w.creation_date, list):
                        date = w.creation_date[0]
                    else:
                        date = w.creation_date
                    
                    date_str = date.strftime('%d.%m.%Y') if date else "Неизвестно"
                    self.registration_dates['Domain'] = f"{date_str} (данные WHOIS для справки)"
                    
                    return f"http://{domain}"
            except Exception as e:
                print(f"Ошибка WHOIS запроса: {e}")
                return None
                
        except Exception as e:
            print(f"Общая ошибка анализа домена: {e}")
            return None

    def run_analysis(self):
        """Запуск всех анализов с ограничениями"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.analyze_vk): 'VK',
                executor.submit(self.analyze_github): 'GitHub',
                executor.submit(self.analyze_domain): 'Domain'
            }
            
            for future in concurrent.futures.as_completed(futures):
                service = futures[future]
                try:
                    self.social_links[service] = future.result()
                except Exception as e:
                    print(f"Ошибка при анализе {service}: {e}")
        
        return {
            'registration_dates': self.registration_dates,
            'name_history': self.name_history,
            'social_links': {k: v for k, v in self.social_links.items() if v}
        }

class Scanner:
    def __init__(self):
        self.session = requests.Session()
        self.results = {'found': [], 'not_found': [], 'errors': [], 'checked': []}
        self.lock = threading.Lock()
        self.counter = 0
        self.stop_event = threading.Event()

    def check_service(self, service_name, url_template, username):
        """Проверка одного сервиса"""
        if self.stop_event.is_set():
            return None

        try:
            url = url_template.format(quote(username))
            headers = {
                'User-Agent': USER_AGENTS[self.counter % len(USER_AGENTS)],
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = self.session.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=False)
            
            with self.lock:
                self.counter += 1

            if response.status_code == 200 and username.lower() in response.text.lower():
                return (service_name, url, 'found')
            return (service_name, url, 'not_found')

        except Exception as e:
            return (service_name, url_template, 'error')

    def run_scan(self, username):
        """Запуск сканирования"""
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            for name, url in SERVICES.items():
                future = executor.submit(self.check_service, name, url, username)
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    service, url, status = result
                    with self.lock:
                        self.results['checked'].append(service)
                        if status == 'found':
                            self.results['found'].append((service, url))
                        elif status == 'error':
                            self.results['errors'].append(service)
                        else:
                            self.results['not_found'].append(service)

        elapsed = time.time() - start_time
        return self.results, elapsed

def save_report(username, results, exec_time, analysis_data=None):
    """Сохранение отчета с учетом правил WHOIS"""
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{RESULTS_DIR}/{username}_report_{timestamp}.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"=== Poisk2004 Report ===\n\n")
        f.write(f"Никнейм: {username}\n")
        f.write(f"Дата: {timestamp}\n")
        f.write(f"Время выполнения: {exec_time:.2f} сек\n")
        f.write(f"Всего проверено сервисов: {len(results['checked'])}\n\n")
        
        if analysis_data:
            f.write("=== Анализ данных ===\n")
            if analysis_data.get('registration_dates'):
                f.write("Даты регистрации:\n")
                for service, date in analysis_data['registration_dates'].items():
                    if service == 'Domain':
                        f.write(f"- {service}: {date}\n")
                    else:
                        f.write(f"- {service}: {date}\n")
            
            if analysis_data.get('name_history'):
                f.write("\nИстория имен:\n")
                for service, history in analysis_data['name_history'].items():
                    f.write(f"- {service}:\n")
                    for item in history[:3]:  # Ограничиваем количество записей
                        f.write(f"  * {item}\n")
            f.write("\n")
        
        f.write("=== Найденные аккаунты ===\n")
        if results['found']:
            for service, url in results['found']:
                f.write(f"{service}: {url}\n")
        else:
            f.write("Не найдено\n")
        
        f.write("\n=== Ошибки проверки ===\n")
        if results['errors']:
            f.write(", ".join(results['errors']) + "\n")
        else:
            f.write("Нет ошибок\n")
        
        f.write("\n=== Все проверенные сервисы ===\n")
        f.write(", ".join(sorted(results['checked'])) + "\n")

    return filename

def format_results(username, results, exec_time, analysis_data=None):
    """Форматирование результатов для Telegram"""
    message = f"🔍 <b>Результаты поиска для:</b> <code>{username}</code>\n\n"
    
    if analysis_data:
        message += "📅 <b>Анализ данных:</b>\n"
        
        if analysis_data.get('registration_dates'):
            message += "🗓 <i>Даты регистрации:</i>\n"
            for service, date in analysis_data['registration_dates'].items():
                message += f"• {service}: {date}\n"
        
        if analysis_data.get('name_history'):
            message += "\n📜 <i>История имен:</i>\n"
            for service, history in analysis_data['name_history'].items():
                message += f"• {service}:\n"
                for item in history[:3]:
                    message += f"  - {item}\n"
        
        message += "\n"
    
    message += f"📊 <b>Статистика:</b>\n"
    message += f"• Всего сервисов: {len(SERVICES)}\n"
    message += f"• Проверено: {len(results['checked'])}\n"
    message += f"• Найдено: {len(results['found'])}\n"
    message += f"• Ошибки: {len(results['errors'])}\n"
    message += f"⏱ Время выполнения: {exec_time:.2f} сек\n\n"
    
    if results['found']:
        message += "✅ <b>Найденные аккаунты:</b>\n"
        for service, url in results['found']:
            message += f"• <a href='{url}'>{service}</a>\n"
    else:
        message += "❌ <b>Аккаунты не найдены</b>\n"
    
    if results['errors']:
        message += "\n⚠️ <b>Ошибки при проверке:</b>\n"
        message += ", ".join(results['errors']) + "\n"
    
    return message

async def start(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    welcome_text = (
        "👋 <b>Poisk2004 Bot</b> - поиск аккаунтов по никнейму\n\n"
        "🔍 Отправьте мне никнейм, и я проверю его наличие в популярных сервисах.\n"
        "📊 <b>Доступные функции:</b>\n"
        "- Поиск аккаунтов в 115+ сервисах\n"
        "- Анализ даты регистрации\n"
        "- История изменений никнейма\n"
        "- Проверка домена \n\n"
        "⏳ Обычно проверка занимает 10-30 секунд."
    )
    
    keyboard = [
        [InlineKeyboardButton("❓ Вопросы", url=SUPPORT_LINK)],
        [InlineKeyboardButton("💵 Поддержать", url=DONATE_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

async def handle_username(update: Update, context: CallbackContext):
    """Обработчик ввода никнейма"""
    username = update.message.text.strip()
    
    if not username:
        await update.message.reply_text("❌ Имя пользователя не может быть пустым!")
        return
    
    msg = await update.message.reply_text(
        f"🔎 Начинаю сканирование для <code>{username}</code>...\n"
        "Это может занять некоторое время ⏳",
        parse_mode='HTML'
    )
    
    try:
        # Анализ данных с ограничениями
        analyzer = UsernameAnalyzer(username)
        analysis_data = analyzer.run_analysis()
        
        # Основное сканирование
        scanner = Scanner()
        results, exec_time = scanner.run_scan(username)
        filename = save_report(username, results, exec_time, analysis_data)
        
        # Формируем результаты
        result_message = format_results(username, results, exec_time, analysis_data)
        
        keyboard = [
            [InlineKeyboardButton("📥 Скачать отчет", callback_data=f"report_{username}")],
            [InlineKeyboardButton("❓ Вопросы", url=SUPPORT_LINK)],
            [InlineKeyboardButton("💵 Поддержать", url=DONATE_LINK)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.edit_message_text(
            chat_id=update.message.chat_id,
            message_id=msg.message_id,
            text=result_message,
            parse_mode='HTML',
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        
        context.user_data['report_filename'] = filename
        
    except Exception as e:
        await update.message.reply_text(f"⚠️ Произошла ошибка: {str(e)}")

async def button_callback(update: Update, context: CallbackContext):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "start_cmd":
        await start(update, context)
    elif query.data.startswith("report_"):
        await send_report(update, context)

async def send_report(update: Update, context: CallbackContext):
    """Отправка отчета с учетом ограничений"""
    query = update.callback_query
    await query.answer()
    
    username = query.data.split('_')[1]
    filename = context.user_data.get('report_filename')
    
    if filename and os.path.exists(filename):
        with open(filename, 'rb') as f:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=f,
                caption=f"📄 Отчет для {username} (WHOIS данные предоставлены для справки)"
            )
    else:
        await query.edit_message_text(text="⚠️ Отчет не найден или был удален")

async def error_handler(update: Update, context: CallbackContext):
    """Обработчик ошибок"""
    error_msg = f"⚠️ Произошла ошибка: {context.error}"
    if update and update.message:
        await update.message.reply_text(error_msg)
    else:
        print(error_msg)

def main():
    """Запуск бота с проверкой зависимостей"""
    TOKEN = '8042992598:AAEShsB161fwFayK8-aQUNVuWF6qOziJN1g'  # Замените на реальный токен
    
    if TOKEN == 'YOUR_BOT_TOKEN':
        print("ОШИБКА: Укажите токен бота!")
        return
    
    # Проверка зависимостей
    try:
        import bs4
        import whois
    except ImportError:
        print("Установите зависимости: pip install beautifulsoup4 python-whois")
        return
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.add_error_handler(error_handler)
    
    print("Бот запущен с соблюдением правил WHOIS")
    application.run_polling()

if __name__ == "__main__":
    main()