from PyQt5 import QtWidgets
from configparser import ConfigParser
import requests

class SettingsWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.setWindowTitle("Innstillinger")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                color: white;
                font-family: Arial, sans-serif;
            }
            QLabel, QCheckBox {
                margin: 5px;
            }
            QPushButton {
                background-color: #3498db;
                border-radius: 10px;
                padding: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLineEdit {
                border-radius: 5px;
                padding: 5px;
                background-color: white;
                color: black;
            }
            QComboBox {
                border-radius: 5px;
                padding: 5px;
                background-color: white;
                color: black;
            }
        """)

        # Les innstillingene fra konfigurasjonsfilen
        self.config = ConfigParser()
        self.config.read('config.ini')
        
        # Opprett layout og widgets
        self.layout = QtWidgets.QVBoxLayout(self)

        # API-nøkkel
        self.api_change_widget = QtWidgets.QLineEdit(self)
        self.api_change_widget.setText(self.config.get('Credentials', 'authorization'))
        api_key_label = QtWidgets.QLabel("API-nøkkel:")
        api_key_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
        self.layout.addWidget(api_key_label)
        self.layout.addWidget(self.api_change_widget)

        # Forklarende tekst og hyperlink for API-nøkkelen
        api_key_info = QtWidgets.QLabel("""
            <p>API-nøkkelen brukes til å autentisere forespørsler til Tibber. 
            Du kan finne din personlige API-nøkkel på 
            <a href="https://developer.tibber.com/settings/access-token">Tibber Developer Portal</a>.</p>
        """)
        api_key_info.setWordWrap(True)
        api_key_info.setOpenExternalLinks(True)
        self.layout.addWidget(api_key_info)

        # Legg til en horisontal linje for visuell separasjon
        # Legg til ekstra vertikalt rom
        self.layout.addSpacing(20)

        # Legg til en horisontal linje med hvit farge
        self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setStyleSheet("background-color: white;")  # Endre bakgrunnsfarge til hvit
        self.layout.addWidget(self.line)

        # Legg til ytterligere litt rom etter linjen for god målsetting
        self.layout.addSpacing(20)


        # Tittel for varsler
        notification_label = QtWidgets.QLabel("Smartvarsler: [ikke implimentert]")
        notification_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
        self.layout.addWidget(notification_label)

        # Horisontal layout for sjekkbokser
        self.notifications_layout = QtWidgets.QHBoxLayout()

        # Sjekkbokser for varsler
        self.low_price_notification = QtWidgets.QCheckBox("Varsle ved lav pris", self)
        self.high_price_notification = QtWidgets.QCheckBox("Varsle ved høy pris", self)
        if self.config.has_section('Notifications'):
            self.low_price_notification.setChecked(self.config.getboolean('Notifications', 'low_price_alert', fallback=False))
            self.high_price_notification.setChecked(self.config.getboolean('Notifications', 'high_price_alert', fallback=False))

        # Legg til sjekkbokser til horisontal layout
        self.notifications_layout.addWidget(self.low_price_notification)
        self.notifications_layout.addWidget(self.high_price_notification)

        # Legg til horisontal layout til hovedlayout
        self.layout.addLayout(self.notifications_layout)

        # Beskrivende tekst for varsler
        notifications_info = QtWidgets.QLabel("""
            <p>Ved å aktivere disse varslene, vil du motta notifikasjoner ved spesielt høye eller lave strømpriser, 
            basert på dine preferanser.</p>
        """)
        notifications_info.setWordWrap(True)
        self.layout.addWidget(notifications_info)

        # Support og versjon
        self.layout.addWidget(QtWidgets.QLabel("Support: anthony@leinebo.com"))
        self.layout.addWidget(QtWidgets.QLabel("Versjon: 1.0.0"))

        # Lagre og avbryt knapper
        self.save_button = QtWidgets.QPushButton("Lagre", self)
        self.cancel_button = QtWidgets.QPushButton("Avbryt", self)
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.button_layout)

        # Koble knapper til hendelser
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.close)

    def save_settings(self):
        # Test API-nøkkelen før lagring
        if self.verify_api_key(self.api_change_widget.text()):
            # Oppdater konfigurasjonen i minnet
            self.config.set('Credentials', 'authorization', self.api_change_widget.text())
            self.config.set('Notifications', 'low_price_alert', str(self.low_price_notification.isChecked()))
            self.config.set('Notifications', 'high_price_alert', str(self.high_price_notification.isChecked()))

            # Skriv den oppdaterte konfigurasjonen til filen én gang
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)

            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, "Feil", "API-nøkkelen er ikke gyldig.")

    def verify_api_key(self, api_key):
        """Verifiser API-nøkkelen ved å sende en testforespørsel."""
        headers = {'Authorization': f'Bearer {api_key}'}
        url = 'https://api.tibber.com/v1-beta/gql'
        test_query = """{
            viewer {
                homes {
                    id
                }
            }
        }"""

        try:
            response = requests.post(url, json={'query': test_query}, headers=headers)
            if response.status_code == 200 and 'data' in response.json():
                return True
        except Exception as e:
            print("Feil under verifisering av API-nøkkel:", e)
        
        return False