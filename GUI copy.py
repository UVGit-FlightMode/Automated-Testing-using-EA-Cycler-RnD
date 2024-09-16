import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTabWidget, QTextEdit, QGridLayout, QFrame, QSizePolicy, QSpacerItem, QDialog, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog, QMessageBox, QStackedWidget
from PyQt5.QtGui import QPixmap, QFont, QIcon
import threading
import time
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal,Qt, QTimer
import pyqtgraph as pg
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
import csv

#Common Paramters
AllData = ['Slot1','Millis','FET_ON_OFF','CFET ON/OFF','FET TEMP1','DSG_VOLT','SC Current',
    'DSG_Current','CHG_VOLT','CHG_Current','DSG Time','CHG Time','DSG Charge','CHG Charge',
    'Cell1','Cell2','Cell3','Cell4','Cell5','Cell6','Cell7','Cell8','Cell9','Cell10','Cell11',
    'Cell12','Cell13','Cell14','Cell Delta Volt','Sum-of-cells','DSG Power','DSG Energy','CHG Power',
    'CHG Energy','Min CV','BAL_ON_OFF','TS1','TS2','TS3','TS4','TS5','TS6','TS7','TS8','TS9',
    'TS10','TS11','TS12','FET Temp Front','BAT + ve Temp','BAT - ve Temp','Pack + ve Temp','TS0_FLT',
    'TS13_FLT','FET_TEMP_REAR','DSG INA','BAL_RES_TEMP','HUM','IMON','Hydrogen','FG_CELL_VOLT',
    'FG_PACK_VOLT','FG_AVG_CURN','SOC','MAX_TTE','MAX_TTF','REPORTED_CAP','TS0_FLT1','IR','Cycles','DS_CAP',
    'FSTAT','VFSOC','CURR','CAP_NOM','REP_CAP.1','AGE','AGE_FCAST','QH','ICHGTERM','DQACC','DPACC','QRESIDUAL','MIXCAP']
GUI2SerialConnectionCycler = None
GraphValv = 20000

#GUI1 Parameter
GUI1GlobalFilePathBMS = None
GUI1SerialConnectionVCU = None
GUI1GlobalDictionary = {}
GUI1ConnectionCompleted = None
GUI1StatusMessages = []
GUI1ErrorMessages = []
GUI1AllThreads = []
GUI1StopButtonClicked = None
GUI1TimeSeriesX = 0
GUI1RoundingValvCheck = 4

