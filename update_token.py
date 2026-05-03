from src.token_store import save_access_token

print("Paste today's Zerodha access token:")
token = input().strip()

if not token:
    print("Invalid token")
else:
    save_access_token(token)
    print("Token saved successfully")
