import logging
from typing import List
import spacy
from spacy.language import Language

logger = logging.getLogger(__name__)

K_DEFAULT_MODEL = "en_core_web_sm"


# /*
# * function name: load_spacy_model()
# * Description: Load a spaCy language model. Downloads the model if not found.
# * Parameter: model_name : str : Name of the spaCy model (default en_core_web_sm).
# * return: Language : Loaded spaCy Language pipeline.
# */
def load_spacy_model(model_name: str = K_DEFAULT_MODEL) -> Language:
    try:
        return spacy.load(model_name)
    except OSError:
        logger.info("Downloading spaCy model '%s'...", model_name)
        spacy.cli.download(model_name)
        return spacy.load(model_name)


# /*
# * function name: tokenize()
# * Description: Tokenize text into words using spaCy, filtering out
# *              punctuation and whitespace tokens.
# * Parameter: nlp : Language : Loaded spaCy model.
# *            text : str : Input text to tokenize.
# * return: List[str] : List of token strings.
# */
def tokenize(nlp: Language, text: str) -> List[str]:
    doc = nlp(text)
    return [token.text for token in doc if not token.is_punct and not token.is_space]


# /*
# * function name: lemmatize()
# * Description: Lemmatize text tokens using spaCy. Converts each token
# *              to its base form and lowercases the result.
# * Parameter: nlp : Language : Loaded spaCy model.
# *            tokens : List[str] : List of token strings to lemmatize.
# * return: List[str] : List of lemma strings (lowercase).
# */
def lemmatize(nlp: Language, tokens: List[str]) -> List[str]:
    doc = nlp(" ".join(tokens))
    return [token.lemma_.lower() for token in doc
            if not token.is_punct and not token.is_space]


# /*
# * function name: sent_tokenize()
# * Description: Segment text into sentences using spaCy.
# * Parameter: nlp : Language : Loaded spaCy model.
# *            text : str : Input text.
# * return: List[str] : List of sentence strings.
# */
def sent_tokenize(nlp: Language, text: str) -> List[str]:
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
