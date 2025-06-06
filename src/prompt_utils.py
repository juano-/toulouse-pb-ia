import tiktoken

def tokens_counter(prompt: str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-4-turbo")
    return len(encoding.encode(prompt))


def prompt_cost(token_count: int, model: str) -> float:   
    model_prices = {
        "gpt-4-turbo": 0.01,
        "gpt-3.5-turbo": 0.003
    }
    price_per_1k = model_prices[model]
    return token_count * price_per_1k / 1000

