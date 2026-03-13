"""
Utility functions for DeepFakeShield.
"""


def get_classification(score):
    """
    Return classification based on authenticity score.
    90-100: Highly Authentic
    75-89:  Likely Real
    40-74:  Possibly Edited / Suspicious
    0-39:   Likely AI Generated / Fake
    """
    if score >= 90:
        return 'authentic'
    elif score >= 75:
        return 'likely_real'
    elif score >= 40:
        return 'suspicious'
    else:
        return 'likely_fake'


def get_classification_label(classification):
    """Return human-readable label for classification."""
    labels = {
        'authentic': 'Highly Authentic',
        'likely_real': 'Likely Real',
        'suspicious': 'Possibly Edited / Suspicious',
        'likely_fake': 'Likely AI Generated / Fake',
    }
    return labels.get(classification, 'Unknown')


def get_score_color(score):
    """Return CSS color class based on score."""
    if score >= 90:
        return 'success'
    elif score >= 75:
        return 'info'
    elif score >= 40:
        return 'warning'
    else:
        return 'danger'


def format_file_size(size_bytes):
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"