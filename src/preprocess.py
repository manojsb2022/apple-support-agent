"""
preprocess.py
Text preprocessing and cleaning pipeline for Apple customer support tweets.
"""

import re
import html
import unicodedata
from typing import List, Union

# Common English and social media contractions
CONTRACTIONS = {
    "can't": "cannot",
    "won't": "will not",
    "n't": " not",
    "'re": " are",
    "'s": " is",
    "'d": " would",
    "'ll": " will",
    "'t": " not",
    "'ve": " have",
    "'m": " am"
}

URL_REGEX = re.compile(r'https?://\S+|www\.\S+')
MENTION_REGEX = re.compile(r'@\w+')
HASHTAG_REGEX = re.compile(r'#(\w+)')
WHITESPACE_REGEX = re.compile(r'\s+')


def expand_contractions(text: str) -> str:
    """Expand common English contractions."""
    for contraction, expansion in CONTRACTIONS.items():
        text = re.sub(re.escape(contraction), expansion, text, flags=re.IGNORECASE)
    return text


def clean_tweet(text: str, remove_mentions: bool = True, remove_urls: bool = True) -> str:
    """
    Clean and normalize tweet text:
    - Decodes HTML entities (&amp; -> &)
    - Normalizes unicode characters
    - Strips or retains @AppleSupport and mentions
    - Strips URLs
    - Normalizes whitespace
    """
    if not isinstance(text, str):
        return ""

    # Unescape HTML entities
    text = html.unescape(text)

    # Normalize unicode (decompose accented/compound characters)
    text = unicodedata.normalize('NFKD', text)

    # Remove URLs
    if remove_urls:
        text = URL_REGEX.sub('', text)

    # Remove mentions (@AppleSupport etc)
    if remove_mentions:
        text = MENTION_REGEX.sub('', text)

    # Replace hashtags with raw word
    text = HASHTAG_REGEX.sub(r'\1', text)

    # Expand contractions
    text = expand_contractions(text)

    # Keep letters, numbers, basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s$%.?!]', ' ', text)

    # Collapse repeated whitespace
    text = WHITESPACE_REGEX.sub(' ', text).strip()

    return text.lower()


def tokenize(text: str) -> List[str]:
    """Tokenize cleaned text into lowercase words."""
    cleaned = clean_tweet(text)
    return [token for token in cleaned.split(' ') if token]


if __name__ == "__main__":
    sample = "@AppleSupport I can't sync my photos to iCloud! URL: https://apple.co/xyz #help"
    print("Original:", sample)
    print("Cleaned: ", clean_tweet(sample))
    print("Tokens:  ", tokenize(sample))
