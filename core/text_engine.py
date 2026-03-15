"""
DeepFake Shield - Text Authenticity Detection Engine
Detects AI-generated text using statistical NLP features.
CPU-friendly, no external API required.
"""

import re
import math
import string
import logging
from collections import Counter

logger = logging.getLogger(__name__)

# Common English stopwords
STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her',
    'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there',
    'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
    'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no',
    'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your',
    'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then',
    'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
    'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
    'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
    'give', 'day', 'most', 'us', 'is', 'are', 'was', 'were', 'been',
    'being', 'has', 'had', 'having', 'does', 'did', 'doing', 'am',
    'very', 'much', 'more', 'such', 'should', 'may', 'might', 'must',
    'shall', 'need', 'dare', 'ought', 'used', 'however', 'therefore',
    'furthermore', 'moreover', 'additionally', 'consequently', 'thus',
    'hence', 'nevertheless', 'nonetheless', 'meanwhile', 'subsequently',
}

# AI-typical phrases (common in ChatGPT, etc.)
AI_PHRASES = [
    'it is important to note',
    'it is worth noting',
    'in conclusion',
    'in summary',
    'to summarize',
    'it should be noted',
    'one might argue',
    'on the other hand',
    'it is evident that',
    'this suggests that',
    'it can be argued',
    'it is crucial',
    'plays a crucial role',
    'it is essential',
    'in today\'s world',
    'in the modern era',
    'serves as a testament',
    'a myriad of',
    'delve into',
    'delve deeper',
    'multifaceted',
    'tapestry',
    'landscape of',
    'realm of',
    'paradigm',
    'foster',
    'leverage',
    'navigate the complexities',
    'in light of',
    'with that being said',
    'it goes without saying',
    'needless to say',
    'at the end of the day',
    'when it comes to',
    'as a matter of fact',
    'by and large',
    'for the most part',
    'in a nutshell',
    'comprehensive',
    'robust',
    'seamlessly',
    'holistic',
    'synergy',
    'cutting-edge',
    'state-of-the-art',
    'groundbreaking',
    'innovative',
    'revolutionize',
]


