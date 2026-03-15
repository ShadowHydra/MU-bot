import telebot
import feedparser
import time
from deep_translator import GoogleTranslator
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# --- ማስተካከያ ---
API_TOKEN = '8683345761:AAGMWkPkvaG1rzh-yAzu6PPRTr9QKo5Bh48'
CHANNEL_ID = '@wewonalot'
# ----------------

bot = telebot.TeleBot(API_TOKEN)
posted_links = set()

def translate_amharic(text):
    if not text: return ""
    try:
        # ጽሁፉ እንዳይቆራረጥ እስከ 1000 ፊደል ይተረጉማል
        return GoogleTranslator(source='auto', target='am').translate(text[:1000])
    except:
        return text

def get_full_details(url):
    """ከሊንኩ ላይ ዝርዝር ጽሁፍ እና ዋና ፎቶ ለመውሰድ"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # ፎቶ ፍለጋ
        img = soup.find('meta', property='og:image') or soup.find('meta', name='twitter:image')
        image_url = img['content'] if img else None
        
        # ዝርዝር ጽሁፍ ፍለጋ (ብዙውን ጊዜ በ <p> ውስጥ ያለውን የመጀመሪያ 2-3 አንቀጽ)
        paragraphs = soup.find_all('p')
        summary = " ".join([p.text for p in paragraphs[:2]]) # የመጀመሪያ 2 አንቀጾች
        
        return image_url, summary
    except:
        return None, None

def send_news():
    global posted_links
    RSS_FEEDS = [
        'https://www.skysports.com/rss/11667',
        'https://www.manchestereveningnews.co.uk/sport/football/manchester-united-fc/?service=rss'
    ]
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                if entry.link not in posted_links:
                    
                    # 1. የ24 ሰዓት ማጣሪያ
                    pub_date = getattr(entry, 'published_parsed', None)
                    if pub_date and datetime(*pub_date[:6]) < datetime.now() - timedelta(days=1):
                        continue

                    if "united" in entry.title.lower():
                        # 2. ዝርዝር መረጃ እና ፎቶ ከድረ-ገጹ መውሰድ
                        image_url, raw_summary = get_full_details(entry.link)
                        
                        # የነበረው summary ከሌለ በ feed ላይ ያለውን ተጠቀም
                        if not raw_summary: raw_summary = entry.get('summary', '')

                        # 3. መተርጎም
                        title_am = translate_amharic(entry.title)
                        summary_am = translate_amharic(raw_summary)
                        
                        caption = (
                            f"🔴 **ሰበር የዩናይትድ ዜና**\n\n"
                            f"📌 **{title_am}**\n\n"
                            f"📝 {summary_am}...\n\n"
                            f"🔗 [ሙሉውን ለማንበብ እዚህ ይጫኑ]({entry.link})\n\n"
                            f"ተከታተሉን 👉 {CHANNEL_ID}"
                        )
                        
                        # 4. መላክ (ፎቶ ካለ በፎቶ፣ ካልሆነ በጽሁፍ)
                        if image_url:
                            bot.send_photo(CHANNEL_ID, image_url, caption=caption, parse_mode='Markdown')
                        else:
                            bot.send_message(CHANNEL_ID, caption, parse_mode='Markdown', disable_web_page_preview=False)
                        
                        posted_links.add(entry.link)
                        time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")

def initialize():
    print("🔄 የቆዩ ዜናዎችን በማጣራት ላይ...")
    for url in ['https://www.skysports.com/rss/11667']:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            posted_links.add(entry.link)

if __name__ == "__main__":
    initialize()
    print("🚀 ቦቱ በዝርዝር ዜና እና በፎቶ ተስተካክሎ ስራ ጀምሯል...")
    while True:
        send_news()
        time.sleep(600)
