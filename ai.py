from PyQt5 import QtWidgets, QtCore, QtGui
import random
import math
from api_client import fetch_data
from data_processor import process_data
from config_manager import load_config
import ai_logic

class Node(QtCore.QObject):
    def __init__(self, x, y, parent=None):
        super(Node, self).__init__(parent)
        self.x = x
        self.y = y
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.speed = random.uniform(0.5, 1.5)

    def move(self, width, height):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        if self.x <= 0 or self.x >= width:
            self.dx = -self.dx
        if self.y <= 0 or self.y >= height:
            self.dy = -self.dy

class NetworkGraphics(QtWidgets.QGraphicsItem):
    def __init__(self, width, height, parent=None):
        super(NetworkGraphics, self).__init__(parent)
        self.width = width
        self.height = height
        self.nodes = [Node(random.randint(0, width), random.randint(0, height)) for _ in range(75)]
        self.connections = {}

    def paint(self, painter, option, widget):
        for node in self.nodes:
            for other_node in self.nodes:
                distance = math.hypot(node.x - other_node.x, node.y - other_node.y)
                if distance < 100:
                    key = tuple(sorted(((node.x, node.y), (other_node.x, other_node.y))))
                    self.connections[key] = min(self.connections.get(key, 0) + 10, 255)
                    alpha = self.connections[key]
                    painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, alpha), 1))
                    painter.drawLine(QtCore.QPointF(node.x, node.y), QtCore.QPointF(other_node.x, other_node.y))
                else:
                    key = tuple(sorted(((node.x, node.y), (other_node.x, other_node.y))))
                    if key in self.connections:
                        self.connections[key] = max(self.connections[key] - 10, 0)



    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.width, self.height)



    def updatePositions(self):
        for node in self.nodes:
            node.move(self.width, self.height)
        self.update()

class AIDemoWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AIDemoWidget, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        
        # Opprett og konfigurer QGraphicsView og QGraphicsScene
        self.graphics_view = QtWidgets.QGraphicsView(self)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)
        self.graphics_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphics_view.setMinimumSize(820, 550)
        self.graphics_view.setStyleSheet("background: transparent")
        self.scene.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.transparent))

        # Legg til NetworkGraphics i scenen
        self.networkItem = NetworkGraphics(self.graphics_view.width(), self.graphics_view.height())
        self.scene.addItem(self.networkItem)

        # Opprett og legg til AI-grafen som en QGraphicsWidget
        self.ai_graph_canvas = ai_logic.create_ai_graph_widget(None)  # Start uten initial data
        self.ai_graph_widget = self.scene.addWidget(self.ai_graph_canvas)
        self.ai_graph_widget.setGeometry(QtCore.QRectF(10, 50, 801, 391))
        self.ai_graph_widget.setZValue(1)

        # Opprett og konfigurer QLabel for ai_widget
        ai_widget_label = QtWidgets.QLabel()
        ai_widget_label.setStyleSheet("background: transparent; color: yellow; font-size: 16px")
        # Tekst vil bli oppdatert i update_ai_graph

        # Opprett og konfigurer QLabel for ai_widget2
        ai_widget2_label = QtWidgets.QLabel()
        ai_widget2_label.setStyleSheet("background: transparent; color: red; font-size: 16px")
        # Tekst vil bli oppdatert i update_ai_graph

        # Konverter QLabel til QGraphicsProxyWidget og legg dem til i scenen
        self.ai_widget_proxy = self.scene.addWidget(ai_widget_label)
        self.ai_widget_proxy.setPos(10, 500)
        self.ai_widget_proxy.setZValue(2)

        self.ai_widget2_proxy = self.scene.addWidget(ai_widget2_label)
        self.ai_widget2_proxy.setPos(350, 500)
        self.ai_widget2_proxy.setZValue(2)

        # Oppdater grafen med faktiske data og forutsigelser
        self.update_ai_graph()

        # Start timer for animasjon
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.networkItem.updatePositions)
        self.timer.start(50)

    def update_ai_graph(self):
        config = load_config()
        raw_data = fetch_data(config)
        processed_data = process_data(raw_data)

        if processed_data:
            self.ai_graph_canvas = ai_logic.create_ai_graph_widget(processed_data)
            self.ai_graph_widget = self.scene.addWidget(self.ai_graph_canvas)
            self.ai_graph_widget.setGeometry(QtCore.QRectF(10, 50, 801, 391))
            self.ai_graph_widget.setZValue(1)
        else:
            print("Ingen historiske data tilgjengelig for å oppdatere grafen")


    def resizeEvent(self, event):
        new_width = self.graphics_view.width()
        new_height = self.graphics_view.height()
        self.networkItem.prepareGeometryChange()
        self.networkItem.width = new_width
        self.networkItem.height = new_height
        self.ai_graph_widget.setGeometry(QtCore.QRectF(10, 50, 801, 391))
        self.ai_widget_proxy.setPos(10, 500)
        self.ai_widget2_proxy.setPos(350, 500)
        super(AIDemoWidget, self).resizeEvent(event)
