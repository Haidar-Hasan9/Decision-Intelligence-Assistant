import re
from textblob import TextBlob

def compute_features(text: str):
    # Length features
    text_length = len(text)
    word_count = len(text.split())
    # Punctuation
    exclamation_count = text.count('!')
    question_count = text.count('?')
    # All-caps ratio
    uppercase_count = len(re.findall(r'[A-Z]', text))
    letter_count = len(re.findall(r'[A-Za-z]', text))
    all_caps_ratio = uppercase_count / letter_count if letter_count > 0 else 0.0
    # Sentiment
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    # Urgency keyword flag
    urgency_kw = r'refund|broken|cancel|down|help|urgent|asap|immediately|issue|complaint|frustrated|angry|problem|fail|stuck|wrong'
    has_urgent_keyword = 1 if re.search(urgency_kw, text, re.IGNORECASE) else 0
    return [text_length, word_count, exclamation_count, question_count, all_caps_ratio,
            polarity, subjectivity, has_urgent_keyword]