"""
Modul zur Wortzählung und Dokumentenanalyse.
"""
import docx
from typing import Dict, List, Optional
from pathlib import Path
import re

class WordCounter:
    """
    Klasse zur Analyse und Wortzählung von DOCX-Dokumenten.
    """
    @staticmethod
    def count_words(document_path: str) -> Dict[str, int]:
        """
        Zählt die Wörter in einem DOCX-Dokument.
        
        Args:
            document_path: Pfad zum DOCX-Dokument
        
        Returns:
            Dictionary mit Wortzählstatistiken
        """
        try:
            doc = docx.Document(document_path)
            
            # Sammle Text aus allen Absätzen
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            
            # Kombiniere den Text
            text = ' '.join(full_text)
            
            # Bereinige und zähle Wörter
            words = re.findall(r'\b\w+\b', text.lower())
            
            # Detaillierte Statistiken
            return {
                'total_words': len(words),
                'unique_words': len(set(words)),
                'word_frequency': WordCounter._get_word_frequency(words)
            }
        except Exception as e:
            raise ValueError(f"Fehler beim Zählen der Wörter: {e}")
    
    @staticmethod
    def _get_word_frequency(words: List[str], top_n: int = 10) -> Dict[str, int]:
        """
        Ermittelt die Häufigkeit von Wörtern.
        
        Args:
            words: Liste der Wörter
            top_n: Anzahl der häufigsten Wörter
        
        Returns:
            Dictionary mit Wortfrequenzen
        """
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sortiere nach Häufigkeit absteigend
        return dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n])
    
    @staticmethod
    def analyze_multiple_documents(document_paths: List[str]) -> List[Dict[str, int]]:
        """
        Analysiert mehrere Dokumente.
        
        Args:
            document_paths: Liste der Dokumentpfade
        
        Returns:
            Liste von Wortzählstatistiken
        """
        results = []
        for path in document_paths:
            try:
                results.append({
                    'file': Path(path).name,
                    **WordCounter.count_words(path)
                })
            except Exception as e:
                results.append({
                    'file': Path(path).name,
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def export_word_count_report(results: List[Dict[str, int]], output_path: Optional[str] = None) -> str:
        """
        Exportiert einen Bericht mit Wortzählstatistiken.
        
        Args:
            results: Liste der Wortzählstatistiken
            output_path: Pfad zum Speichern des Berichts
        
        Returns:
            Pfad zur Berichtsdatei
        """
        if not output_path:
            output_path = 'word_count_report.txt'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("Wortanzahl-Bericht\n")
            f.write("=" * 20 + "\n\n")
            
            for result in results:
                f.write(f"Datei: {result.get('file', 'Unbekannt')}\n")
                
                if 'error' in result:
                    f.write(f"Fehler: {result['error']}\n\n")
                else:
                    f.write(f"Gesamtwörter: {result.get('total_words', 0)}\n")
                    f.write(f"Einzigartige Wörter: {result.get('unique_words', 0)}\n")
                    
                    f.write("Top 10 Wörter:\n")
                    for word, freq in result.get('word_frequency', {}).items():
                        f.write(f"  {word}: {freq}\n")
                    f.write("\n")
        
        return output_path