from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from datetime import datetime
import re  # Assurez-vous d'importer le module re

# Configuration du WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://www.windguru.cz/48617"
driver.get(url)
time.sleep(5)  # Pause pour le chargement de la page

try:
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "tabid_1_0_dates")))

    # Extraction des dates
    dates_elements = driver.find_elements(By.CSS_SELECTOR, "#tabid_1_0_dates td")
    dates = [e.text.strip() for e in dates_elements if e.text.strip()]

    # Traitement des dates
    cleaned_dates = []
    for date in dates:
        match = re.search(r'(\d{1,2})\.\n(\d{1,2})h', date)
        if match:
            cleaned_date = f"{match.group(1)}. {datetime.today().strftime('%m')}."
            cleaned_dates.append(cleaned_date)

    today_str = datetime.today().strftime("%d. %m.")
    indices_today = [i for i, date in enumerate(cleaned_dates) if today_str in date]

    if not indices_today:
        print("Pas de données disponibles pour aujourd'hui.")
    else:
        # Extraction des autres informations
        wind_speeds = [e.text.strip() for e in driver.find_elements(By.CSS_SELECTOR, "#tabid_1_0_WINDSPD td")]
        wind_gusts = [e.text.strip() for e in driver.find_elements(By.CSS_SELECTOR, "#tabid_1_0_GUST td")]
        wind_directions = [e.get_attribute("title") for e in driver.find_elements(By.CSS_SELECTOR, "#tabid_1_0_SMER td span")]

        # Sélectionner les indices pour aujourd'hui
        selected_indices = [indices_today[0], indices_today[len(indices_today) // 2], indices_today[-1]]

        # Extraction des valeurs correspondantes
        selected_data = {
            "Date": [dates[i] for i in selected_indices],
            "Vitesse du Vent (nœuds)": [wind_speeds[i] for i in selected_indices],
            "Rafales (nœuds)": [wind_gusts[i] for i in selected_indices],
            "Direction du Vent": [wind_directions[i] for i in selected_indices]
        }

        # Exporter les données dans un fichier Excel
        df = pd.DataFrame(selected_data)
        df.to_excel("wind_data_today.xlsx", index=False)
        print("Données exportées avec succès.")

except Exception as e:
    print(f"Une erreur est survenue : {str(e)}")
finally:
    driver.quit()
