from src.analysis.grok_client import get_client, GROK_MODEL

if __name__ == "__main__":
    client = get_client()

    response = client.responses.create(
        model=GROK_MODEL,
        input=[
            {"role": "system", "content": "You are a financial news analyst."},
            {"role": "user", "content": "In one sentence, what does the Federal Reserve do?"},
        ],
    )

    print(response.output_text)