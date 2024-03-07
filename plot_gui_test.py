import sys
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel

from plot_csv import plot

# used to test making gui in separate file before moved into main gui file


class PlotGui(QWidget):
    def __init__(self):
        super().__init__()

        self.setLayout(layout)

        canvas = self.create_plot()
        layout.addWidget(canvas)

    def create_plot(self):
        fig, axs = plot(pd.read_csv('chb01_01.csv'), ['FP1-F7', 'F7-T7'],1,120)
        canvas = FigureCanvas(fig)

        return canvas

app = QApplication(sys.argv)
layout = QVBoxLayout()
button = QPushButton("test")
layout.addWidget(button)


window = PlotGui()

window.show()
sys.exit(app.exec_())