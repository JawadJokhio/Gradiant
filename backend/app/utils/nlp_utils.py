import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import re

# Ensure nltk data is handled (assuming downloaded in background/manually)
class NLPProcessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def preprocess(self, text: str) -> list:
        """
        Tokenizes, removes stopwords, and lemmatizes the input text.
        """
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        cleaned_tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in self.stop_words
        ]
        
        return cleaned_tokens

    def get_keywords(self, text: str) -> str:
        """Returns a string of keywords for matching."""
        return " ".join(self.preprocess(text))

nlp_processor = NLPProcessor()
