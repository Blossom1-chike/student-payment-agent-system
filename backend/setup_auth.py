from google_auth_oauthlib.flow import InstalledAppFlow
import os

# The permissions we need
SCOPES = ['https://www.googleapis.com/auth/calendar']

def generate_token():
    if not os.path.exists('credentials.json'):
        print("Error: You are missing 'credentials.json'. Download it from Google Cloud Console first!")
        return

    # This handles the "Log in with Google" pop-up
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    
    # This opens your browser
    creds = flow.run_local_server(port=0)

    # This creates the token.json file automatically
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
        print("Success! 'token.json' has been created.")

if __name__ == "__main__":
    generate_token()