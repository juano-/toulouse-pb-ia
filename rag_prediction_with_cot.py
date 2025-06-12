# 1. load data
import os
import pandas as pd
import src.utils as ut
import prompt_builder as pb

from dotenv import load_dotenv
from src.data_loader import load_and_prepare_projects, load_prediction_set
from prompt_utils import tokens_counter, prompt_cost


path_22 = 'data/projects2022.csv'
path_24 = 'data/projects2024.csv'

df, df22_shuffled = load_and_prepare_projects(path_22,path_24)

ids_to_predict_path = 'data/projects_to_predict_2024.csv'
test = load_prediction_set(df, ids_to_predict_path)

load_dotenv()

conn_params = {
    "host": os.environ["PG_HOST"],
    "database": os.environ["PG_DATABASE"],
    "user": os.environ["PG_USER"],
    "password": os.environ['PG_PASSWORD']
}

#2. build prompt
top_k_voted_22 = pb.get_top_k_projects_from_22_election(df, k=15)
proj_count_avg_by_district= pb.get_project_count_and_avg_votes_by_district(df)
proj_count_avg_by_categories = pb.get_project_count_and_avg_votes_by_categories(df)

test['prompt'] = test.apply(
    lambda x: pb.build_prompt(
        '../prompts/prompt_rag2_CoT.txt',
        {
            'top_k_voted_22': top_k_voted_22,
            'project_count_and_avg_votes_by_district': proj_count_avg_by_district,
            'project_name': x['project_name'],
            'cost': x['cost'],
            'district': x['district'],
            'description': x['description'],
            'top_k_similar_projects_in_22': pb.get_top_k_similar_projects_in_22(df,x['project_id'],conn_params, k=10),
            'count_of_projects22_in_quartier': pb.get_count_of_projects_in_quartier(df,x['district']),
            'top_k_voted_in_district': pb.get_top_k_voted_in_district(df, x['district'], k=5),
            'count_of_projects24_in_quartier': pb.get_count_of_projects_in_quartier(df,x['district'], year=2024),
            'top_k_similar_projects_in_district': pb.get_top_k_similar_projects_in_22_by_district(df, x['project_id'], conn_params,k=5)
        }
    ),
    axis=1
)

test['n_tokens'] = test['prompt'].apply(lambda p: tokens_counter(p))
test['cost_usd'] = test['n_tokens'].apply(lambda n_tokens: prompt_cost(n_tokens, 'gpt-4-turbo'))

print('mean tokens by prompt: {:.2f}'.format(test.n_tokens.mean()))
print('avg.cost of each prediction: ${:.2f}'.format(test.cost_usd.mean()))
print('experiment total cost: {:.2f}'.format(test.cost_usd.sum()))

#3. run experiment! :)
api_key=os.getenv('OPENAI_API_KEY')
from llm_client import call_openai_model 

test['out'] = test['prompt'].apply(lambda prompt: 
                     call_openai_model(prompt=prompt, api_key=api_key))


test['out_json'] = test['out'].apply(
    lambda o: ut.get_json_from_llm_response(o))

test['predicted_votes'] = test['out_json'].apply(lambda x: ut.get_predicted_votes(x))
test['predicted_rank'] = test['out_json'].apply(lambda x: ut.get_predicted_rank(x))
test['is_top5'] = test['out_json'].apply(lambda x: ut.get_if_is_top5(x))
test['is_top10'] = test['out_json'].apply(lambda x: ut.get_if_is_top10(x))


#4. save results.
results = test.filter(['project_id', 
             'real_votes', 
             'real_rank',
             'prompt',
             'out',
             'out_json', 
             'predicted_votes', 
             'predicted_rank', 
             'is_top5', 
             'is_top10']
             )

results.to_csv('output/predictions/rag_cot1.csv', sep=";", index=False)
print('results ready!')