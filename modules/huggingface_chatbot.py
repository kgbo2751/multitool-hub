import os
from huggingface_hub import InferenceClient

def get_hf_response(messages):
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return "API KEY가 설정되지 않았습니다."
        
    client = InferenceClient(api_key=api_key, provider="novita")
    try:
        response = client.chat_completion(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=messages,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"오류 발생: {str(e)}"