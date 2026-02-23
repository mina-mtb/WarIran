import os
import requests
from dotenv import load_dotenv

class Notifier:
    def __init__(self):
        load_dotenv()
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.proxies = {
            "http": os.getenv("TELEGRAM_PROXY"),
            "https": os.getenv("TELEGRAM_PROXY")
        } if os.getenv("TELEGRAM_PROXY") else None

    def send_message(self, text):
        """
        Sends a text message to the configured Telegram chat.
        """
        if not self.bot_token or not self.chat_id:
            print("Error: Telegram credentials missing in .env")
            return False

        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload, proxies=self.proxies, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

    def send_alert(self, event_type, lat, lon, details=None):
        """
        Formats and sends a high-priority alert.
        """
        message = (
            f"🚨 *WARIRAN ALERT: {event_type}* 🚨\n\n"
            f"📍 Location: `{lat}, {lon}`\n"
            f"🌐 [Open in Google Maps](https://www.google.com/maps?q={lat},{lon})\n"
        )
        if details:
            message += f"📝 Details: {details}\n"
        
        message += "\n⚠️ _Immediate verification recommended._"
        
        return self.send_message(message)

if __name__ == "__main__":
    # Test block
    notifier = Notifier()
    notifier.send_message("✅ WarIran Notifier is initialized and ready.")
