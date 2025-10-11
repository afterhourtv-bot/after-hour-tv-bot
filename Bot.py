import os
import tweepy
import random
from openai import OpenAI

# -------------------------------
# Configuración de API Keys desde Secrets
# -------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

# Inicializa el cliente de OpenAI (nuevo formato)
client = OpenAI(api_key=OPENAI_API_KEY)

# Autenticación con Twitter/X
auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_SECRET)
api = tweepy.API(auth)

# -------------------------------
# Función para generar contenido
# -------------------------------
def generate_content():
    """
    Genera un tweet corto y divertido con el estilo de Chicorio Quiñones.
    """
    prompt = (
        "Eres Chicorio Quiñones, presentador de After Hour TV con humor boricua "
        "intenso, estilo callejero y vocablo parecido al de 'No te duermas'. "
        "Siempre hablas con flow, vacilón y chispa boricua. "
        "Genera un tweet corto, gracioso y boricua sobre la vida en Puerto Rico."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # ✅ usa el modelo nuevo más rápido y barato
        messages=[
            {"role": "system", "content": "Eres un personaje con estilo boricua y chispa."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=80
    )

    return response.choices[0].message.content.strip()

# -------------------------------
# Función para publicar en Twitter/X
# -------------------------------
def post_content():
    """
    Genera el contenido y lo publica en X.
    """
    try:
        content = generate_content()

        if len(content) > 280:
            content = content[:277] + "..."  # Evita errores si el texto es muy largo

        api.update_status(content)
        print("✅ Tweet publicado correctamente:")
        print(content)

    except Exception as e:
        print("❌ Error publicando tweet:")
        print(e)

# -------------------------------
# Ejecutar el bot
# -------------------------------
if __name__ == "__main__":
    post_content()
