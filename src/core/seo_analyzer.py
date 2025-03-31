"""
SEO-Textanalyse-Modul für Wortanzahl-Tool.
Erweiterte Metriken für Textagenturen und SEO-Optimierung.
"""
import os
import re
import math
import logging
from typing import Dict, List, Any

# NLTK-Konfiguration mit erweitertem Fallback-Mechanismus
import nltk

# Definiere einen benutzerdefinierten NLTK-Datenordner
nltk_data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'nltk_data')
os.makedirs(nltk_data_path, exist_ok=True)

# Setze den NLTK-Datenordner
nltk.data.path.append(nltk_data_path)

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_nltk_resources(language: str = 'german'):
    """
    Lädt NLTK-Ressourcen sicher herunter mit Fallback-Mechanismus.
    
    Args:
        language: Sprache für Ressourcen (default: deutsch)
    """
    resources = {
        'german': ['punkt', 'stopwords'],
        'english': ['punkt', 'stopwords', 'averaged_perceptron_tagger']
    }
    
    try:
        for resource in resources.get(language, resources['german']):
            try:
                nltk.download(resource, download_dir=nltk_data_path, quiet=True)
            except Exception as e:
                logger.warning(f"Fehler beim Download von {resource}: {e}")
    except Exception as e:
        logger.error(f"Unerwarteter Fehler bei NLTK-Ressourcen-Download: {e}")

# Sichere NLTK-Ressourcen-Downloads
download_nltk_resources()

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textstat import flesch_reading_ease, flesch_kincaid_grade

