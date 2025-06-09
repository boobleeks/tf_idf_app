from collections import Counter
import math
from .models import Statistics

def calculate_tf(text):
    words = text.lower().split()
    word_count = len(words)
    word_freq = Counter(words)
    return {word: freq/word_count for word, freq in word_freq.items()}

def calculate_idf(documents, word):
    doc_count = len(documents)
    doc_with_word = sum(1 for doc in documents if word.lower() in doc.content.lower())
    return math.log(doc_count / (1 + doc_with_word))

def calculate_statistics(document):
    tf_data = calculate_tf(document.content)
    
    # Получаем все коллекции, в которых есть этот документ
    collections = document.collections.all()
    
    statistics = []
    for word, tf in sorted(tf_data.items(), key=lambda x: x[1])[:50]:  # 50 самых редких
        idf = 0
        if collections:
            # Рассчитываем IDF для каждой коллекции
            idf = sum(calculate_idf(col.documents.all(), word) for col in collections) / len(collections)
        
        statistics.append({
            'word': word,
            'tf': tf,
            'idf': idf
        })
    
    # Сохраняем статистику для документа
    Statistics.objects.update_or_create(
        document=document,
        defaults={'data': statistics}
    )
    
    # Обновляем статистику для всех связанных коллекций
    for collection in collections:
        calculate_collection_statistics(collection)

def calculate_collection_statistics(collection):
    documents = collection.documents.all()
    if not documents:
        return None
    
    # Объединяем содержимое всех документов
    combined_content = ' '.join(doc.content for doc in documents)
    tf_data = calculate_tf(combined_content)
    
    statistics = []
    for word, tf in sorted(tf_data.items(), key=lambda x: x[1])[:50]:  # 50 самых редких
        idf = calculate_idf(documents, word)
        statistics.append({
            'word': word,
            'tf': tf,
            'idf': idf
        })
    
    # Сохраняем статистику для коллекции
    Statistics.objects.update_or_create(
        collection=collection,
        defaults={'data': statistics}
    )
    
    return statistics