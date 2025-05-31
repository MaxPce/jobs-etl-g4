import requests
from bs4 import BeautifulSoup
from linkedin_api import Linkedin
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'db_g4'
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    )
}

COOKIES = {
}

def conectar_bd():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empleos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(255),
            empresa VARCHAR(255),
            ubicacion VARCHAR(255),
            descripcion LONGTEXT,
            enlace TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    return conn, cursor

def obtener_detalles_empleo(url):
    response = requests.get(url, headers=HEADERS, cookies=COOKIES)
    if response.status_code != 200:
        return "N/A", "N/A", "N/A"

    soup = BeautifulSoup(response.text, 'html.parser')

    descripcion = (soup.find('div', class_='description__text') or
                   soup.find('div', class_='show-more-less-html__markup'))
    empresa = soup.find('a', class_='topcard__org-name-link') or soup.find('span', class_='topcard__flavor')
    ubicacion = soup.find('span', class_='topcard__flavor topcard__flavor--bullet')

    return (
        descripcion.get_text(strip=True) if descripcion else "Descripción no encontrada",
        empresa.get_text(strip=True) if empresa else "Empresa no encontrada",
        ubicacion.get_text(strip=True) if ubicacion else "Ubicación no encontrada"
    )

def guardar_empleo(cursor, conn, titulo, empresa, ubicacion, descripcion, url):
    cursor.execute('''
        INSERT INTO empleos (titulo, empresa, ubicacion, descripcion, enlace)
        VALUES (%s, %s, %s, %s, %s)
    ''', (titulo, empresa, ubicacion, descripcion, url))
    conn.commit()

def main():
    api = Linkedin('poncemax502@gmail.com', 'azulmorado')
    jobs = api.search_jobs(keywords='python developer', limit=5)

    conn, cursor = conectar_bd()

    for job in jobs:
        titulo = job.get('title') or 'Sin título'
        entity_urn = job.get('entityUrn', '')
        job_id = entity_urn.split(':')[-1] if entity_urn else ''
        url = f"https://www.linkedin.com/jobs/view/{job_id}"

        descripcion, empresa, ubicacion = obtener_detalles_empleo(url)

        guardar_empleo(cursor, conn, titulo, empresa, ubicacion, descripcion, url)
        print(f"{titulo} | {empresa} | {ubicacion}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
