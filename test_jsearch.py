import requests

api_key = "eecba37741msh8aab8cab5e05f9ep185a20jsn9877c391a7b3"  # Replace with your actual key

headers = {
    'X-RapidAPI-Key': api_key,
    'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
}

url = "https://jsearch.p.rapidapi.com/search"
params = {
    'query': 'Python developer',
    'page': '1',
    'num_pages': '1'
}

try:
    response = requests.get(url, headers=headers, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")