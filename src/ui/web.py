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
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

# Projektverzeichnis zum Python-Pfad hinzufügen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Dummy-Klasse für GoogleDriveClient
class GoogleDriveClient:
    @staticmethod
    def list_files():
        return []

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
                f.write(f"  Flesch-Kincaid Grade: {readability.get('flesch_kincaid_grade', 0):.2f}\n")
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
        
        # Benutzerdefinierte Styles
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        
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
            story.append(Paragraph(f"Flesch-Kincaid Grade: {readability.get('flesch_kincaid_grade', 0):.2f}", styles['Normal']))
            story.append(Paragraph(f"Komplexitätslevel: {readability.get('complexity_level', 'Unbekannt')}", styles['Normal']))
            story.append(Spacer(1, 6))

            # WDF-IDF Analyse
            wdf_idf = result.get('wdf_idf', {})
            story.append(Paragraph("WDF-IDF Analyse (Top 5):", styles['Heading3']))
            top_wdf_idf = dict(sorted(wdf_idf.items(), key=lambda x: x[1], reverse=True)[:5])
            for word, score in top_wdf_idf.items():
                story.append(Paragraph(f"{word}: {score:.4f}", styles['Normal']))
            story.append(Spacer(1, 6))

            # Semantische Analyse
            semantic = result.get('semantic', {})
            story.append(Paragraph("Semantische Analyse:", styles['Heading3']))
            story.append(Paragraph(f"Einzigartige bedeutungsvolle Wörter: {semantic.get('unique_meaningful_words', 0)}", styles['Normal']))
            
            top_meaningful = semantic.get('top_meaningful_words', [])
            story.append(Paragraph("Top bedeutungsvolle Wörter:", styles['Heading4']))
            for word, count in top_meaningful[:5]:
                story.append(Paragraph(f"{word}: {count}", styles['Normal']))
            story.append(Spacer(1, 6))

            # Keyword-Dichte
            keyword_density = result.get('keyword_density', {})
            story.append(Paragraph("Keyword-Dichte:", styles['Heading3']))
            for keyword, density in keyword_density.items():
                story.append(Paragraph(f"{keyword}: {density:.2f}%", styles['Normal']))
            
            story.append(Spacer(1, 12))

        doc.build(story)
    
    return filepath

# Rest des Codes bleibt unverändert
def main():
    """
    Hauptfunktion für die Streamlit-Anwendung.
    """
    st.title("📊 SEO Wortanzahl-Analyse")
    
    # Seitennavigation
    page = st.sidebar.radio(
        "Menü", 
        ["Lokale Dateien", "Über"],
        index=0
    )
    
    if page == "Lokale Dateien":
        local_file_analysis()
    else:
        about_page()

# Restliche Funktionen bleiben unverändert
def local_file_analysis():
    """
    Moderne Analyse von lokalen DOCX-Dateien mit Drag & Drop.
    Mobile-optimierte Version.
    """
    st.header("📤 Dokumente analysieren")
    
    uploaded_files = st.file_uploader(
        "Laden Sie DOCX-Dateien hoch", 
        type=['docx'], 
        accept_multiple_files=True,
        help="Ziehen Sie Dateien hierher oder klicken Sie zum Auswählen"
    )
    
    if uploaded_files:
        results = []
        progress_bar = st.progress(0)
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Temporäre Datei speichern
            temp_path = os.path.join(project_root, 'temp', uploaded_file.name)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            result = analyze_document(temp_path)
            
            if result:
                result['file'] = uploaded_file.name
                results.append(result)
                
                # Temporäre Datei löschen
                os.remove(temp_path)
            
            # Fortschrittsanzeige aktualisieren
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        if results:
            display_results(results)
        else:
            st.warning("Keine Dokumente analysiert.")

# Restliche Funktionen bleiben unverändert
def analyze_document(file_path: str) -> Dict[str, Any]:
    """
    Analysiert ein Dokument mit erweiterten SEO-Metriken.
    
    Args:
        file_path: Pfad zur Dokumentdatei
    
    Returns:
        Analyseergebnisse
    """
    with st.spinner(f"Analysiere {os.path.basename(file_path)}..."):
        try:
            # Basisanalyse
            result = WordCounter.count_words(file_path)
            
            # Text extrahieren
            from docx import Document
            doc = Document(file_path)
            full_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            # SEO-Metriken hinzufügen
            try:
                # Lesbarkeitsmetriken
                result['readability'] = SEOAnalyzer.readability_metrics(full_text)
                
                # WDF-IDF Analyse
                result['wdf_idf'] = SEOAnalyzer.calculate_wdf_idf([full_text])
                
                # Semantische Analyse
                result['semantic'] = SEOAnalyzer.semantic_analysis(full_text)
                
                # Keyword-Dichte (Top 10 Wörter als Keywords verwenden)
                top_words = list(dict(sorted(result.get('word_frequency', {}).items(), 
                                            key=lambda x: x[1], reverse=True)[:10]).keys())
                result['keyword_density'] = SEOAnalyzer.keyword_density(full_text, top_words)
                
            except Exception as seo_error:
                st.warning(f"SEO-Metriken konnten nicht berechnet werden: {seo_error}")
                result['readability'] = {
                    'flesch_reading_ease': 0,
                    'flesch_kincaid_grade': 0,
                    'complexity_level': 'Nicht verfügbar'
                }
            
            return result
        except Exception as e:
            st.error(f"Fehler bei der Analyse: {e}")
            return None

