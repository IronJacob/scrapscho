import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time


def cerca_pubblicazioni_scholar(keywords, num_pagine):
    """
    Cerca su Google Scholar le pubblicazioni in open access.

    Args:
        keywords: Una lista di parole chiave o frasi.
        num_pagine: Il numero di pagine di risultati da esplorare.

    Returns:
        Una lista di dizionari, ognuno contenente informazioni su una pubblicazione.
    """

    # Configura il webdriver di Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Errore durante l'inizializzazione di ChromeDriver: {e}")
        return []

    # Unisci le parole chiave in una singola stringa di query
    query = ' '.join(keywords)

    # Costruisci l'URL di ricerca di Google Scholar (senza filtri per l'anno)
    url = f"https://scholar.google.com/scholar?q={query}&hl=it&as_sdt=0,5"
    driver.get(url)

    # Attendi che la pagina si carichi
    time.sleep(5)

    pubblicazioni = []
    pagina_corrente = 1  # Inizializza il contatore della pagina
    while pagina_corrente <= num_pagine:  # Ciclo fino al raggiungimento del numero di pagine desiderato
        soup = BeautifulSoup(driver.page_source, "html.parser")

        for risultato in soup.select('.gs_ri'):
            try:
                titolo = risultato.select_one('.gs_rt a').text
                autori = risultato.select_one('.gs_a').text
                link = risultato.select_one('.gs_rt a')['href']
                # Estrai l'anno dalla stringa degli autori
                anno = risultato.select_one('.gs_a').text.split()[-1]

                pubblicazioni.append({
                    "titolo": titolo,
                    "autori": autori,
                    "anno": anno,
                    "link": link
                })
            except:
                pass

        # Controlla se c'è un pulsante "Avanti" e se non abbiamo superato il numero di pagine desiderato
        next_button = driver.find_elements(By.XPATH, '//b[text()="Avanti"]')
        if next_button and pagina_corrente < num_pagine:
            # Clicca sul pulsante "Avanti" e attendi che la pagina si carichi
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//b[text()="Avanti"]'))).click()
            time.sleep(5)
            pagina_corrente += 1  # Incrementa il contatore della pagina
        else:
            break

    driver.quit()
    return pubblicazioni

def salva_in_csv(pubblicazioni, nome_file):
    """
    Salva le pubblicazioni in un file CSV.

    Args:
        pubblicazioni: Una lista di dizionari, ognuno contenente informazioni su una pubblicazione.
        nome_file: Il nome del file CSV.
    """

    with open(nome_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["titolo", "autori", "anno", "link"])
        writer.writeheader()
        writer.writerows(pubblicazioni)

# Interfaccia Streamlit
st.title("Ricerca Pubblicazioni su Google Scholar")

keywords_input = st.text_input("Inserisci le parole chiave separate da virgola: ")
keywords = [keyword.strip() for keyword in keywords_input.split(",")]

# Input utente per il numero di pagine
while True:
    try:
        num_pagine = int(st.number_input("Inserisci il numero di pagine da esplorare: "))
        break
    except ValueError:
        print("Input non valido. Inserisci un numero intero.")

if st.button("Cerca"):
    # Esegui la ricerca e salva i risultati
    pubblicazioni = cerca_pubblicazioni_scholar(keywords, num_pagine)
    salva_in_csv(pubblicazioni, "pubblicazioni_scholar.csv")

    st.write("Risultati:")
    st.table(pubblicazioni)

    with open("pubblicazioni_scholar.csv", "rb") as f:
        st.download_button("Scarica risultati in CSV", f, file_name="pubblicazioni_scholar.csv")
