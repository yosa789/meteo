from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re  # Pour utiliser les expressions régulières

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

url = "https://www.windguru.cz/48617"
driver.get(url)

time.sleep(5)  # Pause pour le chargement de la page

try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "tabid_1_0_dates"))
    )


    def extract_relevant_values(elements):
        values = [e.text.strip() if hasattr(e, 'text') else str(e).strip() for e in elements if str(e).strip()]
        if values:
            first = values[0]
            last = values[-1]
            middle_index = len(values) // 2  # Trouver l'index du milieu
            middle = values[middle_index]
            return [first, middle, last]
        return []


    # Extraction des dates
    dates_elements = driver.find_elements(By.CSS_SELECTOR, "#tabid_1_0_dates td")
    dates = extract_relevant_values(dates_elements)

    # Extraction des vitesses du vent
    wind_speed_elements = driver.find_elements(By.CSS_SELECTOR, "#tabid_1_0_WINDSPD td")
    wind_speeds = extract_relevant_values(wind_speed_elements)

    # Extraction de la direction du vent
    wind_direction_elements = driver.find_elements(By.CSS_SELECTOR, "#tabid_1_0_SMER td span")
    wind_directions = []
    for direction in wind_direction_elements:
        match = re.search(r"\((\d+)°\)", direction.get_attribute("title"))
        if match:
            wind_directions.append(match.group(1))
    wind_directions = extract_relevant_values(wind_directions)

    if dates and wind_speeds and wind_directions:
        for i in range(3):
            print(f"Date : {dates[i]}")
            print(f"Vitesse du Vent : {wind_speeds[i]} nœuds")
            print(f"Direction du Vent : {wind_directions[i]}°")

        df = pd.DataFrame({
            "Date": dates,
            "Vitesse du Vent (nœuds)": wind_speeds,
            "Direction du Vent (degrés)": wind_directions
        })

        df.to_excel("wind_data_filtered.xlsx", index=False)
        print("Données exportées avec succès.")
    else:
        print("Certaines données sont manquantes.")

except Exception as e:
    print(f"Une erreur est survenue : {str(e)}")
finally:
    driver.quit()
