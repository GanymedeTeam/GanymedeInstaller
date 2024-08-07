import tkinter as tk
from tkinter import ttk
import requests
import zipfile
import shutil
import os
import tempfile
import threading
import sys

# Configuration
if hasattr(sys, 'frozen'):
    INSTALL_DIR = os.path.dirname(sys.executable)
else:
    INSTALL_DIR = os.path.dirname(os.path.abspath(__file__))

RELEASES_API_URL = 'https://api.github.com/repos/GanymedeTeam/GanymedeApp/releases/latest'
APP_DIR = f'{INSTALL_DIR}\\UnityPackage'
LOCAL_VERSION_FILE = os.path.join(APP_DIR, 'version.txt')
APPLICATION_EXECUTABLE = os.path.join(APP_DIR, 'Ganymede.exe')

class UpdateManager:
    @staticmethod
    def get_latest_version():
        print('Vérification de la dernière version...')
        response = requests.get(RELEASES_API_URL)
        if response.status_code == 403:
            print("Accès refusé (403), lancement de l'application...")
            return None, None
        response.raise_for_status()  # Raise an exception for other HTTP errors
        release_info = response.json()
        latest_version = release_info['tag_name']
        assets = release_info['assets']
        for asset in assets:
            if 'UnityPackage.zip' in asset['name']:
                zip_url = asset['browser_download_url']
                return latest_version, zip_url
        raise Exception('Aucun fichier ZIP trouvé dans la dernière release.')

    @staticmethod
    def is_up_to_date(latest_version):
        if os.path.exists(LOCAL_VERSION_FILE):
            with open(LOCAL_VERSION_FILE, 'r') as file:
                current_version = file.read().strip()
            return current_version == latest_version
        return False

    @staticmethod
    def download_file(url, local_filename, progress_callback):
        print(f'Téléchargement de {url}...')
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded_size += len(chunk)
                progress_percentage = (downloaded_size / total_size) * 100
                progress_callback(progress_percentage)
        print(f'Téléchargement terminé : {local_filename}')

    @staticmethod
    def extract_zip(zip_path, extract_to, progress_callback):
        print(f'Décompression de {zip_path} dans {extract_to}...')
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            files = zip_ref.namelist()
            total_files = len(files)
            for index, file in enumerate(files):
                zip_ref.extract(file, extract_to)
                progress_percentage = ((index + 1) / total_files) * 100
                progress_callback(progress_percentage)
        print('Décompression terminée.')

    @staticmethod
    def download_and_install_update(zip_url):
        zip_path = os.path.join(tempfile.gettempdir(), 'update.zip')
        UpdateManager.download_file(zip_url, zip_path, lambda p: app.update_progress(p))
        if os.path.exists(APP_DIR):
            print(f'Suppression de l\'ancienne installation dans {APP_DIR}...')
            shutil.rmtree(APP_DIR)
        os.makedirs(INSTALL_DIR, exist_ok=True)
        UpdateManager.extract_zip(zip_path, INSTALL_DIR, lambda p: app.update_progress(p))
        os.remove(zip_path)
        with open(LOCAL_VERSION_FILE, 'w') as file:
            file.write(UpdateManager.get_latest_version()[0])

    @staticmethod
    def launch_application():
        print('Lancement de l\'application...')
        print(APPLICATION_EXECUTABLE)
        os.startfile(APPLICATION_EXECUTABLE)

class UpdateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mise à jour en cours")
        self.root.geometry("400x100")

        # Set the icon for the window
        self.root.iconbitmap('ganymede_icon.ico')  # Change to .ico format

        latest_version, _ = UpdateManager.get_latest_version()
        if latest_version:
            self.version_label = tk.Label(root, text=f"Nouvelle version disponible: {latest_version}")
            self.version_label.pack(pady=20)

            self.progress = ttk.Progressbar(root, length=300, mode='determinate')
            self.progress.pack(pady=5)
        
            self.label = tk.Label(root, text="Téléchargement et mise à jour en cours...")
            self.label.pack(pady=20)

            # Initialize progress
            self.progress['value'] = 0
            self.progress['maximum'] = 100

            # Start the update process
            self.update_thread = threading.Thread(target=self.perform_update)
            self.update_thread.start()
            self.root.after(100, self.check_update_thread)

    def perform_update(self):
        try:
            latest_version, zip_url = UpdateManager.get_latest_version()
            if latest_version and not UpdateManager.is_up_to_date(latest_version):
                UpdateManager.download_and_install_update(zip_url)
            else:
                print("L'application est déjà à jour.")
                # If already up-to-date, exit without showing the Tkinter window
                self.root.destroy()
                UpdateManager.launch_application()
        except Exception as e:
            print(f"Erreur : {e}")

    def check_update_thread(self):
        if self.update_thread.is_alive():
            self.root.after(100, self.check_update_thread)
        else:
            self.root.destroy()
            UpdateManager.launch_application()

    def update_progress(self, percentage):
        self.progress['value'] = percentage
        self.root.update_idletasks()

def main():
    try:
        if os.path.exists(LOCAL_VERSION_FILE):
            with open(LOCAL_VERSION_FILE, 'r') as file:
                current_version = file.read().strip()
        else:
            current_version = '0.0.0'

        latest_version, zip_url = UpdateManager.get_latest_version()
        if latest_version == None and zip_url == None:
            UpdateManager.launch_application()
            return
        
        if latest_version and latest_version != current_version:
            # Only open Tkinter window if update is needed
            root = tk.Tk()
            global app
            app = UpdateApp(root)
            root.mainloop()
        else:
            print("L'application est déjà à jour.")
            # Launch the application if no update is needed
            UpdateManager.launch_application()

    except Exception as e:
        print(f'Erreur : {e}')

if __name__ == '__main__':
    main()
