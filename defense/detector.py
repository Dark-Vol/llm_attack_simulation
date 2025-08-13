def is_suspicious(email_text):
    suspicious_keywords = ["click the link", "reset your password", "urgent", "confirm account"]
    for word in suspicious_keywords:
        if word in email_text.lower():
            return True
    return False