class SEOAnalyzer:
    @staticmethod
    def safe_tokenize(text: str, language: str = 'german') -> List[str]:
        """
        Sichere Tokenisierung mit mehreren Fallback-Mechanismen.
        
        Args:
            text: Eingabetext
            language: Sprache für Tokenisierung
        
        Returns:
            Liste von Tokens
        """
        try:
            # NLTK-Tokenisierung
            tokens = word_tokenize(text.lower(), language=language)
            return [token for token in tokens if token.isalnum()]
        except Exception as e:
            logger.warning(f"NLTK-Tokenisierung fehlgeschlagen: {e}")
            
            try:
                # Reguläre Ausdrücke als Fallback
                tokens = re.findall(r'\b\w+\b', text.lower())
                return tokens
            except Exception as fallback_error:
                logger.error(f"Fallback-Tokenisierung fehlgeschlagen: {fallback_error}")
                return text.lower().split()

    @staticmethod
    def get_stopwords(language: str = 'german') -> set:
        """
        Holt Stopwords für eine Sprache.
        
        Args:
            language: Sprache der Stopwords
        
        Returns:
            Menge von Stopwords
        """
        try:
            return set(stopwords.words(language))
        except Exception as e:
            logger.warning(f"Stopwords-Fehler für {language}: {e}")
            # Fallback-Stopwords
            return {'der', 'die', 'das', 'und', 'oder', 'in', 'zu', 'ein', 'eine'}

    @staticmethod
    def readability_metrics(text: str) -> Dict[str, Any]:
        """
        Berechnet Lesbarkeitsmetriken.
        
        Args:
            text: Vollständiger Text
        
        Returns:
            Lesbarkeitsmetriken
        """
        try:
            flesch_ease = flesch_reading_ease(text)
            flesch_grade = flesch_kincaid_grade(text)
            
            return {
                'flesch_reading_ease': flesch_ease,
                'flesch_kincaid_grade': flesch_grade,
                'complexity_level': SEOAnalyzer._get_complexity_level(flesch_ease)
            }
        except Exception as e:
            logger.warning(f"Lesbarkeitsmetrik-Fehler: {e}")
            return {
                'flesch_reading_ease': 0,
                'flesch_kincaid_grade': 0,
                'complexity_level': 'Unbekannt'
            }

    @staticmethod
    def _get_complexity_level(score: float) -> str:
        """
        Bestimmt Komplexitätslevel basierend auf Flesch-Reading-Ease-Score.
        
        Args:
            score: Flesch-Reading-Ease-Score
        
        Returns:
            Komplexitätslevel als Text
        """
        if score < 30:
            return "Sehr schwierig"
        elif 30 <= score < 50:
            return "Schwierig"
        elif 50 <= score < 60:
            return "Etwas schwierig"
        elif 60 <= score < 70:
            return "Standard"
        else:
            return "Leicht verständlich"

    @staticmethod
    def calculate_tf_idf(documents: List[str]) -> Dict[str, float]:
        """
        Berechnet TF-IDF für alle Dokumente.
        
        Args:
            documents: Liste von Textdokumenten
        
        Returns:
            TF-IDF Werte für Wörter
        """
        # Tokenisierung und Vorverarbeitung
        def preprocess(text):
            tokens = SEOAnalyzer.safe_tokenize(text)
            return [token for token in tokens if token.isalnum()]
        
        # Vorverarbeitung der Dokumente
        processed_docs = [preprocess(doc) for doc in documents]
        
        # Wortfrequenz im Dokument
        def term_frequency(doc, term):
            return doc.count(term) / len(doc)
        
        # Dokumentenfrequenz
        def document_frequency(term):
            return sum(1 for doc in processed_docs if term in doc)
        
        # TF-IDF Berechnung
        tf_idf_results = {}
        total_docs = len(processed_docs)
        
        for doc in processed_docs:
            for term in set(doc):
                tf = term_frequency(doc, term)
                idf = math.log(total_docs / (document_frequency(term) + 1))
                tf_idf_results[term] = tf * idf
        
        return dict(sorted(tf_idf_results.items(), key=lambda x: x[1], reverse=True))

    @staticmethod
    def calculate_wdf_idf(documents: List[str]) -> Dict[str, float]:
        """
        Berechnet WDF-IDF (Within Document Frequency - Inverse Document Frequency) für Dokumente.
        
        Args:
            documents: Liste von Textdokumenten
        
        Returns:
            WDF-IDF Werte für Wörter
        """
        # Tokenisierung und Vorverarbeitung
        def preprocess(text):
            tokens = SEOAnalyzer.safe_tokenize(text)
            return [token for token in tokens if token.isalnum()]
        
        # Vorverarbeitung der Dokumente
        processed_docs = [preprocess(doc) for doc in documents]
        
        # Within Document Frequency (WDF) - logarithmische Skalierung
        def within_document_frequency(doc, term):
            term_count = doc.count(term)
            return math.log(1 + term_count) if term_count > 0 else 0
        
        # Dokumentenfrequenz
        def document_frequency(term):
            return sum(1 for doc in processed_docs if term in doc)
        
        # WDF-IDF Berechnung
        wdf_idf_results = {}
        total_docs = len(processed_docs)
        
        for doc in processed_docs:
            for term in set(doc):
                wdf = within_document_frequency(doc, term)
                idf = math.log(total_docs / (document_frequency(term) + 1))
                wdf_idf_results[term] = wdf * idf
        
        return dict(sorted(wdf_idf_results.items(), key=lambda x: x[1], reverse=True))

    @staticmethod
    def keyword_density(text: str, keywords: List[str]) -> Dict[str, float]:
        """
        Berechnet die Keyword-Dichte für gegebene Keywords.
        
        Args:
            text: Vollständiger Text
            keywords: Liste von Keywords
        
        Returns:
            Keyword-Dichte pro Keyword
        """
        tokens = SEOAnalyzer.safe_tokenize(text)
        total_words = len(tokens)
        keyword_counts = {keyword: text.lower().count(keyword.lower()) for keyword in keywords}
        
        return {
            keyword: (count / total_words) * 100 
            for keyword, count in keyword_counts.items()
        }

    @staticmethod
    def semantic_analysis(text: str, language: str = 'german') -> Dict[str, Any]:
        """
        Führt eine einfache semantische Analyse durch.
        
        Args:
            text: Vollständiger Text
            language: Sprache für Analyse
        
        Returns:
            Semantische Analyseresultate
        """
        try:
            # Stopwords entfernen
            stop_words = SEOAnalyzer.get_stopwords(language)
            tokens = SEOAnalyzer.safe_tokenize(text, language)
            meaningful_words = [word for word in tokens if word.isalnum() and word not in stop_words]
            
            return {
                'unique_meaningful_words': len(set(meaningful_words)),
                'top_meaningful_words': nltk.FreqDist(meaningful_words).most_common(10)
            }
        except Exception as e:
            logger.warning(f"Semantische Analyse-Fehler: {e}")
            return {
                'unique_meaningful_words': 0,
                'top_meaningful_words': []
            }