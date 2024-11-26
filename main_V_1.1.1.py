import tkinter as tk
from tkinter import messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import pandas as pd
import threading
import time
import random

# Statusvariablen
search_running = False
stop_thread = False


# Scraper für Österreich (firmen.wko.at)
def scrape_wko(branche, ort, nur_ohne_web):
    """Extrahiert Firmendaten von WKO.at basierend auf den Suchparametern."""
    global stop_thread
    base_url = f"https://firmen.wko.at/{branche}/{ort}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    firmendaten = []
    has_more = True

    while has_more and not stop_thread:
        try:
            print(f"Lade URL: {base_url}")
            response = requests.get(base_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Firmeneinträge parsen
            firmeneintraege = soup.find_all('article', class_='search-result-article')
            print(f"Gefundene Einträge: {len(firmeneintraege)}")

            if not firmeneintraege:
                log_error(f"Keine Firmeneinträge gefunden auf: {base_url}")
                break

            for eintrag in firmeneintraege:
                if stop_thread:
                    break

                try:
                    # Name der Firma
                    name_tag = eintrag.find('a', class_='title-link').find('h3')
                    name = name_tag.text.strip() if name_tag else 'Kein Name'

                    # Adresse
                    address_tag = eintrag.find('div', class_='address-container')
                    street_tag = address_tag.find('div', class_='street') if address_tag else None
                    city_tag = address_tag.find('div', class_='place') if address_tag else None
                    address = f"{street_tag.text.strip() if street_tag else 'Keine Straße'}, {city_tag.text.strip() if city_tag else 'Kein Ort'}"

                    # Telefonnummer
                    telefonnummer_tag = eintrag.find('a', itemprop='telephone')
                    telefonnummer = telefonnummer_tag.text.strip() if telefonnummer_tag else 'Keine Telefonnummer'

                    # Webseite
                    website_tag = eintrag.find('a', itemprop='url')
                    website = website_tag['href'] if website_tag else 'Keine Webseite'

                    # E-Mail
                    email_tag = eintrag.find('a', itemprop='email')
                    email = email_tag.text.strip() if email_tag else 'Keine E-Mail'

                    if nur_ohne_web and website != 'Keine Webseite':
                        continue

                    firmendaten.append({
                        'Name': name,
                        'Adresse': address,
                        'Telefonnummer': telefonnummer,
                        'Webseite': website,
                        'E-Mail': email
                    })

                except Exception as e:
                    log_error(f"Fehler beim Parsen eines Eintrags: {str(e)}")

            # Keine weiteren Seiten bei WKO
            has_more = False

        except requests.exceptions.RequestException as e:
            log_error(f"Fehler beim Abrufen der URL: {base_url}. Fehler: {str(e)}")
            break

    return firmendaten


# Scraper für Deutschland (gelbeseiten.de)
def scrape_gelbes_seiten(branche, ort, nur_ohne_web):
    """Extrahiert Firmendaten von Gelbeseiten.de basierend auf den Suchparametern."""
    global stop_thread
    base_url = f"https://www.gelbeseiten.de/branchen/{branche}/{ort}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    firmendaten = []
    seen_urls = set()  # Um doppelte Einträge zu vermeiden
    while not stop_thread:
        try:
            print(f"Lade URL: {base_url}")
            if base_url in seen_urls:
                log_error(f"Endlosschleife entdeckt auf: {base_url}")
                break
            seen_urls.add(base_url)

            response = requests.get(base_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Firmeneinträge parsen
            firmeneintraege = soup.find_all('article', class_='mod-Treffer')
            print(f"Gefundene Einträge: {len(firmeneintraege)}")

            if not firmeneintraege:
                log_error(f"Keine Firmeneinträge gefunden auf: {base_url}")
                break

            for eintrag in firmeneintraege:
                if stop_thread:
                    break

                try:
                    # Name der Firma
                    name_tag = eintrag.find('h2', class_='mod-Treffer__name')
                    name = name_tag.text.strip() if name_tag else 'Kein Name'

                    # Adresse
                    address_tag = eintrag.find('div', class_='mod-AdresseKompakt__adress-text')
                    address = address_tag.text.strip() if address_tag else 'Keine Adresse'

                    # Telefonnummer
                    telefonnummer_tag = eintrag.find('a', class_='mod-TelefonnummerKompakt__phoneNumber')
                    telefonnummer = telefonnummer_tag.text.strip() if telefonnummer_tag else 'Keine Telefonnummer'

                    # Webseite
                    website_tag = eintrag.find('span', class_='mod-WebseiteKompakt__text')
                    website = website_tag.text.strip() if website_tag else 'Keine Webseite'

                    if nur_ohne_web and website != 'Keine Webseite':
                        continue

                    firmendaten.append({
                        'Name': name,
                        'Adresse': address,
                        'Telefonnummer': telefonnummer,
                        'Webseite': website
                    })

                except Exception as e:
                    log_error(f"Fehler beim Parsen eines Eintrags: {str(e)}")

            # Mehr laden
            mehr_laden_button = soup.find('a', {'id': 'mod-LoadMore--button'})
            if mehr_laden_button:
                base_url = mehr_laden_button['href']
                time.sleep(random.uniform(1, 3))
            else:
                print("Keine weiteren Einträge verfügbar.")
                break

        except requests.exceptions.RequestException as e:
            log_error(f"Fehler beim Abrufen der URL: {base_url}. Fehler: {str(e)}")
            break

    return firmendaten


# Länderauswahl
def scrape_data(branche, ort, nur_ohne_web, land):
    if land == "Österreich":
        return scrape_wko(branche, ort, nur_ohne_web)
    elif land == "Deutschland":
        return scrape_gelbes_seiten(branche, ort, nur_ohne_web)
    else:
        log_error(f"Ungültige Länderauswahl: {land}")
        return []


# Fehlerprotokoll
def log_error(message):
    with open("error_log.txt", "a") as f:
        f.write(message + "\n")
    print(f"Fehlerprotokoll: {message}")


# Speichern der Daten
def save_to_excel(firmendaten, nur_ohne_web):
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Dateien", "*.xlsx")])
    if not file_path:
        return False  # Fehler, wenn kein Dateiname ausgewählt wurde

    df = pd.DataFrame(firmendaten)
    if nur_ohne_web:
        df = df[df['Webseite'] == 'Keine Webseite']

    try:
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Erfolg", "Die Daten wurden erfolgreich gespeichert.")
        return True  # Erfolgreiches Speichern
    except Exception as e:
        log_error(f"Fehler beim Speichern der Excel-Datei: {str(e)}")
        messagebox.showerror("Fehler", f"Fehler beim Speichern der Excel-Datei: {str(e)}")
        return False


# Suche starten
def start_search():
    global search_running, stop_thread
    if search_running:
        messagebox.showinfo("Info", "Die Suche läuft bereits.")
        return

    branche = entry_branche.get()
    ort = entry_ort.get()
    land = var_land.get()
    nur_ohne_web = var_nur_ohne_web.get()

    if not branche or not ort:
        messagebox.showerror("Fehler", "Bitte geben Sie Branche und Ort ein.")
        return

    search_running = True
    stop_thread = False
    btn_start.config(state='disabled')
    btn_stop.config(state='normal')
    messagebox.showinfo("Info", "Suche gestartet...")

    thread = threading.Thread(target=lambda: complete_search(branche, ort, nur_ohne_web, land))
    thread.start()


def complete_search(branche, ort, nur_ohne_web, land):
    global search_running
    firmendaten = scrape_data(branche, ort, nur_ohne_web, land)
    if save_to_excel(firmendaten, nur_ohne_web):  # Nur wenn die Datei erfolgreich gespeichert wurde
        search_running = False
        btn_start.config(state='normal')
        btn_stop.config(state='disabled')
        messagebox.showinfo("Info", "Suche beendet.")


# Suche stoppen
def stop_search():
    global search_running, stop_thread
    if search_running:
        stop_thread = True
        search_running = False
        btn_start.config(state='normal')
        btn_stop.config(state='disabled')
        messagebox.showinfo("Info", "Suche wurde gestoppt.")
    else:
        messagebox.showinfo("Info", "Es läuft keine Suche.")


# GUI
root = tk.Tk()
root.title("Firmensuche")

tk.Label(root, text="Land:").grid(row=0, column=0, padx=10, pady=10)
var_land = tk.StringVar(value="Österreich")
dropdown_land = tk.OptionMenu(root, var_land, "Österreich", "Deutschland")
dropdown_land.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Branche:").grid(row=1, column=0, padx=10, pady=10)
entry_branche = tk.Entry(root)
entry_branche.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Ort:").grid(row=2, column=0, padx=10, pady=10)
entry_ort = tk.Entry(root)
entry_ort.grid(row=2, column=1, padx=10, pady=10)

var_nur_ohne_web = tk.BooleanVar()
checkbox_ohne_web = tk.Checkbutton(root, text="Nur Einträge ohne Webseite", variable=var_nur_ohne_web)
checkbox_ohne_web.grid(row=3, columnspan=2, padx=10, pady=10)

btn_start = tk.Button(root, text="Suche starten", command=start_search)
btn_start.grid(row=4, column=0, padx=10, pady=10)

btn_stop = tk.Button(root, text="Suche stoppen", command=stop_search, state='disabled')
btn_stop.grid(row=4, column=1, padx=10, pady=10)

root.mainloop()
