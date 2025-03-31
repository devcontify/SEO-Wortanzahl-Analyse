import asyncio
import os
from pyppeteer import launch

async def test_seo_analysis_app():
    """
    Automatisierter Test der SEO-Analyse-Webanwendung mit Puppeteer
    """
    browser = await launch(headless=False)
    page = await browser.newPage()
    
    # Setze Viewport-Größe
    await page.setViewport({'width': 1920, 'height': 1080})
    
    # Starte Streamlit-Anwendung
    await page.goto('http://localhost:8501')
    await page.waitForSelector('input[type="file"]')
    
    # Testdateien-Verzeichnis
    test_files_dir = r'K:\Meine Ablage\Empirio'
    
    # Dokumente hochladen
    file_input = await page.querySelector('input[type="file"]')
    test_files = [
        os.path.join(test_files_dir, 'literature_research_kor.docx'),
        os.path.join(test_files_dir, 'hypotheses_kor.docx')
    ]
    
    await file_input.uploadFile(*test_files)
    
    # Warte auf Analyse
    await page.waitForSelector('div[data-testid="stMetric"]', timeout=30000)
    
    # Screenshots machen
    screenshots_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'test_screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # Gesamtansicht
    await page.screenshot({'path': os.path.join(screenshots_dir, 'seo_analysis_overview.png')})
    
    # Export-Optionen testen
    await page.click('div[role="radiogroup"] label:nth-child(2)')  # PDF-Option
    await page.click('button:has-text("Ergebnisse exportieren")')
    
    # Warte auf Download-Button
    await page.waitForSelector('a[download]')
    
    # Screenshot der Export-Optionen
    await page.screenshot({'path': os.path.join(screenshots_dir, 'seo_analysis_export.png')})
    
    # Detaillierte Ergebnisse
    await page.screenshot({'path': os.path.join(screenshots_dir, 'seo_analysis_details.png')})
    
    await browser.close()

async def main():
    try:
        await test_seo_analysis_app()
        print("SEO-Analyse-App Test erfolgreich abgeschlossen.")
    except Exception as e:
        print(f"Fehler beim Testen der SEO-Analyse-App: {e}")

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())