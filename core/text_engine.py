import re
import string
from collections import Counter
import numpy as np

STOPWORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'shall', 'can', 'need', 'to', 'of', 'in',
    'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'between', 'out',
    'off', 'over', 'under', 'again', 'further', 'then', 'once', 'and',
    'but', 'or', 'nor', 'not', 'so', 'yet', 'both', 'either', 'neither',
    'each', 'every', 'all', 'any', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'only', 'own', 'same', 'than', 'too', 'very',
    'just', 'because', 'if', 'when', 'where', 'how', 'what', 'which',
    'who', 'whom', 'this', 'that', 'these', 'those', 'i', 'me', 'my',
    'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
    'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
    'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
    'their', 'theirs', 'themselves', 'also', 'however', 'therefore',
    'moreover', 'furthermore', 'although', 'though', 'while', 'whereas',
    'nevertheless', 'nonetheless', 'thus', 'hence',
}


def analyze_text(text):
    results = {
        'word_count': 0,
        'sentence_count': 0,
        'repetition_score': 0,
        'stopword_ratio': 0,
        'punctuation_density': 0,
        'sentence_variance': 0,
        'avg_word_length': 0,
        'unique_word_ratio': 0,
        'avg_sentence_length': 0,
        'paragraph_count': 0,
        'burstiness_score': 0,
        'description': '',
        'analysis_summary': '',
        'real_vs_fake': 'Uncertain',
    }

    if not text or len(text.strip()) < 20:
        results['description'] = 'Text is too short for meaningful analysis.'
        results['analysis_summary'] = 'The input text length is insufficient for authenticity analysis.'
        return results, 50

    text = text.strip()
    words = text.split()
    word_count = len(words)
    results['word_count'] = word_count

    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)
    results['sentence_count'] = sentence_count

    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    results['paragraph_count'] = len(paragraphs)

    words_lower = [w.lower().strip(string.punctuation) for w in words]
    words_clean = [w for w in words_lower if w]

    word_counts = Counter(words_clean)
    repeated_content_words = sum(
        1 for w, c in word_counts.items()
        if c > 1 and w not in STOPWORDS and len(w) > 3
    )
    total_content_words = sum(
        1 for w in words_clean if w not in STOPWORDS and len(w) > 3
    )
    repetition = repeated_content_words / max(total_content_words, 1)
    results['repetition_score'] = round(repetition, 4)

    stopword_count = sum(1 for w in words_clean if w in STOPWORDS)
    stopword_ratio = stopword_count / max(len(words_clean), 1)
    results['stopword_ratio'] = round(stopword_ratio, 4)

    punct_count = sum(1 for c in text if c in string.punctuation)
    punct_density = punct_count / max(len(text), 1)
    results['punctuation_density'] = round(punct_density, 4)

    sentence_lengths = [len(s.split()) for s in sentences] if sentences else [word_count]
    sentence_variance = float(np.std(sentence_lengths)) if sentence_lengths else 0
    avg_sentence_length = float(np.mean(sentence_lengths)) if sentence_lengths else 0
    results['sentence_variance'] = round(sentence_variance, 2)
    results['avg_sentence_length'] = round(avg_sentence_length, 2)

    avg_word_length = sum(len(w) for w in words_clean) / max(len(words_clean), 1)
    results['avg_word_length'] = round(avg_word_length, 2)

    unique_word_ratio = len(set(words_clean)) / max(len(words_clean), 1)
    results['unique_word_ratio'] = round(unique_word_ratio, 4)

    burstiness = sentence_variance / avg_sentence_length if avg_sentence_length > 0 else 0
    results['burstiness_score'] = round(float(burstiness), 4)

    score = _calculate_text_score(results)

    if score >= 75:
        results['real_vs_fake'] = 'Real'
    elif score <= 39:
        results['real_vs_fake'] = 'Fake'
    else:
        results['real_vs_fake'] = 'Uncertain'

    results['analysis_summary'] = _generate_text_summary(score)
    results['description'] = _generate_text_description(results, score)

    return results, score


def _calculate_text_score(results):
    score = 50

    repetition = results.get('repetition_score', 0)
    stopword_ratio = results.get('stopword_ratio', 0)
    punctuation_density = results.get('punctuation_density', 0)
    sentence_variance = results.get('sentence_variance', 0)
    unique_word_ratio = results.get('unique_word_ratio', 0)
    burstiness = results.get('burstiness_score', 0)
    word_count = results.get('word_count', 0)

    if repetition < 0.10:
        score += 15
    elif repetition < 0.22:
        score += 8
    elif repetition > 0.35:
        score -= 18
    elif repetition > 0.25:
        score -= 8

    if 0.32 < stopword_ratio < 0.50:
        score += 10
    elif stopword_ratio > 0.58:
        score -= 14
    elif stopword_ratio < 0.20:
        score -= 6

    if 0.02 < punctuation_density < 0.08:
        score += 8
    elif punctuation_density < 0.015:
        score -= 10
    elif punctuation_density > 0.12:
        score -= 6

    if sentence_variance > 8:
        score += 14
    elif sentence_variance > 4:
        score += 7
    elif sentence_variance < 2:
        score -= 14

    if unique_word_ratio > 0.65:
        score += 10
    elif unique_word_ratio < 0.40:
        score -= 10

    if burstiness > 0.30:
        score += 8
    elif burstiness < 0.10:
        score -= 8

    if word_count > 200:
        score += 5
    elif word_count < 50:
        score -= 5

    return int(round(max(0, min(100, score))))


def _generate_text_summary(score):
    if score >= 75:
        verdict = "likely human-written"
    elif score <= 39:
        verdict = "likely AI-generated"
    else:
        verdict = "suspicious or mixed"

    return (
        f"The text was analyzed using repetition, stopword usage, punctuation density, "
        f"sentence variance, vocabulary diversity, and burstiness. Overall, the text appears {verdict}."
    )


def _generate_text_description(results, score):
    parts = []
    parts.append(
        f"Text contains {results.get('word_count', 0)} words in "
        f"{results.get('sentence_count', 0)} sentences across "
        f"{results.get('paragraph_count', 0)} paragraph(s)."
    )
    parts.append(f"Average sentence length: {results.get('avg_sentence_length', 0)} words.")
    parts.append(f"Sentence variance: {results.get('sentence_variance', 0)}.")
    parts.append(f"Repetition score: {results.get('repetition_score', 0)}.")
    parts.append(f"Stopword ratio: {results.get('stopword_ratio', 0)}.")
    parts.append(f"Unique word ratio: {results.get('unique_word_ratio', 0)}.")
    parts.append(f"Burstiness score: {results.get('burstiness_score', 0)}.")

    if score >= 75:
        parts.append("The linguistic structure appears varied and natural.")
    elif score <= 39:
        parts.append("The linguistic structure appears repetitive and more consistent with AI-generated text.")
    else:
        parts.append("The text contains mixed characteristics and should be interpreted carefully.")

    return " ".join(parts)