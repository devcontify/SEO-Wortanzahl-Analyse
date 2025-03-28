"""
Web-UI für das Wortanzahl-Tool mit Streamlit.
"""
import streamlit as st
import os
from typing import List, Dict

from src.api.drive import GoogleDriveClient
from src.core.word_counter import WordCounter

def main():
    """
    Hauptfunktion für die Streamlit-Anwendung.
    """
    st.title("📊 Wortanzahl-Analyse")
    
    # Seitennavigation
    page = st.sidebar.selectbox(
        "Wählen Sie eine Option",
        ["Lokale Dateien", "Google Drive", "Über"]
    )
    
    if page == "Lokale Dateien":
        local_file_analysis()
    elif page == "Google Drive":
        google_drive_analysis()
    else:
        about_page()

def local_file_analysis():
    """
    Analyse von lokalen DOCX-Dateien.
    """
    st.header("Lokale DOCX-Dateien analysieren")
    
    uploaded_files = st.file_uploader(
        "Laden Sie DOCX-Dateien hoch", 
        type=['docx'], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        results = []
        for uploaded_file in uploaded_files:
            # Temporäre Datei speichern
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                result = WordCounter.count_words(uploaded_file.name)
                result['file'] = uploaded_file.name
                results.append(result)
                
                # Temporäre Datei löschen
                os.remove(uploaded_file.name)
            except Exception as e:
                st.error(f"Fehler bei {uploaded_file.name}: {e}")
        
        display_results(results)

def google_drive_analysis():
    """
    Analyse von Google Drive DOCX-Dateien.
    """
    st.header("Google Drive Dokumente analysieren")
    
    # Google Drive Authentifizierung
    st.write("Bitte authentifizieren Sie sich bei Google Drive.")
    
    try:
        drive_client = GoogleDriveClient()
        
        # Ordner-ID oder Suche
        search_type = st.radio(
            "Wie möchten Sie Dokumente auswählen?", 
            ["Alle Dokumente", "Nach Ordner", "Suche"]
        )
        
        results = []
        if search_type == "Alle Dokumente":
            files = drive_client.list_docx_files()
        elif search_type == "Nach Ordner":
            folder_id = st.text_input("Geben Sie die Ordner-ID ein")
            if folder_id:
                files = drive_client.list_docx_files(folder_id)
            else:
                st.warning("Bitte geben Sie eine Ordner-ID ein.")
                return
        else:  # Suche
            query = st.text_input("Suchbegriff")
            if query:
                files = drive_client.search_docx_files(query)
            else:
                st.warning("Bitte geben Sie einen Suchbegriff ein.")
                return
        
        # Dokumente herunterladen und analysieren
        for file in files:
            try:
                downloaded_file = drive_client.download_file(file['id'])
                result = WordCounter.count_words(downloaded_file)
                result['file'] = file['name']
                results.append(result)
                
                # Temporäre Datei löschen
                os.remove(downloaded_file)
            except Exception as e:
                st.error(f"Fehler bei {file['name']}: {e}")
        
        display_results(results)
    
    except Exception as e:
        st.error(f"Fehler bei der Google Drive-Authentifizierung: {e}")

def display_results(results: List[Dict[str, int]]):
    """
    Zeigt Analyseergebnisse in Streamlit an.
    """
    if results:
        st.subheader("Analyseergebnisse")
        
        for result in results:
            with st.expander(f"📄 {result.get('file', 'Unbekannt')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Gesamtwörter", result.get('total_words', 0))
                
                with col2:
                    st.metric("Einzigartige Wörter", result.get('unique_words', 0))
                
                st.write("Top 10 Wörter:")
                word_freq = result.get('word_frequency', {})
                freq_df = {word: freq for word, freq in word_freq.items()}
                st.bar_chart(freq_df)

def about_page():
    """
    Informationsseite über das Tool.
    """
    st.header("Über Wortanzahl-Analyse")
    st.write("""
    ### 📊 Wortanzahl-Analyse Tool
    
    Ein modernes CLI- und Web-Tool zur Analyse von DOCX-Dokumenten.
    
    #### Funktionen:
    - Wortzählung in lokalen Dokumenten
    - Integration mit Google Drive
    - Detaillierte Wortstatistiken
    - Benutzerfreundliche Oberfläche
    
    #### Technologien:
    - Python
    - Typer (CLI)
    - Streamlit (Web-UI)
    - Google Drive API
    - python-docx
    """)

if __name__ == "__main__":
    main()