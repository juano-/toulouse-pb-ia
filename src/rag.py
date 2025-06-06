import psycopg2
import numpy as np
import ast

import os
from dotenv import load_dotenv
from data_loader import load_and_prepare_projects

"""
conn_params = {
"host": "your_host",
"database": "your_db",
"user": "tu_user",
"password": "tu_password"
}
"""

def get_embedding_by_project_id(project_id, conn_params):
    
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as c:
            c.execute("SELECT embedding FROM openai_3_large_embeddings WHERE project_id = %s", (project_id,))
            result = c.fetchone()
            if result:
                embedding_str = result[0]
                embedding_list = ast.literal_eval(embedding_str)
                return np.array(embedding_list, dtype=float)
            else:
                raise ValueError(f"Project ID {project_id} not found.")


def get_top_k_similar_projects(embedding, conn_params, k=10):
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            query = f"""
                SELECT project_id, embedding <#> %s AS distance
                FROM openai_3_large_embeddings
                ORDER BY embedding <#> %s
                LIMIT %s
            """
            cur.execute(query, (embedding_str, embedding_str, k+1))
            results = cur.fetchall()
            return results  


def get_top_k_similar_projects_from_22(embedding, conn_params, k=5):
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            query = f"""
                SELECT e.project_id, e.embedding <#> %s AS distance
                FROM openai_3_large_embeddings e, projects p
                WHERE p.project_id = e.project_id
                AND p.year=2022
                ORDER BY e.embedding <#> %s
                LIMIT %s
            """
            cur.execute(query, (embedding_str, embedding_str, k))
            results = cur.fetchall()
            return results  
        
def get_top_k_similar_projects_from_22_by_district(embedding, district, conn_params, k=5):
    embedding_str = '[' + ','.join(map(str, embedding)) + ']'

    query = """
        SELECT e.project_id, e.embedding <#> %s AS distance
        FROM openai_3_large_embeddings e
        INNER JOIN projects p ON p.project_id = e.project_id
        WHERE p.year = 2022
        AND p.district = %s
        ORDER BY e.embedding <#> %s
        LIMIT %s
    """

    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (embedding_str, district, embedding_str, k))
            results = cur.fetchall()

    return results
        
if __name__ == '__main__':
    ## this script test rag functions and cosine similarities.
    load_dotenv()

    conn = {
        "host": os.environ["PG_HOST"],
        "database": os.environ["PG_DATABASE"],
        "user": os.environ["PG_USER"],
        "password": os.environ['PG_PASSWORD']
    }

    p_id = 245
    path_22 = '../data/projects2022.csv'
    path_24 = '../data/projects2024.csv'

    df, _ = load_and_prepare_projects(path_22, path_24)
    
    vec = get_embedding_by_project_id(p_id, conn)
    
    print(vec)
    vec = get_embedding_by_project_id(p_id, conn)
    top = get_top_k_similar_projects(vec, conn, k=10)

    similar_projects = df[df.project_id.isin([p[0] for p in top])]
    print(similar_projects)
    #print(f"ID: {similar_projects[similar_projects.project_id == p_id].project_id[0]}, {similar_projects[similar_projects.project_id == p_id].project_name[0]}")

    #print("")
    #print('similar projects:',[p[0] for p in top])
    #print('cosine distance:',[p[1] for p in top])

    #for i, r in similar_projects.iterrows():
    #if r['project_id']!=245:
    #    print(f"ID: {r['project_id']},", f"{r['project_name']}.", f"Votes: {r['votes']}.")



