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

# Input
path_22 = base_dir / 'data' / 'TLS22-idvotant-idproject.csv'
path_24 = base_dir / 'data' / 'TLS24-idvotant-idproject.csv'

# Output
output_dir = base_dir / 'scripts' / 'scrapper' / 'tls-html'
output_dir.mkdir(parents=True, exist_ok=True)

# Data Load
from data_loader import load_and_prepare_voting_detail

df22, df24 = load_and_prepare_voting_detail(path_22, path_24)
df = pd.concat([df22, df24]).reset_index(drop=True)

project_urls = df.groupby('project_id')['project_url'].max()

# HTML Loader
for project_id, url in project_urls.items():
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        continue

    soup = BeautifulSoup(response.text, 'html.parser')
    html_content = soup.find('html')

    if html_content:
        output_file = output_dir / f'project_id_{project_id}.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            print(f'✅ Saved: {output_file}')
            f.write(str(html_content))
    else:
        print(f"⚠️ No HTML content found in {url}")
