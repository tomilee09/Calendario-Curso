from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def main():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)  # abre navegador y autoriza
    with open("token.json", "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    print("Listo: token.json creado")

if __name__ == "__main__":
    main()
