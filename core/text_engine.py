import re
import string
from collections import Counter
from .utils import get_classification

STOPWORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'can', 'to', 'of', 'in', 'for', 'on', 'with',
    'at', 'by', 'from', 'as', 'into', 'during', 'before', 'after', 'above',
    'below', 'between', 'out', 'off', 'over', 'under', 'again', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each',
    'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
    'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
    'because', 'but', 'and', 'or', 'if', 'while', 'about', 'this', 'that',
    'these', 'those', 'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he',
    'him', 'his', 'she', 'her', 'it', 'its', 'they', 'them', 'their'
}

AI_INDICATOR_PHRASES = [
    'it is important to note',
    'it is worth noting',
    'in conclusion',
    'furthermore',
    'moreover',
    'additionally',
    'in summary',
    'it should be noted',
    'plays a crucial role',
    'in today\'s world',
    'comprehensive',
    'nuanced',
    'multifaceted',
    'landscape',
    'paradigm',
    'leverage',
    'holistic',
    'robust',
    'cutting-edge',
    'groundbreaking',
]


def analyze_text(text):
    result = {
        'authenticity_score': 50.0,
        'classification': 'suspicious',
        'details': {},
        'explanation': '',
    }

    try:
        text = text.strip()
        if len(text) < 50:
            result['explanation'] = 'Text too short for reliable analysis.'
            return result

        text_lower = text.lower()
        words = text.split()
        word_count = len(words)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

        scores = {}
        explanations = [f"Text loaded with {word_count} words and {len(sentences)} sentence(s)."]

        # Sentence variance
        if len(sentences) > 1:
            sentence_lengths = [len(s.split()) for s in sentences]
            avg_len = sum(sentence_lengths) / len(sentence_lengths)
            std_len = (sum((l - avg_len) ** 2 for l in sentence_lengths) / len(sentence_lengths)) ** 0.5

            if std_len > 8:
                scores['Sentence Variance'] = 20
                explanations.append(f"Sentence length variance appears natural (std: {std_len:.1f}).")
            elif std_len > 4:
                scores['Sentence Variance'] = 14
                explanations.append(f"Sentence lengths are moderately varied (std: {std_len:.1f}).")
            elif std_len > 2:
                scores['Sentence Variance'] = 8
                explanations.append(f"Sentence lengths are quite uniform (std: {std_len:.1f}).")
            else:
                scores['Sentence Variance'] = 3
                explanations.append(f"Very low sentence variation detected (std: {std_len:.1f}).")
        else:
            scores['Sentence Variance'] = 10
            std_len = 0
            explanations.append("Only one sentence found, so sentence variance is limited.")

        # Vocabulary diversity
        words_lower = [w.lower().strip(string.punctuation) for w in words]
        meaningful_words = [w for w in words_lower if w and len(w) > 2 and w not in STOPWORDS]
        if meaningful_words:
            unique_ratio = len(set(meaningful_words)) / len(meaningful_words)
            if unique_ratio > 0.7:
                scores['Vocabulary Diversity'] = 20
                explanations.append(f"Vocabulary diversity appears strong ({unique_ratio:.2f}).")
            elif unique_ratio > 0.5:
                scores['Vocabulary Diversity'] = 14
                explanations.append(f"Vocabulary diversity is moderate ({unique_ratio:.2f}).")
            elif unique_ratio > 0.3:
                scores['Vocabulary Diversity'] = 8
                explanations.append(f"Vocabulary appears somewhat repetitive ({unique_ratio:.2f}).")
            else:
                scores['Vocabulary Diversity'] = 3
                explanations.append(f"Very repetitive vocabulary detected ({unique_ratio:.2f}).")
        else:
            unique_ratio = 0
            scores['Vocabulary Diversity'] = 10

        # Punctuation density
        punctuation_count = sum(1 for c in text if c in string.punctuation)
        punct_density = punctuation_count / len(text) if len(text) > 0 else 0
        if 0.03 < punct_density < 0.12:
            scores['Punctuation Density'] = 20
            explanations.append(f"Punctuation density appears natural ({punct_density:.2%}).")
        elif 0.02 < punct_density <= 0.03 or 0.12 <= punct_density < 0.15:
            scores['Punctuation Density'] = 14
            explanations.append(f"Punctuation density is slightly unusual ({punct_density:.2%}).")
        else:
            scores['Punctuation Density'] = 7
            explanations.append(f"Punctuation density appears unusual ({punct_density:.2%}).")

        # AI indicator phrases
        found_phrases = [phrase for phrase in AI_INDICATOR_PHRASES if phrase in text_lower]
        phrase_count = len(found_phrases)
        if phrase_count == 0:
            scores['AI Indicator Phrases'] = 20
            explanations.append("No strong AI-indicator phrases detected.")
        elif phrase_count <= 2:
            scores['AI Indicator Phrases'] = 15
            explanations.append(f"Some AI-associated phrases found ({phrase_count}).")
        elif phrase_count <= 5:
            scores['AI Indicator Phrases'] = 8
            explanations.append(f"Several AI-associated phrases found ({phrase_count}).")
        else:
            scores['AI Indicator Phrases'] = 3
            explanations.append(f"Many AI-associated phrases found ({phrase_count}).")

        # Stopword pattern
        total_words = [w.lower().strip(string.punctuation) for w in words if w.strip(string.punctuation)]
        stopword_count = sum(1 for w in total_words if w in STOPWORDS)
        stopword_ratio = stopword_count / len(total_words) if total_words else 0
        if 0.35 < stopword_ratio < 0.55:
            scores['Stopword Ratio'] = 20
            explanations.append(f"Stopword ratio appears natural ({stopword_ratio:.2f}).")
        elif 0.25 < stopword_ratio <= 0.35 or 0.55 <= stopword_ratio < 0.65:
            scores['Stopword Ratio'] = 14
            explanations.append(f"Stopword ratio is somewhat unusual ({stopword_ratio:.2f}).")
        else:
            scores['Stopword Ratio'] = 7
            explanations.append(f"Stopword ratio is unusual ({stopword_ratio:.2f}).")

        final_score = min(max(round(sum(scores.values()), 1), 0), 100)
        result['authenticity_score'] = final_score
        result['classification'] = get_classification(final_score)
        result['details'] = {
            **scores,
            'Word Count': word_count,
            'Sentence Count': len(sentences),
            'Sentence Length Std': round(std_len, 2),
            'Unique Ratio': round(unique_ratio, 2),
            'Punctuation Density': round(punct_density, 4),
            'Stopword Ratio': round(stopword_ratio, 2),
            'AI Phrases Found': found_phrases,
        }
        result['explanation'] = "\n".join(explanations)

    except Exception as e:
        result['explanation'] = f'Text analysis error: {str(e)}'

    return result