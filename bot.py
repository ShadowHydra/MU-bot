
import telebot
import feedparser
import time
from googletrans import Translator
from telebot import types
import re

# --- 1. መለያዎች ---
API_TOKEN = '8683345761:AAGMWkPkvaG1rzh-yAzu6PPRTr9QKo5Bh48' # ያንተን ቶክን እዚህ አስገባ
CHANNEL_ID = '@wewonalot'
DEFAULT_IMAGE = "https://upload.wikimedia.org/wikipedia/en/thumb/7/7a/Manchester_United_FC_crest.svg/1200px-Manchester_United_FC_crest.svg.png"

bot = telebot.TeleBot(API_TOKEN)
translator = Translator()

# --- 2. ሰፊ የዜና ምንጮች (Facebook/Twitter/Transfer News በ Google በኩል) ---
SOURCES = [
    # የፌስቡክ እና ትዊተር ሰበር ዜናዎች
    "https://news.google.com/rss/search?q=Manchester+United+breaking+news+Facebook+Twitter+when:1h&hl=en-US&gl=US&ceid=US:en",
    # የዝውውር ወሬዎች
    "https://news.google.com/rss/search?q=Manchester+United+transfer+rumors+newsnow&hl=en-US&gl=US&ceid=US:en",
    # የጨዋታ ውጤት እና የቀጥታ መረጃ
    "https://news.google.com/rss/search?q=Manchester+United+match+score+live&hl=en-US&gl=US&ceid=US:en",
    # 1. የታወቁ ጋዜጠኞች (Fabrizio, Ornstein, ወዘተ) የዩናይትድ ዜናዎች
    "https://news.google.com/rss/search?q=Manchester+United+Fabrizio+Romano+OR+David+Ornstein+when:1h&hl=en-US&gl=US&ceid=US:en",
    
    # 2. የManchester Evening News ጋዜጠኞች (Samuel Luckhurst)
    "https://news.google.com/rss/search?q=Samuel+Luckhurst+Manchester+United+when:1h&hl=en-US&gl=US&ceid=US:en",
    
    # 3. የሶሻል ሚዲያ ሰበር ወሬዎች (Twitter/X trends)
    "https://news.google.com/rss/search?q=Manchester+United+Twitter+breaking+news+when:1h&hl=en-US&gl=US&ceid=US:en",
    
    # 4. የዝውውር ወሬዎች
    "https://news.google.com/rss/search?q=Manchester+United+transfer+rumors+newsnow&hl=en-US&gl=US&ceid=US:en"
]

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
