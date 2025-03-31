import os
import sys
import streamlit as st
import pandas as pd

# Projektverzeichnis zum Python-Pfad hinzufügen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.core.word_counter import WordCounter

def main():
    st.title("📊 SEO Wortanzahl-Analyse")
    
    uploaded_files = st.file_uploader(
        "Laden Sie DOCX-Dateien hoch", 
        type=['docx'], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        results = []
        for uploaded_file in uploaded_files:
            # Temporäre Datei speichern
            temp_path = os.path.join(project_root, 'temp', uploaded_file.name)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            result = WordCounter.count_words(temp_path)
            result['file'] = uploaded_file.name
            results.append(result)
            
            # Temporäre Datei löschen
            os.remove(temp_path)
        
        display_results(results)

def display_results(results):
    st.subheader("📊 Analyseergebnisse")
    
    total_words = sum(result.get('total_words', 0) for result in results)
    unique_words = sum(result.get('unique_words', 0) for result in results)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Dokumente", len(results))
    col2.metric("📝 Gesamtwörter", total_words)
    col3.metric("🔤 Einzigartige Wörter", unique_words)
    
    for result in results:
        st.markdown(f"## 📄 {result.get('file', 'Unbekannt')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Wörter", result.get('total_words', 0))
            st.metric("Einzigartige Wörter", result.get('unique_words', 0))
        
        with col2:
            word_freq = result.get('word_frequency', {})
            top_words = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10])
            
            st.write("### Top 10 Wörter")
            st.table(pd.DataFrame.from_dict(top_words, orient='index', columns=['Häufigkeit']))
        
        st.markdown("---")

if __name__ == "__main__":
    main()