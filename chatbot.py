"""
Twitter/X Chatbot - After Hour TV Bot
=====================================
Automated chatbot that monitors mentions and replies using AI.
Runs via GitHub Actions on a schedule.
"""

import os
import json
import tweepy
from openai import OpenAI
from pathlib import Path

print("🤖 Iniciando After Hour TV Chatbot...")

# -------------------------------
# Configuration from Environment
# -------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

# File to track replied mentions (persisted via GitHub Actions cache)
REPLIED_FILE = "replied_mentions.json"

# -------------------------------
# Initialize OpenAI Client
# -------------------------------
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------------------
# Initialize Twitter/X API v2 Client
# -------------------------------
twitter_client = tweepy.Client(
    bearer_token=X_BEARER_TOKEN,
    consumer_key=X_API_KEY,
    consumer_secret=X_API_SECRET,
    access_token=X_ACCESS_TOKEN,
    access_token_secret=X_ACCESS_SECRET,
    wait_on_rate_limit=True
)

# Also initialize v1.1 API for some operations
auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_SECRET)
api_v1 = tweepy.API(auth)


def load_replied_mentions():
    """Load the set of already replied mention IDs."""
    if Path(REPLIED_FILE).exists():
        try:
            with open(REPLIED_FILE, "r") as f:
                data = json.load(f)
                return set(data.get("replied_ids", []))
        except Exception as e:
            print(f"⚠️ Error loading replied mentions: {e}")
    return set()


def save_replied_mentions(replied_ids):
    """Save the set of replied mention IDs."""
    try:
        with open(REPLIED_FILE, "w") as f:
            json.dump({"replied_ids": list(replied_ids)}, f)
        print(f"💾 Saved {len(replied_ids)} replied mention IDs")
    except Exception as e:
        print(f"⚠️ Error saving replied mentions: {e}")


def get_bot_user_id():
    """Get the authenticated user's ID."""
    try:
        me = twitter_client.get_me()
        if me.data:
            print(f"✅ Authenticated as: @{me.data.username} (ID: {me.data.id})")
            return me.data.id, me.data.username
        return None, None
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
        return None, None


def get_mentions(user_id, since_id=None):
    """Fetch recent mentions of the bot."""
    try:
        mentions = twitter_client.get_users_mentions(
            id=user_id,
            since_id=since_id,
            max_results=10,
            tweet_fields=["created_at", "author_id", "conversation_id", "in_reply_to_user_id"],
            expansions=["author_id"],
            user_fields=["username"]
        )

        if mentions.data:
            # Create a mapping of user IDs to usernames
            users = {}
            if mentions.includes and "users" in mentions.includes:
                users = {user.id: user.username for user in mentions.includes["users"]}

            return mentions.data, users
        return [], {}
    except Exception as e:
        print(f"❌ Error fetching mentions: {e}")
        return [], {}


def generate_reply(user_message, username):
    """Generate an AI response to a user's message."""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres Chicorio Quiñones, presentador de After Hour TV con humor boricua "
                        "intenso, estilo callejero y vocablo parecido al de 'No te duermas'. "
                        "Siempre hablas con flow, vacilon y chispa boricua. "
                        "Responde a los mensajes de forma amigable, divertida y con sabor puertorriqueno. "
                        "Manten las respuestas cortas (menos de 200 caracteres) para que quepan en Twitter. "
                        "No uses hashtags a menos que sean muy relevantes."
                    )
                },
                {
                    "role": "user",
                    "content": f"@{username} te escribio: \"{user_message}\"\n\nResponde de forma natural y divertida."
                }
            ],
            temperature=0.8,
            max_completion_tokens=100
        )

        reply = response.choices[0].message.content.strip()

        # Remove quotes if the AI wrapped the response
        if reply.startswith('"') and reply.endswith('"'):
            reply = reply[1:-1]

        return reply

    except Exception as e:
        print(f"❌ Error generating reply: {e}")
        return None


