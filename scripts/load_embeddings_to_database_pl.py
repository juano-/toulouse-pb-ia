import ast 
import psycopg2

df_to_save  = pd.read_csv('output/proj16_and_17_pl_embeddings_openai-3-large.csv', sep=";")
df_to_save['embedding'] = df_to_save['embedding'].apply(ast.literal_eval)

conn = psycopg2.connect(
    host=os.environ["PG_HOST"],
    database=os.environ["PG_DATABASE"],
    user=os.environ["PG_USER"],
    password=os.environ['PG_PASSWORD']
)
cur = conn.cursor()

for idx, row in df_to_save.iterrows():
    project_id = row['project_id']
    year = row['year']
    embedding = row['embedding']

    #embedding_list = embedding.tolist()

    cur.execute(
        "INSERT INTO openai_3_large_embeddings_pl (project_id, year, embedding) VALUES (%s, %s, %s)",
        (project_id, year, embedding)
    )

conn.commit()
cur.close()
conn.close()

print('embeddings loaded to database!')