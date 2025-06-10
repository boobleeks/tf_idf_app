from sklearn.feature_extraction.text import TfidfVectorizer
from .models import Statistics

def compute_tfidf(documents, target_document):
    corpus = [doc.content.lower() for doc in documents]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    idf_values = dict(zip(vectorizer.get_feature_names_out(), vectorizer.idf_))

    doc_index = documents.index(target_document)

    tfidf_vector = tfidf_matrix[doc_index]
    tfidf_data = tfidf_vector.tocoo()

    statistics = []
    for idx, tfidf_value in zip(tfidf_data.col, tfidf_data.data):
        word = vectorizer.get_feature_names_out()[idx]
        tf = tfidf_value / idf_values[word]  # tf = tfidf / idf
        idf = idf_values[word]
        
        statistics.append({
            'word': word,
            'tf': tf,
            'idf': idf,
            'tfidf': tfidf_value
        })

    statistics = sorted(statistics, key=lambda x: x['tfidf'])[:50]
    return statistics

def calculate_statistics(document):
    collections = document.collections.all()
    
    if collections:
        documents = set()
        for collection in collections:
            documents.update(collection.documents.all())
        documents = list(documents)
    else:
        documents = [document]

    statistics = compute_tfidf(documents, document)

    Statistics.objects.update_or_create(
        document=document,
        defaults={'data': statistics}
    )
 
    for collection in collections:
        calculate_collection_statistics(collection)

def calculate_collection_statistics(collection):
    documents = list(collection.documents.all())
    if not documents:
        return None

    combined_document = ' '.join(doc.content for doc in documents)
    combined_doc = type('Doc', (object,), {'content': combined_document})
    
    statistics = compute_tfidf(documents + [combined_doc], combined_doc)

    Statistics.objects.update_or_create(
        collection=collection,
        defaults={'data': statistics}
    )
    
    return statistics


