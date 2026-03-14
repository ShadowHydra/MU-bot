import telebot
import feedparser
import time
from deep_translator import GoogleTranslator

# --- ማስተካከያ ---
API_TOKEN = '8683345761:AAGMWkPkvaG1rzh-yAzu6PPRTr9QKo5Bh48'
CHANNEL_ID = '@wewonalot'
# ----------------

bot = telebot.TeleBot(API_TOKEN)
posted_links = set()

def translate_amharic(text):
    try:
        return GoogleTranslator(source='auto', target='am').translate(text)
    except:
        return text

def send_news():
    global posted_links
    RSS_FEEDS = [
        'https://www.skysports.com/rss/11667',
        'https://www.manchestereveningnews.co.uk/sport/football/manchester-united-fc/?service=rss'
    ]
    
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            if entry.link not in posted_links:
                # ዜናው ስለ ዩናይትድ መሆኑን ቼክ አድርግ
                if "united" in entry.title.lower() or "man u" in entry.title.lower():
                    try:
                        title_am = translate_amharic(entry.title)
                        
                        # ፎቶውን ቴሌግራም ራሱ እንዲያመጣው ሊንኩን መላክ
                        caption = (
                            f"🔴 **ሰበር የዩናይትድ ዜና**\n\n"
                            f"📌 {title_am}\n\n"
                            f"🔗 {entry.link}\n\n" # ሊንኩ ከስር መሆኑ ፎቶው እንዲመጣ ይረዳል
                            f"ተከታተሉን 👉 {CHANNEL_ID}"
                        )
                        
                        # በፎቶ ፋንታ በሜሴጅ እንልከዋለን (Link Preview እንዲሰራ)
                        bot.send_message(CHANNEL_ID, caption, parse_mode='Markdown', disable_web_page_preview=False)
                        
                        posted_links.add(entry.link)
                        print(f"✅ ተለጠፈ: {entry.title}")
                        time.sleep(5)
                    except Exception as e:
                        print(f"❌ ስህተት: {e}")

def initialize():
    print("🔄 የቆዩ ዜናዎችን በመመዝገብ ላይ...")
    feed = feedparser.parse('https://www.skysports.com/rss/11667')
    for entry in feed.entries:
        posted_links.add(entry.link)
    print("✅ ዝግጁ!")

if __name__ == "__main__":
    initialize()
    while True:
        try:
            send_news()
        except Exception as e:
            print(f"⚠️ Loop Error: {e}")
        time.sleep(600)
