import os
import json
import logging
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.docx_processor import DocxProcessor
from core.seo_analyzer import SEOAnalyzer

def run_autonomous_docx_test(documents_dir: str):
    """
    Autonomer Test für Word-Dokumente.
    Nur für interne Testzwecke gedacht.
    
    Args:
        documents_dir: Verzeichnis mit Word-Dokumenten
    
    Returns:
        Detaillierter Testbericht
    """
    try:
        # Dokumente laden
        documents = DocxProcessor.read_docx_files(documents_dir)
        
        # Detaillierter Testbericht
        test_report = {
            'total_documents': len(documents),
            'documents': []
        }
        
        for doc in documents:
            # SEO-Analyse durchführen
            seo_metrics = SEOAnalyzer.semantic_analysis(doc['text'])
            readability = SEOAnalyzer.readability_metrics(doc['text'])
            
            doc_report = {
                'filename': doc['filename'],
                'path': doc['path'],
                'word_count': doc['word_count'],
                'seo_metrics': {
                    'unique_meaningful_words': seo_metrics.get('unique_meaningful_words', 0),
                    'top_meaningful_words': seo_metrics.get('top_meaningful_words', [])
                },
                'readability': {
                    'flesch_reading_ease': readability.get('flesch_reading_ease', 0),
                    'flesch_kincaid_grade': readability.get('flesch_kincaid_grade', 0),
                    'complexity_level': readability.get('complexity_level', 'Unbekannt')
                }
            }
            
            test_report['documents'].append(doc_report)
        
        # Bericht speichern
        report_path = os.path.join(documents_dir, 'autonomous_test_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(test_report, f, ensure_ascii=False, indent=4)
        
        print(f"Autonomer Test abgeschlossen. Bericht gespeichert unter: {report_path}")
        return test_report
    
    except Exception as e:
        logging.error(f"Fehler beim autonomen Test: {e}")
        return None

# Nur für Testzwecke
if __name__ == "__main__":
    test_dir = r"K:\Meine Ablage\Empirio"
    result = run_autonomous_docx_test(test_dir)
    if result:
        print(f"Anzahl der getesteten Dokumente: {result['total_documents']}")