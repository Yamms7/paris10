from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from pyzbar.pyzbar import decode
import os
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Vérifier si le dossier 'uploads' existe, sinon le créer
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    if 'file' not in request.files:
        return "Aucun fichier chargé"

    file = request.files['file']
    if file.filename == '':
        return "Aucun fichier sélectionné"

    # Enregistrer le fichier téléchargé
    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)

    # Scanner le QR code
    try:
        img = Image.open(filepath)
        qr_data = decode(img)
    except Exception as e:
        return f"Erreur lors de l'ouverture de l'image: {str(e)}"

    if not qr_data:
        return "Aucun QR code trouvé"

    qr_url = qr_data[0].data.decode('utf-8')

    # Configurer Selenium
    driver = webdriver.Chrome()  # Assurez-vous que le chemin vers ChromeDriver est dans votre PATH
    driver.get(qr_url)

    try:
        # Attendre jusqu'à ce que le champ soit présent et visible dans le DOM
        username_field = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.NAME, "UserName"))  # Ajustez ce sélecteur si nécessaire
        )
        password_field = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.NAME, "Password"))  # Ajustez ce sélecteur si nécessaire
        )

        # Remplir le formulaire
        username_field.send_keys("bennanis2")  # Remplacez par votre identifiant
        password_field.send_keys("Parisparis25")  # Remplacez par votre mot de passe
        
        # Soumettre le formulaire
        password_field.send_keys(Keys.RETURN)
        time.sleep(3)  # Attendre pour observer la connexion

        return f"QR code décodé: {qr_data[0].data.decode('utf-8')} et connexion tentée."
    except Exception as e:
        return f"Erreur lors de la recherche des éléments: {str(e)}"
    finally:
        driver.quit()  # Fermer le navigateur à la fin
        os.remove(filepath)  # Supprimer le fichier téléchargé après utilisation

if __name__ == '__main__':
    app.run(debug=True)
