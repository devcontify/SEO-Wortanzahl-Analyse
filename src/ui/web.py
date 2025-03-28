"""
Moderne Web-UI für das Wortanzahl-Tool mit Streamlit.
Verbesserte Benutzerfreundlichkeit und SEO-Optimierung.
Mobile-optimierte Version.
"""
import os
import sys
import base64
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import List, Dict, Optional, Any

# Projektverzeichnis zum Python-Pfad hinzufügen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.api.drive import GoogleDriveClient
from src.core.word_counter import WordCounter
from src.core.seo_analyzer import SEOAnalyzer

# Mobile-optimierte Konfiguration
st.set_page_config(
    page_title="📊 SEO Wortanzahl-Analyse",
    page_icon="📄",
    layout="wide",  # Breites Layout für bessere Responsiveness
    initial_sidebar_state="auto"  # Dynamische Seitenleiste
)

# CSS für zusätzliche mobile Optimierung
st.markdown("""
<style>
/* Mobile-freundliche Schriftgrößen */
@media (max-width: 600px) {
    .stMarkdown, .stMetric, .stButton > button {
        font-size: 14px !important;
    }
    
    /* Kompaktere Spalten */
    .stColumns > div {
        padding: 0.25rem !important;
    }
    
    /* Anpassung für Diagramme */
    .stPlotlyChart {
        width: 100% !important;
        max-width: 100% !important;
    }
}

/* Verbesserte Touch-Interaktion */
.stFileUploader > div > div > div > input[type="file"] {
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
}

/* Responsive Tabellen */
.stDataFrame {
    overflow-x: auto;
    max-width: 100%;
}
</style>
""", unsafe_allow_html=True)

def cache_result(func):
    """Decorator für Caching von Analyseergebnissen"""
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        cached_result = st.session_state.get(key)
        if cached_result is not None:
            return cached_result
        result = func(*args, **kwargs)
        st.session_state[key] = result
        return result
    return wrapper

@cache_result
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
            import docx
            doc = docx.Document(file_path)
            full_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            # Minimale SEO-Metriken hinzufügen
            try:
                # Nur Lesbarkeitsmetriken - minimal invasiv
                result['readability'] = SEOAnalyzer.readability_metrics(full_text)
            except Exception as seo_error:
                st.warning(f"SEO-Metriken konnten nicht berechnet werden: {seo_error}")
                result['readability'] = {
                    'flesch_reading_ease': 0,
                    'complexity_level': 'Nicht verfügbar'
                }
            
            return result
        except Exception as e:
            st.error(f"Fehler bei der Analyse: {e}")
            return None

def display_word_cloud(word_freq: Dict[str, int]):
    """
    Generiert eine interaktive Wortwolke.
    
    Args:
        word_freq: Wortfrequenz-Dictionary
    """
    import wordcloud
    
    wc = wordcloud.WordCloud(
        width=800, 
        height=400, 
        background_color='white'
    ).generate_from_frequencies(word_freq)
    
    st.image(wc.to_array())

def main():
    """
    Hauptfunktion für die Streamlit-Anwendung.
    """
    st.title("📊 SEO Wortanzahl-Analyse")
    
    # Seitennavigation
    page = st.sidebar.radio(
        "Menü", 
        ["Lokale Dateien", "Google Drive", "Über"],
        index=0
    )
    
    if page == "Lokale Dateien":
        local_file_analysis()
    elif page == "Google Drive":
        google_drive_analysis()
    else:
        about_page()

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

def google_drive_analysis():
    """
    Moderne Analyse von Google Drive Dokumenten.
    """
    st.header("🌐 Google Drive Dokumente")
    st.warning("Google Drive Integration wird noch entwickelt.")

def display_results(results: List[Dict[str, int]]):
    """
    Moderne Darstellung der Analyseergebnisse mit minimalen SEO-Metriken.
    Mobile-optimierte Visualisierungen.
    
    Args:
        results: Liste der Analyseergebnisse
    """
    st.subheader("📊 Analyseergebnisse")
    
    # Gesamtstatistiken
    total_words = sum(result.get('total_words', 0) for result in results)
    unique_words = sum(result.get('unique_words', 0) for result in results)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Dokumente", len(results))
    col2.metric("📝 Gesamtwörter", total_words)
    col3.metric("🔤 Einzigartige Wörter", unique_words)
    
    # Detaillierte Ergebnisse
    for result in results:
        with st.expander(f"📄 {result.get('file', 'Unbekannt')}"):
            # Basis-Statistiken
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Wörter", result.get('total_words', 0))
                st.metric("Einzigartige Wörter", result.get('unique_words', 0))
                
                # Minimale SEO-Metriken
                readability = result.get('readability', {})
                if readability and readability.get('flesch_reading_ease', 0) > 0:
                    st.metric("Lesbarkeit", f"{readability.get('flesch_reading_ease', 0):.2f}")
                    st.metric("Komplexitätslevel", readability.get('complexity_level', 'Unbekannt'))
            
            with col2:
                # Top 10 Wörter
                word_freq = result.get('word_frequency', {})
                top_words = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10])
                
                df = pd.DataFrame.from_dict(top_words, orient='index', columns=['Häufigkeit'])
                df.index.name = 'Wort'
                
                fig = px.bar(
                    df, 
                    x=df.index, 
                    y='Häufigkeit', 
                    title='Top 10 Wörter',
                    labels={'x': 'Wort', 'y': 'Häufigkeit'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Wortwolke
            st.subheader("Wortwolke")
            display_word_cloud(result.get('word_frequency', {}))

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