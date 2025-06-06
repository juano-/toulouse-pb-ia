import openai

#api_key=os.getenv('OPENAI_API_KEY') 

def call_openai_model(prompt, api_key, model = "gpt-4-turbo", temperature=0.4, max_tokens=4000):

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
    return output_text



