"""
CLI-Schnittstelle für das Wortanzahl-Tool.
"""
import typer
from typing import List, Optional
from pathlib import Path
import rich
from rich.console import Console
from rich.table import Table

from src.api.drive import GoogleDriveClient
from src.core.word_counter import WordCounter

app = typer.Typer(help="CLI-Tool zur Wortzählung in DOCX-Dokumenten.")
console = Console()

@app.command("local")
def count_local_files(
    files: List[Path] = typer.Argument(..., help="Pfade zu DOCX-Dateien"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Pfad zur Ausgabedatei")
):
    """
    Zählt Wörter in lokalen DOCX-Dateien.
    
    Beispiel:
    python -m src.ui.cli local dokument1.docx dokument2.docx
    """
    try:
        # Konvertiere Pfade zu Strings
        file_paths = [str(file) for file in files]
        
        # Analysiere Dokumente
        results = WordCounter.analyze_multiple_documents(file_paths)
        
        # Zeige Ergebnisse in der Konsole
        _display_results(results)
        
        # Optional: Exportiere Bericht
        if output:
            report_path = WordCounter.export_word_count_report(results, str(output))
            console.print(f"[green]Bericht exportiert nach: {report_path}[/green]")
    
    except Exception as e:
        console.print(f"[red]Fehler: {e}[/red]")

@app.command("drive")
def count_drive_files(
    folder_id: Optional[str] = typer.Option(None, "--folder", help="Google Drive Ordner-ID"),
    query: Optional[str] = typer.Option(None, "--query", help="Suchbegriff für Dateien"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Pfad zur Ausgabedatei")
):
    """
    Zählt Wörter in Google Drive DOCX-Dokumenten.
    
    Beispiel:
    python -m src.ui.cli drive --folder 1abc123 --output report.txt
    """
    try:
        # Initialisiere Google Drive Client
        drive_client = GoogleDriveClient()
        
        # Dateien abrufen
        if query:
            files = drive_client.search_docx_files(query)
        elif folder_id:
            files = drive_client.list_docx_files(folder_id)
        else:
            files = drive_client.list_docx_files()
        
        # Dateien herunterladen und analysieren
        results = []
        for file in files:
            try:
                # Datei herunterladen
                downloaded_file = drive_client.download_file(file['id'])
                
                # Wortzählung
                result = WordCounter.count_words(downloaded_file)
                result['file'] = file['name']
                results.append(result)
            except Exception as e:
                console.print(f"[yellow]Fehler bei {file['name']}: {e}[/yellow]")
        
        # Zeige Ergebnisse in der Konsole
        _display_results(results)
        
        # Optional: Exportiere Bericht
        if output:
            report_path = WordCounter.export_word_count_report(results, str(output))
            console.print(f"[green]Bericht exportiert nach: {report_path}[/green]")
    
    except Exception as e:
        console.print(f"[red]Fehler: {e}[/red]")

def _display_results(results: List[dict]):
    """
    Zeigt Wortzählungsergebnisse in einer Rich-Tabelle an.
    """
    table = Table(title="Wortanzahl-Analyse")
    table.add_column("Datei", style="cyan")
    table.add_column("Gesamtwörter", style="magenta")
    table.add_column("Einzigartige Wörter", style="green")
    
    for result in results:
        table.add_row(
            result.get('file', 'Unbekannt'),
            str(result.get('total_words', 0)),
            str(result.get('unique_words', 0))
        )
    
    console.print(table)

def main():
    """
    Hauptfunktion zum Starten der CLI-Anwendung.
    """
    app()

if __name__ == "__main__":
    main()