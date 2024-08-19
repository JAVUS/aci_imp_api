import requests

def generate_vlan_payload(row):
    if '-' in row["from-to"]:
        from_vlan, to_vlan = row["from-to"].split('-')
    else:
        from_vlan = to_vlan = row["from-to"]

    name = row["vlanname"]
    dn = f"uni/infra/vlanns-[{name}]-static"
    
    payload = {
        "fvnsVlanInstP": {
            "attributes": {
                "name": name,
                "dn": dn,
                "allocMode": row["type"]
            },
            "children": [
                {
                    "fvnsEncapBlk": {
                        "attributes": {
                            "dn": f"{dn}/from-[vlan-{from_vlan}]-to-[vlan-{to_vlan}]",
                            "from": f"vlan-{from_vlan}",
                            "to": f"vlan-{to_vlan}"
                        }
                    }
                }
            ]
        }
    }
    return payload

def send_vlan_payload_to_aci(payload, token, name, ip):
    url = f"https://{ip}/api/node/mo/uni/infra/vlanns-[{name}]-static.json"
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'APIC-cookie={token}'
    }
    
    response = requests.post(url, json=payload, headers=headers, verify=False)
    
    if response.status_code == 200:
        print(f'Payload para {name} enviado exitosamente')
    else:
        print(f'Error al enviar el payload para {name}:', response.status_code, response.text)
