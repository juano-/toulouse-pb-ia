import openai


def call_openai_model(prompt, api_key, model = "gpt-4-turbo", temperature=0.0, max_tokens=4000):

    client = openai.OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model= model,
        messages=[
            {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
            )    
    output_text = response.choices[0].message.content
    print("LLM response receive!")
    return output_text

def get_embeddings(text, api_key):
    
    client = openai.OpenAI(api_key=api_key) 
    
    response = client.embeddings.create(
        model="text-embedding-3-large", 
        input=text
    )
    return response.data[0].embedding



