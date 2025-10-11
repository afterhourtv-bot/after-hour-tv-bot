import os
import openai
import tweepy
import random

# -------------------------------
# Configuración de API Keys
# -------------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")

api_key = os.getenv("X_API_KEY")
api_secret = os.getenv("X_API_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_secret = os.getenv("X_ACCESS_SECRET")

# Autenticación con Twitter/X
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

# -------------------------------
# Función para generar contenido
# -------------------------------
def generate_content():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres Chicorio Quiñones, presentador de After Hour TV con humor boricua "
                    "intenso, estilo callejero y vocablo parecido al de 'No te duermas'. "
                    "Siempre hablas con flow, vacilón y chispa boricua."
                )
            },
            {
                "role": "user",
                "content": "Genera un tweet divertido, corto, con vacilón boricua sobre la vida en Puerto Rico."
            }
        ],
        temperature=0.7,
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

# -------------------------------
# Función para publicar en Twitter/X
# -------------------------------
def post_content():
    try:
        content = generate_content()
        api.update_status(content)
        print("Tweet publicado correctamente:")
        print(content)
    except Exception as e:
        print("Error publicando tweet:", e)

# -------------------------------
# Ejecutar el bot
# -------------------------------
if __name__ == "__main__":
    post_content()
