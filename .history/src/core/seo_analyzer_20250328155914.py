"""
SEO-Textanalyse-Modul für Wortanzahl-Tool.
Erweiterte Metriken für Textagenturen und SEO-Optimierung.
"""
import math
from typing import Dict, List, Any
import nltk
from nltk.corpus import stopwords
from textstat import flesch_reading_ease, flesch_kincaid_grade

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

class SEOAnalyzer:
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
            tokens = nltk.word_tokenize(text.lower())
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
    def keyword_density(text: str, keywords: List[str]) -> Dict[str, float]:
        """
        Berechnet die Keyword-Dichte für gegebene Keywords.
        
        Args:
            text: Vollständiger Text
            keywords: Liste von Keywords
        
        Returns:
            Keyword-Dichte pro Keyword
        """
        total_words = len(nltk.word_tokenize(text))
        keyword_counts = {keyword: text.lower().count(keyword.lower()) for keyword in keywords}
        
        return {
            keyword: (count / total_words) * 100 
            for keyword, count in keyword_counts.items()
        }
    
    @staticmethod
    def readability_metrics(text: str) -> Dict[str, Any]:
        """
        Berechnet Lesbarkeitsmetriken.
        
        Args:
            text: Vollständiger Text
        
        Returns:
            Lesbarkeitsmetriken
        """
        return {
            'flesch_reading_ease': flesch_reading_ease(text),
            'flesch_kincaid_grade': flesch_kincaid_grade(text),
            'complexity_level': SEOAnalyzer._get_complexity_level(flesch_reading_ease(text))
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
    def semantic_analysis(text: str) -> Dict[str, Any]:
        """
        Führt eine einfache semantische Analyse durch.
        
        Args:
            text: Vollständiger Text
        
        Returns:
            Semantische Analyseresultate
        """
        # Stopwords entfernen
        stop_words = set(stopwords.words('german'))
        tokens = nltk.word_tokenize(text.lower())
        meaningful_words = [word for word in tokens if word.isalnum() and word not in stop_words]
        
        return {
            'unique_meaningful_words': len(set(meaningful_words)),
            'top_meaningful_words': nltk.FreqDist(meaningful_words).most_common(10)
        }