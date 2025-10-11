import os
import tweepy
from openai import OpenAI

print("🚀 Iniciando After Hour TV Bot...")

# -------------------------------
# Configuración de API Keys desde Secrets
# -------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

# -------------------------------
# Inicializar cliente de OpenAI
# -------------------------------
client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------------------
# Autenticación con Twitter/X
# -------------------------------
auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_SECRET)
api = tweepy.API(auth)

# -------------------------------
# Función para generar contenido
# -------------------------------
def generate_content():
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
            temperature=0.8,
            max_completion_tokens=80
        )

        tweet = response.choices[0].message.content.strip()
        return tweet

    except Exception as e:
        print("Error generando contenido con OpenAI:", e)
        return None

# -------------------------------
# Función para publicar en Twitter/X
# -------------------------------
def post_content():
    content = generate_content()
    if not content:
        print("No se pudo generar contenido. Abortando.")
        return

    try:
        api.update_status(content)
        print("✅ Tweet publicado correctamente:")
        print(content)
    except Exception as e:
        print("Error publicando tweet:", e)

# -------------------------------
# Ejecutar el bot
# -------------------------------
if __name__ == "__main__":
    post_content()
    print("🏁 Ejecución completada.")
