import pandas as pd
import re

def load_and_prepare_projects(path_2022, path_2024):
    
    df22 = pd.read_csv(path_2022, sep=";")
    df24 = pd.read_csv(path_2024, sep=";")

    df22['district_number'] = df22['district'].apply(lambda x: get_district_number(x))
    df24['district_number'] = df24['district'].apply(lambda x: get_district_number(x))

    df22 = df22.sort_values(by='votes', ascending=False).reset_index(drop=True)
    df22['rank'] = df22.index + 1
    df24 = df24.sort_values(by='votes', ascending=False).reset_index(drop=True)
    df24['rank'] = df24.index + 1

    df22['year'] = 2022
    df24['year'] = 2024

    df22_shuffled = df22.sample(frac=1, random_state=42).reset_index(drop=True)

    df24['description'] = df24['description'].apply(clean_2024_description)

    df = pd.concat([df22, df24]).reset_index(drop=True)

    return df, df22_shuffled

def load_and_prepare_voting_detail(path_2022, path_2024):
    
    origin_c = ['ID', 'project_id', 'project_title','created_at','checked_out_at','project_url','vote_finished']
    rename_c = ['voter_id','project_id','project_title','created_at','checked_out_at','project_url','vote_finished']

    df22 = pd.read_csv(path_2022, sep=";").filter(origin_c)
    df22.columns = rename_c

    df22 = df22[df22['vote_finished'] == True]
    df22['project_id'] = df22.project_id.astype('int')
    df22['date'] = df22['checked_out_at'].apply(pd.to_datetime).dt.date


    origin_c = ['Decidim User ID', 'Project ID', 'Project Title', 'Created At', 'Checked Out At', 'Project URL', 'Vote Finished']
    rename_c = ['voter_id','project_id','project_title','created_at','checked_out_at','project_url','vote_finished']

    df24 = pd.read_csv(path_2024, sep=";").filter(origin_c)
    df24.columns = rename_c

    df24['project_id'] = df24.project_id.astype('int')
    df24['date'] = df24['checked_out_at'].apply(pd.to_datetime).dt.date
    
    return df22, df24


def clean_2024_description(text):
    patron = r"^.*L'IDÉE EXPRIMÉE PAR @\S+(?:\s*:\s*)?"
    new_text = re.sub(patron, '', text)
    return new_text.strip()

def get_district_number(district_name):
    return district_name.split("-")[0].strip()

def load_prediction_set(df, ids_path, rows=37):

    ids_df = pd.read_csv(ids_path, sep=";")

    filtered = pd.merge(
        left=df,
        right=ids_df,
        on='project_id',
        how='inner'
    ).filter(['project_id', 'project_name', 'description', 'cost', 'district', 'votes', 'rank'])
    
    filtered.rename(
        columns={'votes': 'real_votes', 'rank': 'real_rank'},
        inplace=True
    )

    filtered = filtered.iloc[0:rows,]

    return filtered



if __name__ == "__main__":

    path_22 = '../data/projects2022.csv'
    path_24 = '../data/projects2024.csv'
    
    df, _ = load_and_prepare_projects(path_22,path_24)
    print('projects loaded:')
    print(df.groupby(['year']).count()['project_id'])