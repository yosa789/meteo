from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re  # Pour utiliser les expressions régulières

# Configuration du navigateur (non-headless pour voir ce qu'il fait)
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Lancer en pleine taille

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# URL cible
url = "https://www.windguru.cz/48617"
driver.get(url)

try:
    # Pause pour laisser le JavaScript charger
    time.sleep(5)  # Augmentez si les données prennent du temps à charger

    # Vérification de la présence d'un élément du tableau
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tr[id^='tabid_1_0_']"))
    )

    # Capture de la source HTML
    page_source = driver.page_source

    # Sauvegarde de la page HTML pour analyse
    html_file = "windguru_page_source.html"
    with open(html_file, "w", encoding="utf-8") as file:
        file.write(page_source)

    print(f"Source HTML enregistrée dans {html_file}.")
    print("Ouvrez ce fichier dans un navigateur et inspectez les sélecteurs.")

except Exception as e:
    print(f"Une erreur est survenue : {str(e)}")

try:
    # Attente que les éléments du tableau soient présents
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "tabid_1_0_dates"))
    )

    # Extraction des dates (prendre seulement les 3 premières valeurs)
    dates_elements = driver.find_elements(By.CSS_SELECTOR, "#tabid_1_0_dates td")
    dates = [date.text.strip() for date in dates_elements if date.text.strip()]  # Prendre les premières valeurs
    dates = dates[:3]  # Limiter à 3

    if not dates:
        print("Aucune date trouvée.")

    # Extraction des vitesses du vent (prendre seulement les 3 premières valeurs en texte)
    wind_speed_elements = driver.find_elements(By.CSS_SELECTOR, "#tabid_1_0_WINDSPD td")
    wind_speeds = [speed.text.strip() for speed in wind_speed_elements if speed.text.strip()]  # 3 premières valeurs
    wind_speeds = wind_speeds[:3]  # Limiter à 3

    if not wind_speeds:
        print("Aucune vitesse de vent trouvée.")

    # Extraction de la direction du vent (prendre seulement les 3 premières valeurs)
    wind_direction_elements = driver.find_elements(By.CSS_SELECTOR, "#tabid_1_0_SMER td span")
    wind_directions = []
    for direction in wind_direction_elements:
        # Extraction du nombre (degré) de la direction à partir de l'attribut 'title'
        match = re.search(r"\((\d+)°\)", direction.get_attribute("title"))
        if match:
            wind_directions.append(match.group(1))  # Ajouter la valeur numérique du degré
    wind_directions = wind_directions[:3]  # Limiter à 3

    if not wind_directions:
        print("Aucune direction du vent trouvée.")

    # Vérification des résultats
    if dates and wind_speeds and wind_directions:
        print("Les 3 premières données extraites :")
        for i in range(3):
            print(f"Date : {dates[i]}")
            print(f"Vitesse du Vent : {wind_speeds[i]} nœuds")
            print(f"Direction du Vent : {wind_directions[i]}°")

        # Création d'un DataFrame Pandas pour exporter les données
        data = {
            "Date": dates,
            "Vitesse du Vent (nœuds)": wind_speeds,
            "Direction du Vent (degrés)": wind_directions
        }
        df = pd.DataFrame(data)

        # Export des données vers un fichier Excel
        excel_file = "wind_data_3.xlsx"
        df.to_excel(excel_file, index=False)
        print(f"Données exportées avec succès vers {excel_file}")
    else:
        print("Certaines données sont manquantes.")

except Exception as e:
    print(f"Une erreur est survenue : {str(e)}")
finally:
    driver.quit()