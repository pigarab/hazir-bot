import telebot
from telebot.apihelper import ApiTelegramException
from PIL import Image
import face_recognition
import io
import config
import numpy as np  # הוספנו את הייבוא הזה
import time
import os

# הגדרות הבוט
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

def improve_transparency(image, alpha_threshold=100):
    img = image.convert("RGBA")
    data = np.array(img)
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    
    # יצירת מסיכה מדויקת יותר
    transparent = (a <= alpha_threshold) | ((r > 200) & (g > 200) & (b > 200))
    data[:,:,3] = np.where(transparent, 0, 255)
    
    return Image.fromarray(data)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            # קבלת התמונה מהמשתמש
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # פתיחת התמונה כ-RGB במקום RGBA
            image = Image.open(io.BytesIO(downloaded_file)).convert("RGB")
            
            # המרה ל-numpy array לפני העברה ל-face_recognition
            image_np = np.array(image)
            
            # זיהוי פנים בתמונה
            face_locations = face_recognition.face_locations(image_np)
            
            if face_locations:
                # המרה חזרה ל-RGBA לצורך הוספת האימוג'י
                image = image.convert("RGBA")
                for face_location in face_locations:
                    top, right, bottom, left = face_location
                    nose_y = (top + bottom) // 2
                    nose_x = (left + right) // 2
                    
                    # הוספת האימוג'י לתמונה
                    emoji = Image.open(config.EMOJI_PATH).convert("RGBA")
                    emoji = improve_transparency(emoji)  # הפיכת האימוג'י לשקוף
                    emoji_size = int((right - left) * config.EMOJI_SIZE_RATIO * 0.7)  # הקטנה ב-30%
                    emoji = emoji.resize((emoji_size, emoji_size), Image.LANCZOS)
                    
                    # שימוש במסיכת האלפא של האימוג'י
                    image.paste(emoji, (nose_x - emoji.width // 2, nose_y - emoji.height // 2), emoji)
            
            # שמירת התמונה המעודכנת
            output = io.BytesIO()
            image.save(output, format='PNG')  # שינוי לפורמט PNG
            output.seek(0)
            
            # שליחת התמונה כתמונה ולא כקובץ
            bot.send_photo(message.chat.id, output)
            
            # אם הצלחנו, נצא מהלולאה
            break
        
        except (ApiTelegramException, requests.exceptions.ReadTimeout) as e:
            if attempt < max_retries - 1:
                print(f"ניסיון {attempt + 1} נכשל. מנסה שוב בעוד {retry_delay} שניות...")
                time.sleep(retry_delay)
            else:
                print(f"כל הניסיונות נכשלו. השגיאה האחרונה: {str(e)}")
                bot.reply_to(message, "מצטער, נתקלתי בבעיה בעיבוד התמונה. אנא נסה שוב מאוחר יותר.")