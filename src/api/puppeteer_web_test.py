import asyncio
import os
from pyppeteer import launch

async def login_to_claude(email: str, password: str):
    """
    Automatisierte Anmeldung bei Claude
    """
    browser = await launch(headless=False)
    page = await browser.newPage()
    
    # Setze Viewport-Größe
    await page.setViewport({'width': 1920, 'height': 1080})
    
    # Navigiere zur Claude-Anmeldeseite
    await page.goto('https://claude.ai/chat/ec32fd23-baed-4374-8487-3e16fc96b0e8')
    
    # Warte auf die Eingabefelder für die Anmeldung
    await page.waitForSelector('input[name="email"]')
    await page.waitForSelector('input[name="password"]')
    
    # Fülle die Anmeldedaten aus
    await page.type('input[name="email"]', email)
    await page.type('input[name="password"]', password)
    
    # Klicke auf den Anmeldebutton
    await page.click('button[type="submit"]')
    
    # Warte auf die Navigation nach der Anmeldung
    await page.waitForNavigation()
    
    # Hier können weitere Schritte zur Interaktion mit der Seite hinzugefügt werden
    
    await browser.close()

async def main():
    email = "your_email@example.com"  # Ersetzen Sie dies durch die tatsächliche E-Mail
    password = "your_password"          # Ersetzen Sie dies durch das tatsächliche Passwort
    await login_to_claude(email, password)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
