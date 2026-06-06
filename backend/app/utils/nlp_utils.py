import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import re

_NLTK_RESOURCES = (
    ("punkt_tab", "tokenizers/punkt_tab"),
    ("punkt", "tokenizers/punkt"),
    ("stopwords", "corpora/stopwords"),
    ("wordnet", "corpora/wordnet"),
    ("omw-1.4", "corpora/omw-1.4"),
)


def _ensure_nltk_data() -> None:
    """Download NLTK corpora/tokenizers if missing (e.g. fresh venv)."""
    for package, path in _NLTK_RESOURCES:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(package, quiet=True)


_ensure_nltk_data()


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