def reply_to_tweet(tweet_id, reply_text, username):
    """Post a reply to a specific tweet."""
    try:
        # Ensure reply includes the @mention and fits Twitter's limit
        full_reply = f"@{username} {reply_text}"

        # Truncate if too long (280 chars max)
        if len(full_reply) > 280:
            full_reply = full_reply[:277] + "..."

        response = twitter_client.create_tweet(
            text=full_reply,
            in_reply_to_tweet_id=tweet_id
        )

        if response.data:
            print(f"✅ Reply posted successfully (ID: {response.data['id']})")
            return True
        return False
    except Exception as e:
        print(f"❌ Error posting reply: {e}")
        return False


def process_mentions():
    """Main function to process mentions and reply."""
    print("\n📬 Checking for new mentions...")

    # Get bot's user ID
    user_id, bot_username = get_bot_user_id()
    if not user_id:
        print("❌ Could not get bot user ID. Exiting.")
        return

    # Load already replied mentions
    replied_ids = load_replied_mentions()
    print(f"📋 Already replied to {len(replied_ids)} mentions")

    # Get recent mentions
    mentions, users = get_mentions(user_id)

    if not mentions:
        print("📭 No new mentions found.")
        return

    print(f"📨 Found {len(mentions)} mentions to process")

    new_replies = 0
    for mention in mentions:
        tweet_id = str(mention.id)

        # Skip if already replied
        if tweet_id in replied_ids:
            print(f"⏭️ Skipping mention {tweet_id} (already replied)")
            continue

        # Get author username
        author_username = users.get(mention.author_id, "usuario")
        tweet_text = mention.text

        # Remove @bot_username from the message for cleaner processing
        clean_message = tweet_text
        if bot_username:
            clean_message = tweet_text.replace(f"@{bot_username}", "").strip()

        print(f"\n💬 Processing mention from @{author_username}:")
        print(f"   \"{tweet_text[:100]}...\"" if len(tweet_text) > 100 else f"   \"{tweet_text}\"")

        # Generate reply
        reply = generate_reply(clean_message, author_username)
        if not reply:
            print(f"⚠️ Could not generate reply for mention {tweet_id}")
            continue

        print(f"🤖 Generated reply: \"{reply}\"")

        # Post the reply
        if reply_to_tweet(tweet_id, reply, author_username):
            replied_ids.add(tweet_id)
            new_replies += 1

    # Save updated replied mentions
    save_replied_mentions(replied_ids)

    print(f"\n✨ Finished processing. Replied to {new_replies} new mentions.")


def generate_standalone_content():
    """Generate and post a standalone tweet (original bot functionality)."""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres Chicorio Quiñones, presentador de After Hour TV con humor boricua "
                        "intenso, estilo callejero y vocablo parecido al de 'No te duermas'. "
                        "Siempre hablas con flow, vacilon y chispa boricua."
                    )
                },
                {
                    "role": "user",
                    "content": "Genera un tweet divertido, corto, con vacilon boricua sobre la vida en Puerto Rico."
                }
            ],
            temperature=0.8,
            max_completion_tokens=80
        )

        tweet = response.choices[0].message.content.strip()
        return tweet

    except Exception as e:
        print(f"❌ Error generating content: {e}")
        return None


def post_standalone_tweet():
    """Post a standalone tweet."""
    content = generate_standalone_content()
    if not content:
        print("❌ No se pudo generar contenido.")
        return False

    try:
        response = twitter_client.create_tweet(text=content)
        if response.data:
            print(f"✅ Tweet publicado: {content}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        return False


# -------------------------------
# Main Execution
# -------------------------------
if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "chatbot"

    if mode == "chatbot":
        # Process mentions and reply
        process_mentions()
    elif mode == "post":
        # Post a standalone tweet
        post_standalone_tweet()
    elif mode == "both":
        # Do both: process mentions AND post a tweet
        process_mentions()
        print("\n" + "="*50 + "\n")
        post_standalone_tweet()
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python chatbot.py [chatbot|post|both]")
        sys.exit(1)

    print("\n🏁 Ejecucion completada.")
