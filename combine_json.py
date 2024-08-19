import json

def load_combined_json(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error al cargar el archivo JSON: {e}")
        return []

def create_structure_level(level_name, attributes, children):
    return {
        level_name: {
            "attributes": attributes,
            "children": children
        }
    }

def merge_vlan_objects(json_list):
    merged_dict = {}
    previous_vlan = None
    
    for obj in json_list:
        vlan_inst = obj.get("fvnsVlanInstP")
        if vlan_inst:
            name = vlan_inst["attributes"]["name"]
            if name == previous_vlan:
                # Agregar los rangos adicionales a la misma VLAN si se encuentra en filas consecutivas
                merged_dict[name]["children"].extend(vlan_inst["children"])
            else:
                # Crear una nueva entrada para la VLAN si es una nueva fila
                if name not in merged_dict:
                    merged_dict[name] = vlan_inst
                else:
                    existing_children = {
                        child["attributes"]["dn"] 
                        for child in merged_dict[name]["children"]
                        if "attributes" in child and "dn" in child["attributes"]
                    }
                    for child in vlan_inst["children"]:
                        if "attributes" in child and child["attributes"]["dn"] not in existing_children:
                            merged_dict[name]["children"].append(child)
            previous_vlan = name

    return [{"fvnsVlanInstP": value} for value in merged_dict.values()]

def merge_domain_objects(json_list):
    merged_dict = {}
    for obj in json_list:
        if "physDomP" in obj:
            domain_name = obj["physDomP"]["attributes"]["name"]
            if domain_name not in merged_dict:
                merged_dict[domain_name] = obj["physDomP"]
            else:
                existing_tDns = {
                    child["attributes"]["tDn"]
                    for child in merged_dict[domain_name]["children"]
                    if "attributes" in child and "tDn" in child["attributes"]
                }
                for child in obj["physDomP"]["children"]:
                    if "attributes" in child and child["attributes"]["tDn"] not in existing_tDns:
                        merged_dict[domain_name]["children"].append(child)
    return [{"physDomP": value} for value in merged_dict.values()]

def merge_aaep_objects(json_list):
    merged_dict = {}
    for obj in json_list:
        aaep_inst = obj.get("infraAttEntityP")
        if aaep_inst:
            name = aaep_inst["attributes"]["name"]
            if name not in merged_dict:
                merged_dict[name] = aaep_inst
            else:
                existing_tDns = {
                    child["attributes"]["tDn"]
                    for child in merged_dict[name]["children"]
                    if "attributes" in child and "tDn" in child["attributes"]
                }
                for child in aaep_inst["children"]:
                    if "attributes" in child and child["attributes"]["tDn"] not in existing_tDns:
                        merged_dict[name]["children"].append(child)
    return [{"infraAttEntityP": value} for value in merged_dict.values()]

def build_structure(level_name, payloads, child_levels=[]):
    structure = {
        level_name: {
            "attributes": {"status": "modified"},
            "children": payloads
        }
    }
    for level in child_levels:
        structure = create_structure_level(level, {"status": "modified"}, [structure])
    return structure

def build_vlan_structure(vlan_payloads):
    return build_structure("infraInfra", vlan_payloads, ["polUni"])

def build_domain_structure(domain_payloads):
    return build_structure("polUni", domain_payloads)

def build_aaep_structure(aaep_payloads):
    return build_structure("infraInfra", aaep_payloads, ["polUni"])

def process_combined_file(input_file, output_file_vlan, output_file_domain, output_file_aaep):
    try:
        with open(input_file, "r") as file:
            lines = file.readlines()
        
        # Convertir las líneas de texto en objetos JSON
        json_list = [eval(line.strip()) for line in lines if line.strip()]  # Usa eval solo si confías en la fuente del archivo
        
    except Exception as e:
        print(f"Error al cargar el archivo TXT: {e}")
        json_list = []
    
    # Separar y combinar los objetos como antes
    vlan_payloads = merge_vlan_objects(json_list)
    domain_payloads = merge_domain_objects(json_list)
    aaep_payloads = merge_aaep_objects(json_list)

    # Construir las estructuras independientes para VLAN, Dominio y AAEP
    vlan_structure = build_vlan_structure(vlan_payloads)
    domain_structure = build_domain_structure(domain_payloads)
    aaep_structure = build_aaep_structure(aaep_payloads)

    # Guardar los archivos independientes
    with open(output_file_vlan, "w") as file:
        json.dump(vlan_structure, file, indent=2)

    with open(output_file_domain, "w") as file:
        json.dump(domain_structure, file, indent=2)

    with open(output_file_aaep, "w") as file:
        json.dump(aaep_structure, file, indent=2)


def combine_multiple_json_files(input_files, output_file):
    combined_infra_children = []
    domain_children = []

    for input_file in input_files:
        with open(input_file, 'r') as file:
            try:
                data = json.load(file)
                if "polUni" in data:
                    for child in data["polUni"]["children"]:
                        if "infraInfra" in child:
                            combined_infra_children.extend(child["infraInfra"]["children"])
                        else:
                            domain_children.append(child)
            except json.JSONDecodeError as e:
                print(f"Error al leer el archivo {input_file}: {e}")

    final_data = {
        "polUni": {
            "attributes": {
                "status": "modified"
            },
            "children": [
                {
                    "infraInfra": {
                        "attributes": {
                            "status": "modified"
                        },
                        "children": combined_infra_children
                    }
                }
            ] + domain_children
        }
    }

    with open(output_file, 'w') as file:
        json.dump(final_data, file, indent=2)
