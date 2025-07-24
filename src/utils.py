
import re
import json

def get_json_from_llm_response(out):
    match = re.search(r"```json\s*({.*?})\s*```", out, re.DOTALL)
    if match:
        json_str = match.group(1)
        data = json.loads(json_str)
        return data
    else:
        return "No JSON in LLM answer..."
    
def get_predicted_votes(df, out_json, city = 'Toulouse'):
    
    if city != 'Toulouse':
        raise ValueError(f"City '{city}' not supported")

    if isinstance(out_json, str):
        try:
            out_json = json.loads(out_json)
        except json.JSONDecodeError:
            return None
    
    votes_2022 = df[df['year'] == 2022].votes.sum()
    votes_2024 = df[df['year'] == 2024].votes.sum()

    relative_estimation = out_json['voix_estimées'] / votes_2022
    adjusted_prediction = relative_estimation * votes_2024

    return adjusted_prediction
    
def get_predicted_rank(out_json):
    
    if isinstance(out_json, str):
        try:
            out_json = json.loads(out_json)
        except json.JSONDecodeError:
            return None
        
    return out_json['position_attendue']

def get_if_is_top5(out_json):

    if isinstance(out_json, str):
        try:
            out_json = json.loads(out_json)
        except json.JSONDecodeError:
            return None
        
    return out_json['dans_top_5']

def get_if_is_top10(out_json):

    if isinstance(out_json, str):
        try:
            out_json = json.loads(out_json)
        except json.JSONDecodeError:
            return None
        
    return out_json['dans_top_10']
