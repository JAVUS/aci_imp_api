# Script Principal Modificado
from datetime import datetime
from aci_auth import login_to_aci
from table_reader import read_excel_table
from file_utils import save_payload_to_file
from combine_json import process_combined_file, combine_multiple_json_files  # Importa la nueva función para combinar archivos
from table_locate import table_config  # Importa la configuración de tablas
from vlan_pool import generate_vlan_payload, send_vlan_payload_to_aci
from domain import generate_domain_payload, send_domain_payload_to_aci
from aaep import generate_aaep_payload, send_aaep_payload_to_aci

# root path
root_path = "F:/visual_studio/aci_imp"

# Configuración de autenticación para ACI
APIC_IP = "192.168.0.50"
USERNAME = "admin"
PASSWORD = "Cisco123"
ACI_URL = f"https://{APIC_IP}/api/aaaLogin.json"

# Configuración del archivo Excel
config_data = f"{root_path}/template/imp_v3.xlsx"

# Obtener el timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Rutas para guardar los payloads con timestamp
comb_log_path = f"{root_path}/payloads/raw/combined_raw_{timestamp}.txt"  # Ruta para log combinado con timestamp

# Ruta para el archivo combinado final
final_combined_path_vlan = f"{root_path}/payloads/ready/each_ready_{timestamp}_01_vlan.json"
final_combined_path_domain = f"{root_path}/payloads/ready/each_ready_{timestamp}_02_domain.json"
final_combined_path_aaep = f"{root_path}/payloads/ready/each_ready_{timestamp}_03_aaep.json"
final_combined_all = f"{root_path}/payloads/ready/combined_ready_{timestamp}_00_all.json"  # Nuevo archivo combinado

if __name__ == "__main__":
    vlan_rows = read_excel_table(config_data, table_config["vlan"]["sheet"], table_config["vlan"]["start_cells"], table_config["vlan"]["column_count"])
    domi_rows = read_excel_table(config_data, table_config["dominio"]["sheet"], table_config["dominio"]["start_cells"], table_config["dominio"]["column_count"])
    aaep_rows = read_excel_table(config_data, table_config["aaep"]["sheet"], table_config["aaep"]["start_cells"], table_config["aaep"]["column_count"])
    
    token = login_to_aci(ACI_URL, USERNAME, PASSWORD)
    if token:
        for vlanrow in vlan_rows:
            payload = generate_vlan_payload(vlanrow)
            save_payload_to_file(payload, comb_log_path, "txt")  # Guardar directamente como JSON
            send_vlan_payload_to_aci(payload, token, vlanrow['vlanname'], APIC_IP)

        for domrow in domi_rows:
            payload = generate_domain_payload(domrow)
            save_payload_to_file(payload, comb_log_path, "txt")  # Guardar directamente como JSON
            send_domain_payload_to_aci(payload, token, domrow['domname'], domrow['domtype'], APIC_IP)

        for aeprow in aaep_rows:
            payload = generate_aaep_payload(aeprow)
            save_payload_to_file(payload, comb_log_path, "txt")  # Guardar directamente como JSON
            send_aaep_payload_to_aci(payload, token, aeprow['aaepname'], APIC_IP)
        
        # Procesar archivos combinados para VLAN, Dominio y AAEP
        process_combined_file(comb_log_path.format(ext="txt"), final_combined_path_vlan, final_combined_path_domain, final_combined_path_aaep)

        # Combinar los archivos generados en un solo archivo final
        combine_multiple_json_files([final_combined_path_vlan, final_combined_path_domain, final_combined_path_aaep], final_combined_all)

        print(f"Archivos combinados finales generados en:\n{final_combined_path_vlan}\n{final_combined_path_domain}\n{final_combined_path_aaep}\n{final_combined_all}")
    else:
        print('No se pudo autenticar en la API de Cisco ACI.')

