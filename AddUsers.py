from framework.GoogleAPI import GoogleAdminClient
from configparser import RawConfigParser

# Set config variables
config_path = '/configs/config.ini'
config = RawConfigParser()
config.read(config_path)

SERVICE_EMAIL = 'admin_user@example.com'
SECRET = config.get('google_admin_creds', 'secret')
SCOPES = config.get('google_admin_creds', 'scopes')

# Group Mappings
sales = config['groups']['sales']
eng = config['groups']['eng']
fall_back = config['groups']['catch_all']


# Build client
client = GoogleAdminClient(scopes=SCOPES.split(','),
                           service_account_pkcs12_file_path=SECRET)


def add_user(filename):
    with open(filename, 'r') as f:
        f.seek(0)
        f_char = f.read(1)

        if not f_char:
            exit(0)
        else:
            next(f)
            for line in f:
                # Chop it up
                x = line.strip('\n').split('\t')
                if 'activate' in x[8].lower():
                    # Set user vars
                    email = x[6]
                    dep_code = x[9]

                    # Get current membership regardless of department
                    groups = client.get_membership(email)

                    # Parse file for department code and trigger
                    # subsequent action(s)

                    # SALES Example
                    if 'SALES' in dep_code:
                        for g in sales.split(','):
                            if g not in groups:
                                print(client.add_membership(g, email))
                    elif 'ENG' in dep_code:
                        for g in eng.split(','):
                            if g not in groups:
                                print(client.add_membership(g, email))
                    elif 'NULL' in dep_code:
                        for g in fall_back.split(','):
                            if g not in groups:
                                print(client.add_membership(g, email))


def main():
    add_user('examples/sample.tsv')


if __name__ == '__main__':
    main()
