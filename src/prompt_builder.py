import pandas as pd
import src.rag as rag

def build_prompt(prompt_template_path, values):
    with open(prompt_template_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    prompt = prompt_template.format(**values)
    return prompt

def get_all_projects_from_22_election(df22_shuffled):
    projects_22_text = ""
    
    for _,row in df22_shuffled.iterrows():
        projects_22_text += f"- {row['project_name']}: (Coût: {row['cost']} €, District: {row['district']}). {row['votes']} Voix, Classement: {row['rank']}\n"
    
    return projects_22_text

def get_top_k_projects_from_22_election(df, k):
    projects_22_text = ""
     
    df22 = df[(df['year'] == 2022) & (df['rank']<=k)]
    df22 = df22.sort_values(by=['votes'], ascending=False)
     
    for _ , row in df22.iterrows():
        projects_22_text += f"- {row['project_name']}: (Coût: {row['cost']} €, District: {row['district']}). {row['votes']} Voix, Classement: {row['rank']}\n"
        
    return projects_22_text

def get_top_k_projects_from_16_election(df, k):
    projects_16_text = ""
     
    df16 = df[(df['year'] == 2016) & (df['rank']<=k)]
    df16 = df16.sort_values(by=['votes'], ascending=False)
     
    for _ , row in df16.iterrows():
        projects_16_text += f"- {row['project_name']}: (Cost: {row['cost']} €, District: {row['district']}). {row['votes']} Votes, Ranking: {row['rank']}\n"
        
    return projects_16_text

def get_project_count_and_avg_votes_by_district(df, city = 'Toulouse'):

    if city == 'Toulouse':
        
        df22 = df[(df['year'] == 2022)]
        
        foo = pd.merge(left = df22.groupby(['district'])['project_id'].count().reset_index(name='_count'),
                       right = df22.groupby(['district'])['votes'].mean().reset_index(name='_avg'),
                       on= 'district',
                       how = 'inner'
                       )

        district_projects_and_votes = ""

        for _ , row in foo.iterrows():
            district_projects_and_votes += f"{row['district']} : {row['_count']} projets, moyenne de voix {row['_avg']}.\n"

        return(district_projects_and_votes)
    
    if city == 'Wroclaw':
        
        df16 = df[(df['year'] == 2016)]
        
        foo = pd.merge(left = df16.groupby(['district'])['project_id'].count().reset_index(name='_count'),
                       right = df16.groupby(['district'])['votes'].mean().reset_index(name='_avg'),
                       on= 'district',
                       how = 'inner'
                       )
        
        district_projects_and_votes = ""

        for _ , row in foo.iterrows():
            district_projects_and_votes += f"{row['district']} : {row['_count']} Projects, Votes Average: {row['_avg']}.\n"
            
        return(district_projects_and_votes)


def get_project_count_and_avg_votes_by_categories(df, city = "Toulouse"):
    
    if city == "Toulouse":
        
        df22 = df[(df['year'] == 2022)]
        
        foo = pd.merge(left = df22.groupby('category')['project_id'].count().reset_index(name='_count'),
                       right =df22.groupby('category')['votes'].mean().reset_index(name='_avg'),
                       on= 'category',
                       how = 'inner')

        category_projects_and_votes = ""

        for _ , row in foo.iterrows():
            category_projects_and_votes += "{} : {} projets, moyenne de voix: {:.2f}\n".format(row['category'],row['_count'], row['_avg'])

        return category_projects_and_votes
    
    if city == "Wroclaw":
        
        df16 = df[(df['year'] == 2016)]
        
        foo = pd.merge(left = df16.groupby('category')['project_id'].count().reset_index(name='_count'),
                       right =df16.groupby('category')['votes'].mean().reset_index(name='_avg'),
                       on= 'category',
                       how = 'inner')

        category_projects_and_votes = ""

        for _ , row in foo.iterrows():
            category_projects_and_votes += "{} : {} projets, moyenne de voix: {:.2f}\n".format(row['category'],row['_count'], row['_avg'])

        return category_projects_and_votes


def get_count_of_projects_in_quartier(df, district, year=2022):
    return int(df[(df['district'] == district) & (df['year'] == year)]['project_id'].count())


def get_top_k_voted_in_district(df, district, k=3, year=2022):
    df22 = df[(df['year']==year) & (df['district'] == district)].sort_values(by=['votes'], ascending=False).iloc[0:k]
      
    projects_22_text=""

    for _ , row in df22.iterrows():
        projects_22_text += f"- {row['project_name'].strip()}: (Coût: {row['cost']} €). {row['votes']} Voix, Classement: {row['rank']}\n"
    
    return projects_22_text

def get_top_k_voted_in_district_eng(df, district, k=3, year=2016):
    df16 = df[(df['year']==year) & (df['district'] == district)].sort_values(by=['votes'], ascending=False).iloc[0:k]
      
    projects_16_text=""

    for _ , row in df16.iterrows():
        projects_16_text += f"- {row['project_name'].strip()}: (Cost: {row['cost']} €). {row['votes']} Votes, Ranking: {row['rank']}\n"
    
    return projects_16_text

def get_top_k_similar_projects_in_22(df, project_id, conn_params,k=5):
    
    emb = rag.get_embedding_by_project_id(project_id,conn_params)
    ids = [d[0] for d in rag.get_top_k_similar_projects_from_22(emb,conn_params, k+1) if d[0]!= project_id]

    df_aux = df[df.project_id.isin(ids)]

    projects_22_text=""
    for _,row in df_aux.iterrows():
        projects_22_text += f"- {row['project_name']}: (Coût: {row['cost']} €, District: {row['district']}). {row['votes']} Voix, Classement: {row['rank']}\n"
    
    return projects_22_text

def get_top_k_similar_projects_in_16(df, project_id, year, conn_params,k=5):

    emb = rag.get_embedding_by_project_id(project_id, conn_params, city="Wroclaw", year=year)
    ids = [d[0] for d in rag.get_top_k_similar_projects_from_16(emb, conn_params, k+1) if d[0]!= project_id]

    df_aux = df[df.project_id.isin(ids)]

    projects_text=""
    for _,row in df_aux.iterrows():
        projects_text += f"- {row['project_name']}: (Cost: {row['cost']} €, District: {row['district']}). {row['votes']} Votes, Ranking: {row['rank']}\n"

    return projects_text

def get_top_k_similar_projects_in_22_by_district(df, project_id, conn_params,k=5):
    district = df[df['project_id'] == project_id]['district_number'].iloc[0]
    emb = rag.get_embedding_by_project_id(project_id,conn_params)
    ids = [d[0] for d in rag.get_top_k_similar_projects_from_22_by_district(emb, district, conn_params, k+1) if d[0]!= project_id]

    df_aux = df[df.project_id.isin(ids)]

    projects_22_text=""
    for _,row in df_aux.iterrows():
        projects_22_text += f"- {row['project_name'].strip()}: (Coût: {row['cost']} €, District: {row['district']}). {row['votes']} Voix, Classement: {row['rank']}\n"

    return projects_22_text


def get_top_k_similar_projects_in_16_by_district(df, project_id, year, conn_params,k=5):
    district = df[df['project_id'] == project_id]['district'].iloc[0]
    emb = rag.get_embedding_by_project_id(project_id,conn_params, city="Wroclaw", year=year)
    ids = [d[0] for d in rag.get_top_k_similar_projects_from_16_by_district(emb, district, conn_params, k+1) if d[0]!= project_id]

    df_aux = df[df.project_id.isin(ids)]

    projects_16_text=""
    for _,row in df_aux.iterrows():
        projects_16_text += f"- {row['project_name'].strip()}: (Cost: {row['cost']} €, District: {row['district']}). {row['votes']} Votes, Ranking: {row['rank']}\n"

    return projects_16_text

