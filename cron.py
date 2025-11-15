import requests

def ping():
    try:
        url = "https://convertify-3jxm.onrender.com/"
        r = requests.get(url, timeout=10)
        print(f"Status: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")


ping()
