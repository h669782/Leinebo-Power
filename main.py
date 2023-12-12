from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.text import Annotation
from PyQt5.QtCore import QTimer
from design import Ui_MainWindow  # Importer Ui_MainWindow fra din design.py
from api_client import fetch_data, fetch_hourly_price_data, fetch_monthly_data
from data_processor import process_data, process_monthly_data
from config_manager import load_config
import matplotlib.pyplot as plt
import calendar
from datetime import datetime
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from settings import SettingsWindow
from ai import AIDemoWidget
from PyQt5.QtGui import QIcon

class MainApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.setupUi(self)
        with open("stylesheet.css", "r") as f:
            self.setStyleSheet(f.read())
        
        plt.style.use('dark_background')
        plt.rcParams['figure.facecolor'] = 'none'  # Gjør bakgrunnen transparent
        plt.rcParams['axes.facecolor'] = 'none'  # Gjør aksebakgrunnen transparent
        plt.rcParams['axes.edgecolor'] = 'white'
        plt.rcParams['axes.labelcolor'] = 'white'
        plt.rcParams['xtick.color'] = 'white'
        plt.rcParams['ytick.color'] = 'white'
        plt.rcParams['grid.color'] = '#444444'
        plt.rcParams['text.color'] = 'white'



        # Legg til AI-widgeten i en ny fane
        self.ai_demo_widget = AIDemoWidget(self)
        ai_tab_index = self.tabWidget.addTab(self.ai_demo_widget, "AI")

        # Sett ikonet til AI-fanen
        ai_icon_path = "img/robot.png"  # Endre til den faktiske stien til robotbildet ditt
        self.tabWidget.setTabIcon(ai_tab_index, QIcon(ai_icon_path))


        # Forbered et område for matplotlib-plotting inne i 'graph'-widgeten
        self.graphCanvas = FigureCanvas(Figure())
        self.graphLayout = QtWidgets.QVBoxLayout(self.graph)
        self.graphLayout.addWidget(self.graphCanvas)

        # Forbered et område for matplotlib-plotting inne i 'graph2'-widgeten
        self.graph2Canvas = FigureCanvas(Figure())
        self.graph2Layout = QtWidgets.QVBoxLayout(self.graph2)  # Opprett QVBoxLayout for 'graph2' widget
        self.graph2Layout.addWidget(self.graph2Canvas)

        self.current_date = datetime.now()
        self.cached_data = {}

        self.highestPriceLabel = None
        self.lowestPriceLabel = None

        self.show_data()
        self.show_hourly_prices()

        self.monthlyCanvas = FigureCanvas(Figure())
        self.monthlyLayout = QtWidgets.QVBoxLayout(self.graph3)
        self.monthlyLayout.addWidget(self.monthlyCanvas)

        self.show_monthly_data()

        self.settingsButton.clicked.connect(self.open_settings)

        

    def show_data(self):
        config = load_config()
        raw_data = fetch_data(config)
        processed_data = process_data(raw_data)

        if processed_data:
            self.update_total_cost_widget(processed_data['total_cost'])
            self.update_total_consumption_widget(processed_data['total_consumption'])
            self.add_plot(processed_data)
            
    def show_hourly_prices(self):
        config = load_config()
        hourly_price_data = fetch_hourly_price_data(config)
        if hourly_price_data:
            self.update_hourly_price_chart(hourly_price_data)
            self.update_price_widgets(hourly_price_data)

    def update_hourly_price_chart(self, hourly_price_data):
        # Fjern den eksisterende grafen fra graph2Layout
        if self.graph2Canvas:
            self.graph2Layout.removeWidget(self.graph2Canvas)
            self.graph2Canvas.deleteLater()

        # Opprett en ny graf
        self.price_figure = Figure()
        self.price_canvas = FigureCanvas(self.price_figure)
        self.graph2Layout.addWidget(self.price_canvas)
        ax = self.price_figure.add_subplot(111)

        # Tegn grafen
        times = hourly_price_data['times']
        prices = hourly_price_data['prices']
        ax.plot(times, prices, color='tab:red')

        # Hent nåværende time og legg til en prikk og en tekstetikett på dette punktet i grafen
        hour = datetime.now().hour
        current_hour = f"{hour:02d}"

        if str(current_hour) in times:
            current_index = times.index(str(current_hour))
            current_price = prices[current_index]

            # Tegn en prikk for nåværende time og legg til tekst
            ax.scatter([current_hour], [current_price], color='red')
            ax.text(current_hour, current_price, f'{current_price:.2f} Kr', color='red', verticalalignment='bottom')

        # Sett akselabeler og tittel
        ax.set_xlabel('Time')
        ax.set_ylabel('Pris (NOK)')
        ax.set_title('Pris per time i dag')
        # Tegn grafen på nytt
        self.price_canvas.draw()

    

    def update_price_widgets(self, hourly_price_data):
        prices = hourly_price_data['prices']

        highest_price = max(prices)
        lowest_price = min(prices)

        if not self.highestPriceLabel:
            self.highestPriceLabel = QtWidgets.QLabel(self.widget3)
            self.highestPriceLabel.setAlignment(Qt.AlignCenter)
            self.highestPriceLabel.setGeometry(10, 10, 371, 60)

        font = QFont("Arial", 16, QFont.Bold)
        self.highestPriceLabel.setFont(font)
        self.highestPriceLabel.setStyleSheet("QLabel { color : red; }")
        self.highestPriceLabel.setText(f"Høyest Pris idag: {highest_price:.2f} Kr")
        self.highestPriceLabel.show()

        if not self.lowestPriceLabel:
            self.lowestPriceLabel = QtWidgets.QLabel(self.widget4)
            self.lowestPriceLabel.setAlignment(Qt.AlignCenter)
            self.lowestPriceLabel.setGeometry(10, 10, 371, 60)
        font = QFont("Arial", 16, QFont.Bold)
        self.lowestPriceLabel.setFont(font)
        self.lowestPriceLabel.setStyleSheet("QLabel { color : green; }")
        self.lowestPriceLabel.setText(f"Lavest Pris idag: {lowest_price:.2f} Kr")
        self.lowestPriceLabel.show()



    def update_total_cost_widget(self, total_cost):
        self.totalCostLabel = QtWidgets.QLabel(self.widget1)
        self.totalCostLabel.setAlignment(Qt.AlignCenter)
        self.totalCostLabel.setGeometry(10, 10, 395, 60)  # Juster størrelsen og posisjonen etter behov

        # Sett opp stil og font
        font = QFont("Arial", 16, QFont.Bold)
        self.totalCostLabel.setFont(font)
        self.totalCostLabel.setStyleSheet("QLabel { color : red; }")  # Juster farge og stil

        self.totalCostLabel.setText(f"Total Kostnad: {total_cost:.2f} kr")
        
    def update_total_consumption_widget(self, total_consumption):
        self.totalConsumptionLabel = QtWidgets.QLabel(self.widget2)
        self.totalConsumptionLabel.setAlignment(Qt.AlignCenter)
        self.totalConsumptionLabel.setGeometry(10, 10, 395, 60)  # Juster størrelsen og posisjonen etter behov

        # Sett opp stil og font
        font = QFont("Arial", 16, QFont.Bold)
        self.totalConsumptionLabel.setFont(font)
        self.totalConsumptionLabel.setStyleSheet("QLabel { color : yellow; }")  # Juster farge og stil

        self.totalConsumptionLabel.setText(f"Totalt Forbruk: {total_consumption:.2f} kWh")


    def add_plot(self, data):
            

            ax = self.graphCanvas.figure.subplots()
            ax.clear()
            
            today = datetime.today()
            total_days = calendar.monthrange(today.year, today.month)[1]
            all_dates = [datetime(today.year, today.month, day) for day in range(1, total_days + 1)]
            date_strings = [date.strftime("%Y-%m-%d") for date in all_dates]



            # Forbruk
            consumption_values = [0] * total_days  # Initialiser med nullverdier
            for i, date in enumerate(data['dates']):
                if date in date_strings:
                    index = date_strings.index(date)
                    consumption_values[index] = data['consumption'][i]

            # Kostnad
            cost_values = [0] * total_days  # Initialiser med nullverdier
            for i, date in enumerate(data['dates']):
                if date in date_strings:
                    index = date_strings.index(date)
                    cost_values[index] = data['cost'][i]

            # Plott
            bars = ax.bar(date_strings, consumption_values, label='Forbruk (kWh)', color='yellow')
            ax.plot(date_strings, cost_values, label='Kostnad (Kr)', color='red')

            # Lager en annotasjon, men gjør den usynlig først
            annot = ax.annotate("", xy=(0,0), xytext=(20,20),
                                textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="white", ec="black", lw=2),
                                arrowprops=dict(arrowstyle="-", color="black"))
            annot.set_visible(False)

            def update_annot(bar):
                x = bar.get_x() + bar.get_width() / 2
                y = bar.get_height()
                annot.xy = (x, y)
                text = f"{y:.2f} kWh"
                annot.set_text(text)
                annot.get_bbox_patch().set_facecolor('white')  # Setter bakgrunnen til annotasjonen til hvit
                annot.get_bbox_patch().set_alpha(0.8)  # Justerer transparensen til annotasjonens bakgrunn
                annot.get_bbox_patch().set_edgecolor('black')  # Setter kanten til annotasjonen til svart
                annot.set_color('black')  # Setter teksten til svart

            def hover(event):
                vis = annot.get_visible()
                if event.inaxes == ax:
                    for bar in bars:
                        cont, _ = bar.contains(event)
                        if cont:
                            update_annot(bar)
                            annot.set_visible(True)
                            self.graphCanvas.draw_idle()
                            return
                if vis:
                    annot.set_visible(False)
                    self.graphCanvas.draw_idle()


            # Koble hendelsesbehandleren til hover-hendelsen
            self.graphCanvas.mpl_connect("motion_notify_event", hover)

            ax.set_xlabel('Dag')
            ax.set_ylabel('Verdier')
            ax.set_title('Forbruk hittill denne måneden')
            ax.legend()
            ax.set_xticklabels([date.strftime("%d") for date in all_dates])
            self.graphCanvas.draw()

    def show_monthly_data(self):
        config = load_config()
        raw_monthly_data = fetch_monthly_data(config)
        processed_monthly_data = process_monthly_data(raw_monthly_data)
        if processed_monthly_data:
            self.plot_monthly_data(processed_monthly_data)

    def plot_monthly_data(self, processed_data):
        ax = self.monthlyCanvas.figure.subplots()
        ax.clear()


        month_labels = processed_data['dates']
        consumption_values = processed_data['consumption']
        cost_values = processed_data['cost']


        bars = ax.bar(month_labels, consumption_values, label='Forbruk (kWh)', color='yellow')
        ax.plot(month_labels, cost_values, label='Kostnad (Kr)', color='red')



        annot = ax.annotate("", xy=(0,0), xytext=(20,20),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="white", ec="black", lw=2),
                            arrowprops=dict(arrowstyle="->", color="black"))
        annot.set_visible(False)

        def update_annot(bar):
            x = bar.get_x() + bar.get_width() / 2
            y = bar.get_height()
            annot.xy = (x, y)
            text = f"{y:.2f} kWh"
            annot.set_text(text)
            annot.get_bbox_patch().set_facecolor('white')  # Setter bakgrunnen til annotasjonen til hvit
            annot.get_bbox_patch().set_alpha(0.8)  # Justerer transparensen til annotasjonens bakgrunn
            annot.get_bbox_patch().set_edgecolor('black')  # Setter kanten til annotasjonen til svart
            annot.set_color('black')

        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                for bar in bars:
                    cont, _ = bar.contains(event)
                    if cont:
                        update_annot(bar)
                        annot.set_visible(True)
                        self.monthlyCanvas.draw_idle()
                        return
            if vis:
                annot.set_visible(False)
                self.monthlyCanvas.draw_idle()

        # Koble hendelsesbehandleren til hover-hendelsen
        self.monthlyCanvas.mpl_connect("motion_notify_event", hover)

        ax.set_xlabel('Måned')
        ax.set_ylabel('Verdier')
        ax.set_title('Forbruk og Kostnad Siste 12 Måneder')
        ax.legend()
        self.monthlyCanvas.draw()



    def open_settings(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    main_app = MainApp()
    main_app.show()
    app.exec_()
