def log_event(message):
    with open("event_log.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)