#GUI2 Parameters
GUI2AllThreads = []
GUI2GlobalDictionary = {}
GUI2SerialConnectionVCU = None
GUI2ConnectionCompleted = None
GUI2StopButtonClicked = None
GUI2GlobalFilePathBMS = None
GUI2StatusMessages = []
GUI2ErrorMessages = []
GUI2RoundingValvCheck = 4
GUI2TimeSeriesX = 0
GUI2StepProcedure = None
GUI2GlobalFilePathCycler = None
GUI2CyclingStatus = None
GUI2PortAssignedToCycler = None
GUI2CyclerData = {}
GUI2FirstSinkPowerValue = None
GUI2FirstSinkCapacityValue = None
GUI2FirstSourcePowerValue = None
GUI2FirstSourceCapacityValue = None
GUI2StepParm = None

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("RnD Cycling Test Automation")
        
        # Create the stacked widget
        self.stacked_widget = QStackedWidget()
        
        initial_widget = QWidget()
        self.initalLayoutFinal = QVBoxLayout()
        initial_layout = QHBoxLayout()
        initial_layout.setAlignment(Qt.AlignCenter)
        initial_layout.setSpacing(20)
        self.Initialbutton1 = QPushButton("Open GUI 1")
        self.Initialbutton1.clicked.connect(self.GUI1show)
        self.Initialbutton1.setMinimumSize(150, 50)  # Set a minimum size for the buttons
        initial_layout.addWidget(self.Initialbutton1)
        self.Initialbutton2 = QPushButton("Open GUI 2")
        self.Initialbutton2.clicked.connect(self.GUI2show)
        self.Initialbutton2.setMinimumSize(150, 50)  # Set a minimum size for the buttons
        initial_layout.addWidget(self.Initialbutton2)
        self.InitialImage()
        self.initalLayoutFinal.addLayout(initial_layout)
        initial_widget.setLayout(self.initalLayoutFinal)
        self.stacked_widget.addWidget(initial_widget)
        
        # Create GUI 1 layout
        self.gui1_widget = QWidget()
        self.Gui1DivisionalLayout = QVBoxLayout()
        self.Gui1MainLayout = QHBoxLayout()
        self.Gui1FinalLayout = QVBoxLayout()
        self.GUI1Image()
        self.GUI1Buttons()
        self.GUI1StatusDataLabels()
        self.GUI1Tabs()
        GUI1Outerframe = QFrame()
        GUI1Outerframe.setLayout(self.Gui1DivisionalLayout)
        GUI1Outerframe.setFrameShape(QFrame.Box)
        GUI1Outerframe.setFrameShadow(QFrame.Raised)
        GUI1Outerframe.setLineWidth(5)
        self.Gui1MainLayout.addWidget(GUI1Outerframe)
        self.GUI1StatusErrorResult()
        self.Gui1FinalLayout.addLayout(self.Gui1MainLayout)
        self.gui1_widget.setLayout(self.Gui1FinalLayout)
        self.stacked_widget.addWidget(self.gui1_widget)

        # Create GUI 2 layout
        self.gui2_widget = QWidget()
        self.Gui2DivisionalLayout = QVBoxLayout()
        self.Gui2MainLayout = QHBoxLayout()
        self.Gui2FinalLayout = QVBoxLayout()
        self.GUI2Image()
        self.GUI2Buttons()
        self.GUI2StatusDataLabels()
        self.GUI2Tabs()
        GUI2Outerframe = QFrame()
        GUI2Outerframe.setLayout(self.Gui2DivisionalLayout)
        GUI2Outerframe.setFrameShape(QFrame.Box)
        GUI2Outerframe.setFrameShadow(QFrame.Raised)
        GUI2Outerframe.setLineWidth(5)
        self.Gui2MainLayout.addWidget(GUI2Outerframe)
        self.GUI2StatusErrorResult()
        self.Gui2FinalLayout.addLayout(self.Gui2MainLayout)
        self.gui2_widget.setLayout(self.Gui2FinalLayout)
        self.stacked_widget.addWidget(self.gui2_widget)
        
        # Set the stacked widget as the central widget
        self.setCentralWidget(self.stacked_widget)
    
    def show_initial(self):
        self.stacked_widget.setCurrentIndex(0)
    
    def InitialImage(self):
        ImageName = "UV_LOGO.png"
        pixmap = QPixmap(ImageName)
        pixmap = pixmap.scaled(500, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Adjust size as needed
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        spacer = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.initalLayoutFinal.addWidget(image_label)

    def GUI1show(self):
        global GUI1AllThreads

        #Stack 1
        self.stacked_widget.setCurrentIndex(1)

        #Threads
        self.GUI1DataLoggingThread = GUI1DataLoggingVCU()
        self.GUI1DataLoggingThread.start()
        GUI1AllThreads.append(self.GUI1DataLoggingThread)

        #LiveDataStoring
        self.GUI1LiveDataStoringThread = GUI1liveDataStoring()
        self.GUI1LiveDataStoringThread.start()
        GUI1AllThreads.append(self.GUI1LiveDataStoringThread)

        #All Display threads
        self.GUI1AllDisplayThreads = GUI1DisplayThreads()
        self.GUI1AllDisplayThreads.StatusBoxUpdate.connect(self.GUI1UpdateStatusDisplayBox)
        self.GUI1AllDisplayThreads.ErrorBoxUpdate.connect(self.GUI1UpdateErrorDisplayBox)
        self.GUI1AllDisplayThreads.StatusDataUpdate.connect(self.GUI1UpdateStatusParms)
        self.GUI1AllDisplayThreads.BMSDataUpdate.connect(self.GUI1UpdateBMSParms)
        self.GUI1AllDisplayThreads.GraphStatusUpdate.connect(self.GUI1UpdatePlot)
        self.GUI1AllDisplayThreads.start()
        GUI1AllThreads.append(self.GUI1AllDisplayThreads)

    def GUI1Image(self):
        ImageName = "UV_LOGO.png"
        pixmap = QPixmap(ImageName)
        pixmap = pixmap.scaled(500, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Adjust size as needed
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        spacer = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.Gui1FinalLayout.addWidget(image_label)

    def GUI1Buttons(self):
        ButtonsLayout = QHBoxLayout()
        self.GUI1button1 = QPushButton("Set Location")
        self.GUI1button2 = QPushButton("Connect and Start")
        self.GUI1button3 = QPushButton("Stop and Reset")

        # Set button sizes individually
        self.GUI1button1.setFixedSize(350, 50)  # Width: 120, Height: 50
        self.GUI1button2.setFixedSize(350, 50)  # Width: 130, Height: 50
        self.GUI1button3.setFixedSize(350, 50)  # Width: 130, Height: 50

        #Styling Buttons
        button1_style = ('''
        QPushButton {background-color: #FFD4A3; color: black; font-size: 16px; font-family: Arial; border-radius: 10px; border: 2px solid #FFAB5F; padding: 10px;}
        QPushButton:hover {background-color: #FFE3C2;}
        QPushButton:pressed {background-color: #E3A07D; border: 2px solid #E3A07D; padding-left: 12px; padding-top: 12px;}
        QPushButton:disabled {background-color: #E0E0E0; color: #A0A0A0; border: 1px solid #A0A0A0;}
        ''')
        button2_style = ('''
        QPushButton {background-color: #A3DAFF; color: black; font-size: 16px; font-family: Arial; border-radius: 10px; border: 2px solid #5FBFFF; padding: 10px;}
        QPushButton:hover {background-color: #C2E6FF;}
        QPushButton:pressed {background-color: #7DB8E3; border: 2px solid #7DB8E3; padding-left: 12px; padding-top: 12px;}
        QPushButton:disabled {background-color: #E0E0E0; color: #A0A0A0; border: 1px solid #A0A0A0;}
        ''')
        button3_style = ('''
        QPushButton {background-color: #FFA3A3; color: black; font-size: 16px; font-family: Arial; border-radius: 10px; border: 2px solid #FF5F5F; padding: 10px;}
        QPushButton:hover {background-color: #FFC2C2;}
        QPushButton:pressed {background-color: #E37D7D; border: 2px solid #E37D7D; padding-left: 12px; padding-top: 12px;}
        QPushButton:disabled {background-color: #E0E0E0; color: #A0A0A0; border: 1px solid #A0A0A0;}
        ''')

        self.GUI1button1.setStyleSheet(button1_style)
        self.GUI1button2.setStyleSheet(button2_style)
        self.GUI1button3.setStyleSheet(button3_style)

        ButtonsLayout.addWidget(self.GUI1button1)
        ButtonsLayout.addWidget(self.GUI1button2)
        ButtonsLayout.addWidget(self.GUI1button3)

        self.GUI1button1.clicked.connect(self.GUI1SaveBMSDataGUI)
        self.GUI1button2.clicked.connect(self.GUI1ConnectButtonClicked)
        self.GUI1button3.clicked.connect(self.GUI1StopButtonTask)

        self.Gui1FinalLayout.addLayout(ButtonsLayout)

    def GUI1StatusDataLabels(self):

        LabelsLayout = QHBoxLayout()

        def create_frame(label_text):
            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            frame.setLineWidth(1)
            frame.setFixedSize(180, 80)
            frame.setStyleSheet("""
                QFrame {
                    border: 1px solid black;
                    border-radius: 15px;
                    background-color: white;
                }
            """)

            frame_layout = QVBoxLayout()
            frame.setLayout(frame_layout)

            label1 = QLabel(label_text, frame)
            label1.setAlignment(Qt.AlignCenter)
            label1.setStyleSheet("font-weight: bold;")
            label1.setStyleSheet("font-size: 18px;")
            frame_layout.addWidget(label1)

            label2 = QLabel('None', frame)
            label2.setAlignment(Qt.AlignCenter)
            label2.setStyleSheet("font-size: 16px;")
            frame_layout.addWidget(label2)

            return frame, label2

        labels = [
            'DSG Current (A)',
            'CHG Current (A)',
            'FET Status',
            'Voltage (V)',
            'SoC (%)',
            'Max Temp (°C)',
            'Time',
            'Time'
        ]
        self.GUI1StatusLabels = []
        for text in labels:
            frame, label2 = create_frame(text)
            LabelsLayout.addWidget(frame)
            self.GUI1StatusLabels.append(label2)

        self.Gui1DivisionalLayout.addLayout(LabelsLayout)

    def GUI1Tabs(self):

        global AllData

        # Tab widget
        TabWidget = QTabWidget()

        tab1 = QWidget()
        Tab1Layout = QVBoxLayout()

        # Create a plot widget
        plotWidget2 = pg.PlotWidget()
        Tab1Layout.addWidget(plotWidget2)

        # Enable multiple y-axes
        plotWidget2.showAxis('right')
        plotWidget2.scene().sigMouseClicked.connect(self.GUI1mouseClicked)

        # Create another ViewBox for the second y-axis
        self.GUI1vb2 = pg.ViewBox()
        plotWidget2.scene().addItem(self.GUI1vb2)
        plotWidget2.getAxis('right').linkToView(self.GUI1vb2)
        self.GUI1vb2.setXLink(plotWidget2)
        
        # Connect the view of GUI1vb2 with plotWidget
        def updateViews():
            self.GUI1vb2.setGeometry(plotWidget2.getViewBox().sceneBoundingRect())
            self.GUI1vb2.linkedViewChanged(plotWidget2.getViewBox(), self.GUI1vb2.XAxis)
        
        plotWidget2.getViewBox().sigResized.connect(updateViews)

        # Initialize empty data
        self.GUI1x = []
        self.GUI1y1 = []
        self.GUI1y2 = []

        # Plot initial empty data
        self.GUI1curve1 = plotWidget2.plot(self.GUI1x, self.GUI1y1, pen=pg.mkPen(color='r', width=2), name="Voltage(V)")
        self.GUI1curve2 = pg.PlotCurveItem(self.GUI1x, self.GUI1y2, pen=pg.mkPen(color='b', width=2, style=Qt.DashLine), name="Current(A)")
        self.GUI1vb2.addItem(self.GUI1curve2)

        # Add grid lines
        plotWidget2.showGrid(x=True, y=True, alpha=0.3)

        # Add axis labels
        plotWidget2.setLabel('left', 'Voltage(V)', color='black')
        plotWidget2.setLabel('right', 'Current(A)', color='black')
        plotWidget2.setLabel('bottom', 'Time Series', color='black')

        # Add a title
        plotWidget2.setTitle('Voltage-Current vs Time', color='black', size='20pt')

        # Add a legend
        self.GUI1legend = plotWidget2.addLegend()
        self.GUI1legend.addItem(self.GUI1curve1, 'Voltage (V)')
        self.GUI1legend.addItem(self.GUI1curve2, 'Current (A)')
        self.GUI1legend.setParentItem(plotWidget2.getPlotItem())
        self.GUI1legend.anchor((0.025, 0.05), (0.025,0.05), offset=(10, 10))

        tab1.setLayout(Tab1Layout)
        TabWidget.addTab(tab1, "Graph")

        tab2 = QWidget()
        Tab2Layout = QGridLayout()

        self.GUI1AllLabels = []  # List to store the label references

        # Add 84 labels to tab2
        for i in range(84):
            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            frame.setLineWidth(1)

            # Create a vertical box layout for the frame
            vbox_layout = QVBoxLayout()
            vbox_layout.setAlignment(Qt.AlignCenter)
            vbox_layout.setSpacing(2)

            # Create two labels
            label_top = QLabel(AllData[i], frame)
            label_top.setAlignment(Qt.AlignCenter)
            label_top.setFont(QFont(label_top.font().family(), label_top.font().pointSize(), QFont.Bold))
            
            label_bottom = QLabel('None', frame)
            label_bottom.setAlignment(Qt.AlignCenter)

            font____ = label_bottom.font()
            font____.setPointSize(font____.pointSize() + 1)  # Increase font size by 2 points (adjust as needed)
            label_bottom.setFont(font____)

            # Add labels to the vertical box layout
            vbox_layout.addWidget(label_top)
            vbox_layout.addWidget(label_bottom)

            # Set the layout for the frame
            frame.setLayout(vbox_layout)

            Tab2Layout.addWidget(frame, i // 9, i % 9)  # 7 columns in a row
            self.GUI1AllLabels.append(label_bottom)
        
        tab2.setLayout(Tab2Layout)
        TabWidget.addTab(tab2, "BMS Data")
        TabWidget.setStyleSheet("""
        QTabBar::tab {
            height: 10px; 
            width: 100px; 
            font-size: 12px; 
            padding: 10px;
        }
        QTabBar::tab:selected {
            background: #dcdcdc;
        }
        """)
        self.Gui1DivisionalLayout.addWidget(TabWidget)

    def GUI1mouseClicked(self, event):
        pass

    def GUI1StatusErrorResult(self):

        #Top Label
        TopLabel = QLabel("Status")
        font = TopLabel.font()
        font.setBold(True)
        font.setPointSize(16)
        TopLabel.setFont(font)
        TopLabel.setAlignment(Qt.AlignCenter)
        
        # Status display with heading
        statusLabel = QLabel("Status Logging")
        self.GUI1StatusDisplay = QTextEdit()
        self.GUI1StatusDisplay.setFixedWidth(350)
        
        # Error display with heading
        errorLabel = QLabel("Errors")
        self.GUI1ErrorDisplay = QTextEdit()
        self.GUI1ErrorDisplay.setFixedWidth(350)

        # Create a horizontal layout
        hLayout = QVBoxLayout()

        # Add labels and text edits to the horizontal layout
        vLayout2 = QVBoxLayout()
        vLayout2.addWidget(statusLabel)
        vLayout2.addWidget(self.GUI1StatusDisplay)
        
        vLayout3 = QVBoxLayout()
        vLayout3.addWidget(errorLabel)
        vLayout3.addWidget(self.GUI1ErrorDisplay)
        
        hLayout.addWidget(TopLabel)
        hLayout.addLayout(vLayout2)
        hLayout.addLayout(vLayout3)

        # Create a frame to surround the hLayout
        frame = QFrame()
        frame.setLayout(hLayout)
        frame.setFrameShape(QFrame.Box)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLineWidth(5)

        # Add the frame to the main layout
        self.Gui1MainLayout.addWidget(frame)

    def GUI1UpdateStatusDisplayBox(self, message):
        self.GUI1StatusDisplay.append(message)

    def GUI1UpdateErrorDisplayBox(self, message):
        self.GUI1ErrorDisplay.append(message)

    def GUI1UpdateStatusParms(self, DSGCurrentStat, CHGCurrentStat, FETStat, VoltageStat, SoCStat, MaxTemp, Timestamps1, Timestamps2):
        self.GUI1StatusLabels[0].setText(str(DSGCurrentStat))
        self.GUI1StatusLabels[1].setText(str(CHGCurrentStat))
        self.GUI1StatusLabels[2].setText(str(FETStat))
        self.GUI1StatusLabels[3].setText(str(VoltageStat))
        self.GUI1StatusLabels[4].setText(str(SoCStat))
        self.GUI1StatusLabels[5].setText(str(MaxTemp))
        self.GUI1StatusLabels[6].setText(str(Timestamps1))
        self.GUI1StatusLabels[7].setText(str(Timestamps2))

    def GUI1UpdateBMSParms(self, Parmss):
        for iterateee in range(len(self.GUI1AllLabels)):
            self.GUI1AllLabels[iterateee].setText(str(Parmss[iterateee]))

    def GUI1UpdatePlot(self, new_x, new_y1, new_y2):
        global GraphValv
        # Update data
        if len(self.GUI1x) <= int(GraphValv):
            self.GUI1x.append(new_x)
            self.GUI1y1.append(new_y1)
            self.GUI1y2.append(new_y2)
            self.GUI1curve1.setData(self.GUI1x, self.GUI1y1)
            self.GUI1curve2.setData(self.GUI1x, self.GUI1y2)
        else:
            self.GUI1x = self.GUI1x[int(GraphValv/2):]
            self.GUI1y1 = self.GUI1y1[int(GraphValv/2):]
            self.GUI1y2 = self.GUI1y2[int(GraphValv/2):]

            self.GUI1x.append(new_x)
            self.GUI1y1.append(new_y1)
            self.GUI1y2.append(new_y2)
            self.GUI1curve1.setData(self.GUI1x, self.GUI1y1)
            self.GUI1curve2.setData(self.GUI1x, self.GUI1y2)

    def GUI1ConnectButtonClicked(self):
        global GUI1AllThreads
        self.GUI1ConnectButtonThread = GUI1ConnectButton()
        self.GUI1ConnectButtonThread.start()
        GUI1AllThreads.append(self.GUI1ConnectButtonThread)

    def GUI1StopButtonTask(self):
        self.GUI1StopButtonThread = GUI1StopButton()
        self.GUI1StopButtonThread.Signal1.connect(self.GUI1intializeDisplays)
        self.GUI1StopButtonThread.Signal2.connect(self.GUI1CallAllThreads)
        self.GUI1StopButtonThread.start()

    def GUI1intializeDisplays(self):
        #Initialize graphs
        self.GUI1x = []
        self.GUI1y1 = []
        self.GUI1y2 = []
        self.GUI1curve1.setData(self.GUI1x, self.GUI1y1)
        self.GUI1curve2.setData(self.GUI1x, self.GUI1y2)
        #Initialize Status Data
        for statuslabelsiterate in range(len(self.GUI1StatusLabels)):
            self.GUI1StatusLabels[statuslabelsiterate].setText(str('None'))
        #Initialize BMS Data
        for BMSlabelsiterate in range(len(self.GUI1AllLabels)):
            self.GUI1AllLabels[BMSlabelsiterate].setText(str('None'))
        #Clear Status Display
        self.GUI1StatusDisplay.clear()
        #Clear Error Display
        self.GUI1ErrorDisplay.clear()

    def GUI1CallAllThreads(self):
        global GUI1AllThreads
        global GUI1StatusMessages

        #Threads
        self.GUI1DataLoggingThread = GUI1DataLoggingVCU()
        self.GUI1DataLoggingThread.start()
        GUI1AllThreads.append(self.GUI1DataLoggingThread)

        #LiveDataStoring
        self.GUI1LiveDataStoringThread = GUI1liveDataStoring()
        self.GUI1LiveDataStoringThread.start()
        GUI1AllThreads.append(self.GUI1LiveDataStoringThread)

        #All Display threads
        self.GUI1AllDisplayThreads = GUI1DisplayThreads()
        self.GUI1AllDisplayThreads.StatusBoxUpdate.connect(self.GUI1UpdateStatusDisplayBox)
        self.GUI1AllDisplayThreads.ErrorBoxUpdate.connect(self.GUI1UpdateErrorDisplayBox)
        self.GUI1AllDisplayThreads.StatusDataUpdate.connect(self.GUI1UpdateStatusParms)
        self.GUI1AllDisplayThreads.BMSDataUpdate.connect(self.GUI1UpdateBMSParms)
        self.GUI1AllDisplayThreads.GraphStatusUpdate.connect(self.GUI1UpdatePlot)
        self.GUI1AllDisplayThreads.start()
        GUI1AllThreads.append(self.GUI1AllDisplayThreads)

        #Updating message
        GUI1StatusMessages.append('Ready for Use...')

    def GUI1SaveBMSDataGUI(self):
        global GUI1GlobalFilePathBMS
        options = QFileDialog.Options()
        GUI1GlobalFilePathBMS, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv);;All Files (*)", options=options)


    def GUI2show(self):

        global GUI2AllThreads

        #Stack 2
        self.stacked_widget.setCurrentIndex(2)

        #Threads
        self.GUI2DataLoggingThread = GUI2DataLoggingVCU()
        self.GUI2DataLoggingThread.start()
        GUI2AllThreads.append(self.GUI2DataLoggingThread)

        #LiveDataStoring
        self.GUI2LiveDataStoringThread = GUI2liveDataStoring()
        self.GUI2LiveDataStoringThread.start()
        GUI2AllThreads.append(self.GUI2LiveDataStoringThread)

        #All Display threads
        self.GUI2AllDisplayThreads = GUI2DisplayThreads()
        self.GUI2AllDisplayThreads.StatusBoxUpdate.connect(self.GUI2UpdateStatusDisplayBox)
        self.GUI2AllDisplayThreads.ErrorBoxUpdate.connect(self.GUI2UpdateErrorDisplayBox)
        self.GUI2AllDisplayThreads.StatusDataUpdate.connect(self.GUI2UpdateStatusParms)
        self.GUI2AllDisplayThreads.BMSDataUpdate.connect(self.GUI2UpdateBMSParms)
        self.GUI2AllDisplayThreads.GraphStatusUpdate.connect(self.GUI2UpdatePlot)
        self.GUI2AllDisplayThreads.start()
        GUI2AllThreads.append(self.GUI2AllDisplayThreads)

    def GUI2Image(self):
        ImageName = "UV_LOGO.png"
        pixmap = QPixmap(ImageName)
        pixmap = pixmap.scaled(500, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Adjust size as needed
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        spacer = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.Gui2FinalLayout.addWidget(image_label)

    def GUI2Buttons(self):
        ButtonsLayout = QHBoxLayout()
        self.GUI2button1 = QPushButton("Process Settings")
        self.GUI2button2 = QPushButton("Connect")
        self.GUI2button3 = QPushButton("Start")
        self.GUI2button4 = QPushButton("Emergency Stop")
        # self.GUI2button6 = QPushButton("Go Back")

        # Set button sizes individually
        self.GUI2button1.setFixedSize(350, 50)  # Width: 120, Height: 50
        self.GUI2button2.setFixedSize(350, 50)  # Width: 130, Height: 50
        self.GUI2button3.setFixedSize(350, 50)  # Width: 140, Height: 50
        self.GUI2button4.setFixedSize(350, 50)  # Width: 150, Height: 50
        # self.GUI2button6.setFixedSize(300, 50)  # Width: 160, Height: 50

        #Styling Buttons
        button1_style = ('''
        QPushButton {background-color: #FFD4A3; color: black; font-size: 16px; font-family: Arial; border-radius: 10px; border: 2px solid #FFAB5F; padding: 10px;}
        QPushButton:hover {background-color: #FFE3C2;}
        QPushButton:pressed {background-color: #E3A07D; border: 2px solid #E3A07D; padding-left: 12px; padding-top: 12px;}
        QPushButton:disabled {background-color: #E0E0E0; color: #A0A0A0; border: 1px solid #A0A0A0;}
        ''')
        button2_style = ('''
        QPushButton {background-color: #A3DAFF; color: black; font-size: 16px; font-family: Arial; border-radius: 10px; border: 2px solid #5FBFFF; padding: 10px;}
        QPushButton:hover {background-color: #C2E6FF;}
        QPushButton:pressed {background-color: #7DB8E3; border: 2px solid #7DB8E3; padding-left: 12px; padding-top: 12px;}
        QPushButton:disabled {background-color: #E0E0E0; color: #A0A0A0; border: 1px solid #A0A0A0;}
        ''')
        button3_style = ('''
        QPushButton {background-color: #96FF8A; color: black; font-size: 16px; font-family: Arial; border-radius: 10px; border: 2px solid #4CFF38; padding: 10px;}
        QPushButton:hover {background-color: #B6FFB2;}
        QPushButton:pressed {background-color: #75D657; border: 2px solid #75D657; padding-left: 12px; padding-top: 12px;}
        QPushButton:disabled {/* Your disabled style here */background-color: #E0E0E0; /* Light gray background for disabled */color: #A0A0A0; /* Light gray text color for disabled *//* You can also adjust other properties to make it visually distinct */border: 1px solid #A0A0A0; /* Light gray border for disabled *//* Add any other styling you desire for disabled buttons */}
        ''')
        button4_style = ('''
        QPushButton {background-color: #FFA3A3; color: black; font-size: 16px; font-family: Arial; border-radius: 10px; border: 2px solid #FF5F5F; padding: 10px;}
        QPushButton:hover {background-color: #FFC2C2;}
        QPushButton:pressed {background-color: #E37D7D; border: 2px solid #E37D7D; padding-left: 12px; padding-top: 12px;}
        QPushButton:disabled {background-color: #E0E0E0; color: #A0A0A0; border: 1px solid #A0A0A0;}
        ''')
        # button6_style = ('''
        # QPushButton {background-color: #FFD700; color: black; font-size: 16px; font-family: Arial; border-radius: 10px; border: 2px solid #FFC300; padding: 10px;}
        # QPushButton:hover {background-color: #FFE066;}
        # QPushButton:pressed {background-color: #FFB300; border: 2px solid #FFB300; padding-left: 12px; padding-top: 12px;}
        # QPushButton:disabled {background-color: #E0E0E0; color: #A0A0A0; border: 1px solid #A0A0A0;}
        # ''')

        self.GUI2button1.setStyleSheet(button1_style)
        self.GUI2button2.setStyleSheet(button2_style)
        self.GUI2button3.setStyleSheet(button3_style)
        self.GUI2button4.setStyleSheet(button4_style)
        # self.GUI2button6.setStyleSheet(button6_style)

        ButtonsLayout.addWidget(self.GUI2button1)
        ButtonsLayout.addWidget(self.GUI2button2)
        ButtonsLayout.addWidget(self.GUI2button3)
        ButtonsLayout.addWidget(self.GUI2button4)
        # ButtonsLayout.addWidget(self.GUI2button6)

        self.GUI2button1.clicked.connect(self.GUI2ProcessSettingsButtonClicked)
        self.GUI2button2.clicked.connect(self.GUI2ConnectButtonClicked)
        self.GUI2button3.clicked.connect(self.GUI2StartButtonClicked)
        self.GUI2button4.clicked.connect(self.GUI2StopButtonTask)
        # self.GUI2button6.clicked.connect(self.show_initial)

        self.Gui2FinalLayout.addLayout(ButtonsLayout)

    def GUI2StatusDataLabels(self):

        LabelsLayout = QHBoxLayout()

        def create_frame(label_text):
            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            frame.setLineWidth(1)
            frame.setFixedSize(180, 80)
            frame.setStyleSheet("""
                QFrame {
                    border: 1px solid black;
                    border-radius: 15px;
                    background-color: white;
                }
            """)

            frame_layout = QVBoxLayout()
            frame.setLayout(frame_layout)

            label1 = QLabel(label_text, frame)
            label1.setAlignment(Qt.AlignCenter)
            label1.setStyleSheet("font-weight: bold;")
            label1.setStyleSheet("font-size: 18px;")
            frame_layout.addWidget(label1)

            label2 = QLabel('None', frame)
            label2.setAlignment(Qt.AlignCenter)
            label2.setStyleSheet("font-size: 16px;")
            frame_layout.addWidget(label2)

            return frame, label2

        labels = [
            'DSG Current (A)',
            'CHG Current (A)',
            'FET Status',
            'Voltage (V)',
            'SoC (%)',
            'Max Temp (°C)',
            'Time',
            'Time'
        ]
        self.GUI2StatusLabels = []
        for text in labels:
            frame, label2 = create_frame(text)
            LabelsLayout.addWidget(frame)
            self.GUI2StatusLabels.append(label2)

        self.Gui2DivisionalLayout.addLayout(LabelsLayout)

    def GUI2Tabs(self):

        global AllData

        # Tab widget
        TabWidget = QTabWidget()

        tab1 = QWidget()
        Tab1Layout = QVBoxLayout()

        # Create a plot widget
        plotWidget2 = pg.PlotWidget()
        Tab1Layout.addWidget(plotWidget2)

        # Enable multiple y-axes
        plotWidget2.showAxis('right')
        plotWidget2.scene().sigMouseClicked.connect(self.GUI2mouseClicked)

        # Create another ViewBox for the second y-axis
        self.GUI2vb2 = pg.ViewBox()
        plotWidget2.scene().addItem(self.GUI2vb2)
        plotWidget2.getAxis('right').linkToView(self.GUI2vb2)
        self.GUI2vb2.setXLink(plotWidget2)
        
        # Connect the view of GUI2vb2 with plotWidget
        def updateViews():
            self.GUI2vb2.setGeometry(plotWidget2.getViewBox().sceneBoundingRect())
            self.GUI2vb2.linkedViewChanged(plotWidget2.getViewBox(), self.GUI2vb2.XAxis)
        
        plotWidget2.getViewBox().sigResized.connect(updateViews)

        # Initialize empty data
        self.GUI2x = []
        self.GUI2y1 = []
        self.GUI2y2 = []

        # Plot initial empty data
        self.GUI2curve1 = plotWidget2.plot(self.GUI2x, self.GUI2y1, pen=pg.mkPen(color='r', width=2), name="Voltage(V)")
        self.GUI2curve2 = pg.PlotCurveItem(self.GUI2x, self.GUI2y2, pen=pg.mkPen(color='b', width=2, style=Qt.DashLine), name="Current(A)")
        self.GUI2vb2.addItem(self.GUI2curve2)

        # Add grid lines
        plotWidget2.showGrid(x=True, y=True, alpha=0.3)

        # Add axis labels
        plotWidget2.setLabel('left', 'Voltage(V)', color='black')
        plotWidget2.setLabel('right', 'Current(A)', color='black')
        plotWidget2.setLabel('bottom', 'Time Series', color='black')

        # Add a title
        plotWidget2.setTitle('Voltage-Current vs Time', color='black', size='20pt')

        # Add a legend
        self.GUI2legend = plotWidget2.addLegend()
        self.GUI2legend.addItem(self.GUI2curve1, 'Voltage (V)')
        self.GUI2legend.addItem(self.GUI2curve2, 'Current (A)')
        self.GUI2legend.setParentItem(plotWidget2.getPlotItem())
        self.GUI2legend.anchor((0.025, 0.05), (0.025,0.05), offset=(10, 10))

        tab1.setLayout(Tab1Layout)
        TabWidget.addTab(tab1, "Graph")

        tab2 = QWidget()
        Tab2Layout = QGridLayout()

        self.GUI2AllLabels = []  # List to store the label references

        # Add 84 labels to tab2
        for i in range(84):
            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            frame.setLineWidth(1)

            # Create a vertical box layout for the frame
            vbox_layout = QVBoxLayout()
            vbox_layout.setAlignment(Qt.AlignCenter)
            vbox_layout.setSpacing(2)

            # Create two labels
            label_top = QLabel(AllData[i], frame)
            label_top.setAlignment(Qt.AlignCenter)
            label_top.setFont(QFont(label_top.font().family(), label_top.font().pointSize(), QFont.Bold))
            
            label_bottom = QLabel('None', frame)
            label_bottom.setAlignment(Qt.AlignCenter)

            font____ = label_bottom.font()
            font____.setPointSize(font____.pointSize() + 1)  # Increase font size by 2 points (adjust as needed)
            label_bottom.setFont(font____)

            # Add labels to the vertical box layout
            vbox_layout.addWidget(label_top)
            vbox_layout.addWidget(label_bottom)

            # Set the layout for the frame
            frame.setLayout(vbox_layout)

            Tab2Layout.addWidget(frame, i // 9, i % 9)  # 7 columns in a row
            self.GUI2AllLabels.append(label_bottom)
        
        tab2.setLayout(Tab2Layout)
        TabWidget.addTab(tab2, "BMS Data")
        TabWidget.setStyleSheet("""
        QTabBar::tab {
            height: 10px; 
            width: 100px; 
            font-size: 12px; 
            padding: 10px;
        }
        QTabBar::tab:selected {
            background: #dcdcdc;
        }
        """)
        self.Gui2DivisionalLayout.addWidget(TabWidget)

    def GUI2mouseClicked(self, event):
        pass

    def GUI2StatusErrorResult(self):

        #Top Label
        TopLabel = QLabel("Status")
        font = TopLabel.font()
        font.setBold(True)
        font.setPointSize(16)
        TopLabel.setFont(font)
        TopLabel.setAlignment(Qt.AlignCenter)
        
        # Status display with heading
        statusLabel = QLabel("Status Logging")
        self.GUI2StatusDisplay = QTextEdit()
        self.GUI2StatusDisplay.setFixedWidth(350)
        
        # Error display with heading
        errorLabel = QLabel("Errors")
        self.GUI2ErrorDisplay = QTextEdit()
        self.GUI2ErrorDisplay.setFixedWidth(350)

        # Create a horizontal layout
        hLayout = QVBoxLayout()

        # Add labels and text edits to the horizontal layout
        vLayout2 = QVBoxLayout()
        vLayout2.addWidget(statusLabel)
        vLayout2.addWidget(self.GUI2StatusDisplay)
        
        vLayout3 = QVBoxLayout()
        vLayout3.addWidget(errorLabel)
        vLayout3.addWidget(self.GUI2ErrorDisplay)
        
        hLayout.addWidget(TopLabel)
        hLayout.addLayout(vLayout2)
        hLayout.addLayout(vLayout3)

        # Create a frame to surround the hLayout
        frame = QFrame()
        frame.setLayout(hLayout)
        frame.setFrameShape(QFrame.Box)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLineWidth(5)

        # Add the frame to the main layout
        self.Gui2MainLayout.addWidget(frame)

    def GUI2UpdateStatusDisplayBox(self, message):
        self.GUI2StatusDisplay.append(message)

    def GUI2UpdateErrorDisplayBox(self, message):
        self.GUI2ErrorDisplay.append(message)

    def GUI2UpdateStatusParms(self, DSGCurrentStat, CHGCurrentStat, FETStat, VoltageStat, SoCStat, MaxTemp, Timestamps1, Timestamps2):
        self.GUI2StatusLabels[0].setText(str(DSGCurrentStat))
        self.GUI2StatusLabels[1].setText(str(CHGCurrentStat))
        self.GUI2StatusLabels[2].setText(str(FETStat))
        self.GUI2StatusLabels[3].setText(str(VoltageStat))
        self.GUI2StatusLabels[4].setText(str(SoCStat))
        self.GUI2StatusLabels[5].setText(str(MaxTemp))
        self.GUI2StatusLabels[6].setText(str(Timestamps1))
        self.GUI2StatusLabels[7].setText(str(Timestamps2))

    def GUI2UpdateBMSParms(self, Parmss):
        for iterateee in range(len(self.GUI2AllLabels)):
            self.GUI2AllLabels[iterateee].setText(str(Parmss[iterateee]))

    def GUI2UpdatePlot(self, new_x, new_y1, new_y2):
        global GraphValv
        # Update data
        if len(self.GUI2x) <= int(GraphValv):
            self.GUI2x.append(new_x)
            self.GUI2y1.append(new_y1)
            self.GUI2y2.append(new_y2)
            self.GUI2curve1.setData(self.GUI2x, self.GUI2y1)
            self.GUI2curve2.setData(self.GUI2x, self.GUI2y2)
        else:
            self.GUI2x = self.GUI2x[int(GraphValv/2):]
            self.GUI2y1 = self.GUI2y1[int(GraphValv/2):]
            self.GUI2y2 = self.GUI2y2[int(GraphValv/2):]

            self.GUI2x.append(new_x)
            self.GUI2y1.append(new_y1)
            self.GUI2y2.append(new_y2)
            self.GUI2curve1.setData(self.GUI2x, self.GUI2y1)
            self.GUI2curve2.setData(self.GUI2x, self.GUI2y2)

    def GUI2ConnectButtonClicked(self):
        global GUI2AllThreads
        self.GUI2ConnectButtonThread = GUI2ConnectButton()
        self.GUI2ConnectButtonThread.start()
        GUI2AllThreads.append(self.GUI2ConnectButtonThread)

    def GUI2ProcessSettingsButtonClicked(self):
        self.GUI2ProcessDefinationOpen = GUI2ProcessDefinationWindow()
        self.GUI2ProcessDefinationOpen.show()

    def GUI2StartButtonClicked(self):
        global GUI2AllThreads
        self.GUI2StartButtonThread = GUI2StartButton()
        self.GUI2StartButtonThread.start()
        GUI2AllThreads.append(self.GUI2StartButtonThread)

    def GUI2StopButtonTask(self):
        self.GUI2StopButtonThread = GUI2StopButton()
        self.GUI2StopButtonThread.Signal1.connect(self.GUI2intializeDisplays)
        self.GUI2StopButtonThread.Signal2.connect(self.GUI2CallAllThreads)
        self.GUI2StopButtonThread.start()

    def GUI2intializeDisplays(self):
        #Initialize graphs
        self.GUI2x = []
        self.GUI2y1 = []
        self.GUI2y2 = []
        self.GUI2curve1.setData(self.GUI2x, self.GUI2y1)
        self.GUI2curve2.setData(self.GUI2x, self.GUI2y2)
        #Initialize Status Data
        for statuslabelsiterate in range(len(self.GUI2StatusLabels)):
            self.GUI2StatusLabels[statuslabelsiterate].setText(str('None'))
        #Initialize BMS Data
        for BMSlabelsiterate in range(len(self.GUI2AllLabels)):
            self.GUI2AllLabels[BMSlabelsiterate].setText(str('None'))
        #Clear Status Display
        self.GUI2StatusDisplay.clear()
        #Clear Error Display
        self.GUI2ErrorDisplay.clear()

    def GUI2CallAllThreads(self):
        global GU2StatusMessages
        global GUI2AllThreads

        #Threads
        self.GUI2DataLoggingThread = GUI2DataLoggingVCU()
        self.GUI2DataLoggingThread.start()
        GUI2AllThreads.append(self.GUI2DataLoggingThread)

        #LiveDataStoring
        self.GUI2LiveDataStoringThread = GUI2liveDataStoring()
        self.GUI2LiveDataStoringThread.start()
        GUI2AllThreads.append(self.GUI2LiveDataStoringThread)

        #All Display threads
        self.GUI2AllDisplayThreads = GUI2DisplayThreads()
        self.GUI2AllDisplayThreads.StatusBoxUpdate.connect(self.GUI2UpdateStatusDisplayBox)
        self.GUI2AllDisplayThreads.ErrorBoxUpdate.connect(self.GUI2UpdateErrorDisplayBox)
        self.GUI2AllDisplayThreads.StatusDataUpdate.connect(self.GUI2UpdateStatusParms)
        self.GUI2AllDisplayThreads.BMSDataUpdate.connect(self.GUI2UpdateBMSParms)
        self.GUI2AllDisplayThreads.GraphStatusUpdate.connect(self.GUI2UpdatePlot)
        self.GUI2AllDisplayThreads.start()
        GUI2AllThreads.append(self.GUI2AllDisplayThreads)

        #Updating message
        GUI2StatusMessages.append('Ready for Use...')

    def closeEvent(self, event):
        # global GUI2SerialConnectionCycler
        # if GUI2SerialConnectionCycler:
        #     #Initialize Cycler
        #     GUI2SerialConnectionCycler.write(b"SYST:LOCK ON")
        #     #Turn off cycler
        #     for trying in range(0,10):
        #         GUI2SerialConnectionCycler.write(b"OUTP OFF")
        #         time.sleep(0.1)
        #         GUI2SerialConnectionCycler.write(b"OUTPUT?")
        #         if GUI2SerialConnectionCycler.readline().decode().strip() == 'OFF':
        #             time.sleep(0.1)
        #             break
        os._exit(0)

class GUI1DataLoggingVCU(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):

        global GUI1GlobalDictionary
        global GUI1SerialConnectionVCU
        global GUI1ConnectionCompleted
        global GUI1StopButtonClicked

        SLFaultArray = ['STAT_DSG_FET_STATUS_FLAG','STAT_CHG_FET_STATUS_FLAG','STAT_BAL_TIMER_STATUS_FLAG','STAT_BAL_ACT_STATUS_FLAG','STAT_LTC2946_DSG_ALERT_FLAG','STAT_LTC2946_CHG_ALERT_FLAG','STAT_PWR_MODE_CHARGE','STAT_PWR_MODE_CHARGE_NX','STAT_BMS_UNECOVERABLE_FAILURE','STAT_UV_THR_FLAG','STAT_OV_THR_FLAG','STAT_LTC6812_WDT_SET_FLAG','STAT_BATTERY_TEMP_OVER_MIN_THRESHOLD','STAT_BATTERY_TEMP_OVER_MAX_THRESHOLD','STAT_BATTERY_TEMP_TOO_LOW','STAT_LTC6812_SAFETY_TIMER_FLAG','STAT_BALANCER_ABORT_FLAG','STAT_BALANCER_RESET_FLAG','STAT_BALANCING_COMPLETE_FLAG','STAT_LTC6812_PEC_ERROR','STAT_UV_OV_THR_FOR_TURN_ON','STAT_ECC_ERM_ERR_FLAG','STAT_DSG_INA302_ALERT1','STAT_DSG_INA302_ALERT2','STAT_MOSFET_OVER_TMP_ALERT','STAT_FET_FRONT_OVER_TMP_ALERT','STAT_BAT_PLUS_OVER_TMP_ALERT','STAT_BAT_MINUS_OVER_TMP_ALERT','STAT_PACK_PLUS_MCPCB_OVER_TMP_ALERT','STAT_REL_HUMIDITY_OVERVALUE_ALERT','STAT_DSG_FUSE_BLOWN_ALERT','STAT_CHG_FUSE_BLOWN_ALERT']
        SHValvArray = ['STAT_FET_TURN_ON_FAILURE','STAT_FET_TURN_OFF_FAILURE','STAT_BAL_RES_OVER_TEMPERATURE','STAT_LTC2946_COMM_FAILURE','STAT_HW_UV_SHUTDOWN','STAT_HW_OV_SHUTDOWN','STAT_HW_OVER_TMP_SHUTDOWN','STAT_LTC7103_PGOOD','STAT_SYS_BOOT_FAILURE','STAT_CAN_MSG_SIG_ERR','STAT_FG_I2C_BUS_RECOVERY_EXEC','STAT_FG_MEAS_ABORT','STAT_BAT_TAMPER_DETECTED','STAT_TMP_THR_FOR_TURN_ON','STAT_FET_FRONT_OVER_TMP_WARN','STAT_BAT_PLUS_OVER_TMP_WARN','STAT_BAT_MINUS_OVER_TMP_WARN','STAT_PACK_PLUS_OVER_TMP_WARN','STAT_FG_MEAS_ERROR','STAT_PM_CHG_CURRENT_LIMIT_UPDATE','STAT_H2_SNS_ALERT','STAT_THRM_RUNAWAY_ALRT_V','STAT_THRM_RUNAWAY_ALRT_T','STAT_THRM_RUNAWAY_ALRT_H','STAT_PRE_DISCHARGE_STRESSED','STAT_FG_SETTINGS_UPDATE','STAT_BIT_UNUSED16','STAT_BIT_UNUSED17','STAT_BIT_UNUSED18','STAT_BIT_UNUSED19','STAT_BIT_UNUSED20','MAX_BMS_STATUS_FLAGS']
        NotErrorsArr = []#['STAT_DSG_FET_STATUS_FLAG', 'STAT_CHG_FET_STATUS_FLAG', 'STAT_BAL_TIMER_STATUS_FLAG', 'STAT_BAL_ACT_STATUS_FLAG','STAT_PWR_MODE_CHARGE','STAT_PWR_MODE_CHARGE_NX','STAT_LTC6812_WDT_SET_FLAG', 'STAT_LTC6812_SAFETY_TIMER_FLAG', 'STAT_BALANCER_ABORT_FLAG','STAT_BALANCER_RESET_FLAG','STAT_BALANCING_COMPLETE_FLAG','STAT_LTC6812_PEC_ERROR','STAT_ECC_ERM_ERR_FLAG', 'STAT_LTC2946_COMM_FAILURE', 'STAT_LTC7103_PGOOD','STAT_SYS_BOOT_FAILURE','STAT_CAN_MSG_SIG_ERR','STAT_FG_I2C_BUS_RECOVERY_EXEC','STAT_FG_MEAS_ABORT,STAT_TMP_THR_FOR_TURN_ON','STAT_FET_FRONT_OVER_TMP_WARN','STAT_BAT_PLUS_OVER_TMP_WARN,STAT_FG_SETTINGS_UPDATE','STAT_BAT_MINUS_OVER_TMP_WARN','STAT_PACK_PLUS_OVER_TMP_WARN','STAT_FG_MEAS_ERROR','STAT_PM_CHG_CURRENT_LIMIT_UPDATE','STAT_H2_SNS_ALERT']
        AlreadyFetchedFaults = []

        while (GUI1StopButtonClicked == None):
            if GUI1ConnectionCompleted == 'Success':
                while (GUI1StopButtonClicked == None):
                    time.sleep(0.01)
                    try:
                        string_data_res = GUI1SerialConnectionVCU.read(size = 2000).decode('utf-8')
                        #Errors
                        index_Valv_string = string_data_res.find('I,0,SL | SH:')
                        ErrorHexValue = string_data_res[index_Valv_string:][:string_data_res[index_Valv_string:].find('\n')][string_data_res[index_Valv_string:][:string_data_res[index_Valv_string:].find('\n')].find(':'):][2:]
                        SLValv = bin(int(ErrorHexValue[:ErrorHexValue.find(' | ')], 16))[2:].zfill(32)[::-1]
                        SHValv = bin(int(ErrorHexValue[ErrorHexValue.find('| '):][2:], 16))[2:].zfill(32)[::-1]
                        SLValvIndex = [i for i in range(len(SLValv)) if SLValv.startswith('1', i)]
                        SHValvindex = [i for i in range(len(SHValv)) if SHValv.startswith('1', i)]
                        if len(SLValvIndex) > 0:
                            for TargetIndex_ in SLValvIndex:
                                if (SLFaultArray[TargetIndex_] not in NotErrorsArr) and (SLFaultArray[TargetIndex_] not in AlreadyFetchedFaults):
                                    AlreadyFetchedFaults.append(SLFaultArray[TargetIndex_])
                                    Time_Now = datetime.now()
                                    Time_Now_PRINT = Time_Now.strftime("%Y-%m-%d %H-%M")
                                    GUI1ErrorMessages.append(f'Error : {SLFaultArray[TargetIndex_]} ({Time_Now_PRINT})')
                        if len(SHValvindex) > 0:
                            for TargetIndex_ in SHValvindex:
                                if (SHValvArray[TargetIndex_] not in NotErrorsArr) and (SHValvArray[TargetIndex_] not in AlreadyFetchedFaults):
                                    AlreadyFetchedFaults.append(SHValvArray[TargetIndex_])
                                    Time_Now = datetime.now()
                                    Time_Now_PRINT = Time_Now.strftime("%Y-%m-%d %H-%M")
                                    GUI1ErrorMessages.append(f'Error : {SHValvArray[TargetIndex_]} ({Time_Now_PRINT})')
                        #Other Data
                        if '*' not in string_data_res:
                            if '(' and ')' and '[' and ']' and'{' and '}' in string_data_res:
                                #Initializing
                                string_curved_bracket = ''
                                string_flower_bracket = ''
                                string_squared_bracket = ''
                                #Curved brackets
                                curverd_bracket_starting_indexes = [i for i, char in enumerate(string_data_res) if char == '(']
                                curverd_bracket_ending_indexes = [i for i, char in enumerate(string_data_res) if char == ')']
                                #Flower brackets
                                flowerd_bracket_starting_indexes = [i for i, char in enumerate(string_data_res) if char == '{']
                                flowerd_bracket_ending_indexes = [i for i, char in enumerate(string_data_res) if char == '}']
                                #Square brackets
                                squared_bracket_starting_indexes = [i for i, char in enumerate(string_data_res) if char == '[']
                                squared_bracket_ending_indexes = [i for i, char in enumerate(string_data_res) if char == ']']
                                #Extracting the latest Curved bracket string
                                for i in range(0, len(curverd_bracket_starting_indexes)):
                                    if curverd_bracket_ending_indexes[0] > curverd_bracket_starting_indexes[i]:
                                        string_curved_bracket = string_data_res[curverd_bracket_starting_indexes[i]+1:curverd_bracket_ending_indexes[0]]
                                #Extracting the latest Flower bracket string
                                for i in range(0, len(flowerd_bracket_starting_indexes)):
                                    if flowerd_bracket_ending_indexes[0] > flowerd_bracket_starting_indexes[i]:
                                        string_flower_bracket = string_data_res[flowerd_bracket_starting_indexes[i]+1:flowerd_bracket_ending_indexes[0]]
                                #Extracting the latest Squared bracket string
                                for i in range(0, len(squared_bracket_starting_indexes)):
                                    if squared_bracket_ending_indexes[0] > squared_bracket_starting_indexes[i]:
                                        string_squared_bracket = string_data_res[squared_bracket_starting_indexes[i]+1:squared_bracket_ending_indexes[0]]
                                if string_curved_bracket and string_flower_bracket and string_squared_bracket != '':
                                    #Extracting the data
                                    array_string_flower_bracket = string_flower_bracket.split(",")
                                    array_string_squared_bracket = string_squared_bracket.split(",")
                                    array_string_curved_bracket = string_curved_bracket.split(",")
                                    if len(array_string_flower_bracket) == 20 and len(array_string_squared_bracket) == 36 and len(array_string_curved_bracket) == 32:
                                        MILLIS2 = array_string_flower_bracket[1]
                                        TS1 = float(array_string_flower_bracket[2])
                                        TS2 = float(array_string_flower_bracket[3])
                                        TS3 = float(array_string_flower_bracket[4])
                                        TS4 = float(array_string_flower_bracket[5])
                                        TS5 = float(array_string_flower_bracket[6])
                                        TS6 = float(array_string_flower_bracket[7])
                                        TS7 = float(array_string_flower_bracket[8])
                                        TS8 = float(array_string_flower_bracket[9])
                                        TS9 = float(array_string_flower_bracket[10])
                                        TS10 = float(array_string_flower_bracket[11])
                                        TS11 = float(array_string_flower_bracket[12])
                                        TS12 = float(array_string_flower_bracket[13])
                                        FET_Temp_Front = float(array_string_flower_bracket[14])
                                        BAT_POS_TEMP = float(array_string_flower_bracket[15])
                                        BAT_NEG_TEMP = float(array_string_flower_bracket[16])
                                        PACK_POS_TEMP = float(array_string_flower_bracket[17])
                                        TS0_FLT = float(array_string_flower_bracket[18])
                                        TS13_FLT = float(array_string_flower_bracket[19])

                                        SLOT1 = float(array_string_squared_bracket[0])
                                        MILLIS = float(array_string_squared_bracket[1])
                                        FET_ON_OFF = float(array_string_squared_bracket[2])
                                        CFET_ON_OFF = float(array_string_squared_bracket[3])
                                        FET_TEMP1 = float(array_string_squared_bracket[4])
                                        DSG_VOLT = float(array_string_squared_bracket[5])
                                        SC_Current = float(array_string_squared_bracket[6])
                                        DSG_Current = float(array_string_squared_bracket[7])
                                        CHG_VOLT = float(array_string_squared_bracket[8])
                                        CHG_Current = float(array_string_squared_bracket[9])
                                        DSG_Time = float(array_string_squared_bracket[10])
                                        CHG_Time = float(array_string_squared_bracket[11])
                                        DSG_Charge = float(array_string_squared_bracket[12])
                                        CHG_Charge = float(array_string_squared_bracket[13])
                                        Cell1 = float(array_string_squared_bracket[14])
                                        Cell2 = float(array_string_squared_bracket[15])
                                        Cell3 = float(array_string_squared_bracket[16])
                                        Cell4 = float(array_string_squared_bracket[17])
                                        Cell5 = float(array_string_squared_bracket[18])
                                        Cell6 = float(array_string_squared_bracket[19])
                                        Cell7 = float(array_string_squared_bracket[20])
                                        Cell8 = float(array_string_squared_bracket[21])
                                        Cell9 = float(array_string_squared_bracket[22])
                                        Cell10 = float(array_string_squared_bracket[23])
                                        Cell11 = float(array_string_squared_bracket[24])
                                        Cell12 = float(array_string_squared_bracket[25])
                                        Cell13 = float(array_string_squared_bracket[26])
                                        Cell14 = float(array_string_squared_bracket[27])
                                        Cell_Delta_Volt = float(array_string_squared_bracket[28])
                                        Sum_of_cells = float(array_string_squared_bracket[29])
                                        DSG_Power = float(array_string_squared_bracket[30])
                                        DSG_Energy = float(array_string_squared_bracket[31])
                                        CHG_Power = float(array_string_squared_bracket[32])
                                        CHG_Energy = float(array_string_squared_bracket[33])
                                        Min_CV = float(array_string_squared_bracket[34])
                                        BAL_ON_OFF = float(array_string_squared_bracket[35])

                                        MILLIS3 = float(array_string_curved_bracket[1])
                                        FET_TEMP_REAR = float(array_string_curved_bracket[2])
                                        DSG_INA = float(array_string_curved_bracket[3])
                                        BAL_RES_TEMP = float(array_string_curved_bracket[4])
                                        HUM = float(array_string_curved_bracket[5])
                                        IMON = float(array_string_curved_bracket[6])
                                        Hydrogen = float(array_string_curved_bracket[7])
                                        FG_CELL_VOLT = float(array_string_curved_bracket[8])
                                        FG_PACK_VOLT = float(array_string_curved_bracket[9])
                                        FG_AVG_CURN = float(array_string_curved_bracket[10])
                                        SOC = float(array_string_curved_bracket[11])
                                        MAX_TTE = float(array_string_curved_bracket[12])
                                        MAX_TTF = float(array_string_curved_bracket[13])
                                        REPORTED_CAP = float(array_string_curved_bracket[14])
                                        TS0_FLT1 = float(array_string_curved_bracket[15])
                                        IR = float(array_string_curved_bracket[16])
                                        Cycles = float(array_string_curved_bracket[17])
                                        DS_CAP = float(array_string_curved_bracket[18])
                                        FSTAT = float(array_string_curved_bracket[19])
                                        VFSOC = float(array_string_curved_bracket[20])
                                        CURR = float(array_string_curved_bracket[21])
                                        CAP_NOM = float(array_string_curved_bracket[22])
                                        REP_CAP_1 = float(array_string_curved_bracket[23])
                                        AGE = float(array_string_curved_bracket[24])
                                        AGE_FCAST = float(array_string_curved_bracket[25])
                                        QH = float(array_string_curved_bracket[26])
                                        ICHGTERM = float(array_string_curved_bracket[27])
                                        DQACC = float(array_string_curved_bracket[28])
                                        DPACC = float(array_string_curved_bracket[29])
                                        QRESIDUAL = float(array_string_curved_bracket[30])
                                        MIXCAP = float(array_string_curved_bracket[31])

                                        #Creating a dictionary
                                        DICTIONARY = {'Slot1':[SLOT1],'Millis':[MILLIS],'FET_ON_OFF':[FET_ON_OFF],'CFET ON/OFF':[CFET_ON_OFF],'FET TEMP1':[FET_TEMP1],'DSG_VOLT':[DSG_VOLT],'SC Current':[SC_Current],'DSG_Current':[DSG_Current],'CHG_VOLT':[CHG_VOLT],'CHG_Current':[CHG_Current],'DSG Time':[DSG_Time],'CHG Time':[CHG_Time],'DSG Charge':[DSG_Charge],'CHG Charge':[CHG_Charge],'Cell1':[Cell1],'Cell2':[Cell2],'Cell3':[Cell3],'Cell4':[Cell4],'Cell5':[Cell5],'Cell6':[Cell6],'Cell7':[Cell7],'Cell8':[Cell8],'Cell9':[Cell9],'Cell10':[Cell10],'Cell11':[Cell11],'Cell12':[Cell12],'Cell13':[Cell13],'Cell14':[Cell14],'Cell Delta Volt':[Cell_Delta_Volt],'Sum-of-cells':[Sum_of_cells],'DSG Power':[DSG_Power],'DSG Energy':[DSG_Energy],'CHG Power':[CHG_Power],'CHG Energy':[CHG_Energy],'Min CV':[Min_CV],'BAL_ON_OFF':[BAL_ON_OFF],'Millis2':[MILLIS2],'TS1':[TS1],'TS2':[TS2],'TS3':[TS3],'TS4':[TS4],'TS5':[TS5],'TS6':[TS6],'TS7':[TS7],'TS8':[TS8],'TS9':[TS9],'TS10':[TS10],'TS11':[TS11],'TS12':[TS12],'FET Temp Front':[FET_Temp_Front],'BAT + ve Temp':[BAT_POS_TEMP],'BAT - ve Temp':[BAT_NEG_TEMP],'Pack + ve Temp':[PACK_POS_TEMP],'TS0_FLT':[TS0_FLT],'TS13_FLT':[TS13_FLT],'Millis3':[MILLIS3],'FET_TEMP_REAR':[FET_TEMP_REAR],'DSG INA':[DSG_INA],'BAL_RES_TEMP':[BAL_RES_TEMP],'HUM':[HUM],'IMON':[IMON],'Hydrogen':[Hydrogen],'FG_CELL_VOLT':[FG_CELL_VOLT],'FG_PACK_VOLT':[FG_PACK_VOLT],'FG_AVG_CURN':[FG_AVG_CURN],'SOC':[SOC],'MAX_TTE':[MAX_TTE],'MAX_TTF':[MAX_TTF],'REPORTED_CAP':[REPORTED_CAP],'TS0_FLT1':[TS0_FLT1],'IR':[IR],'Cycles':[Cycles],'DS_CAP':[DS_CAP],'FSTAT':[FSTAT],'VFSOC':[VFSOC],'CURR':[CURR],'CAP_NOM':[CAP_NOM],'REP_CAP.1':[REP_CAP_1],'AGE':[AGE],'AGE_FCAST':[AGE_FCAST],'QH':[QH],'ICHGTERM':[ICHGTERM],'DQACC':[DQACC],'DPACC':[DPACC],'QRESIDUAL':[QRESIDUAL],'MIXCAP':[MIXCAP]}                        
                                        for key, value in DICTIONARY.items():
                                            if key in GUI1GlobalDictionary:
                                                GUI1GlobalDictionary[key].extend(value)
                                            else:
                                                GUI1GlobalDictionary[key] = value
                                        break
                    except:
                        pass
            time.sleep(0.01)

class GUI1liveDataStoring(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global GUI1GlobalFilePathBMS
        global GUI1GlobalDictionary
        global GUI1ConnectionCompleted
        global GUI1StatusMessages
        global GUI1StopButtonClicked

        while (GUI1StopButtonClicked == None):
            if GUI1ConnectionCompleted == 'Success':
                try:
                    if GUI1GlobalFilePathBMS != None:
                        GlobalDictionaryPandas = pd.DataFrame.from_dict(GUI1GlobalDictionary)
                        GlobalDictionaryPandas.to_csv(GUI1GlobalFilePathBMS, index = False)
                except:
                    GUI1StatusMessages.append('Close the csv file to save data')
            time.sleep(5)

class GUI1DisplayThreads(QThread):

    StatusBoxUpdate = pyqtSignal(str)
    ErrorBoxUpdate = pyqtSignal(str)
    StatusDataUpdate = pyqtSignal(float, float, float, float, float, float, float, float)
    BMSDataUpdate = pyqtSignal(list)
    GraphStatusUpdate = pyqtSignal(int, float, float)

    def __init__(self):
        super().__init__()
        self.GUI1timer = QTimer()
        self.GUI1timer.setInterval(1000)
        self.GUI1timer.timeout.connect(self.GUI1update_timer)
        self.GUI1timer.start()
        self.GUI1current_time = 0

    def run(self):
        global GUI1ErrorMessages
        global GUI1StatusMessages
        global GUI1GlobalDictionary
        global GUI1ConnectionCompleted
        global GUI1RoundingValvCheck
        global AllData
        global GUI1StopButtonClicked
        global GUI1TimeSeriesX

        while (GUI1StopButtonClicked == None):
            if len(GUI1StatusMessages) > 0:
                self.StatusBoxUpdate.emit(GUI1StatusMessages[0])
                GUI1StatusMessages = GUI1StatusMessages[1:]
            if len(GUI1ErrorMessages) > 0:
                self.ErrorBoxUpdate.emit(GUI1ErrorMessages[0])
                GUI1ErrorMessages = GUI1ErrorMessages[1:]
            if (GUI1ConnectionCompleted == 'Success') and (len(GUI1GlobalDictionary) != 0):
                
                self.StatusDataUpdate.emit(
                    round(GUI1GlobalDictionary['DSG_Current'][-1], GUI1RoundingValvCheck),
                    round(GUI1GlobalDictionary['CHG_Current'][-1], GUI1RoundingValvCheck),
                    round(GUI1GlobalDictionary['FET_ON_OFF'][-1], GUI1RoundingValvCheck),
                    round(GUI1GlobalDictionary['Sum-of-cells'][-1], GUI1RoundingValvCheck),
                    round(GUI1GlobalDictionary['SOC'][-1], GUI1RoundingValvCheck),
                    round(max([GUI1GlobalDictionary['TS1'][-1], GUI1GlobalDictionary['TS2'][-1], GUI1GlobalDictionary['TS3'][-1], GUI1GlobalDictionary['TS4'][-1], GUI1GlobalDictionary['TS5'][-1], GUI1GlobalDictionary['TS6'][-1], GUI1GlobalDictionary['TS7'][-1], GUI1GlobalDictionary['TS8'][-1], GUI1GlobalDictionary['TS9'][-1], GUI1GlobalDictionary['TS10'][-1], GUI1GlobalDictionary['TS11'][-1], GUI1GlobalDictionary['TS12'][-1], GUI1GlobalDictionary['TS13_FLT'][-1], GUI1GlobalDictionary['TS0_FLT'][-1]]), GUI1RoundingValvCheck),
                    self.GUI1current_time,
                    self.GUI1current_time
                )

                Arr = [round(GUI1GlobalDictionary[element][-1], GUI1RoundingValvCheck) for element in AllData]
                self.BMSDataUpdate.emit(Arr)
                
                GUI1TimeSeriesX = GUI1TimeSeriesX + 1
                new_x = int(GUI1TimeSeriesX)
                new_y1 = float(GUI1GlobalDictionary['Sum-of-cells'][-1])
                new_y2 = float(GUI1GlobalDictionary['DSG_Current'][-1] + GUI1GlobalDictionary['CHG_Current'][-1])
                self.GraphStatusUpdate.emit(new_x, new_y1, new_y2)

            time.sleep(0.1)

    def GUI1update_timer(self):
        self.GUI1current_time += 1

class GUI1ConnectButton(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):

        global GUI1SerialConnectionVCU
        global GUI1StatusMessages
        global GUI1ConnectionCompleted

        GUI1StatusMessages.append('Connection in Progress...')

        #All Available ports
        available_ports = [port.device for port in serial.tools.list_ports.comports()]

        #VCU
        for port in serial.tools.list_ports.comports():
            if port.device in available_ports:
                if 'USB' in port.description:
                    GUI1SerialConnectionVCU = serial.Serial(port.device, baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
                    available_ports = [pr for pr in available_ports if pr != port.device]
                    break

        #Status Messages
        if (GUI1SerialConnectionVCU != None):
            GUI1StatusMessages.append('Success : Connection with VCU')
            GUI1StatusMessages.append('Started BMS Data Logging')
            GUI1ConnectionCompleted = 'Success'
        else:
            if GUI1SerialConnectionVCU:
                GUI1SerialConnectionVCU.close()
            GUI1StatusMessages.append('Fail : Connection with VCU')

class GUI1StopButton(QThread):
    
    Signal1 = pyqtSignal(int)
    Signal2 = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        global GUI1StatusMessages
        global GUI1StopButtonClicked
        global GUI1AllThreads
        global GUI1SerialConnectionVCU
        global GUI1GlobalFilePathBMS
        global GUI1GlobalDictionary
        global GUI1ConnectionCompleted
        global GUI1ErrorMessages
        global GUI1TimeSeriesX
        
        #Updating message
        GUI1StatusMessages.append('Stop Button Clicked')
        #Real time doer
        GUI1StopButtonClicked = 'Clicked'
        #Checking if all threads are closed or not
        for ThreadNumber in GUI1AllThreads:
            if isinstance(ThreadNumber, threading.Thread):
                while True:
                    if not ThreadNumber.is_alive():
                        break
                    time.sleep(0.001)
            elif isinstance(ThreadNumber, QThread):
                while True:
                    if not ThreadNumber.isRunning():
                        break
                    time.sleep(0.001)
        #Closing all connections
        if GUI1SerialConnectionVCU != None:
            GUI1SerialConnectionVCU.close()

        #Signal1
        self.Signal1.emit(1)

        #TimeSleep
        time.sleep(2)

        #Initializing all parameters
        GUI1GlobalFilePathBMS = None
        GUI1SerialConnectionVCU = None
        GUI1GlobalDictionary = {}
        GUI1ConnectionCompleted = None
        GUI1StatusMessages = []
        GUI1ErrorMessages = []
        GUI1AllThreads = []
        GUI1StopButtonClicked = None
        GUI1TimeSeriesX = 0

        #Signal2
        self.Signal2.emit(1)


class GUI2DataLoggingVCU(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):

        global GUI2GlobalDictionary
        global GUI2SerialConnectionVCU
        global GUI2ConnectionCompleted
        global GUI2StopButtonClicked
        global GUI2StepParm
        global GUI2ErrorMessages

        SLFaultArray = ['STAT_DSG_FET_STATUS_FLAG','STAT_CHG_FET_STATUS_FLAG','STAT_BAL_TIMER_STATUS_FLAG','STAT_BAL_ACT_STATUS_FLAG','STAT_LTC2946_DSG_ALERT_FLAG','STAT_LTC2946_CHG_ALERT_FLAG','STAT_PWR_MODE_CHARGE','STAT_PWR_MODE_CHARGE_NX','STAT_BMS_UNECOVERABLE_FAILURE','STAT_UV_THR_FLAG','STAT_OV_THR_FLAG','STAT_LTC6812_WDT_SET_FLAG','STAT_BATTERY_TEMP_OVER_MIN_THRESHOLD','STAT_BATTERY_TEMP_OVER_MAX_THRESHOLD','STAT_BATTERY_TEMP_TOO_LOW','STAT_LTC6812_SAFETY_TIMER_FLAG','STAT_BALANCER_ABORT_FLAG','STAT_BALANCER_RESET_FLAG','STAT_BALANCING_COMPLETE_FLAG','STAT_LTC6812_PEC_ERROR','STAT_UV_OV_THR_FOR_TURN_ON','STAT_ECC_ERM_ERR_FLAG','STAT_DSG_INA302_ALERT1','STAT_DSG_INA302_ALERT2','STAT_MOSFET_OVER_TMP_ALERT','STAT_FET_FRONT_OVER_TMP_ALERT','STAT_BAT_PLUS_OVER_TMP_ALERT','STAT_BAT_MINUS_OVER_TMP_ALERT','STAT_PACK_PLUS_MCPCB_OVER_TMP_ALERT','STAT_REL_HUMIDITY_OVERVALUE_ALERT','STAT_DSG_FUSE_BLOWN_ALERT','STAT_CHG_FUSE_BLOWN_ALERT']
        SHValvArray = ['STAT_FET_TURN_ON_FAILURE','STAT_FET_TURN_OFF_FAILURE','STAT_BAL_RES_OVER_TEMPERATURE','STAT_LTC2946_COMM_FAILURE','STAT_HW_UV_SHUTDOWN','STAT_HW_OV_SHUTDOWN','STAT_HW_OVER_TMP_SHUTDOWN','STAT_LTC7103_PGOOD','STAT_SYS_BOOT_FAILURE','STAT_CAN_MSG_SIG_ERR','STAT_FG_I2C_BUS_RECOVERY_EXEC','STAT_FG_MEAS_ABORT','STAT_BAT_TAMPER_DETECTED','STAT_TMP_THR_FOR_TURN_ON','STAT_FET_FRONT_OVER_TMP_WARN','STAT_BAT_PLUS_OVER_TMP_WARN','STAT_BAT_MINUS_OVER_TMP_WARN','STAT_PACK_PLUS_OVER_TMP_WARN','STAT_FG_MEAS_ERROR','STAT_PM_CHG_CURRENT_LIMIT_UPDATE','STAT_H2_SNS_ALERT','STAT_THRM_RUNAWAY_ALRT_V','STAT_THRM_RUNAWAY_ALRT_T','STAT_THRM_RUNAWAY_ALRT_H','STAT_PRE_DISCHARGE_STRESSED','STAT_FG_SETTINGS_UPDATE','STAT_BIT_UNUSED16','STAT_BIT_UNUSED17','STAT_BIT_UNUSED18','STAT_BIT_UNUSED19','STAT_BIT_UNUSED20','MAX_BMS_STATUS_FLAGS']
        NotErrorsArr = []#['STAT_DSG_FET_STATUS_FLAG', 'STAT_CHG_FET_STATUS_FLAG', 'STAT_BAL_TIMER_STATUS_FLAG', 'STAT_BAL_ACT_STATUS_FLAG','STAT_PWR_MODE_CHARGE','STAT_PWR_MODE_CHARGE_NX','STAT_LTC6812_WDT_SET_FLAG', 'STAT_LTC6812_SAFETY_TIMER_FLAG', 'STAT_BALANCER_ABORT_FLAG','STAT_BALANCER_RESET_FLAG','STAT_BALANCING_COMPLETE_FLAG','STAT_LTC6812_PEC_ERROR','STAT_ECC_ERM_ERR_FLAG', 'STAT_LTC2946_COMM_FAILURE', 'STAT_LTC7103_PGOOD','STAT_SYS_BOOT_FAILURE','STAT_CAN_MSG_SIG_ERR','STAT_FG_I2C_BUS_RECOVERY_EXEC','STAT_FG_MEAS_ABORT,STAT_TMP_THR_FOR_TURN_ON','STAT_FET_FRONT_OVER_TMP_WARN','STAT_BAT_PLUS_OVER_TMP_WARN,STAT_FG_SETTINGS_UPDATE','STAT_BAT_MINUS_OVER_TMP_WARN','STAT_PACK_PLUS_OVER_TMP_WARN','STAT_FG_MEAS_ERROR','STAT_PM_CHG_CURRENT_LIMIT_UPDATE','STAT_H2_SNS_ALERT']
        AlreadyFetchedFaults = []

        while (GUI2StopButtonClicked == None):
            if GUI2ConnectionCompleted == 'Success':
                while (GUI2StopButtonClicked == None):
                    time.sleep(0.01)
                    try:
                        string_data_res = GUI2SerialConnectionVCU.read(size = 2000).decode('utf-8')
                        #Errors
                        index_Valv_string = string_data_res.find('I,0,SL | SH:')
                        ErrorHexValue = string_data_res[index_Valv_string:][:string_data_res[index_Valv_string:].find('\n')][string_data_res[index_Valv_string:][:string_data_res[index_Valv_string:].find('\n')].find(':'):][2:]
                        SLValv = bin(int(ErrorHexValue[:ErrorHexValue.find(' | ')], 16))[2:].zfill(32)[::-1]
                        SHValv = bin(int(ErrorHexValue[ErrorHexValue.find('| '):][2:], 16))[2:].zfill(32)[::-1]
                        SLValvIndex = [i for i in range(len(SLValv)) if SLValv.startswith('1', i)]
                        SHValvindex = [i for i in range(len(SHValv)) if SHValv.startswith('1', i)]
                        if len(SLValvIndex) > 0:
                            for TargetIndex_ in SLValvIndex:
                                if (SLFaultArray[TargetIndex_] not in NotErrorsArr):# and (SLFaultArray[TargetIndex_] not in AlreadyFetchedFaults):
                                    #AlreadyFetchedFaults.append(SLFaultArray[TargetIndex_])
                                    Time_Now = datetime.now()
                                    Time_Now_PRINT = Time_Now.strftime("%Y-%m-%d %H-%M")
                                    GUI2ErrorMessages.append(f'Error : {SLFaultArray[TargetIndex_]} ({Time_Now_PRINT})')
                        if len(SHValvindex) > 0:
                            for TargetIndex_ in SHValvindex:
                                if (SHValvArray[TargetIndex_] not in NotErrorsArr):# and (SHValvArray[TargetIndex_] not in AlreadyFetchedFaults):
                                    #AlreadyFetchedFaults.append(SHValvArray[TargetIndex_])
                                    Time_Now = datetime.now()
                                    Time_Now_PRINT = Time_Now.strftime("%Y-%m-%d %H-%M")
                                    GUI2ErrorMessages.append(f'Error : {SHValvArray[TargetIndex_]} ({Time_Now_PRINT})')
                        #Other Data
                        if '*' not in string_data_res:
                            if '(' and ')' and '[' and ']' and'{' and '}' in string_data_res:
                                #Initializing
                                string_curved_bracket = ''
                                string_flower_bracket = ''
                                string_squared_bracket = ''
                                #Curved brackets
                                curverd_bracket_starting_indexes = [i for i, char in enumerate(string_data_res) if char == '(']
                                curverd_bracket_ending_indexes = [i for i, char in enumerate(string_data_res) if char == ')']
                                #Flower brackets
                                flowerd_bracket_starting_indexes = [i for i, char in enumerate(string_data_res) if char == '{']
                                flowerd_bracket_ending_indexes = [i for i, char in enumerate(string_data_res) if char == '}']
                                #Square brackets
                                squared_bracket_starting_indexes = [i for i, char in enumerate(string_data_res) if char == '[']
                                squared_bracket_ending_indexes = [i for i, char in enumerate(string_data_res) if char == ']']
                                #Extracting the latest Curved bracket string
                                for i in range(0, len(curverd_bracket_starting_indexes)):
                                    if curverd_bracket_ending_indexes[0] > curverd_bracket_starting_indexes[i]:
                                        string_curved_bracket = string_data_res[curverd_bracket_starting_indexes[i]+1:curverd_bracket_ending_indexes[0]]
                                #Extracting the latest Flower bracket string
                                for i in range(0, len(flowerd_bracket_starting_indexes)):
                                    if flowerd_bracket_ending_indexes[0] > flowerd_bracket_starting_indexes[i]:
                                        string_flower_bracket = string_data_res[flowerd_bracket_starting_indexes[i]+1:flowerd_bracket_ending_indexes[0]]
                                #Extracting the latest Squared bracket string
                                for i in range(0, len(squared_bracket_starting_indexes)):
                                    if squared_bracket_ending_indexes[0] > squared_bracket_starting_indexes[i]:
                                        string_squared_bracket = string_data_res[squared_bracket_starting_indexes[i]+1:squared_bracket_ending_indexes[0]]
                                if string_curved_bracket and string_flower_bracket and string_squared_bracket != '':
                                    #Extracting the data
                                    array_string_flower_bracket = string_flower_bracket.split(",")
                                    array_string_squared_bracket = string_squared_bracket.split(",")
                                    array_string_curved_bracket = string_curved_bracket.split(",")
                                    if len(array_string_flower_bracket) == 20 and len(array_string_squared_bracket) == 36 and len(array_string_curved_bracket) == 32:
                                        MILLIS2 = array_string_flower_bracket[1]
                                        TS1 = float(array_string_flower_bracket[2])
                                        TS2 = float(array_string_flower_bracket[3])
                                        TS3 = float(array_string_flower_bracket[4])
                                        TS4 = float(array_string_flower_bracket[5])
                                        TS5 = float(array_string_flower_bracket[6])
                                        TS6 = float(array_string_flower_bracket[7])
                                        TS7 = float(array_string_flower_bracket[8])
                                        TS8 = float(array_string_flower_bracket[9])
                                        TS9 = float(array_string_flower_bracket[10])
                                        TS10 = float(array_string_flower_bracket[11])
                                        TS11 = float(array_string_flower_bracket[12])
                                        TS12 = float(array_string_flower_bracket[13])
                                        FET_Temp_Front = float(array_string_flower_bracket[14])
                                        BAT_POS_TEMP = float(array_string_flower_bracket[15])
                                        BAT_NEG_TEMP = float(array_string_flower_bracket[16])
                                        PACK_POS_TEMP = float(array_string_flower_bracket[17])
                                        TS0_FLT = float(array_string_flower_bracket[18])
                                        TS13_FLT = float(array_string_flower_bracket[19])

                                        SLOT1 = float(array_string_squared_bracket[0])
                                        MILLIS = float(array_string_squared_bracket[1])
                                        FET_ON_OFF = float(array_string_squared_bracket[2])
                                        CFET_ON_OFF = float(array_string_squared_bracket[3])
                                        FET_TEMP1 = float(array_string_squared_bracket[4])
                                        DSG_VOLT = float(array_string_squared_bracket[5])
                                        SC_Current = float(array_string_squared_bracket[6])
                                        DSG_Current = float(array_string_squared_bracket[7])
                                        CHG_VOLT = float(array_string_squared_bracket[8])
                                        CHG_Current = float(array_string_squared_bracket[9])
                                        DSG_Time = float(array_string_squared_bracket[10])
                                        CHG_Time = float(array_string_squared_bracket[11])
                                        DSG_Charge = float(array_string_squared_bracket[12])
                                        CHG_Charge = float(array_string_squared_bracket[13])
                                        Cell1 = float(array_string_squared_bracket[14])
                                        Cell2 = float(array_string_squared_bracket[15])
                                        Cell3 = float(array_string_squared_bracket[16])
                                        Cell4 = float(array_string_squared_bracket[17])
                                        Cell5 = float(array_string_squared_bracket[18])
                                        Cell6 = float(array_string_squared_bracket[19])
                                        Cell7 = float(array_string_squared_bracket[20])
                                        Cell8 = float(array_string_squared_bracket[21])
                                        Cell9 = float(array_string_squared_bracket[22])
                                        Cell10 = float(array_string_squared_bracket[23])
                                        Cell11 = float(array_string_squared_bracket[24])
                                        Cell12 = float(array_string_squared_bracket[25])
                                        Cell13 = float(array_string_squared_bracket[26])
                                        Cell14 = float(array_string_squared_bracket[27])
                                        Cell_Delta_Volt = float(array_string_squared_bracket[28])
                                        Sum_of_cells = float(array_string_squared_bracket[29])
                                        DSG_Power = float(array_string_squared_bracket[30])
                                        DSG_Energy = float(array_string_squared_bracket[31])
                                        CHG_Power = float(array_string_squared_bracket[32])
                                        CHG_Energy = float(array_string_squared_bracket[33])
                                        Min_CV = float(array_string_squared_bracket[34])
                                        BAL_ON_OFF = float(array_string_squared_bracket[35])

                                        MILLIS3 = float(array_string_curved_bracket[1])
                                        FET_TEMP_REAR = float(array_string_curved_bracket[2])
                                        DSG_INA = float(array_string_curved_bracket[3])
                                        BAL_RES_TEMP = float(array_string_curved_bracket[4])
                                        HUM = float(array_string_curved_bracket[5])
                                        IMON = float(array_string_curved_bracket[6])
                                        Hydrogen = float(array_string_curved_bracket[7])
                                        FG_CELL_VOLT = float(array_string_curved_bracket[8])
                                        FG_PACK_VOLT = float(array_string_curved_bracket[9])
                                        FG_AVG_CURN = float(array_string_curved_bracket[10])
                                        SOC = float(array_string_curved_bracket[11])
                                        MAX_TTE = float(array_string_curved_bracket[12])
                                        MAX_TTF = float(array_string_curved_bracket[13])
                                        REPORTED_CAP = float(array_string_curved_bracket[14])
                                        TS0_FLT1 = float(array_string_curved_bracket[15])
                                        IR = float(array_string_curved_bracket[16])
                                        Cycles = float(array_string_curved_bracket[17])
                                        DS_CAP = float(array_string_curved_bracket[18])
                                        FSTAT = float(array_string_curved_bracket[19])
                                        VFSOC = float(array_string_curved_bracket[20])
                                        CURR = float(array_string_curved_bracket[21])
                                        CAP_NOM = float(array_string_curved_bracket[22])
                                        REP_CAP_1 = float(array_string_curved_bracket[23])
                                        AGE = float(array_string_curved_bracket[24])
                                        AGE_FCAST = float(array_string_curved_bracket[25])
                                        QH = float(array_string_curved_bracket[26])
                                        ICHGTERM = float(array_string_curved_bracket[27])
                                        DQACC = float(array_string_curved_bracket[28])
                                        DPACC = float(array_string_curved_bracket[29])
                                        QRESIDUAL = float(array_string_curved_bracket[30])
                                        MIXCAP = float(array_string_curved_bracket[31])
                                        #Creating a dictionary
                                        if GUI2StepParm != None:
                                            StepParmValv = int(GUI2StepParm) + 1
                                        else:
                                            StepParmValv = None
                                        DICTIONARY = {'Step Number':[StepParmValv],'Slot1':[SLOT1],'Millis':[MILLIS],'FET_ON_OFF':[FET_ON_OFF],'CFET ON/OFF':[CFET_ON_OFF],'FET TEMP1':[FET_TEMP1],'DSG_VOLT':[DSG_VOLT],'SC Current':[SC_Current],'DSG_Current':[DSG_Current],'CHG_VOLT':[CHG_VOLT],'CHG_Current':[CHG_Current],'DSG Time':[DSG_Time],'CHG Time':[CHG_Time],'DSG Charge':[DSG_Charge],'CHG Charge':[CHG_Charge],'Cell1':[Cell1],'Cell2':[Cell2],'Cell3':[Cell3],'Cell4':[Cell4],'Cell5':[Cell5],'Cell6':[Cell6],'Cell7':[Cell7],'Cell8':[Cell8],'Cell9':[Cell9],'Cell10':[Cell10],'Cell11':[Cell11],'Cell12':[Cell12],'Cell13':[Cell13],'Cell14':[Cell14],'Cell Delta Volt':[Cell_Delta_Volt],'Sum-of-cells':[Sum_of_cells],'DSG Power':[DSG_Power],'DSG Energy':[DSG_Energy],'CHG Power':[CHG_Power],'CHG Energy':[CHG_Energy],'Min CV':[Min_CV],'BAL_ON_OFF':[BAL_ON_OFF],'Millis2':[MILLIS2],'TS1':[TS1],'TS2':[TS2],'TS3':[TS3],'TS4':[TS4],'TS5':[TS5],'TS6':[TS6],'TS7':[TS7],'TS8':[TS8],'TS9':[TS9],'TS10':[TS10],'TS11':[TS11],'TS12':[TS12],'FET Temp Front':[FET_Temp_Front],'BAT + ve Temp':[BAT_POS_TEMP],'BAT - ve Temp':[BAT_NEG_TEMP],'Pack + ve Temp':[PACK_POS_TEMP],'TS0_FLT':[TS0_FLT],'TS13_FLT':[TS13_FLT],'Millis3':[MILLIS3],'FET_TEMP_REAR':[FET_TEMP_REAR],'DSG INA':[DSG_INA],'BAL_RES_TEMP':[BAL_RES_TEMP],'HUM':[HUM],'IMON':[IMON],'Hydrogen':[Hydrogen],'FG_CELL_VOLT':[FG_CELL_VOLT],'FG_PACK_VOLT':[FG_PACK_VOLT],'FG_AVG_CURN':[FG_AVG_CURN],'SOC':[SOC],'MAX_TTE':[MAX_TTE],'MAX_TTF':[MAX_TTF],'REPORTED_CAP':[REPORTED_CAP],'TS0_FLT1':[TS0_FLT1],'IR':[IR],'Cycles':[Cycles],'DS_CAP':[DS_CAP],'FSTAT':[FSTAT],'VFSOC':[VFSOC],'CURR':[CURR],'CAP_NOM':[CAP_NOM],'REP_CAP.1':[REP_CAP_1],'AGE':[AGE],'AGE_FCAST':[AGE_FCAST],'QH':[QH],'ICHGTERM':[ICHGTERM],'DQACC':[DQACC],'DPACC':[DPACC],'QRESIDUAL':[QRESIDUAL],'MIXCAP':[MIXCAP]}                        
                                        for key, value in DICTIONARY.items():
                                            if key in GUI2GlobalDictionary:
                                                GUI2GlobalDictionary[key].extend(value)
                                            else:
                                                GUI2GlobalDictionary[key] = value
                                        break
                    except Exception as e:
                        print("An error occurred:", e)

            time.sleep(0.01)

class GUI2liveDataStoring(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global GUI2GlobalFilePathBMS
        global GUI2GlobalDictionary
        global GUI2ConnectionCompleted
        global GUI2StatusMessages
        global GUI2StopButtonClicked
        global GUI2CyclerData
        global GUI2GlobalFilePathCycler

        while (GUI2StopButtonClicked == None):
            if GUI2ConnectionCompleted == 'Success':
                try:
                    if GUI2GlobalFilePathBMS != None:
                        GlobalDictionaryPandas = pd.DataFrame.from_dict(GUI2GlobalDictionary)
                        GlobalDictionaryPandas.to_csv(GUI2GlobalFilePathBMS, index = False)
                except:
                    pass
                try: 
                    if GUI2GlobalFilePathCycler != None:
                        CyclerDictionaryPandas = pd.DataFrame.from_dict(GUI2CyclerData)
                        CyclerDictionaryPandas.to_csv(GUI2GlobalFilePathCycler, index = False)
                except:
                    pass

            time.sleep(3)

class GUI2DisplayThreads(QThread):

    StatusBoxUpdate = pyqtSignal(str)
    ErrorBoxUpdate = pyqtSignal(str)
    StatusDataUpdate = pyqtSignal(float, float, float, float, float, float, float, float)
    BMSDataUpdate = pyqtSignal(list)
    GraphStatusUpdate = pyqtSignal(int, float, float)

    def __init__(self):
        super().__init__()
        self.GUI2timer = QTimer()
        self.GUI2timer.setInterval(1000)
        self.GUI2timer.timeout.connect(self.GUI2update_timer)
        self.GUI2timer.start()
        self.GUI2current_time = 0

    def run(self):
        global GUI2ErrorMessages
        global GUI2StatusMessages
        global GUI2GlobalDictionary
        global GUI2ConnectionCompleted
        global GUI2RoundingValvCheck
        global AllData
        global GUI2StopButtonClicked
        global GUI2TimeSeriesX

        while (GUI2StopButtonClicked == None):
            if len(GUI2StatusMessages) > 0:
                self.StatusBoxUpdate.emit(GUI2StatusMessages[0])
                GUI2StatusMessages = GUI2StatusMessages[1:]
            if len(GUI2ErrorMessages) > 0:
                self.ErrorBoxUpdate.emit(GUI2ErrorMessages[0])
                GUI2ErrorMessages = GUI2ErrorMessages[1:]
            if (GUI2ConnectionCompleted == 'Success') and (len(GUI2GlobalDictionary) != 0):
                
                self.StatusDataUpdate.emit(
                    round(GUI2GlobalDictionary['DSG_Current'][-1], GUI2RoundingValvCheck),
                    round(GUI2GlobalDictionary['CHG_Current'][-1], GUI2RoundingValvCheck),
                    round(GUI2GlobalDictionary['FET_ON_OFF'][-1], GUI2RoundingValvCheck),
                    round(GUI2GlobalDictionary['Sum-of-cells'][-1], GUI2RoundingValvCheck),
                    round(GUI2GlobalDictionary['SOC'][-1], GUI2RoundingValvCheck),
                    round(max([GUI2GlobalDictionary['TS1'][-1], GUI2GlobalDictionary['TS2'][-1], GUI2GlobalDictionary['TS3'][-1], GUI2GlobalDictionary['TS4'][-1], GUI2GlobalDictionary['TS5'][-1], GUI2GlobalDictionary['TS6'][-1], GUI2GlobalDictionary['TS7'][-1], GUI2GlobalDictionary['TS8'][-1], GUI2GlobalDictionary['TS9'][-1], GUI2GlobalDictionary['TS10'][-1], GUI2GlobalDictionary['TS11'][-1], GUI2GlobalDictionary['TS12'][-1], GUI2GlobalDictionary['TS13_FLT'][-1], GUI2GlobalDictionary['TS0_FLT'][-1]]), GUI2RoundingValvCheck),
                    self.GUI2current_time,
                    self.GUI2current_time
                )

                Arr = [round(GUI2GlobalDictionary[element][-1], GUI2RoundingValvCheck) for element in AllData]
                self.BMSDataUpdate.emit(Arr)
                
                GUI2TimeSeriesX = GUI2TimeSeriesX + 1
                new_x = int(GUI2TimeSeriesX)
                new_y1 = float(GUI2GlobalDictionary['Sum-of-cells'][-1])
                new_y2 = float(GUI2GlobalDictionary['DSG_Current'][-1] + GUI2GlobalDictionary['CHG_Current'][-1])
                self.GraphStatusUpdate.emit(new_x, new_y1, new_y2)

            time.sleep(0.1)

    def GUI2update_timer(self):
        self.GUI2current_time += 1

class GUI2ConnectButton(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):

        global GUI2SerialConnectionCycler
        global GUI2SerialConnectionVCU
        global GUI2StatusMessages
        global GUI2ConnectionCompleted
        global GUI2PortAssignedToCycler

        GUI2StatusMessages.append('Connection in Progress...')

        #All Available ports
        available_ports = [port.device for port in serial.tools.list_ports.comports()]

        #Cycler
        for port in serial.tools.list_ports.comports():
            if port.device in available_ports:
                if 'PSB' in port.description:
                    GUI2SerialConnectionCycler = serial.Serial(port.device, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
                    available_ports = [pr for pr in available_ports if pr != port.device]
                    GUI2PortAssignedToCycler = port.device
                    break
        if GUI2SerialConnectionCycler != None:
            GUI2StatusMessages.append('Success : Connection with Cycler')
        else:
            GUI2StatusMessages.append('Fail : Connection with Cycler')

        #VCU
        for port in serial.tools.list_ports.comports():
            if port.device in available_ports:
                if 'USB' in port.description:
                    GUI2SerialConnectionVCU = serial.Serial(port.device, baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
                    available_ports = [pr for pr in available_ports if pr != port.device]
                    break
        if GUI2SerialConnectionVCU != None:
            GUI2StatusMessages.append('Success : Connection with VCU')
        else:
            GUI2StatusMessages.append('Fail : Connection with VCU')

        #Status Messages
        if (GUI2SerialConnectionVCU != None) and (GUI2SerialConnectionCycler != None):
            GUI2StatusMessages.append('Success : Connection')
            GUI2StatusMessages.append('Started BMS Data Logging')
            GUI2ConnectionCompleted = 'Success'
        else:
            if GUI2SerialConnectionCycler:
                GUI2SerialConnectionCycler.close()
            if GUI2SerialConnectionVCU:
                GUI2SerialConnectionVCU.close()
            GUI2StatusMessages.append('Fail : Connection | Check Connections and Connect Again')

class GUI2ProcessDefinationWindow(QMainWindow):
 
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Process Dynamics")
        self.setGeometry(400, 280, 1050, 600)
        self.setFixedSize(1050, 600)
        
        # QLabel
        self.label1 = QLabel("Process Sequence")
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)  # Adjust the size as needed
        self.label1.setFont(font)
        
        # Create the table widget
        self.table = QTableWidget()
        self.table.setRowCount(0)  # Start with one row
        self.table.setColumnCount(11)  # Set the number of columns

        # Set column headers
        self.headers = ['Mode', 'Current (A)', 'Voltage (V)', 'End Current (A)', 'End SOC (%)', 'Timer (s)', 'Min Temperature (℃)', 'Max Temperature (℃)', 'GOTO Step Number', 'GOTO REPEAT', 'Next Step']
        self.table.setHorizontalHeaderLabels(self.headers)

        # Add dropdowns to the first column
        self.populate_first_column()

        # Add dropdowns to the last column
        self.populate_last_column()

        # Create buttons
        self.add_row_button = QPushButton("Add Row")
        self.add_row_button.clicked.connect(self.add_row)
        
        self.save_button = QPushButton("Save Data")
        self.save_button.clicked.connect(self.save_data)
        
        self.load_button = QPushButton("Load Data")
        self.load_button.clicked.connect(self.show_load_options)
        
        self.Proceed_button = QPushButton("Proceed")
        self.Proceed_button.clicked.connect(self.proceed_work)
        
        # Set up layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_row_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.Proceed_button)
        
        # QLabel
        self.label2 = QLabel("Data File Location")
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)  # Adjust the size as needed
        self.label2.setFont(font)
        
        # QLabel
        FileSavingLayoutUpper = QVBoxLayout()
        FileSavingLayout1 = QHBoxLayout()
        FileSavingLayout2 = QHBoxLayout()

        self.label3 = QLabel("BMS Data File Path")
        self.BMSDataPushButton = QPushButton('BMS Location')
        self.BMSDataPushButton.setFixedSize(140, 25)
        self.BMSDataPushButton.clicked.connect(self.open_save_dialog1)
        FileSavingLayout1.addWidget(self.label3)
        FileSavingLayout1.addWidget(self.BMSDataPushButton)

        self.label4 = QLabel("Cycler Data File Path")
        self.CyclerDataPushButton = QPushButton('Cycler Location')
        self.CyclerDataPushButton.setFixedSize(140, 25)
        self.CyclerDataPushButton.clicked.connect(self.open_save_dialog2)
        FileSavingLayout2.addWidget(self.label4)
        FileSavingLayout2.addWidget(self.CyclerDataPushButton)
        
        FileSavingLayoutUpper.addLayout(FileSavingLayout1)
        FileSavingLayoutUpper.addLayout(FileSavingLayout2)
        
        # Complete Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        layout.addWidget(self.label2)
        layout.addLayout(FileSavingLayoutUpper)

        # Create a container widget and set layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)    
        
    def open_save_dialog1(self):
        global GUI2GlobalFilePathBMS
        global GUI2StatusMessages
        # Open a file dialog and get the selected file path
        options = QFileDialog.Options()
        GUI2GlobalFilePathBMS, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if GUI2GlobalFilePathBMS:
            self.BMSDataPushButton.setEnabled(False)
            GUI2StatusMessages.append('BMS data Path Saved')

    def open_save_dialog2(self):
        global GUI2GlobalFilePathCycler
        global GUI2StatusMessages
        # Open a file dialog and get the selected file path
        options = QFileDialog.Options()
        GUI2GlobalFilePathCycler, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if GUI2GlobalFilePathCycler:
            self.CyclerDataPushButton.setEnabled(False)
            GUI2StatusMessages.append('Cycler data Path Saved')
        
    def proceed_work(self):
        global GUI2StepProcedure
        global GUI2StatusMessages
        GUI2StepProcedure = self.get_table_data()
        if len(GUI2StepProcedure) != 0:
            GUI2StatusMessages.append('Sequence Saved for Cycling')
        else:
            dialog = QDialog(self)
            dialog.setWindowTitle("Incorrect data")
            dialog.setFixedSize(300, 150)
            label = QLabel("FEED CORRECT DATA!!", dialog)
            label.setAlignment(Qt.AlignCenter)  # Align the text in the center
            layout = QVBoxLayout(dialog)
            layout.addWidget(label)
            dialog.exec_()

    def populate_first_column(self):
        # Add a QComboBox to the first column for each row
        for row in range(self.table.rowCount()):
            combo_box = QComboBox()
            combo_box.addItems(["CHARGING", "DISCHARGING", "REST", "GOTO"])
            self.table.setCellWidget(row, 0, combo_box)

    def populate_last_column(self):
        # Add a QComboBox to the first column for each row
        for row in range(self.table.rowCount()):
            combo_box = QComboBox()
            combo_box.addItems(["NEXT", "STOP"])
            self.table.setCellWidget(row, 10, combo_box)

    def add_row(self):
        # Add a new row to the table
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        
        # Add a QComboBox to the new row's first column
        combo_box = QComboBox()
        combo_box.addItems(["CHARGING", "DISCHARGING", "REST", 'GOTO'])
        self.table.setCellWidget(row_position, 0, combo_box)

        # Add a QComboBox to the new row's first column
        combo_box = QComboBox()
        combo_box.addItems(["NEXT", "STOP"])
        self.table.setCellWidget(row_position, 10, combo_box)

    def get_table_data(self):
        data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    row_data.append(item.text())
                else:
                    # For cells with widgets like QComboBox
                    widget = self.table.cellWidget(row, col)
                    if widget:
                        row_data.append(widget.currentText())
                    else:
                        row_data.append(None)
            data.append(row_data)
        return data

    def save_to_csv(self, file_path):
        global GUI2StatusMessages
        data = self.get_table_data()
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(self.headers)  # Write the headers first
            writer.writerows(data)
            GUI2StatusMessages.append('Sequence saved in the directory')

    def save_data(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_path:
            self.save_to_csv(file_path)

    def clear_table(self):
        # Clear all rows from the table
        self.table.setRowCount(0)

    def load_from_csv(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Read the headers
            
            # Check if headers match
            if headers != self.headers:
                QMessageBox.critical(self, "Error", "The file you're trying to load has incorrect columns.")
                return
            
            # # Clear existing data before loading new data
            # self.clear_table()
            
            # Load data into the table
            for row_data in reader:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                for col, data in enumerate(row_data):
                    if col == 0:  # Assuming the first column has a dropdown
                        combo_box = QComboBox()
                        combo_box.addItems(["CHARGING", "DISCHARGING", "REST", "GOTO"])
                        combo_box.setCurrentText(data)
                        self.table.setCellWidget(row_position, col, combo_box)
                    if col == 10:  # Assuming the first column has a dropdown
                        combo_box = QComboBox()
                        combo_box.addItems(["NEXT", "STOP"])
                        combo_box.setCurrentText(data)
                        self.table.setCellWidget(row_position, col, combo_box)
                    else:
                        item = QTableWidgetItem(data)
                        self.table.setItem(row_position, col, item)

    def show_load_options(self):
        # Create a custom dialog for load options
        dialog = QDialog(self)
        dialog.setWindowTitle("Load Options")
        dialog.setFixedSize(300, 150)
        
        # Create the label
        label = QLabel("Do you want to append in existing sequence\nor make new sequence?", dialog)
        
        # Create the buttons
        append_button = QPushButton("Append", dialog)
        clear_button = QPushButton("Clear", dialog)
        
        # Connect the buttons to their respective functions
        append_button.clicked.connect(lambda: self.load_data(dialog, append=True))
        clear_button.clicked.connect(lambda: self.load_data(dialog, append=False))
        
        # Set up the layout for the dialog
        layout = QVBoxLayout(dialog)
        layout.addWidget(label)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(append_button)
        button_layout.addWidget(clear_button)
        
        layout.addLayout(button_layout)
        
        # Show the dialog
        dialog.exec_()
    
    def show_load_options(self):
        # Create a custom dialog for load options
        dialog = QDialog(self)
        dialog.setWindowTitle("Load Options")
        dialog.setFixedSize(300, 150)
        
        # Create the label
        label = QLabel("Do you want to append in existing sequence\nor make new sequence?", dialog)
        
        # Create the buttons
        append_button = QPushButton("Append", dialog)
        clear_button = QPushButton("Clear", dialog)
        
        # Connect the buttons to their respective functions
        append_button.clicked.connect(lambda: self.load_data(dialog, append=True))
        clear_button.clicked.connect(lambda: self.load_data(dialog, append=False))
        
        # Set up the layout for the dialog
        layout = QVBoxLayout(dialog)
        layout.addWidget(label)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(append_button)
        button_layout.addWidget(clear_button)
        
        layout.addLayout(button_layout)
        
        # Show the dialog
        dialog.exec_()

    def load_data(self, dialog, append):
        dialog.accept()
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_path:
            if not append:
                self.clear_table()
            self.load_from_csv(file_path)

class GUI2StartButton(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global GUI2StepProcedure
        global GUI2StatusMessages
        global GUI2GlobalDictionary
        global GUI2GlobalFilePathBMS
        global GUI2GlobalFilePathCycler
        global GUI2FirstSinkPowerValue
        global GUI2FirstSinkCapacityValue
        global GUI2FirstSourcePowerValue
        global GUI2FirstSourceCapacityValue
        global GUI2StepParm

        if GUI2StepProcedure != None:

            #Updating the status
            GUI2StatusMessages.append('Reviewing the sequence file...')

            #Checking data given by the USER
            SignalArr = []
            for stepNumber in range(0, len(GUI2StepProcedure)):
                StepData = GUI2StepProcedure[stepNumber]
                stepMode = StepData[0]
                if (stepMode == "DISCHARGING") or (stepMode == "CHARGING"):
                    TurnAround = 0
                    try:
                        StepData[1] = float(StepData[1])
                        StepData[2] = float(StepData[2])
                        TurnAround = 1
                    except:
                        pass
                    if TurnAround == 1:
                        TurnAround2 = 0
                        try:
                            StepData[3] = float(StepData[3])
                            TurnAround2 = 1
                        except:
                            pass
                        try:
                            StepData[4] = float(StepData[4])
                            TurnAround2 = 1
                        except:
                            pass
                        try:
                            StepData[5] = float(StepData[5])
                            TurnAround2 = 1
                        except:
                            pass
                        try:
                            StepData[6] = float(StepData[6])
                            TurnAround2 = 1
                        except:
                            pass
                        try:
                            StepData[7] = float(StepData[7])
                            TurnAround2 = 1
                        except:
                            pass

                        if TurnAround2 == 1:
                            SignalArr.append('PASS')
                        else:
                            SignalArr.append('FAIL')
                    else:
                        SignalArr.append('FAIL')

                if stepMode == "REST":
                    TurnAround2 = 0
                    try:
                        StepData[5] = float(StepData[5])
                        TurnAround2 = 1
                    except:
                        pass
                    try:
                        StepData[6] = float(StepData[6])
                        TurnAround2 = 1
                    except:
                        pass
                    try:
                        StepData[7] = float(StepData[7])
                        TurnAround2 = 1
                    except:
                        pass

                    if TurnAround2 == 1:
                        SignalArr.append('PASS')
                    else:
                        SignalArr.append('FAIL')

                if stepMode == "GOTO":
                    TurnAround2 = 0
                    try:
                        StepData[8] = int(StepData[8])
                        StepData[9] = int(StepData[9])
                        TurnAround2 = 1
                    except:
                        pass

                    if TurnAround2 == 1:
                        SignalArr.append('PASS')
                    else:
                        SignalArr.append('FAIL')

            #Making decision to start the cycling on the basis of data
            if 'FAIL' not in SignalArr:

                #Updating the status
                GUI2StatusMessages.append('Pass: Review of sequence file')

                #Checking for Paths
                if (GUI2GlobalFilePathBMS != None) or (GUI2GlobalFilePathCycler != None):

                    #Waiting till the data start uploading
                    while True:
                        if GUI2GlobalDictionary != {}:
                            break
                        time.sleep(1)

                    #Checking FET Status
                    if (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 1):

                        #Initializing Parms
                        GUI2SerialConnectionCycler.write(b"FETCh:SINK:WHOur?")
                        time.sleep(0.01)
                        GUI2FirstSinkPowerValue = float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0])

                        GUI2SerialConnectionCycler.write(b"FETCh:SINK:AHOur?")
                        time.sleep(0.01)
                        GUI2FirstSinkCapacityValue = float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0])

                        GUI2SerialConnectionCycler.write(b"FETCh:WHOur?")
                        time.sleep(0.01)
                        GUI2FirstSourcePowerValue = float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0])

                        GUI2SerialConnectionCycler.write(b"FETCh:AHOur?")
                        time.sleep(0.01)
                        GUI2FirstSourceCapacityValue = float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0])

                        #Starting the Cycling Process
                        for stepNumber in range(0, len(GUI2StepProcedure)):
                            StepData = GUI2StepProcedure[stepNumber]
                            stepMode = StepData[0]
                            NextStepInstructions = StepData[-1]
                            GUI2StepParm = stepNumber
                            if stepMode == "DISCHARGING":
                                self.DischargingMode(FeedParms = StepData[1:])
                                if NextStepInstructions == "STOP":
                                    break
                            if stepMode == "CHARGING":
                                self.ChargingMode(FeedParms = StepData[1:])
                                if NextStepInstructions == "STOP":
                                    break
                            if stepMode == "REST":
                                self.RestMode(FeedParms = StepData[1:])
                                if NextStepInstructions == "STOP":
                                    break
                            if stepMode == "GOTO":
                                if (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 1) and (GUI2StopButtonClicked == None):
                                    GUI2StatusMessages.append(f'Started : GOTO Mode. Total Iterations : {StepData[9]}. Starting step : {StepData[8]}')
                                    TotalinternalIterations = int(StepData[9])
                                    for ChakkiChalo in range(0, TotalinternalIterations):
                                        for InternalIteration in range(int(StepData[8])-1, stepNumber):
                                            InternalStepData = GUI2StepProcedure[InternalIteration]
                                            InternalStepMode = InternalStepData[0]
                                            InternalNextStepInstructions = InternalStepData[-1]
                                            if InternalStepMode == "DISCHARGING":
                                                self.DischargingMode(FeedParms = InternalStepData[1:])
                                                if InternalNextStepInstructions == "STOP":
                                                    break
                                            if InternalStepMode == "CHARGING":
                                                self.ChargingMode(FeedParms = InternalStepData[1:])
                                                if InternalNextStepInstructions == "STOP":
                                                    break
                                            if InternalStepMode == "REST":
                                                self.RestMode(FeedParms = InternalStepData[1:])
                                                if InternalNextStepInstructions == "STOP":
                                                    break
                                    GUI2StatusMessages.append(f'Completed : GOTO Mode')
                                if NextStepInstructions == "STOP":
                                    break

                        #Checking FET Status
                        if (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 0):
                            GUI2StatusMessages.append('FET Status : 0. Cycler Turned OFF')
                        else:
                            GUI2StatusMessages.append('Cycling Completed as per Sequence provided')

                        #Step Number
                        GUI2StepParm = None

                    else:
                        GUI2StatusMessages.append('FET Status : 0. Turn ON the FET and Click START button again!')
                else:
                    if (GUI2GlobalFilePathBMS == None) and (GUI2GlobalFilePathCycler == None):
                        GUI2StatusMessages.append('BMS and Cycler data path not provided!!')
                    elif (GUI2GlobalFilePathCycler == None):
                        GUI2StatusMessages.append('Cycler data path not provided!!')
                    elif (GUI2GlobalFilePathBMS == None):
                        GUI2StatusMessages.append('BMS data path not provided!!')
            else:
                GUI2StatusMessages.append(f'Fail: Review of Sequence file : Step - {SignalArr.index("FAIL") + 1}')
        else:
            GUI2StatusMessages.append('No Sequence File Available')
 
    def DischargingMode(self, FeedParms):
        global GUI2CyclingStatus
        global GUI2StatusMessages
        global GUI2SerialConnectionCycler
        global GUI2GlobalDictionary
        global GUI2StopButtonClicked
        global GUI2PortAssignedToCycler
        global GUI2CyclerData
        global GUI2FirstSinkPowerValue
        global GUI2FirstSinkCapacityValue
        global GUI2FirstSourcePowerValue
        global GUI2FirstSourceCapacityValue

        #Fetching the feed parms
        DSGCurrentValv = float(FeedParms[0])
        DSGVoltageValv = float(FeedParms[1])
        try:
            DSGEndCurrentValv = float(FeedParms[2])
        except:
            DSGEndCurrentValv = FeedParms[2]
        try:
            DSGEndSoCValv = float(FeedParms[3])
        except:
            DSGEndSoCValv = FeedParms[3]
        try:
            DSGTimerValv = float(FeedParms[4])
        except:
            DSGTimerValv = FeedParms[4]
        try:
            DSGMinTempValv = float(FeedParms[5])
        except:
            DSGMinTempValv = FeedParms[5]
        try:
            DSGMaxTempValv = float(FeedParms[6])
        except:
            DSGMaxTempValv = FeedParms[6]
        #Fetching indexes with None or ''
        DSGArrValv = {
            'Current':[DSGEndCurrentValv],
            'SoC':[DSGEndSoCValv],
            'Timer':[DSGTimerValv],
            'MinTemp':[DSGMinTempValv],
            'MaxTemp':[DSGMaxTempValv]
        }
        ArrIndexNoneSpace = []
        try:
            float(DSGArrValv['Current'][0])
            ArrIndexNoneSpace.append('Current')
        except:
            pass
        try:
            float(DSGArrValv['SoC'][0])
            ArrIndexNoneSpace.append('SoC')
        except:
            pass
        try:
            float(DSGArrValv['Timer'][0])
            ArrIndexNoneSpace.append('Timer')
        except:
            pass
        try:
            float(DSGArrValv['MinTemp'][0])
            ArrIndexNoneSpace.append('MinTemp')
        except:
            pass
        try:
            float(DSGArrValv['MaxTemp'][0])
            ArrIndexNoneSpace.append('MaxTemp')
        except:
            pass
        ArrIndexNoneSpace = ArrIndexNoneSpace[0]
        #DISCHARGING
        ##########################################################################################################################
        if (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 1) and (GUI2StopButtonClicked == None):
            #Updating status
            GUI2StatusMessages.append(f'Started : Discharging ({datetime.now().strftime("%Y-%m-%d %H:%M")})')
            #Initialize Cycler
            GUI2SerialConnectionCycler.write(b"SYST:LOCK ON")
            time.sleep(0.1)
            #Setting parms
            Parms = f'SINK:CURR {DSGCurrentValv};VOLT {DSGVoltageValv}'
            ByteParms = bytes(Parms, 'utf-8')
            GUI2SerialConnectionCycler.write(ByteParms)
            time.sleep(0.1)
            #Turing cycler ON
            while True:
                GUI2SerialConnectionCycler.write(b"OUTP ON")
                time.sleep(0.1)
                GUI2SerialConnectionCycler.write(b"OUTPUT?")
                if GUI2SerialConnectionCycler.readline().decode().strip() == 'ON':
                    time.sleep(0.1)
                    break
            GUI2CyclingStatus = 'Discharging'

        #Reading the Cycler before starting DSG
        GUI2SerialConnectionCycler.write(b"FETCh:SINK:WHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Sink Power'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSinkPowerValue]
        GUI2SerialConnectionCycler.write(b"FETCh:SINK:AHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Sink Capacity'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSinkCapacityValue]
        GUI2SerialConnectionCycler.write(b"FETCh:WHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Source Power'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSourcePowerValue]
        GUI2SerialConnectionCycler.write(b"FETCh:AHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Source Capacity'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSourceCapacityValue]
        GUI2SerialConnectionCycler.write(b"SOUR:BATTery:TEST?")
        time.sleep(0.01)
        GUI2CyclerData['DSG Energy'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition('Wh,')[0].partition(', ')[2])]
        
        #Discharging Loop
        PresentTimeLoop = 0
        while (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 1) and (GUI2StopButtonClicked == None):
            time.sleep(1)
            #Reading POWER STATUS FROM CYCLER
            GUI2SerialConnectionCycler.write(b"STAT:QUES:COND?")
            time.sleep(0.01)
            power_resistor_ques = GUI2SerialConnectionCycler.readline().decode().strip()
            power_status = int(bin(int(power_resistor_ques))[2:].zfill(16)[2])
            #Checking data
            PresentDSGCurrent = GUI2GlobalDictionary['DSG_Current'][-1]
            PresentDSGSoC = GUI2GlobalDictionary['SOC'][-1]
            PresentTimeLoop = PresentTimeLoop + 1
            PresentMinTemp = min([GUI2GlobalDictionary['TS1'][-1], GUI2GlobalDictionary['TS2'][-1], GUI2GlobalDictionary['TS3'][-1], GUI2GlobalDictionary['TS4'][-1], GUI2GlobalDictionary['TS5'][-1], GUI2GlobalDictionary['TS6'][-1], GUI2GlobalDictionary['TS7'][-1], GUI2GlobalDictionary['TS8'][-1], GUI2GlobalDictionary['TS9'][-1], GUI2GlobalDictionary['TS10'][-1], GUI2GlobalDictionary['TS11'][-1], GUI2GlobalDictionary['TS12'][-1], GUI2GlobalDictionary['TS13_FLT'][-1], GUI2GlobalDictionary['TS0_FLT'][-1]])
            PresentMaxTemp = max([GUI2GlobalDictionary['TS1'][-1], GUI2GlobalDictionary['TS2'][-1], GUI2GlobalDictionary['TS3'][-1], GUI2GlobalDictionary['TS4'][-1], GUI2GlobalDictionary['TS5'][-1], GUI2GlobalDictionary['TS6'][-1], GUI2GlobalDictionary['TS7'][-1], GUI2GlobalDictionary['TS8'][-1], GUI2GlobalDictionary['TS9'][-1], GUI2GlobalDictionary['TS10'][-1], GUI2GlobalDictionary['TS11'][-1], GUI2GlobalDictionary['TS12'][-1], GUI2GlobalDictionary['TS13_FLT'][-1], GUI2GlobalDictionary['TS0_FLT'][-1]])
            #Conditions of Stop
            if 'Current' in ArrIndexNoneSpace:
                if (PresentDSGCurrent <= DSGEndCurrentValv) and (PresentDSGCurrent > 1) and (power_status == 0):
                    #Turning the cycler off
                    while True:
                        GUI2SerialConnectionCycler.write(b"OUTP OFF")
                        time.sleep(0.1)
                        GUI2SerialConnectionCycler.write(b"OUTPUT?")
                        if GUI2SerialConnectionCycler.readline().decode().strip() == 'OFF':
                            time.sleep(0.1)
                            break
                    break
            elif 'SoC' in ArrIndexNoneSpace:
                if ((PresentDSGSoC <= DSGEndSoCValv) and (power_status == 0)):
                    #Turning the cycler off
                    while True:
                        GUI2SerialConnectionCycler.write(b"OUTP OFF")
                        time.sleep(0.1)
                        GUI2SerialConnectionCycler.write(b"OUTPUT?")
                        if GUI2SerialConnectionCycler.readline().decode().strip() == 'OFF':
                            time.sleep(0.1)
                            break
                    break
            elif 'Timer' in ArrIndexNoneSpace:
                if ((PresentTimeLoop >= DSGTimerValv) and (power_status == 0)):
                    #Turning the cycler off
                    while True:
                        GUI2SerialConnectionCycler.write(b"OUTP OFF")
                        time.sleep(0.1)
                        GUI2SerialConnectionCycler.write(b"OUTPUT?")
                        if GUI2SerialConnectionCycler.readline().decode().strip() == 'OFF':
                            time.sleep(0.1)
                            break
                    break  
            elif 'MinTemp' in ArrIndexNoneSpace:
                if ((PresentMinTemp <= DSGMinTempValv) and (power_status == 0)):
                    #Turning the cycler off
                    while True:
                        GUI2SerialConnectionCycler.write(b"OUTP OFF")
                        time.sleep(0.1)
                        GUI2SerialConnectionCycler.write(b"OUTPUT?")
                        if GUI2SerialConnectionCycler.readline().decode().strip() == 'OFF':
                            time.sleep(0.1)
                            break
                    break
            elif 'MaxTemp' in ArrIndexNoneSpace:
                if ((PresentMaxTemp >= DSGMaxTempValv) and (power_status == 0)):
                    #Turning the cycler off
                    while True:
                        GUI2SerialConnectionCycler.write(b"OUTP OFF")
                        time.sleep(0.1)
                        GUI2SerialConnectionCycler.write(b"OUTPUT?")
                        if GUI2SerialConnectionCycler.readline().decode().strip() == 'OFF':
                            time.sleep(0.1)
                            break
                    break
            #Condition for Power Cut
            if power_status == 1:
                GUI2StatusMessages.append(f'Power Cut ({datetime.now().strftime("%Y-%m-%d %H:%M")})')
                #Saving Previous Current
                for FindingValvs in range(0,len(GUI2GlobalDictionary['DSG_Current'][::-1])):
                    if GUI2GlobalDictionary['DSG_Current'][::-1][FindingValvs] > 1:
                        StoppageCurrentDuetoPowerCut = GUI2GlobalDictionary['DSG_Current'][::-1][FindingValvs]
                        break
                #Closing Cycler port
                GUI2SerialConnectionCycler.close()
                #Power Cut functions
                time.sleep(20)
                #Try to make connection with cycler
                while (GUI2StopButtonClicked == None):
                    #Restoring Serial Connection Aand Power Status
                    try:
                        GUI2SerialConnectionCycler = serial.Serial(port=GUI2PortAssignedToCycler, baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
                        GUI2SerialConnectionCycler.write(b"STAT:QUES:COND?")
                        PowerCutStatus = GUI2SerialConnectionCycler.readline().decode().strip()
                        PowerStatus = int(bin(int(PowerCutStatus))[2:].zfill(16)[2])
                        if PowerStatus == 0:
                            break
                        else:
                            GUI2SerialConnectionCycler.close()
                    except serial.SerialException:
                        time.sleep(0.1)
                #Intializing cycler
                if (GUI2StopButtonClicked == None):
                    GUI2SerialConnectionCycler.write(b"SYST:LOCK ON")
                    time.sleep(0.1)
                    #SETTING UP ALL PARAMETERS FOR DISCHARGING PHASE again after the power restoration
                    Parms = f'SINK:CURR {StoppageCurrentDuetoPowerCut};VOLT {DSGVoltageValv}'
                    ByteParms = bytes(Parms, 'utf-8')
                    GUI2SerialConnectionCycler.write(ByteParms)
                    time.sleep(0.1)
                    #Turing Cycler 'ON'
                    while True:
                        GUI2SerialConnectionCycler.write(b"OUTP ON")
                        time.sleep(0.1)
                        GUI2SerialConnectionCycler.write(b"OUTPUT?")
                        if GUI2SerialConnectionCycler.readline().decode().strip() == 'ON':
                            time.sleep(0.1)
                            break
                    GUI2StatusMessages.append(f'Power Cut Restored ({datetime.now().strftime("%Y-%m-%d %H:%M")})')
        
        #Reading the Cycler after DSG completed
        GUI2SerialConnectionCycler.write(b"FETCh:SINK:WHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Sink Power'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSinkPowerValue]
        GUI2SerialConnectionCycler.write(b"FETCh:SINK:AHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Sink Capacity'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSinkCapacityValue]
        GUI2SerialConnectionCycler.write(b"FETCh:WHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Source Power'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSourcePowerValue]
        GUI2SerialConnectionCycler.write(b"FETCh:AHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Source Capacity'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSourceCapacityValue]
        GUI2SerialConnectionCycler.write(b"SOUR:BATTery:TEST?")
        time.sleep(0.01)
        GUI2CyclerData['DSG Energy'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition('Wh,')[0].partition(', ')[2])]
        
        if (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 1) and (GUI2StopButtonClicked == None):
            GUI2StatusMessages.append(f'Completed : Discharging ({datetime.now().strftime("%Y-%m-%d %H:%M")})')
        if (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 0):
            #Turn off cycler
            while True:
                GUI2SerialConnectionCycler.write(b"OUTP OFF")
                time.sleep(0.1)
                GUI2SerialConnectionCycler.write(b"OUTPUT?")
                if GUI2SerialConnectionCycler.readline().decode().strip() == 'OFF':
                    time.sleep(0.1)
                    break
        ##########################################################################################################################

    def ChargingMode(self, FeedParms):
        global GUI2CyclingStatus
        global GUI2StatusMessages
        global GUI2SerialConnectionCycler
        global GUI2GlobalDictionary
        global GUI2StopButtonClicked
        global GUI2PortAssignedToCycler
        global GUI2CyclerData
        global GUI2FirstSinkPowerValue
        global GUI2FirstSinkCapacityValue
        global GUI2FirstSourcePowerValue
        global GUI2FirstSourceCapacityValue

        #Fetching the feed parms
        CHGCurrentValv = float(FeedParms[0])
        CHGVoltageValv = float(FeedParms[1])
        try:
            CHGEndCurrentValv = float(FeedParms[2])
        except:
            CHGEndCurrentValv = FeedParms[2]
        try:
            CHGEndSoCValv = float(FeedParms[3])
        except:
            CHGEndSoCValv = FeedParms[3]
        try:
            CHGTimerValv = float(FeedParms[4])
        except:
            CHGTimerValv = FeedParms[4]
        try:
            CHGMinTempValv = float(FeedParms[5])
        except:
            CHGMinTempValv = FeedParms[5]
        try:
            CHGMaxTempValv = float(FeedParms[6])
        except:
            CHGMaxTempValv = FeedParms[6]
        #Fetching indexes with None or ''
        CHGArrValv = {
            'Current':[CHGEndCurrentValv],
            'SoC':[CHGEndSoCValv],
            'Timer':[CHGTimerValv],
            'MinTemp':[CHGMinTempValv],
            'MaxTemp':[CHGMaxTempValv]
        }
        ArrIndexNoneSpace = []
        try:
            float(CHGArrValv['Current'][0])
            ArrIndexNoneSpace.append('Current')
        except:
            pass
        try:
            float(CHGArrValv['SoC'][0])
            ArrIndexNoneSpace.append('SoC')
        except:
            pass
        try:
            float(CHGArrValv['Timer'][0])
            ArrIndexNoneSpace.append('Timer')
        except:
            pass
        try:
            float(CHGArrValv['MinTemp'][0])
            ArrIndexNoneSpace.append('MinTemp')
        except:
            pass
        try:
            float(CHGArrValv['MaxTemp'][0])
            ArrIndexNoneSpace.append('MaxTemp')
        except:
            pass
        ArrIndexNoneSpace = ArrIndexNoneSpace[0]
        #CHARGING
        ##########################################################################################################################
        if (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 1) and (GUI2StopButtonClicked == None):
            #Updating status
            GUI2StatusMessages.append(f'Started : Charging ({datetime.now().strftime("%Y-%m-%d %H:%M")})')
            #Initialize Cycler
            GUI2SerialConnectionCycler.write(b"SYST:LOCK ON")
            time.sleep(0.1)
            #Setting parms
            Parms = f'SOUR:CURRENT {CHGCurrentValv}A;VOLT {CHGVoltageValv}'
            ByteParms = bytes(Parms, 'utf-8')
            GUI2SerialConnectionCycler.write(ByteParms)
            time.sleep(0.1)
            #Turing cycler ON
            while True:
                GUI2SerialConnectionCycler.write(b"OUTP ON")
                time.sleep(0.1)
                GUI2SerialConnectionCycler.write(b"OUTPUT?")
                if GUI2SerialConnectionCycler.readline().decode().strip() == 'ON':
                    time.sleep(0.1)
                    break
            GUI2CyclingStatus = 'Charging'
        
        #Reading the Cycler before starting CHG
        GUI2SerialConnectionCycler.write(b"FETCh:SINK:WHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Sink Power'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSinkPowerValue]
        GUI2SerialConnectionCycler.write(b"FETCh:SINK:AHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Sink Capacity'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSinkCapacityValue]
        GUI2SerialConnectionCycler.write(b"FETCh:WHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Source Power'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSourcePowerValue]
        GUI2SerialConnectionCycler.write(b"FETCh:AHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Source Capacity'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSourceCapacityValue]
        GUI2SerialConnectionCycler.write(b"SOUR:BATTery:TEST?")
        time.sleep(0.01)
        GUI2CyclerData['CHG Energy'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition('Wh,')[0].partition(', ')[2])]
        
        #Charging Loop
        PresentTimeLoop = 0
        while (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 1) and (GUI2StopButtonClicked == None):
            time.sleep(1)
            #Reading POWER STATUS FROM CYCLER
            GUI2SerialConnectionCycler.write(b"STAT:QUES:COND?")
            time.sleep(0.01)
            power_resistor_ques = GUI2SerialConnectionCycler.readline().decode().strip()
            power_status = int(bin(int(power_resistor_ques))[2:].zfill(16)[2])
            #Checking data
            PresentCHGCurrent = GUI2GlobalDictionary['CHG_Current'][-1]
            PresentCHGSoC = GUI2GlobalDictionary['SOC'][-1]
            PresentTimeLoop = PresentTimeLoop + 1
            PresentMinTemp = min([GUI2GlobalDictionary['TS1'][-1], GUI2GlobalDictionary['TS2'][-1], GUI2GlobalDictionary['TS3'][-1], GUI2GlobalDictionary['TS4'][-1], GUI2GlobalDictionary['TS5'][-1], GUI2GlobalDictionary['TS6'][-1], GUI2GlobalDictionary['TS7'][-1], GUI2GlobalDictionary['TS8'][-1], GUI2GlobalDictionary['TS9'][-1], GUI2GlobalDictionary['TS10'][-1], GUI2GlobalDictionary['TS11'][-1], GUI2GlobalDictionary['TS12'][-1], GUI2GlobalDictionary['TS13_FLT'][-1], GUI2GlobalDictionary['TS0_FLT'][-1]])
            PresentMaxTemp = max([GUI2GlobalDictionary['TS1'][-1], GUI2GlobalDictionary['TS2'][-1], GUI2GlobalDictionary['TS3'][-1], GUI2GlobalDictionary['TS4'][-1], GUI2GlobalDictionary['TS5'][-1], GUI2GlobalDictionary['TS6'][-1], GUI2GlobalDictionary['TS7'][-1], GUI2GlobalDictionary['TS8'][-1], GUI2GlobalDictionary['TS9'][-1], GUI2GlobalDictionary['TS10'][-1], GUI2GlobalDictionary['TS11'][-1], GUI2GlobalDictionary['TS12'][-1], GUI2GlobalDictionary['TS13_FLT'][-1], GUI2GlobalDictionary['TS0_FLT'][-1]])
            #Conditions of Stop
            if 'Current' in ArrIndexNoneSpace:
                if (PresentCHGCurrent <= CHGEndCurrentValv) and (PresentCHGCurrent > 1) and (power_status == 0):
                    #Turning the cycler off
                    while True:
                        GUI2SerialConnectionCycler.write(b"OUTP OFF")
                        time.sleep(0.1)
                        GUI2SerialConnectionCycler.write(b"OUTPUT?")
                        if GUI2SerialConnectionCycler.readline().decode().strip() == 'OFF':
                            time.sleep(0.1)
                            break
                    break
            elif 'SoC' in ArrIndexNoneSpace:
                if ((PresentCHGSoC >= CHGEndSoCValv) and (power_status == 0)):
                    #Turning the cycler off
                    while True:
                        GUI2SerialConnectionCycler.write(b"OUTP OFF")
                        time.sleep(0.1)
                        GUI2SerialConnectionCycler.write(b"OUTPUT?")
                        if GUI2SerialConnectionCycler.readline().decode().strip() == 'OFF':
                            time.sleep(0.1)
                            break
                    break
            elif 'Timer' in ArrIndexNoneSpace:
                if ((PresentTimeLoop >= CHGTimerValv) and (power_status == 0)):
                    #Turning the cycler off
                    while True:
                        GUI2SerialConnectionCycler.write(b"OUTP OFF")
                        time.sleep(0.1)
                        GUI2SerialConnectionCycler.write(b"OUTPUT?")
                        if GUI2SerialConnectionCycler.readline().decode().strip() == 'OFF':
                            time.sleep(0.1)
                            break
                    break  
            elif 'MinTemp' in ArrIndexNoneSpace:
                if ((PresentMinTemp <= CHGMinTempValv) and (power_status == 0)):
                    #Turning the cycler off
                    while True:
                        GUI2SerialConnectionCycler.write(b"OUTP OFF")
                        time.sleep(0.1)
                        GUI2SerialConnectionCycler.write(b"OUTPUT?")
                        if GUI2SerialConnectionCycler.readline().decode().strip() == 'OFF':
                            time.sleep(0.1)
                            break
                    break
            elif 'MaxTemp' in ArrIndexNoneSpace:
                if ((PresentMaxTemp >= CHGMaxTempValv) and (power_status == 0)):
                    #Turning the cycler off
                    while True:
                        GUI2SerialConnectionCycler.write(b"OUTP OFF")
                        time.sleep(0.1)
                        GUI2SerialConnectionCycler.write(b"OUTPUT?")
                        if GUI2SerialConnectionCycler.readline().decode().strip() == 'OFF':
                            time.sleep(0.1)
                            break
                    break
            #Condition for Power Cut
            if power_status == 1:
                GUI2StatusMessages.append(f'Power Cut ({datetime.now().strftime("%Y-%m-%d %H:%M")})')
                #Saving Previous Current
                for FindingValvs in range(0,len(GUI2GlobalDictionary['CHG_Current'][::-1])):
                    if GUI2GlobalDictionary['CHG_Current'][::-1][FindingValvs] > 1:
                        StoppageCurrentDuetoPowerCut = GUI2GlobalDictionary['CHG_Current'][::-1][FindingValvs]
                        break
                #Closing Cycler port
                GUI2SerialConnectionCycler.close()
                #Power Cut functions
                time.sleep(20)
                #Try to make connection with cycler
                while (GUI2StopButtonClicked == None):
                    #Restoring Serial Connection Aand Power Status
                    try:
                        GUI2SerialConnectionCycler = serial.Serial(port=GUI2PortAssignedToCycler, baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
                        GUI2SerialConnectionCycler.write(b"STAT:QUES:COND?")
                        PowerCutStatus = GUI2SerialConnectionCycler.readline().decode().strip()
                        PowerStatus = int(bin(int(PowerCutStatus))[2:].zfill(16)[2])
                        if PowerStatus == 0:
                            break
                        else:
                            GUI2SerialConnectionCycler.close()
                    except serial.SerialException:
                        time.sleep(0.1)
                #Intializing cycler
                if (GUI2StopButtonClicked == None):
                    GUI2SerialConnectionCycler.write(b"SYST:LOCK ON")
                    time.sleep(0.1)
                    #SETTING UP ALL PARAMETERS FOR DISCHARGING PHASE again after the power restoration
                    Parms = f'SOUR:CURRENT {StoppageCurrentDuetoPowerCut}A;VOLT {CHGVoltageValv}'
                    ByteParms = bytes(Parms, 'utf-8')
                    GUI2SerialConnectionCycler.write(ByteParms)
                    time.sleep(0.1)
                    #Turing Cycler 'ON'
                    while True:
                        GUI2SerialConnectionCycler.write(b"OUTP ON")
                        time.sleep(0.1)
                        GUI2SerialConnectionCycler.write(b"OUTPUT?")
                        if GUI2SerialConnectionCycler.readline().decode().strip() == 'ON':
                            time.sleep(0.1)
                            break
                    GUI2StatusMessages.append(f'Power Cut Restored ({datetime.now().strftime("%Y-%m-%d %H:%M")})')
        
        #Reading the Cycler before starting CHG
        GUI2SerialConnectionCycler.write(b"FETCh:SINK:WHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Sink Power'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSinkPowerValue]
        GUI2SerialConnectionCycler.write(b"FETCh:SINK:AHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Sink Capacity'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSinkCapacityValue]
        GUI2SerialConnectionCycler.write(b"FETCh:WHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Source Power'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSourcePowerValue]
        GUI2SerialConnectionCycler.write(b"FETCh:AHOur?")
        time.sleep(0.01)
        GUI2CyclerData['Source Capacity'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition(' ')[0]) - GUI2FirstSourceCapacityValue]
        GUI2SerialConnectionCycler.write(b"SOUR:BATTery:TEST?")
        time.sleep(0.01)
        GUI2CyclerData['CHG Energy'] = [float(GUI2SerialConnectionCycler.readline().decode().strip().partition('Wh,')[0].partition(', ')[2])]
        
        if (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 1) and (GUI2StopButtonClicked == None):
            GUI2StatusMessages.append(f'Completed : Charging ({datetime.now().strftime("%Y-%m-%d %H:%M")})')
        if (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 0):
            #Turn off cycler
            while True:
                GUI2SerialConnectionCycler.write(b"OUTP OFF")
                time.sleep(0.1)
                GUI2SerialConnectionCycler.write(b"OUTPUT?")
                if GUI2SerialConnectionCycler.readline().decode().strip() == 'OFF':
                    time.sleep(0.1)
                    break
        ##########################################################################################################################

    def RestMode(self, FeedParms):
        global GUI2GlobalDictionary
        global GUI2StatusMessages
        global GUI2SerialConnectionCycler
        global GUI2CyclingStatus
        global GUI2StopButtonClicked
        global GUI2PortAssignedToCycler

        #Feed Params
        try:
            RestTimerParms = int(FeedParms[4])
        except:
            RestTimerParms = FeedParms[4]
        try:
            RestMinTempParms = float(FeedParms[5])
        except:
            RestMinTempParms = FeedParms[5]
        try:
            RestMaxTempParms = float(FeedParms[6])
        except:
            RestMaxTempParms = FeedParms[6]

        #Fetching indexes with None or ''
        RSTArrValv = {
            'Timer':[RestTimerParms],
            'MinTemp':[RestMinTempParms],
            'MaxTemp':[RestMaxTempParms]
        }
        ArrIndexNoneSpace = []
        try:
            float(RSTArrValv['Timer'][0])
            ArrIndexNoneSpace.append('Timer')
        except:
            pass
        try:
            float(RSTArrValv['MinTemp'][0])
            ArrIndexNoneSpace.append('MinTemp')
        except:
            pass
        try:
            float(RSTArrValv['MaxTemp'][0])
            ArrIndexNoneSpace.append('MaxTemp')
        except:
            pass
        ArrIndexNoneSpace = ArrIndexNoneSpace[0]

        #REST
        ##########################################################################################################################
        if (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 1) and (GUI2StopButtonClicked == None):
            GUI2StatusMessages.append(f'Started : Rest ({datetime.now().strftime("%Y-%m-%d %H:%M")})')
        #Turning the cycler off
        while True:
            GUI2SerialConnectionCycler.write(b"OUTP OFF")
            time.sleep(0.1)
            GUI2SerialConnectionCycler.write(b"OUTPUT?")
            if GUI2SerialConnectionCycler.readline().decode().strip() == 'OFF':
                time.sleep(0.1)
                break
        #Updating Cycling Status
        GUI2CyclingStatus = 'Rest'
        #Initializing parms for Power cut
        PowerCutSignal = 0
        #Iterations
        IterationsInRestMode = 0
        #Starting Rest Period and collecting data
        while (GUI2StopButtonClicked == None):
            time.sleep(1)
            #Present Temperatures
            PresentMinTemp = min([GUI2GlobalDictionary['TS1'][-1], GUI2GlobalDictionary['TS2'][-1], GUI2GlobalDictionary['TS3'][-1], GUI2GlobalDictionary['TS4'][-1], GUI2GlobalDictionary['TS5'][-1], GUI2GlobalDictionary['TS6'][-1], GUI2GlobalDictionary['TS7'][-1], GUI2GlobalDictionary['TS8'][-1], GUI2GlobalDictionary['TS9'][-1], GUI2GlobalDictionary['TS10'][-1], GUI2GlobalDictionary['TS11'][-1], GUI2GlobalDictionary['TS12'][-1], GUI2GlobalDictionary['TS13_FLT'][-1], GUI2GlobalDictionary['TS0_FLT'][-1]])
            PresentMaxTemp = max([GUI2GlobalDictionary['TS1'][-1], GUI2GlobalDictionary['TS2'][-1], GUI2GlobalDictionary['TS3'][-1], GUI2GlobalDictionary['TS4'][-1], GUI2GlobalDictionary['TS5'][-1], GUI2GlobalDictionary['TS6'][-1], GUI2GlobalDictionary['TS7'][-1], GUI2GlobalDictionary['TS8'][-1], GUI2GlobalDictionary['TS9'][-1], GUI2GlobalDictionary['TS10'][-1], GUI2GlobalDictionary['TS11'][-1], GUI2GlobalDictionary['TS12'][-1], GUI2GlobalDictionary['TS13_FLT'][-1], GUI2GlobalDictionary['TS0_FLT'][-1]])
            #Logic
            if 'Timer' in ArrIndexNoneSpace:
                if (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 1) and (IterationsInRestMode <= RestTimerParms):
                    if PowerCutSignal == 0:
                        #Checking Power Status
                        GUI2SerialConnectionCycler.write(b"STAT:QUES:COND?")
                        PowerCutStatus = GUI2SerialConnectionCycler.readline().decode().strip()
                        PowerStatus = int(bin(int(PowerCutStatus))[2:].zfill(16)[2])
                        if PowerStatus == 1:
                            GUI2SerialConnectionCycler.close()
                            PowerCutSignal = PowerCutSignal + 1
                            GUI2StatusMessages.append(f'Power Cut ({datetime.now().strftime("%Y-%m-%d %H:%M")})')
                else:
                    break
            elif 'MinTemp' in ArrIndexNoneSpace:
                if (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 1) and (PresentMinTemp <= RestMinTempParms):
                    if PowerCutSignal == 0:
                        #Checking Power Status
                        GUI2SerialConnectionCycler.write(b"STAT:QUES:COND?")
                        PowerCutStatus = GUI2SerialConnectionCycler.readline().decode().strip()
                        PowerStatus = int(bin(int(PowerCutStatus))[2:].zfill(16)[2])
                        if PowerStatus == 1:
                            GUI2SerialConnectionCycler.close()
                            PowerCutSignal = PowerCutSignal + 1
                            GUI2StatusMessages.append(f'Power Cut ({datetime.now().strftime("%Y-%m-%d %H:%M")})')
                else:
                    break
            elif 'MaxTemp' in ArrIndexNoneSpace:
                if (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 1) and (PresentMaxTemp <= RestMaxTempParms):
                    if PowerCutSignal == 0:
                        #Checking Power Status
                        GUI2SerialConnectionCycler.write(b"STAT:QUES:COND?")
                        PowerCutStatus = GUI2SerialConnectionCycler.readline().decode().strip()
                        PowerStatus = int(bin(int(PowerCutStatus))[2:].zfill(16)[2])
                        if PowerStatus == 1:
                            GUI2SerialConnectionCycler.close()
                            PowerCutSignal = PowerCutSignal + 1
                            GUI2StatusMessages.append(f'Power Cut ({datetime.now().strftime("%Y-%m-%d %H:%M")})')
                else:
                    break
            IterationsInRestMode = IterationsInRestMode + 1
            
        #Waiting till Power returns
        if (GUI2GlobalDictionary['FET_ON_OFF'][-1] == 1) and (GUI2StopButtonClicked == None):
            if PowerCutSignal != 0:
                while (GUI2StopButtonClicked == None):
                    try:
                        GUI2SerialConnectionCycler = serial.Serial(port=GUI2PortAssignedToCycler, baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
                        GUI2SerialConnectionCycler.write(b"STAT:QUES:COND?")
                        PowerCutStatus = GUI2SerialConnectionCycler.readline().decode().strip()
                        if PowerCutStatus:
                            PowerStatus = int(bin(int(PowerCutStatus))[2:].zfill(16)[2])
                            if PowerStatus == 0:
                                GUI2StatusMessages.append(f'Power Cut Restored ({datetime.now().strftime("%Y-%m-%d %H:%M")})')
                                break
                        GUI2SerialConnectionCycler.close()
                    except serial.SerialException:
                        time.sleep(0.1)
            if (GUI2StopButtonClicked == None):
                GUI2StatusMessages.append(f'Completed : Rest ({datetime.now().strftime("%Y-%m-%d %H:%M")})')
        ##########################################################################################################################

class GUI2StopButton(QThread):

    Signal1 = pyqtSignal(int)
    Signal2 = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        global GUI2SerialConnectionCycler
        global GUI2AllThreads
        global GUI2GlobalDictionary
        global GUI2SerialConnectionVCU
        global GUI2ConnectionCompleted
        global GUI2StopButtonClicked
        global GUI2GlobalFilePathBMS
        global GUI2StatusMessages
        global GUI2ErrorMessages
        global GUI2RoundingValvCheck
        global GUI2TimeSeriesX
        global GUI2StepProcedure
        global GUI2GlobalFilePathCycler
        global GUI2CyclingStatus
        global GUI2PortAssignedToCycler
        global GUI2CyclerData
        global GUI2FirstSinkPowerValue
        global GUI2FirstSinkCapacityValue
        global GUI2FirstSourcePowerValue
        global GUI2FirstSourceCapacityValue
        global GUI2StepParm

        #Updating message
        GUI2StatusMessages.append('Stop Button Clicked')

        #Real time doer
        GUI2StopButtonClicked = 'Clicked'

        #Checking if all threads are closed or not
        for ThreadNumber in GUI2AllThreads:
            if isinstance(ThreadNumber, threading.Thread):
                while True:
                    if not ThreadNumber.is_alive():
                        break
                    time.sleep(0.001)
            elif isinstance(ThreadNumber, QThread):
                while True:
                    if not ThreadNumber.isRunning():
                        break
                    time.sleep(0.001)

        #Closing all connections
        if GUI2SerialConnectionVCU != None:
            GUI2SerialConnectionVCU.close()
        if GUI2SerialConnectionCycler != None:
            GUI2SerialConnectionCycler.close()
            
        #Signal1
        self.Signal1.emit(1)

        #TimeSleep
        time.sleep(2)

        #Initializing all parameters
        GUI2AllThreads = []
        GUI2GlobalDictionary = {}
        GUI2SerialConnectionVCU = None
        GUI2SerialConnectionCycler = None
        GUI2ConnectionCompleted = None
        GUI2StopButtonClicked = None
        GUI2GlobalFilePathBMS = None
        GUI2StatusMessages = []
        GUI2ErrorMessages = []
        GUI2RoundingValvCheck = 4
        GUI2TimeSeriesX = 0
        GUI2StepProcedure = None
        GUI2GlobalFilePathCycler = None
        GUI2CyclingStatus = None
        GUI2PortAssignedToCycler = None
        GUI2CyclerData = {}
        GUI2FirstSinkPowerValue = None
        GUI2FirstSinkCapacityValue = None
        GUI2FirstSourcePowerValue = None
        GUI2FirstSourceCapacityValue = None
        GUI2StepParm = None

        #Signal2
        self.Signal2.emit(1)

if __name__ == '__main__':
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())