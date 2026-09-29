import os
from app import create_app

env_name = os.getenv("FLASK_ENV", "development").lower()
app = create_app(env_name)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    if env_name == "production":
        debug = os.getenv("FLASK_DEBUG", "0") == "1"
    else:
        debug = os.getenv("FLASK_DEBUG", "1") == "1"
    print(f"[READY] AI Project Interview Trainer ({env_name}) starting on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
