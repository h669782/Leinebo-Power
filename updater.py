import requests
import configparser

def check_for_updates():
    # Last inn lokal versjon fra config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')
    local_version = config['Application']['version']

    # API-kall til OneDrive for å hente den nyeste versjonen
    # Du må sette opp dette kallet basert på din OneDrive-konfigurasjon
    response = requests.get('onedrive_api_url')
    latest_version = response.json()['latest_version']

    if latest_version > local_version:
        update_files()
    else:
        print("Ingen oppdateringer tilgjengelig.")

def update_files():
    # Logikk for å laste ned og erstatte filer
    pass

if __name__ == "__main__":
    check_for_updates()
