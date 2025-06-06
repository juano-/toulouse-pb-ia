import pandas as pd
import psycopg2
import numpy as np
import ast

import os
from dotenv import load_dotenv

load_dotenv()

embedding_df2022 = pd.read_csv('../results/proj2022_embeddings_openai-3-large.csv')
embedding_df2022['embedding'] = embedding_df2022['embedding'].apply(ast.literal_eval)

embedding_df2024 = pd.read_csv('../results/proj2024_embeddings_openai-3-large.csv')
embedding_df2024['embedding'] = embedding_df2024['embedding'].apply(ast.literal_eval)

embedding_df = pd.concat([embedding_df2022, embedding_df2024]).reset_index(drop=True)
embedding_df['embedding'] = embedding_df['embedding'].apply(np.array)


conn = psycopg2.connect(
    host=os.environ["PG_HOST"],
    database=os.environ["PG_DATABASE"],
    user=os.environ["PG_USER"],
    password=os.environ['PG_PASSWORD']
)
cur = conn.cursor()

for idx, row in embedding_df.iterrows():
    project_id = row['project_id']
    embedding = row['embedding']

    embedding_list = embedding.tolist()

    cur.execute(
        "INSERT INTO openai_3_large_embeddings (project_id, embedding) VALUES (%s, %s)",
        (project_id, embedding_list)
    )

conn.commit()
cur.close()
conn.close()

print('embeddings loaded to database!')