from flask import Flask, request
import webbrowser
import requests
import csv
import os

# Variables del usuario
client_id = "5133875641332998"  # Reemplaza con tu App ID
client_secret = "hJAiQSuCcT1577tuFCVbvFYpQjdrsMXc"  # Reemplaza con tu App Secret
access_token = None
user_id = None

app = Flask(__name__)

# Reemplaza con tu URL de Render, asegúrate de que esté configurada correctamente
REDIRECT_URI = 'https://nombre-de-tu-aplicacion.onrender.com/callback'  # Cambia esto por tu URL de Render

# Paso 1: Generar la URL de autorización y abrirla en el navegador
def obtener_codigo_autorizacion():
    auth_url = (
        f"https://auth.mercadolibre.cl/authorization"  # Cambiar ".com.ar" por ".cl"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    webbrowser.open(auth_url)  # Abre la URL de autorización en el navegador

# Paso 2: Crear la ruta de redirección en Flask para capturar el código de autorización
@app.route('/callback')
def callback():
    global access_token
    # Extraer el código de autorización de los parámetros de la URL
    authorization_code = request.args.get('code')
    if authorization_code:
        print(f"Código de autorización obtenido: {authorization_code}")
        # Llamar a la función para intercambiar el código por un token de acceso
        obtener_access_token(authorization_code)
    else:
        return "No se obtuvo código de autorización."
    return "Código recibido, revisa tu terminal."

# Paso 3: Intercambiar el código de autorización por un access token
def obtener_access_token(authorization_code):
    global access_token
    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    response = requests.post(url, data=payload, headers=headers)
    
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        print(f"Access token obtenido: {access_token}")
        obtener_user_id()  # Obtener el user_id del vendedor
    else:
        print(f"Error al obtener el access token: {response.status_code}, {response.text}")

# Paso 4: Obtener el ID del vendedor
def obtener_user_id():
    global user_id
    url = f"https://api.mercadolibre.com/users/me?access_token={access_token}"
    response = requests.get(url)
    
    if response.status_code == 200:
        user_id = response.json().get('id')
        print(f"User ID obtenido: {user_id}")
        # Ahora que tenemos el token y el user_id, podemos proceder a obtener las publicaciones
        publicaciones = obtener_publicaciones()
        exportar_a_csv(publicaciones)
    else:
        print(f"Error al obtener el user ID: {response.status_code}, {response.text}")

# Paso 5: Obtener las publicaciones del vendedor
def obtener_publicaciones():
    url = f"https://api.mercadolibre.com/users/{user_id}/items/search?access_token={access_token}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Error al obtener las publicaciones: {response.status_code}, {response.text}")
        return []

# Paso 6: Obtener detalles del producto
def obtener_detalles_producto(item_id):
    url = f"https://api.mercadolibre.com/items/{item_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al obtener detalles del producto {item_id}: {response.status_code}, {response.text}")
        return None

# Paso 7: Exportar los productos a CSV
def exportar_a_csv(productos):
    with open('productos_mercadolibre.csv', mode='w', newline='', encoding='utf-8') as archivo_csv:
        campos = ['titulo', 'precio', 'stock', 'sku', 'categoria', 'link', 'imagenes']
        escritor_csv = csv.DictWriter(archivo_csv, fieldnames=campos)
        escritor_csv.writeheader()

        for item_id in productos:
            detalles = obtener_detalles_producto(item_id)
            if detalles:
                producto = {
                    'titulo': detalles.get('title'),
                    'precio': detalles.get('price'),
                    'stock': detalles.get('available_quantity'),
                    'sku': detalles.get('seller_custom_field', 'No SKU'),
                    'categoria': detalles.get('category_id'),
                    'link': detalles.get('permalink'),
                    'imagenes': ','.join([img['url'] for img in detalles.get('pictures', [])])
                }
                escritor_csv.writerow(producto)
    print(f"Productos exportados a 'productos_mercadolibre.csv'. Total: {len(productos)} productos.")

# Paso 8: Ejecutar el servidor Flask
if __name__ == "__main__":
    # Inicia el proceso de autorización
    obtener_codigo_autorizacion()

    # Inicia el servidor Flask
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))  # Utiliza el puerto asignado por Render
