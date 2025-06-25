import pandas as pd
import sys
import requests

from bs4 import BeautifulSoup
from pathlib import Path

# Path cfg.
try:
    base_dir = Path(__file__).resolve().parents[2]
except NameError:
    base_dir = Path().resolve()

src_path = base_dir / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


## projects finder.
project_id = 3
url = f'https://www.wroclaw.pl/budzet-obywatelski-wroclaw/projekty-2016/szukaj,id,{project_id},name,,rejon,,kategoria,,prog,,selected,2'
response = requests.get(url)

if response.status_code == 200:
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    print("HTML obtenido y parseado con éxito.")
    print(soup.title.string)
else:
    print(f"Error al acceder a la página. Código: {response.status_code}")

# Buscar todos los <a> con clase lnkTitle dentro de cada proyecto
links = [a["href"] for a in soup.find_all("a", class_="lnkTitle") if a.has_attr("href")]

for link in links:
    print(link)