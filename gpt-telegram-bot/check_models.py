# English code/comments
from google import genai

# Replace with your actual API Key
API_KEY = "AIzaSyAYgUklHs97lCCNb7UIiLaDLvKhCcbB3Ck" 

try:
    client = genai.Client(api_key=API_KEY)
    
    print("--- Fetching supported models from your API key ---")
    
    # List all available models and their exact names
    available_models = []
    for m in client.models.list():
        # Clean the name (sometimes it comes as 'models/gemini-1.5-flash')
        clean_name = m.name.split('/')[-1]
        available_models.append(clean_name)
        print(f"✅ Found: {clean_name} (Full path: {m.name})")

    if not available_models:
        print("❌ No models found for this API key. Check Google AI Studio permissions.")
    else:
        # Try to call the first available model from the list
        test_model = available_models[0]
        print(f"\n--- Testing first available model: {test_model} ---")
        
        response = client.models.generate_content(
            model=test_model,
            contents="Hi, confirm you are working!"
        )
        print(f"🚀 SUCCESS! Response: {response.text}")

except Exception as e:
    print(f"❌ Critical Error: {e}")
