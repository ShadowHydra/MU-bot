import telebot
import feedparser
import time
from googletrans import Translator
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
# ከላይ ከኢምፖርቶቹ ጋር ይሄን ጨምር
from deep_translator import GoogleTranslator





# --- ማስተካከያ ---
API_TOKEN = '8683345761:AAGMWkPkvaG1rzh-yAzu6PPRTr9QKo5Bh48'
CHANNEL_ID = '@wewonalot'
# ----------------

bot = telebot.TeleBot(API_TOKEN)
translator = Translator()

# የተለጠፉ ዜናዎችን ለማስታወስ (ድግግሞሽ ለመከላከል)
posted_links = set()

def get_image(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        img = soup.find('meta', property='og:image')
        if img: return img['content']
    except:
        return "https://upload.wikimedia.org/wikipedia/en/7/7a/Manchester_United_FC_crest.svg"
    return "https://upload.wikimedia.org/wikipedia/en/7/7a/Manchester_United_FC_crest.svg"

def send_news():
    global posted_links
    RSS_FEEDS = [
        'https://www.dailymail.co.uk/sport/teampages/manchester-united.rss',
        'https://www.skysports.com/rss/11667',
        'https://news.google.com/rss/search?q=Manchester+United+news'
    ]
    
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]: # ከእያንዳንዱ ምንጭ የቅርብ 5ቱን ብቻ እይ
            if entry.link not in posted_links:
                
                # ከ24 ሰዓት በፊት የነበሩ የቆዩ ዜናዎችን ዝለል
                pub_date = getattr(entry, 'published_parsed', None)
                if pub_date:
                    dt = datetime(*pub_date[:6])
                    if dt < datetime.now() - timedelta(days=1):
                        continue

                try:
                    # ትርጉም
# ኮዱ ውስጥ translator = Translator() የሚለውን አጥፍተህ በዚህ ተካው
def translate_to_amharic(text):
    try:
        return GoogleTranslator(source='auto', target='am').translate(text)
    except:
        return text # ትርጉሙ ካልሰራ ዋናውን እንግሊዝኛውን ይላክ
                    
                    # ፎቶ መፈለግ
                    image_url = get_image(entry.link)
                    
                    caption = f"🔴 **ሰበር የዩናይትድ ዜና**\n\n📌 {title_am}\n\n🔗 [ሙሉውን ለማንበብ እዚህ ይጫኑ]({entry.link})\n\n@wewonalot"
                    
                    # መጀመሪያ ፎቶ ለመላክ ይሞክራል፣ ካልተሳካ በጽሁፍ ብቻ
                    try:
                        bot.send_photo(CHANNEL_ID, image_url, caption=caption, parse_mode='Markdown')
                    except:
                        bot.send_message(CHANNEL_ID, caption, parse_mode='Markdown')
                    
                    # ድግግሞሽ ለመከላከል ሊንኩን መመዝገብ
                    posted_links.add(entry.link)
                    print(f"✅ ተለጠፈ: {entry.title}")
                    
                    time.sleep(5) 
                except Exception as e:
                    print(f"❌ ስህተት: {e}")

# ቦቱ ሲነሳ መጀመሪያ ያሉትን ዜናዎች እንደተለጠፉ ይቁጠራቸው (ድግግሞሽ ለመከላከል)
def initialize_links():
    global posted_links
    feeds = ['https://www.dailymail.co.uk/sport/teampages/manchester-united.rss']
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            posted_links.add(entry.link)

print("🚀 ቦቱ ስራ ጀምሯል...")
initialize_links() # መጀመሪያ የቆዩትን ይዝለል

while True:
    try:
        send_news()
    except Exception as e:
        print(f"⚠️ Error in loop: {e}")
    time.sleep(600) # በየ 10 ደቂቃው ይፈልጋል    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if entry.link not in posted_links:
                # ከ24 ሰዓት በፊት የነበሩትን ዝለል
                pub_date = getattr(entry, 'published_parsed', None)
                if pub_date and datetime(*pub_date[:6]) < datetime.now() - timedelta(days=1):
                    continue

                # ትርጉም
                title_am = translator.translate(entry.title, dest='am').text
                summary_am = translator.translate(entry.summary[:300], dest='am').text if 'summary' in entry else ""
                
                # ፎቶ ፍለጋ
                image_url = get_image(entry.link)
                
                caption = f"🔴 **ሰበር የዩናይትድ ዜና**\n\n📌 {title_am}\n\n📝 {summary_am}...\n\n🔗 [ሙሉውን ለማንበብ እዚህ ይጫኑ]({entry.link})\n\n@wewonalot"
                
                try:
                    bot.send_photo(CHANNEL_ID, image_url, caption=caption, parse_mode='Markdown')
                    posted_links.add(entry.link)
                    print(f"✅ ተለጠፈ: {entry.title}")
                except:
                    bot.send_message(CHANNEL_ID, caption, parse_mode='Markdown')
                
                time.sleep(5)

while True:
    try:
        send_news()
    except Exception as e:
        print(f"❌ ስህተት: {e}")
    time.sleep(600) # በየ 10 ደቂቃው ይፈልጋል
def create_markup(link):
    markup = types.InlineKeyboardMarkup(row_width=4)
    btns = [
        types.InlineKeyboardButton("🔥", callback_data="1"),
        types.InlineKeyboardButton("❤️", callback_data="2"),
        types.InlineKeyboardButton("👏", callback_data="3"),
        types.InlineKeyboardButton("😮", callback_data="4")
    ]
    share_btn = types.InlineKeyboardButton("📤 ለጓደኛዎ ያጋሩ", url=f"https://t.me/share/url?url={link}")
    markup.add(*btns)
    markup.row(share_btn)
    return markup

def start_bot():
    print("🚀 Render ላይ ስራ ተጀምሯል - ሰፊ ፍለጋ...")
    
    for url in SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                title_en = entry.title.split(" - ")[0]
                # የላቲን ኮዶችን ማጽጃ
                summary_en = re.sub('<[^<]+?>', '', entry.summary)[:500]
                link = entry.link

                try:
                    # Render ላይ ትርጉሙ በደንብ ይሰራል
                    title_am = translator.translate(title_en, dest='am').text
                    summary_am = translator.translate(summary_en, dest='am').text
                    
                    caption = (
                        f"🔴 **{title_am}**\n\n"
                        f"📝 **ዝርዝር መረጃ:**\n{summary_am}...\n\n"
                        f"🔗 [ሙሉውን ለማንበብ እዚህ ይጫኑ]({link})\n\n"
                        f"👉 @wewonalot"
                    )

                    bot.send_photo(CHANNEL_ID, DEFAULT_IMAGE, caption=caption, parse_mode="Markdown", reply_markup=create_markup(link))
                    print(f"✅ ተለጠፈ: {title_en[:20]}")
                    time.sleep(15) # ለቴሌግራም ደህንነት
                except Exception as e:
                    print(f"⚠️ ትርጉም/መላክ አልተሳካም: {e}")

        except Exception as e:
            print(f"❌ ምንጩ አልሰራም: {e}")

    time.sleep(600) # በየ 10 ደቂቃው እንዲፈልግ

if __name__ == "__main__":
    while True:
        start_bot()
