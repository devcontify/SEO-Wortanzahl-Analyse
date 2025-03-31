"""
Moderne Web-UI für das Wortanzahl-Tool mit Streamlit.
Verbesserte Benutzerfreundlichkeit und SEO-Optimierung.
Mobile-optimierte Version.
"""
import os
import sys
import base64
import json
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import List, Dict, Optional, Any
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Projektverzeichnis zum Python-Pfad hinzufügen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.api.drive import GoogleDriveClient
from src.core.word_counter import WordCounter
from src.core.seo_analyzer import SEOAnalyzer

# Ergebnisordner definieren
RESULTS_DIR = os.path.join(project_root, 'seo_analysis_results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def export_results_to_text(results: List[Dict[str, Any]], format: str = 'txt') -> str:
    """
    Exportiert Analyseergebnisse in eine Textdatei oder PDF.
    
    Args:
        results: Liste der Analyseergebnisse
        format: Ausgabeformat ('txt' oder 'pdf')
    
    Returns:
        Pfad zur exportierten Datei
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"seo_analysis_results_{timestamp}.{format}"
    filepath = os.path.join(RESULTS_DIR, filename)
    
    if format == 'txt':
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("SEO Analyse Ergebnisse\n")
            f.write("====================\n\n")
            
            for result in results:
                f.write(f"Dokument: {result.get('file', 'Unbekannt')}\n")
                f.write("-" * 40 + "\n")
                
                # Basisstatistiken
                f.write("Basisstatistiken:\n")
                f.write(f"  Wörter: {result.get('total_words', 0)}\n")
                f.write(f"  Einzigartige Wörter: {result.get('unique_words', 0)}\n\n")
                
                # Lesbarkeitsmetriken
                readability = result.get('readability', {})
                f.write("Lesbarkeit:\n")
                f.write(f"  Flesch Reading Ease: {readability.get('flesch_reading_ease', 0):.2f}\n")
                f.write(f"  Komplexitätslevel: {readability.get('complexity_level', 'Unbekannt')}\n\n")
                
                # WDF-IDF Analyse
                wdf_idf = result.get('wdf_idf', {})
                f.write("WDF-IDF Analyse (Top 5):\n")
                top_wdf_idf = dict(sorted(wdf_idf.items(), key=lambda x: x[1], reverse=True)[:5])
                for word, score in top_wdf_idf.items():
                    f.write(f"  {word}: {score:.4f}\n")
                f.write("\n")
                
                # Semantische Analyse
                semantic = result.get('semantic', {})
                f.write("Semantische Analyse:\n")
                f.write(f"  Einzigartige bedeutungsvolle Wörter: {semantic.get('unique_meaningful_words', 0)}\n")
                top_meaningful = semantic.get('top_meaningful_words', [])
                f.write("  Top bedeutungsvolle Wörter:\n")
                for word, count in top_meaningful[:5]:
                    f.write(f"    {word}: {count}\n")
                f.write("\n")
                
                # Keyword-Dichte
                keyword_density = result.get('keyword_density', {})
                f.write("Keyword-Dichte:\n")
                for keyword, density in keyword_density.items():
                    f.write(f"  {keyword}: {density:.2f}%\n")
                f.write("\n" + "=" * 40 + "\n\n")
    
    elif format == 'pdf':
        try:
            # Fallback-Schriftart
            pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica'))
        except Exception:
            pass

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Titel
        story.append(Paragraph("SEO Analyse Ergebnisse", styles['Title']))
        story.append(Spacer(1, 12))

        for result in results:
            story.append(Paragraph(f"Dokument: {result.get('file', 'Unbekannt')}", styles['Heading2']))
            
            # Basisstatistiken
            story.append(Paragraph("Basisstatistiken:", styles['Heading3']))
            story.append(Paragraph(f"Wörter: {result.get('total_words', 0)}", styles['Normal']))
            story.append(Paragraph(f"Einzigartige Wörter: {result.get('unique_words', 0)}", styles['Normal']))
            story.append(Spacer(1, 6))

            # Lesbarkeitsmetriken
            readability = result.get('readability', {})
            story.append(Paragraph("Lesbarkeit:", styles['Heading3']))
            story.append(Paragraph(f"Flesch Reading Ease: {readability.get('flesch_reading_ease', 0):.2f}", styles['Normal']))
            story.append(Paragraph(f"Komplexitätslevel: {readability.get('complexity_level', 'Unbekannt')}", styles['Normal']))
            story.append(Spacer(1, 6))

            # Weitere Metriken analog hinzufügen...
            story.append(Spacer(1, 12))

        doc.build(story)
    
    return filepath

# Restlicher Code bleibt unverändert...

def display_results(results: List[Dict[str, Any]]):
    """
    Moderne Darstellung der Analyseergebnisse mit erweiterten SEO-Metriken.
    Mobile-optimierte Visualisierungen.
    
    Args:
        results: Liste der Analyseergebnisse
    """
    st.subheader("📊 Analyseergebnisse")
    
    # Export-Optionen
    export_format = st.radio(
        "Ergebnisse exportieren als:", 
        ['Textdatei (.txt)', 'PDF (.pdf)'], 
        horizontal=True
    )
    
    # Exportieren
    if st.button("📥 Ergebnisse exportieren"):
        format_mapping = {
            'Textdatei (.txt)': 'txt',
            'PDF (.pdf)': 'pdf'
        }
        selected_format = format_mapping[export_format]
        export_file = export_results_to_text(results, selected_format)
        
        with open(export_file, 'rb') as f:
            st.download_button(
                label=f"📥 {export_format} herunterladen",
                data=f,
                file_name=os.path.basename(export_file),
                mime='application/octet-stream'
            )
    
    # Restliche Analyseergebnisse-Anzeige bleibt unverändert...
    # (vorheriger Code für Detailansicht)