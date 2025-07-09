import pandas as pd
import numpy as np
import sys
import os

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


def get_project_data(filepath):
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')

    project_id = int(filepath.split("/")[-1].split("_")[2].replace(".html",""))
    project_title = soup.find('h2', class_='heading2')
    project_description = soup.find('div', class_='ql-editor-display')    

    divs_m_botton = soup.find_all('div', class_='m-bottom')

    project_budget = None
    for div in divs_m_botton:
        title_span = div.find('span', class_='definition-data__title')
        if title_span and title_span.text.strip() == 'Budget':
            project_budget = div
            break

    project_votes = soup.find('span', class_='project-votes display-block')

    ul_project_tags = soup.find('ul', class_='tags tags--project')

    if ul_project_tags:
        li_project_tags = ul_project_tags.find_all('li')
        category = li_project_tags[0].find_all('span')
        location = li_project_tags[1].find_all('span')
    else:
        category = None
        location = None

    project = {}
    
    if project_id:
        project['project_id'] = project_id

    if project_title:
        project["project_name"] = project_title.text
    
    if project_description:
        project["description"] = project_description.text

    if project_budget:
        project_budget = project_budget.text.strip().replace("Budget\n","")
        project_budget = float(project_budget.replace('€', '').replace(' ', ''))
        project['cost'] = project_budget
    
    if project_votes:
        project['votes'] = project_votes.text.replace(" votes", "")

    if category:
        project['category'] = category[1].text

    if location:
        project['district'] = location[1].text
    
    return project


if __name__ == '__main__':

    html_folder = base_dir / 'scripts/scrapper/tls-html/'
    data = [os.path.join(html_folder, f) for f in os.listdir(html_folder) if os.path.isfile(os.path.join(html_folder, f))]

    l = []
    for path in data:
        l.append(get_project_data(path))
    
    df = pd.DataFrame(l)
    print(df)




    