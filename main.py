# main.py

from attack.phishing_generator import generate_email
from defense.detector import is_suspicious
from utils.logger import log_event

# Пример запуска генерации и проверки письма
def main():
    print("Симуляция атаки через LLM...")
    email = generate_email("Reset your password urgently!")

    print("Сгенерированное письмо:")
    print(email)

    if is_suspicious(email):
        log_event("Обнаружена подозрительная активность!")
        print("⚠️ Защита сработала: письмо подозрительное.")
    else:
        print("✅ Письмо выглядит безопасным.")

if __name__ == "__main__":
    main()
