import requests

def generate_aaep_payload(row):
    print(f"Procesando fila: {row}")
    
    name = row["aaepname"]  # Nombre del AAEP (columna N2)
    domain_type = row["domtype"]  # Tipo de dominio (columna O2)
    domain_name = row["domain"]  # Nombre del dominio (columna P2)
    
    tDn = f"uni/{domain_type}-{domain_name}"  # Construir el tDn correctamente
    
    payload = {
        "infraAttEntityP": {
            "attributes": {
                "name": name
            },
            "children": [
                {
                    "infraRsDomP": {
                        "attributes": {
                            "tDn": tDn
                        }
                    }
                }
            ]
        }
    }
    
    return payload

def send_aaep_payload_to_aci(payload, token, name, ip):
    url = f"https://{ip}/api/node/mo/uni/infra/attentp-{name}.json"
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'APIC-cookie={token}'
    }
    
    response = requests.post(url, json=payload, headers=headers, verify=False)
    
    if response.status_code == 200:
        print(f'Payload para el AAEP {name} enviado exitosamente')
    else:
        print(f'Error al enviar el payload para el AAEP {name}:', response.status_code, response.text)
