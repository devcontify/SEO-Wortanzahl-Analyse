"""
Moderne Web-UI für das Wortanzahl-Tool mit Streamlit.
Verbesserte Benutzerfreundlichkeit und Funktionalität.
"""
import os
import sys
import base64
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import List, Dict, Optional

# Projektverzeichnis zum Python-Pfad hinzufügen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.api.drive import GoogleDriveClient
from src.core.word_counter import WordCounter

# Globale Konfiguration
st.set_page_config(
    page_title="📊 Wortanzahl-Analyse",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    Analysiert ein Dokument mit Fortschrittsanzeige.
    
    Args:
        file_path: Pfad zur Dokumentdatei
    
    Returns:
        Analyseergebnisse
    """
    with st.spinner(f"Analysiere {os.path.basename(file_path)}..."):
        try:
            result = WordCounter.count_words(file_path)
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
    st.title("📊 Wortanzahl-Analyse")
    
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
    Moderne Darstellung der Analyseergebnisse mit interaktiven Visualisierungen.
    
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
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Wörter", result.get('total_words', 0))
                st.metric("Einzigartige Wörter", result.get('unique_words', 0))
            
            with col2:
                # Interaktive Worthäufigkeitsvisualisierung
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
    """
    st.header("🔍 Über Wortanzahl-Analyse")
    st.markdown("""
    ### 📊 Moderne Dokumentenanalyse

    Ein fortschrittliches Tool zur Analyse von Dokumenten mit:
    - 🚀 Drag & Drop Unterstützung
    - 📊 Interaktiven Visualisierungen
    - 🌐 Google Drive Integration (in Entwicklung)
    - 🔤 Detaillierten Wortstatistiken

    #### Technologien
    - Python
    - Streamlit
    - Plotly
    - WordCloud
    """)

if __name__ == "__main__":
    main()