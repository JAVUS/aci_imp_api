import requests
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning # type: ignore

# Función para autenticarse y obtener el token
def login_to_aci(url, username, password):
    payload = {"aaaUser": {"attributes": {"name": username, "pwd": password}}}
    headers = {'Content-Type': 'application/json'}
    
    warnings.filterwarnings('ignore', category=InsecureRequestWarning)
    
    response = requests.post(url, json=payload, headers=headers, verify=False)
    
    if response.status_code == 200:
        print('Login exitoso')
        return response.json()['imdata'][0]['aaaLogin']['attributes']['token']
    else:
        print('Error en el login:', response.status_code, response.text)
        return None