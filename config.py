import os

# הגדרות הבוט
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# נתיב לקובץ האימוג'י
EMOJI_PATH = os.path.join(os.path.dirname(__file__), 'pig_nose.png')

# הגדרות עיבוד תמונה
EMOJI_SIZE_RATIO = 1/3  # יחס גודל האימוג'י ביחס לגודל הפנים

# הגדרות שגיאה
MAX_RETRIES = 3  # מספר הניסיונות המקסימלי לעיבוד תמונה