from flask import Flask, request, redirect
import requests
import os

app = Flask(__name__)

# Configuración de la aplicación
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

@app.route('/')
def home():
    return "Bienvenido a la aplicación de MercadoLibre en Render"

# Ruta para iniciar el proceso de autorización
@app.route('/login')
def login():
    auth_url = (
        f"https://auth.mercadolibre.com.ar/authorization"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(auth_url)

# Ruta de callback para capturar el código de autorización
@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        # Intercambio de código por un token de acceso
        token_url = "https://api.mercadolibre.com/oauth/token"
        payload = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(token_url, data=payload, headers=headers)
        token_data = response.json()

        # Mostrar el token recibido
        return f"Access Token: {token_data.get('access_token')}"
    else:
        return "Error: No se obtuvo el código de autorización."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
