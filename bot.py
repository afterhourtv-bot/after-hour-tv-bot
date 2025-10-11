import os
import openai
import tweepy
import random

# -------------------------------
# Load API keys from environment variables (GitHub Secrets)
# -------------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")

api_key = os.getenv("X_API_KEY")
api_secret = os.getenv("X_API_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_secret = os.getenv("X_ACCESS_SECRET")

# -------------------------------
# Authenticate with Twitter/X
# -------------------------------
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

# -------------------------------
# Generate content with OpenAI
# -------------------------------
def generate_content():
    try:
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
    except Exception as e:
        print("Error generando contenido con OpenAI:", e)
        return None

# -------------------------------
# Post content to Twitter/X
# -------------------------------
def post_content():
    content = generate_content()
    if not content:
        print("No se pudo generar contenido. Abortando.")
        return

    print("Contenido a publicar:", content)

    try:
        tweet = api.update_status(content)
        print("✅ Tweet publicado correctamente:")
        print(tweet)
    except tweepy.TweepError as e:
        print("❌ Error de Twitter/X:", e.response.text)
    except Exception as e:
        print("❌ Otro error:", e)

# -------------------------------
# Main execution
# -------------------------------
if __name__ == "__main__":
    print("🚀 Iniciando After Hour TV Bot...")
    post_content()
    print("🏁 Ejecución completada.")
