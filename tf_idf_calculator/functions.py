import re
import math 
from collections import Counter

stop_words = [
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further",
    "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've",
    "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself",
    "let's",
    "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not",
    "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these",
    "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up",
    "very",
    "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't",
    "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves", "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то", "все", "она", "так", "его", "но", "да",
    "ты", "к", "у", "же", "вы", "за", "бы", "по", "ее", "мне", "было", "вот", "от", "меня", "еще", "нет", "о", "из",
    "ему", "теперь", "когда", "даже", "ну", "вдруг", "ли", "если", "уже", "или", "ни", "быть", "был", "него", "до",
    "вас", "нибудь", "опять", "уж", "вам", "ведь", "там", "потом", "себя", "ничего", "ей", "может", "они", "тут", "где",
    "есть", "надо", "ней", "для", "мы", "тебя", "их", "чем", "была", "сам", "чтоб", "без", "будто", "чего", "раз",
    "тоже", "себе", "под", "будет", "ж", "тогда", "кто", "этот", "того", "потому", "этого", "какой", "совсем", "ним",
    "здесь", "этом", "один", "почти", "мой", "тем", "чтобы", "нее", "сейчас", "были", "куда", "зачем", "всех", "никогда",
    "можно", "при", "наконец", "два", "об", "другой", "хоть", "после", "над", "больше", "тот", "через", "эти", "нас",
    "про", "всего", "них", "какая", "много", "разве", "три", "эту", "моя", "впрочем", "хорошо", "свою", "этой", "перед",
    "иногда", "лучше", "чуть", "том", "нельзя", "такой", "им", "более", "всегда", "конечно", "всю", "между",
]

class TfidfComputer:
    """
    Класс создан для гибкости рассчетов и во избежании каши в views.py))

    """

    def __init__(self, files):
        documents = files
        self.whole_texts = self.all_docs_text_joiner(documents)
        self.docs = self.clean_and_tokenize(self.whole_texts)
        self.N = len(self.docs)
        self.results = self.tf_idf_counter()
        self.idf = self.all_idf_counter()


    def all_docs_text_joiner(self, documents):
        whole_text = []

        for file in documents:
            text = file.read().decode("utf-8")
            whole_text.append(text)
            
        return whole_text


    def clean_and_tokenize(self, texts):
        all_docs_tokens = []

        for text in texts:
            text_lower = text.lower()
            words = re.findall(r"\b\w+(?:'\w+)?\b", text_lower)
            all_docs_tokens.append(words)

        return all_docs_tokens


    def all_idf_counter(self):
        idf = {}
        unique_words = set()
        filtered_doc = self.stop_word_filter(self.docs)
        for doc in filtered_doc:
            for word in doc:
                unique_words.add(word)
        
        for word in unique_words:
            doc_count = 0
            for doc in self.docs:
                if word in doc:
                    doc_count += 1
            idf[word] = math.log((1 + self.N) / (1 + doc_count))
        return idf

    def stop_word_filter(self, document):
        filtered = [word for word in document if word not in stop_words]
        return filtered
    
    def tf_idf_counter(self):
        results = []
        idf = self.all_idf_counter()
        for doc_index in range(self.N):
            doc = self.docs[doc_index]
            filtered_doc = self.stop_word_filter(doc)
            total_words = len(filtered_doc)
            word_count = Counter(filtered_doc)
            unique_words = word_count.keys()

            for word in unique_words:
                tf = word_count[word] / total_words
                word_idf = idf.get(word, 0)
                tfidf = tf * word_idf

                results.append({
                    'doc': doc_index + 1,
                    'word': word,
                    'tf': round(tf, 3),
                    'idf': round(word_idf, 3),
                    'tfidf': round(tfidf, 3)
                })
        return results