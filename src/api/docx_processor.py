import os
import logging
from typing import List, Dict, Any
import docx

class DocxProcessor:
    @staticmethod
    def read_docx_files(directory: str) -> List[Dict[str, str]]:
        """
        Liest alle Word-Dokumente aus einem Verzeichnis.
        
        Args:
            directory: Pfad zum Verzeichnis mit Word-Dokumenten
        
        Returns:
            Liste von Dokumenten mit Metadaten
        """
        documents = []
        
        try:
            # Überprüfen, ob Verzeichnis existiert
            if not os.path.exists(directory):
                logging.error(f"Verzeichnis nicht gefunden: {directory}")
                return documents

            # Alle Dateien im Verzeichnis durchsuchen
            for filename in os.listdir(directory):
                if filename.lower().endswith('.docx'):
                    filepath = os.path.join(directory, filename)
                    
                    try:
                        doc = docx.Document(filepath)
                        full_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
                        
                        documents.append({
                            'filename': filename,
                            'path': filepath,
                            'text': full_text,
                            'word_count': len(full_text.split())
                        })
                    except Exception as doc_error:
                        logging.error(f"Fehler beim Lesen von {filename}: {doc_error}")
        
        except PermissionError:
            logging.error(f"Keine Berechtigung, Verzeichnis zu lesen: {directory}")
        except Exception as e:
            logging.error(f"Unerwarteter Fehler beim Durchsuchen des Verzeichnisses {directory}: {e}")
        
        return documents

    @staticmethod
    def analyze_docx_files(directory: str) -> Dict[str, Any]:
        """
        Analysiert Word-Dokumente und gibt Gesamtstatistiken zurück.
        
        Args:
            directory: Pfad zum Verzeichnis mit Word-Dokumenten
        
        Returns:
            Dictionary mit Dokumentenstatistiken
        """
        documents = DocxProcessor.read_docx_files(directory)
        
        return {
            'total_documents': len(documents),
            'total_words': sum(doc['word_count'] for doc in documents),
            'documents': documents
        }