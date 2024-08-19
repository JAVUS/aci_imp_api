import requests

def generate_domain_payload(row):
    print(f"Procesando fila: {row}")
    
    name = row["domname"]  # Nombre del dominio (columna H2)
    domain_type = row["domtype"]  # Tipo de dominio (columna I2)
    vlan_pool_type = row["vlantype"]  # Tipo de VLAN pool (columna J2)
    vlan_pool_name = row["vlanname"]  # Nombre del VLAN pool (columna K2)
    
    tDn = f"uni/infra/vlanns-[{vlan_pool_name}]-{vlan_pool_type}"  # Construir el tDn correctamente
    dn = f"uni/{domain_type}-[{name}]"  # Construir el dn del dominio
    
    payload = {
        "physDomP": {
            "attributes": {
                "dn": dn,
                "name": name
            },
            "children": [
                {
                    "infraRsVlanNs": {
                        "attributes": {
                            "tDn": tDn
                        }
                    }
                }
            ]
        }
    }
    
    return payload

def send_domain_payload_to_aci(payload, token, name, domain_type, ip):
    url = f"https://{ip}/api/node/mo/uni/{domain_type}-[{name}].json"
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'APIC-cookie={token}'
    }
    
    response = requests.post(url, json=payload, headers=headers, verify=False)
    
    if response.status_code == 200:
        print(f'Payload para el dominio {name} enviado exitosamente')
    else:
        print(f'Error al enviar el payload para el dominio {name}:', response.status_code, response.text)
