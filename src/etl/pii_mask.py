import re

PHONE_PATTERN = re.compile(r'(\+84|0)[0-9]{9,10}')
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
CARD_PATTERN = re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b')
ACCOUNT_PATTERN = re.compile(r'\b\d{10,16}\b')

def mask_phone(text):
    return PHONE_PATTERN.sub('[PHONE]', text)

def mask_email(text):
    return EMAIL_PATTERN.sub('[EMAIL]', text)

def mask_card(text):
    return CARD_PATTERN.sub('[CARD]', text)

def mask_account(text):
    return ACCOUNT_PATTERN.sub('[ACCOUNT]', text)

def mask_pii(text):
    if not text:
        return text

    text = mask_email(text)
    text = mask_phone(text)
    text = mask_card(text)

    return text

def mask_pii_full(text):
    text = mask_pii(text)
    text = mask_account(text)
    return text
