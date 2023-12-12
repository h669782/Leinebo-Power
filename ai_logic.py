from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
import random
from api_client import fetch_data
from data_processor import process_data
from config_manager import load_config
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import requests
from datetime import datetime
import calendar
from PyQt5 import QtWidgets, QtCore, QtGui

def generate_fake_ai_predictions():
    # Generer fiktive data for demonstrasjonsformål
    today = datetime.today()
    future_dates = [today + timedelta(days=i) for i in range(30)]
    future_consumption = [random.uniform(10, 20) for _ in future_dates]
    future_cost = [random.uniform(5, 15) for _ in future_dates]
    return future_dates, future_consumption, future_cost

def create_ai_graph_widget(processed_data):
        figure = Figure(figsize=(5, 3), dpi=100, facecolor='none', edgecolor='none', frameon=False)
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)
        ax.patch.set_alpha(0.0)  # Gjør aksebakgrunnen gjennomsiktig

        if processed_data is not None:
            # Tegn historiske data
            dates = processed_data['dates']
            consumption = processed_data['consumption']
            cost = processed_data['cost']
            ax.plot(dates, consumption, label='Forbruk (kWh)', color='yellow')
            ax.plot(dates, cost, label='Kostnad (NOK)', color='red')
        ax.legend()
        ax.set_xlabel('Dato')
        ax.set_ylabel('Verdier')
        ax.set_title('Leinebo AI [FEIL: 4186]')
        ax.tick_params(axis='x', rotation=45)

        canvas.setStyleSheet("background: transparent")
        return canvas


def update_ai_graph(self):
    config = load_config()
    raw_data = fetch_data(config)
    processed_data = process_data(raw_data)

    if processed_data:
        self.ai_graph_canvas = create_ai_graph_widget(processed_data)
        self.ai_graph_widget = self.scene.addWidget(self.ai_graph_canvas)
        self.ai_graph_widget.setGeometry(QtCore.QRectF(0, 0, 800, 450))
        self.ai_graph_widget.setZValue(1)


from datetime import datetime, timedelta
import calendar