def analyze_text(text):
    """
    Main text analysis function.
    Analyzes text for AI-generated content indicators.
    """
    logger.info(f"Starting text analysis ({len(text)} characters)")

    results = {
        'text_length': len(text),
        'word_count': 0,
        'sentence_count': 0,
        'paragraph_count': 0,
        'repetition_score': 0.0,
        'stopword_ratio': 0.0,
        'punctuation_density': 0.0,
        'sentence_variance': 0.0,
        'avg_sentence_length': 0.0,
        'avg_word_length': 0.0,
        'unique_word_ratio': 0.0,
        'burstiness_score': 0.0,
        'ai_phrase_count': 0,
        'ai_phrase_density': 0.0,
        'vocabulary_richness': 0.0,
        'authenticity_score': 0.0,
        'real_vs_fake': 'Unknown',
        'classification': 'suspicious',
        'summary': '',
        'explanation': '',
        'description': '',
        'detailed_metrics': {},
    }

    try:
        if not text or len(text.strip()) < 50:
            results['explanation'] = 'Text is too short for reliable analysis.'
            results['summary'] = 'Insufficient text for analysis (minimum 50 characters).'
            results['authenticity_score'] = 50.0
            return results

        text_clean = text.strip()

        # ── Basic Metrics ──
        words = re.findall(r'\b[a-zA-Z\']+\b', text_clean.lower())
        word_count = len(words)
        results['word_count'] = word_count

        if word_count < 10:
            results['explanation'] = 'Too few words for reliable analysis.'
            results['summary'] = 'Insufficient word count for analysis.'
            results['authenticity_score'] = 50.0
            return results

        # Sentences
        sentences = re.split(r'[.!?]+', text_clean)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
        sentence_count = len(sentences)
        results['sentence_count'] = max(1, sentence_count)

        # Paragraphs
        paragraphs = [p.strip() for p in text_clean.split('\n\n') if p.strip()]
        if not paragraphs:
            paragraphs = [p.strip() for p in text_clean.split('\n') if p.strip()]
        results['paragraph_count'] = max(1, len(paragraphs))

        # ── Word-level Analysis ──

        # Average word length
        if words:
            avg_word_len = sum(len(w) for w in words) / len(words)
        else:
            avg_word_len = 0
        results['avg_word_length'] = round(avg_word_len, 2)

        # Unique word ratio (vocabulary diversity)
        unique_words = set(words)
        unique_ratio = len(unique_words) / word_count if word_count > 0 else 0
        results['unique_word_ratio'] = round(unique_ratio, 4)

        # Vocabulary richness (Yule's K-like measure)
        word_freq = Counter(words)
        freq_spectrum = Counter(word_freq.values())
        n = word_count
        if n > 0:
            m2 = sum(i * i * freq_spectrum[i] for i in freq_spectrum)
            vocab_richness = (m2 - n) / (n * n) if n > 1 else 0
        else:
            vocab_richness = 0
        results['vocabulary_richness'] = round(vocab_richness, 6)

        # ── Repetition Score ──
        # Measure n-gram repetition
        bigrams = [' '.join(words[i:i + 2]) for i in range(len(words) - 1)]
        trigrams = [' '.join(words[i:i + 3]) for i in range(len(words) - 2)]

        bigram_counts = Counter(bigrams)
        trigram_counts = Counter(trigrams)

        repeated_bigrams = sum(1 for c in bigram_counts.values() if c > 2)
        repeated_trigrams = sum(1 for c in trigram_counts.values() if c > 1)

        repetition_score = 0.0
        if bigrams:
            repetition_score += (repeated_bigrams / len(bigrams)) * 100
        if trigrams:
            repetition_score += (repeated_trigrams / len(trigrams)) * 50
        results['repetition_score'] = round(min(100.0, repetition_score), 2)

        # ── Stopword Ratio ──
        stopword_count = sum(1 for w in words if w in STOPWORDS)
        stopword_ratio = stopword_count / word_count if word_count > 0 else 0
        results['stopword_ratio'] = round(stopword_ratio, 4)

        # ── Punctuation Density ──
        punct_count = sum(1 for c in text_clean if c in string.punctuation)
        punct_density = punct_count / len(text_clean) if len(text_clean) > 0 else 0
        results['punctuation_density'] = round(punct_density, 4)

        # ── Sentence Analysis ──
        sentence_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences if s]
        if sentence_lengths:
            avg_sentence_len = sum(sentence_lengths) / len(sentence_lengths)
            sentence_variance = (
                sum((l - avg_sentence_len) ** 2 for l in sentence_lengths) / len(sentence_lengths)
            ) if len(sentence_lengths) > 1 else 0.0
        else:
            avg_sentence_len = 0
            sentence_variance = 0

        results['avg_sentence_length'] = round(avg_sentence_len, 2)
        results['sentence_variance'] = round(sentence_variance, 2)

        # ── Burstiness Score ──
        # Human text has "bursty" sentence lengths; AI tends to be uniform
        if len(sentence_lengths) > 2:
            diffs = [abs(sentence_lengths[i] - sentence_lengths[i - 1]) for i in range(1, len(sentence_lengths))]
            burstiness = sum(diffs) / len(diffs) if diffs else 0
            max_burst = max(diffs) if diffs else 0
            burstiness_score = min(100.0, (burstiness / max(1, avg_sentence_len)) * 100)
        else:
            burstiness_score = 50.0
        results['burstiness_score'] = round(burstiness_score, 2)

        # ── AI Phrase Detection ──
        text_lower = text_clean.lower()
        ai_phrase_matches = 0
        matched_phrases = []
        for phrase in AI_PHRASES:
            count = text_lower.count(phrase)
            if count > 0:
                ai_phrase_matches += count
                matched_phrases.append(phrase)

        results['ai_phrase_count'] = ai_phrase_matches
        results['ai_phrase_density'] = round(
            (ai_phrase_matches / max(1, sentence_count)) * 100, 2
        )

        # ═══════════════════════════════════════
        # AUTHENTICITY SCORING
        # ═══════════════════════════════════════

        score = 50.0  # Base score

        # 1. Sentence variance (human text is more varied)
        if sentence_variance > 30:
            score += 12.0  # High variance = human-like
        elif sentence_variance > 15:
            score += 8.0
        elif sentence_variance > 5:
            score += 3.0
        elif sentence_variance < 3 and sentence_count > 5:
            score -= 10.0  # Very uniform = AI-like

        # 2. Burstiness (human text is bursty)
        if burstiness_score > 40:
            score += 10.0
        elif burstiness_score > 20:
            score += 5.0
        elif burstiness_score < 10 and sentence_count > 5:
            score -= 8.0

        # 3. Unique word ratio
        if unique_ratio > 0.7:
            score += 8.0  # Rich vocabulary
        elif unique_ratio > 0.5:
            score += 5.0
        elif unique_ratio < 0.3 and word_count > 100:
            score -= 8.0  # Very repetitive

        # 4. AI phrase density
        if ai_phrase_matches == 0:
            score += 8.0
        elif ai_phrase_matches <= 2:
            score += 2.0
        elif ai_phrase_matches <= 5:
            score -= 5.0
        else:
            score -= 12.0  # Heavy AI phrasing

        # 5. Stopword ratio (AI tends to use more functional language)
        if 0.35 < stopword_ratio < 0.55:
            score += 5.0  # Normal range
        elif stopword_ratio > 0.6:
            score -= 5.0  # Too many stopwords
        elif stopword_ratio < 0.25:
            score -= 3.0  # Unusually low

        # 6. Average word length
        if 4.0 < avg_word_len < 6.0:
            score += 5.0  # Normal English
        elif avg_word_len > 7.0:
            score -= 3.0  # Unusually complex

        # 7. Punctuation density
        if 0.03 < punct_density < 0.10:
            score += 3.0
        elif punct_density > 0.15:
            score -= 3.0

        # 8. Repetition
        if repetition_score < 5:
            score += 5.0
        elif repetition_score > 20:
            score -= 8.0

        # 9. Average sentence length
        if 10 < avg_sentence_len < 25:
            score += 5.0  # Natural range
        elif avg_sentence_len > 35:
            score -= 5.0  # Very long sentences

        # Clamp score
        final_score = max(0.0, min(100.0, round(score, 1)))
        results['authenticity_score'] = final_score

        # Classification
        if final_score >= 75:
            results['classification'] = 'likely_real'
            results['real_vs_fake'] = 'Likely Human-Written'
        elif final_score >= 40:
            results['classification'] = 'suspicious'
            results['real_vs_fake'] = 'Suspicious / Mixed Signals'
        else:
            results['classification'] = 'likely_fake'
            results['real_vs_fake'] = 'Likely AI-Generated'

        # Description
        results['description'] = (
            f"Text analysis: {word_count} words, {sentence_count} sentences, "
            f"{results['paragraph_count']} paragraph(s)."
        )

        # Explanation
        explanations = []

        if sentence_variance > 15:
            explanations.append("Sentence length variation is consistent with human writing.")
        elif sentence_variance < 5 and sentence_count > 5:
            explanations.append("Sentences have unusually uniform length, typical of AI-generated text.")

        if burstiness_score > 30:
            explanations.append("Text shows natural burstiness in sentence structure.")
        elif burstiness_score < 15 and sentence_count > 5:
            explanations.append("Text lacks natural burstiness, suggesting algorithmic generation.")

        if ai_phrase_matches > 3:
            explanations.append(
                f"Detected {ai_phrase_matches} AI-typical phrases "
                f"(e.g., '{matched_phrases[0] if matched_phrases else 'N/A'}')."
            )
        elif ai_phrase_matches == 0:
            explanations.append("No common AI-typical phrases detected.")

        if unique_ratio > 0.6:
            explanations.append("Vocabulary diversity is consistent with human authorship.")
        elif unique_ratio < 0.35 and word_count > 100:
            explanations.append("Low vocabulary diversity suggests potential AI generation.")

        results['explanation'] = " ".join(explanations) if explanations else "Analysis completed with mixed indicators."

        results['summary'] = (
            f"Text Authenticity Score: {final_score:.1f}/100 — "
            f"{results['classification'].replace('_', ' ').title()}. "
            f"{results['explanation']}"
        )

        results['detailed_metrics'] = {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'paragraph_count': results['paragraph_count'],
            'avg_sentence_length': round(avg_sentence_len, 2),
            'avg_word_length': round(avg_word_len, 2),
            'sentence_variance': round(sentence_variance, 2),
            'unique_word_ratio': round(unique_ratio, 4),
            'stopword_ratio': round(stopword_ratio, 4),
            'punctuation_density': round(punct_density, 4),
            'repetition_score': round(repetition_score, 2),
            'burstiness_score': round(burstiness_score, 2),
            'ai_phrase_count': ai_phrase_matches,
            'ai_phrase_density': round(results['ai_phrase_density'], 2),
            'vocabulary_richness': round(vocab_richness, 6),
        }

        logger.info(f"Text analysis complete: score={final_score}")

    except Exception as e:
        logger.error(f"Text analysis failed: {e}", exc_info=True)
        results['explanation'] = f'Text analysis encountered an error: {str(e)}'
        results['summary'] = 'Text analysis could not be completed.'

    return results