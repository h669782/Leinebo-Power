import requests
import configparser
import tkinter as tk
from tkinter import messagebox
from packaging import version
import os
import zipfile
import tempfile
import shutil
import subprocess
import sys

def download_and_extract(url, extract_to):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with tempfile.TemporaryDirectory() as tmp_dir:
            zip_file_path = os.path.join(tmp_dir, "download.zip")
            with open(zip_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)


def preserve_config(config_path, temp_extract_path, new_version):
    temp_config_path = os.path.join(temp_extract_path, 'config.ini')
    if os.path.exists(temp_config_path):
        temp_config = configparser.ConfigParser()
        temp_config.read(temp_config_path)

        current_config = configparser.ConfigParser()
        current_config.read(config_path)

        # Bevarer Credentials hvis de eksisterer
        if 'Credentials' in temp_config and 'authorization' in temp_config['Credentials']:
            if not current_config.has_section('Credentials'):
                current_config.add_section('Credentials')
            current_config['Credentials']['authorization'] = temp_config['Credentials']['authorization']

        # Oppdaterer applikasjonsversjonen
        if not current_config.has_section('Application'):
            current_config.add_section('Application')
        current_config['Application']['version'] = new_version

        with open(config_path, 'w') as configfile:
            current_config.write(configfile)


def update_files(latest_version):
    print(f"Oppdaterer til versjon {latest_version}")
    download_url = f"https://github.com/h669782/Leinebo-Power/archive/refs/tags/{latest_version}.zip"
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        download_and_extract(download_url, temp_dir)

        # Finn den korrekte mappen inne i den midlertidige mappen
        extracted_folder = os.path.join(temp_dir, os.listdir(temp_dir)[0])
        print("Ekstrahert til:", extracted_folder)



        # Kopier filene fra den ekstraherte mappen til nåværende arbeidsmappe
        for item in os.listdir(extracted_folder):
            s = os.path.join(extracted_folder, item)
            d = os.path.join(os.getcwd(), item)
            if os.path.isdir(s):
                print(f"Kopierer mappe: {s} til {d}")
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                print(f"Kopierer fil: {s} til {d}")
                shutil.copy2(s, d)
        
        # Oppdater config.ini med nye verdier
        preserve_config('config.ini', temp_dir, str(latest_version))


        print("Oppdateringen fullført. Starter programmet på nytt.")

        # Start programmet på nytt
        python = sys.executable
        os.execl(python, python, *sys.argv)

    except Exception as e:
        print(f"En feil oppsto under oppdateringen: {e}")
    finally:
        shutil.rmtree(temp_dir)


def check_for_updates():
    config = configparser.ConfigParser()
    config.read('config.ini')
    local_version = version.parse(config['Application']['version'])

    response = requests.get('https://api.github.com/repos/h669782/Leinebo-Power/releases/latest')
    latest_version = version.parse(response.json()['tag_name'])

    if latest_version > local_version:
        ask_user_to_update(str(latest_version))  # Konverter til streng for visning
    else:
        print("Ingen oppdateringer tilgjengelig.")

def ask_user_to_update(latest_version):
    root = tk.Tk()
    root.withdraw()  # Gjemmer hovedvinduet
    response = messagebox.askyesno("LEINEBO - Oppdatering Tilgjengelig",
                                   f"Versjon {latest_version} er tilgjengelig. Vil du oppdatere nå?")
    if response:
        update_files(latest_version)

if __name__ == "__main__":
    check_for_updates()
