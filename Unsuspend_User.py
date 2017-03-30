from framework.GoogleAPI import GoogleAdminClient
from configparser import RawConfigParser

# Set config variables
config_path = 'configs/config.ini'
config = RawConfigParser()
config.read(config_path)

SERVICE_EMAIL = 'user@example.com'
SECRET = config.get('google_admin_creds', 'secret')
SCOPES = config.get('google_admin_creds', 'scopes')
FILE = config.get('file_path', 'file')

# Build client
client = GoogleAdminClient(scopes=SCOPES.split(','),
                           service_account_pkcs12_file_path=SECRET)

with open(FILE, 'r') as f:
    for line in f:

        # UnSuspend
        out = client.unsuspend_user(line.strip('\n'))

        # Print Any errors
        if out is not None:
            print(out)

f.close()
