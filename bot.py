import telebot
import feedparser
import time
from deep_translator import GoogleTranslator
import requests
from bs4 import BeautifulSoup

# --- ማስተካከያ ---
API_TOKEN = '8683345761:AAGMWkPkvaG1rzh-yAzu6PPRTr9QKo5Bh48'
CHANNEL_ID = '@wewonalot'
# ----------------

bot = telebot.TeleBot(API_TOKEN)
posted_links = set()

def translate_amharic(text):
    if not text: return ""
    try:
        # ትርጉሙ ጥራት እንዲኖረው
        return GoogleTranslator(source='auto', target='am').translate(text)
    except:
        return text

def get_football_content(url):
    """ከድረ-ገጹ ላይ ትክክለኛ ፎቶ እና ዝርዝር መረጃ ለመውሰድ"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # ፎቶ ፍለጋ (OpenGraph)
        img_tag = soup.find('meta', property='og:image')
        image_url = img_tag['content'] if img_tag else None
        
        # ሎጎ ከሆነ ውድቅ ለማድረግ
        if image_url and ("logo" in image_url.lower() or "crest" in image_url.lower()):
            image_url = None

        # ዝርዝር ዜና ፍለጋ (የመጀመሪያዎቹን 2-3 አንቀጾች)
        paragraphs = soup.find_all('p')
        summary = " ".join([p.text for p in paragraphs[:3] if len(p.text) > 50])
        
        return image_url, summary
    except:
        return None, None

def send_news():
    global posted_links
    # 100% የእግር ኳስ ዜና ብቻ የሚለቁ ምንጮች
    RSS_FEEDS = [
        'https://www.skysports.com/rss/11667',
        'https://www.manchestereveningnews.co.uk/sport/football/manchester-united-fc/?service=rss'
    ]
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                if entry.link not in posted_links:
                    
                    # ዜናው እና ፎቶው ከድረ-ገጹ ይምጣ
                    image_url, full_summary = get_football_content(entry.link)
                    
                    if not full_summary:
                        full_summary = entry.get('summary', '')

                    title_am = translate_amharic(entry.title)
                    summary_am = translate_amharic(full_summary[:500]) # የመጀመሪያ 500 ቃላት

                    caption = (
                        f"🔴 **ሰበር የዩናይትድ ዜና**\n\n"
                        f"📌 **{title_am}**\n\n"
                        f"📝 {summary_am}...\n\n"
                        f"🔗 [ሙሉውን ለማንበብ እዚህ ይጫኑ]({entry.link})\n\n"
                        f"ተከታተሉን 👉 {CHANNEL_ID}"
                    )
                    
                    if image_url:
                        bot.send_photo(CHANNEL_ID, image_url, caption=caption, parse_mode='Markdown')
                        posted_links.add(entry.link)
                        time.sleep(10)
                    else:
                        # ፎቶ ከሌለ ሎጎ ከመላክ በጽሁፍ ብቻ ይላክ (Link Preview ፎቶ ያመጣል)
                        bot.send_message(CHANNEL_ID, caption, parse_mode='Markdown', disable_web_page_preview=False)
                        posted_links.add(entry.link)
                        time.sleep(10)
                        
        except Exception as e:
            print(f"Error: {e}")

def initialize():
    # ቦቱ ሲነሳ ያሉትን ዜናዎች መዝግብ (ድግግሞሽ ለመከላከል)
    for url in ['https://www.skysports.com/rss/11667']:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            posted_links.add(entry.link)

if __name__ == "__main__":
    initialize()
    print("🚀 ቦቱ ተስተካክሎ ስራ ጀምሯል...")
    while True:
        send_news()
        time.sleep(900) # በየ 15 ደቂቃው አንዴ
