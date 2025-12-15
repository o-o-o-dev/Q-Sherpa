import requests
import json

url = "http://127.0.0.1:8005/optimize"

payload = {
  "members": [
    {"id": 1, "name": "Sato", "grade": 3, "role": "CL", "gender": "M", "driver": True, "carrier": "au", "exp_years": 2.5},
    {"id": 2, "name": "Tanaka", "grade": 1, "role": "Equip", "gender": "F", "driver": False, "carrier": "docomo", "exp_years": 0.5},
    {"id": 3, "name": "Suzuki", "grade": 2, "role": "Food", "gender": "M", "driver": True, "carrier": "softbank", "exp_years": 1.5},
    {"id": 4, "name": "Yamada", "grade": 4, "role": "Medical", "gender": "F", "driver": False, "carrier": "au", "exp_years": 3.5}
  ],
  "equipments": [
    {"id": "t1", "name": "Montbell V6", "capacity": 6, "weight_kg": 4.5},
    {"id": "t2", "name": "AirRaiz 2", "capacity": 3, "weight_kg": 2.1}
  ],
  "num_teams": 2
}

headers = {
  'Content-Type': 'application/json'
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