# Restliche Funktionen bleiben unverändert
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
    
    # Gesamtstatistiken
    total_words = sum(result.get('total_words', 0) for result in results)
    unique_words = sum(result.get('unique_words', 0) for result in results)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Dokumente", len(results))
    col2.metric("📝 Gesamtwörter", total_words)
    col3.metric("🔤 Einzigartige Wörter", unique_words)
    
    # Detaillierte Ergebnisse
    for result in results:
        st.markdown(f"## 📄 {result.get('file', 'Unbekannt')}")
        
        # Basis-Statistiken
        st.subheader("📈 Basisstatistiken")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Wörter", result.get('total_words', 0))
            st.metric("Einzigartige Wörter", result.get('unique_words', 0))
            
            # Lesbarkeitsmetriken
            readability = result.get('readability', {})
            if readability and readability.get('flesch_reading_ease', 0) > 0:
                st.metric("Lesbarkeit (Flesch)", f"{readability.get('flesch_reading_ease', 0):.2f}")
                st.metric("Flesch-Kincaid Grade", f"{readability.get('flesch_kincaid_grade', 0):.2f}")
                st.metric("Komplexitätslevel", readability.get('complexity_level', 'Unbekannt'))
        
        with col2:
            # Top 10 Wörter
            word_freq = result.get('word_frequency', {})
            top_words = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10])
            
            st.write("### Top 10 Wörter")
            st.table(pd.DataFrame.from_dict(top_words, orient='index', columns=['Häufigkeit']))
        
        # SEO-Metriken
        st.subheader("🔍 SEO-Metriken")
        
        # WDF-IDF Analyse
        if 'wdf_idf' in result:
            st.write("### 📊 WDF-IDF Analyse")
            st.markdown("""
            **WDF-IDF (Within Document Frequency - Inverse Document Frequency)** misst die Wichtigkeit eines Wortes im Dokument.
            - Logarithmische Skalierung der Wortfrequenz
            - Berücksichtigt Häufigkeit und Verteilung von Wörtern
            - Zeigt thematisch relevante Schlüsselwörter
            """)
            
            wdf_idf = result.get('wdf_idf', {})
            if wdf_idf:
                # Top 10 WDF-IDF Wörter
                top_wdf_idf = dict(list(wdf_idf.items())[:10])
                st.table(pd.DataFrame.from_dict(top_wdf_idf, orient='index', columns=['WDF-IDF Score']))
        
        # Semantische Analyse
        if 'semantic' in result:
            st.write("### 🧠 Semantische Analyse")
            semantic = result.get('semantic', {})
            if semantic:
                st.metric("Einzigartige bedeutungsvolle Wörter", semantic.get('unique_meaningful_words', 0))
                
                top_meaningful = semantic.get('top_meaningful_words', [])
                if top_meaningful:
                    meaningful_dict = {word: count for word, count in top_meaningful}
                    st.table(pd.DataFrame.from_dict(meaningful_dict, orient='index', columns=['Häufigkeit']))
        
        # Keyword-Dichte
        if 'keyword_density' in result:
            st.write("### 🎯 Keyword-Dichte")
            keyword_density = result.get('keyword_density', {})
            if keyword_density:
                st.table(pd.DataFrame.from_dict(keyword_density, orient='index', columns=['Dichte (%)']))
        
        st.markdown("---")  # Trennlinie zwischen Dokumenten

def about_page():
    """
    Moderne Informationsseite über das Tool.
    Mobile-optimierte Version.
    """
    st.header("🔍 Über SEO Wortanzahl-Analyse")
    st.markdown("""
    ### 📊 Moderne Dokumentenanalyse
    
    Ein Tool zur Textanalyse mit:
    - 🚀 Drag & Drop Datei-Upload
    - 📊 Interaktiven Visualisierungen
    - 📝 Wortanzahl und Häufigkeitsanalyse
    - 📖 Grundlegende Lesbarkeitsmetriken
    
    #### Technologien
    - Python
    - Streamlit
    - Plotly
    - WordCloud
    """)

if __name__ == "__main__":
    main()