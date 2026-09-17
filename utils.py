import os
import streamlit as st
from database import log_notification

def show_image(path, caption="", width=None, fallback_emoji="🏥"):
    if path and os.path.exists(path):
        st.image(path, caption=caption, width=width)
    else:
        st.markdown(
            f"<div style='text-align:center; font-size:4rem;'>{fallback_emoji}</div>",
            unsafe_allow_html=True
        )

def send_email(user_id, recipient, subject, body):
    log_notification(user_id, recipient, subject, body)
    print(f"[EMAIL] To: {recipient} | Subject: {subject}\n {body}")

def send_sms(user_id, phone, message):
    log_notification(user_id, phone, "SMS", message)
    print(f"[SMS] To: {phone} | {message}")

def process_payment(card_number, expiry, cvv, amount):
    if len(str(card_number)) < 13 or len(str(cvv)) < 3:
        return False, "Invalid card details"
    return True, f"Payment of Rs. {amount} processed successfully (Demo)"
