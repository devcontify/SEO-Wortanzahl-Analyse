"""
Google Drive API-Integration für den Zugriff auf DOCX-Dokumente.
"""
import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Berechtigungen, die für den Zugriff auf Google Drive benötigt werden
SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

class GoogleDriveClient:
    """
    Client für die Interaktion mit der Google Drive API.
    """
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.pickle'):
        """
        Initialisiert den Google Drive Client.
        
        Args:
            credentials_path: Pfad zur credentials.json-Datei
            token_path: Pfad zur token.pickle-Datei
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """
        Authentifiziert den Benutzer bei der Google Drive API.
        """
        creds = None
        
        # Token aus der Datei laden, falls vorhanden
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Wenn keine gültigen Anmeldeinformationen verfügbar sind, den Benutzer anmelden lassen
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Token für die zukünftige Verwendung speichern
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Drive API-Service erstellen
        self.service = build('drive', 'v3', credentials=creds)
    
    def list_docx_files(self, folder_id: Optional[str] = None, page_size: int = 100) -> List[Dict[str, Any]]:
        """
        Listet alle DOCX-Dateien im Google Drive des Benutzers auf.
        
        Args:
            folder_id: ID des Ordners, in dem gesucht werden soll (optional)
            page_size: Anzahl der Ergebnisse pro Seite
            
        Returns:
            Liste von DOCX-Dateien mit Metadaten
        """
        query = "mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'"
        
        if folder_id:
            query += f" and '{folder_id}' in parents"
            
        results = self.service.files().list(
            q=query,
            pageSize=page_size,
            fields="nextPageToken, files(id, name, createdTime, modifiedTime, size)"
        ).execute()
        
        return results.get('files', [])
    
    def download_file(self, file_id: str, output_path: Optional[str] = None) -> str:
        """
        Lädt eine Datei aus Google Drive herunter.
        
        Args:
            file_id: ID der Datei
            output_path: Pfad, unter dem die Datei gespeichert werden soll (optional)
            
        Returns:
            Pfad zur heruntergeladenen Datei
        """
        file_metadata = self.service.files().get(fileId=file_id, fields="name").execute()
        file_name = file_metadata.get('name', f'document_{file_id}.docx')
        
        if not output_path:
            output_path = os.path.join('downloads', file_name)
        
        # Sicherstellen, dass das Verzeichnis existiert
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        request = self.service.files().get_media(fileId=file_id)
        
        with open(output_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        
        return output_path
    
    def search_docx_files(self, query_string: str, page_size: int = 100) -> List[Dict[str, Any]]:
        """
        Sucht nach DOCX-Dateien, die dem Suchbegriff entsprechen.
        
        Args:
            query_string: Suchbegriff
            page_size: Anzahl der Ergebnisse pro Seite
            
        Returns:
            Liste von DOCX-Dateien mit Metadaten
        """
        query = f"mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document' and fullText contains '{query_string}'"
        
        results = self.service.files().list(
            q=query,
            pageSize=page_size,
            fields="nextPageToken, files(id, name, createdTime, modifiedTime, size)"
        ).execute()
        
        return results.get('files', [])