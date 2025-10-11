import openai
import tweepy
import time

# Claves de Twitter
api_key = " ${{ secrets.X_API_KEY }}"
api_secret = " ${{ secrets.X_API_SECRET }}"
access_token = " ${{ secrets.X_ACCESS_TOKEN }}"
access_secret = "${{ secrets.X_ACCESS_SECRET }}"

# Clave de OpenAI
openai.api_key = " ${{ secrets.OPENAI_API_KEY }}"

# Autenticación con Twitter
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

# Prompt base para generar contenido con estilo Chicorio
base_prompt = """
Eres Chicorio Quiñones, el presentador energético y carismático de After Hour TV.
Tu estilo es directo, irreverente y lleno de humor boricua.
Hablas con entusiasmo, usas frases como '¡Esto es un vacilón!' y '¡A fuego, mi gente!'.
Genera contenido para Twitter que sea corto, impactante y con actitud.
"""

# Función para generar contenido con OpenAI
def generate_content():
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=base_prompt,
        temperature=0.7,
        max_tokens=100
    )
    return response.choices[0].text.strip()

# Publicar contenido en Twitter
def post_content():
    content = generate_content()
    api.update_status(content)
    print(f"Publicado: {content}")

# Ejecutar el bot
while True:
    post_content()
    time.sleep(3600)  # Espera de 1 hora entre publicaciones
