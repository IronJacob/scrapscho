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

    # Configura il webdriver di Selenium (usa opzioni headless per evitare che il browser si apra)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Errore durante l'inizializzazione di ChromeDriver: {e}")
        return []  # Restituisci una lista vuota in caso di errore

    # Unisci le parole chiave in una singola stringa di query
    query = ' '.join(keywords)

    # Costruisci l'URL di ricerca di Google Scholar (senza filtri per l'anno)
    url = f"https://scholar.google.com/scholar?q={query}&hl=it&as_sdt=0,5" 
    driver.get(url)

    # Attendi che la pagina si carichi
    time.sleep(5)

    pubblicazioni = []
    pagina_corrente = 1
    while pagina_corrente <= num_pagine:
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
            pagina_corrente += 1
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

keywords_input = st.text_input("Inserisci le parole chiave separate da virgola:")
keywords = [keyword.strip() for keyword in keywords_input.split(",") if keyword.strip()]

num_pagine = st.number_input("Inserisci il numero di pagine da esplorare:", min_value=1, value=10)

if st.button("Cerca"):
    if keywords:
        pubblicazioni = cerca_pubblicazioni_scholar(keywords, num_pagine)

        # Mostra i risultati in una tabella
        st.write("Risultati:")
        st.table(pubblicazioni)

        # Crea un pulsante per scaricare il file CSV
        salva_in_csv(pubblicazioni, "pubblicazioni_scholar.csv")
        with open("pubblicazioni_scholar.csv", "rb") as f:
            st.download_button("Scarica risultati in CSV", f, file_name="pubblicazioni_scholar.csv")
    else:
        st.warning("Inserisci almeno una parola chiave.")
