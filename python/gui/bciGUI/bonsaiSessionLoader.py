import numpy as np
import sys, zmq, os, subprocess, threading, queue, json
import socket as skt
from pathlib import Path
from PyQt6.QtWidgets import  QMenuBar, QLineEdit, QHBoxLayout, QLabel, QErrorMessage, QApplication, QMenuBar, QMenu, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QGroupBox, QInputDialog, QFileDialog
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QIntValidator, QAction
import seaborn as sns
import pandas as pd
from datetime import datetime, date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from aind_behavior_services import rig as srig
import aind_bci_no_movement.rig as rig
import aind_bci_no_movement.session as session
import aind_bci_no_movement.task_logic as task_logic
from aind_bci_no_movement.rig import BciNoMovementRig
from aind_bci_no_movement.session import BciNoMovementSession
from aind_bci_no_movement.task_logic import BciNoMovementTaskLogic


today = str(date.today())
print('Running Bonsai on:', today)

repoUpdateScriptPath = 'C:/git/AllenNeuralDynamics/aind-bci-no-movement/src/DataSchemas'
currentDir = 'C:/Users/svc_ncbehavior/bonsaiSubscription'

bonsaiPath = 'C:/git/AllenNeuralDynamics/aind-bci-no-movement/bonsai/bonsai.exe'
bonsaiScript = 'C:/git/AllenNeuralDynamics/aind-bci-no-movement/src/main_test.bonsai' #make this defined by sys.argv so can run as bat file

#object to run bonsai from app
class WorkerThread(QThread):
    result_ready = pyqtSignal(str)
    def run(self):
        process = subprocess.Popen([bonsaiPath, bonsaiScript])#, stdout=subprocess.PIPE, stderr=subprocess.PIPE)



def bonsaiSubscriptionService(stopEvent, msgQue):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://localhost:5556') #port for listening to bonsai
    socket.setsockopt_string(zmq.SUBSCRIBE, 'bci-no-movement')
    print('Subscribed to bonsai...')
    while not stopEvent.is_set():
        try: 
            data = socket.recv()
            if len(data)>15:
                message = data.decode('utf-8')
                entries = message.split(',')
                messageDict ={}
                for entry in entries:
                    dataName = (entry.split(':')[0]).split('"')[1]
                    dataMessage = entry.split(':')[1]
                    if dataName == 'name' or dataName == 'data':
                        messageDict[dataName] = dataMessage
                #successful baseline --> response outcome = reaction time
                now = datetime.now()
                messageDict['SoftwareTime'] = now.strftime("%H:%M:%S") + f':{now.microsecond // 1000:03d}'
                msgQue.put(messageDict) #we just care about returning this for this function... timestamped software events
        except zmq.Again:
            pass
    socket.close()
    context.term()
    print('Session Complete!')

msgQue = queue.Queue()

class sessionLoader(QWidget):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle('BCI Session Loader')
        # self.setGeometry(100,100,280,80)
        self.subscriberThread = None
        self.bonsaiThread = None
        self.stopEvent = threading.Event()
        self.bonsaiEvent = threading.Event()
        self.openMsg = 'Opening Bonsai'
        self.data = []
        self.trialStarting = True
        self.startTime = None
        self.sessionStartTime = None
        self.outcomeArr = []
        self.calculatePerformance = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.processMessages)
        self.timer.start(100) #100 ms
        self.trialCounter = 1
        self.pathToJsonSave = 'C:/Users/svc_ncbehavior/bonsaiSubscription/savedMice'
        self.dataToSave = {
            'RXNTimes': [],
            'Outcomes': []
            }
        #App Settings
        self.iti = 0.5
        self.lickResponseTime = 2
        self.responsePeriod = 20
        self.noMovePreTrial = 0.5
        self.consumePeriod = 5
        self.rewSize = 0.2
        self.waitForLickBool = False
        self.bciActiveGain = 2.0
        self.bciPassiveGain = 0.25
        self.bciThreshold = 3000
        self.punishmentDuration = 1.0
        self.delayTime = 0.5
        self.subjectWRID = 'test_subject'
        self.subjectIDentry = str(123123)

        self.initializeUI()

        #for now, this is going to be used for perf plot
        self.allowedResponseTime = 20
        self.performanceDF = None
        
        
    def initializeUI(self):
        layout = QVBoxLayout()
        
        #Space for Experiment Settings
        editArea1 = QHBoxLayout()
        editArea2 = QHBoxLayout()
        
        #Space for Mouse Data
        mouseEntryArea1 = QHBoxLayout()
        
        #Defining Text Boxes--- its easy this way when in vs code...
        h = 30
        self.textEdit1      = QTextEdit()
        self.textEdit1.setFixedHeight(h)
        self.textEdit2      = QTextEdit()
        self.textEdit2.setFixedHeight(h)
        self.textEdit3      = QTextEdit()
        self.textEdit3.setFixedHeight(h)
        self.textEdit4      = QTextEdit()
        self.textEdit4.setFixedHeight(h)
        self.textEdit5      = QTextEdit()
        self.textEdit5.setFixedHeight(h)
        self.textEdit6      = QTextEdit()
        self.textEdit6.setFixedHeight(h)
        self.textEdit7      = QTextEdit()
        self.textEdit7.setFixedHeight(h)
        self.textEdit8      = QTextEdit()
        self.textEdit8.setFixedHeight(h)
        self.textEdit9      = QTextEdit()
        self.textEdit9.setFixedHeight(h)
        self.textEdit10     = QTextEdit()
        self.textEdit10.setFixedHeight(h)
        self.textEdit11     = QTextEdit()
        self.textEdit11.setFixedHeight(h)
        self.subjectName    = QTextEdit()
        self.subjectName.setFixedHeight(h)
        
        self.subjectID      = QLineEdit()
        self.subjectID.setValidator(QIntValidator())
        self.subjectID.setMaxLength(6)
        self.subjectID.setFixedHeight(h)
        
        #just remember to convert everything to floats (where necessary) when grabbing the text
        
        #ITI Entry
        self.itiLabel = QGroupBox('ITI')
        self.textEdit1.setPlainText(str(self.iti))
        self.itiLayout = QVBoxLayout()
        self.itiLayout.addWidget(self.textEdit1)
        self.itiLabel.setLayout(self.itiLayout)
        
        #Answer Period Entry (Time to get reward)
        self.responseTimeLabel = QGroupBox('Time to Respond To Reward')
        self.textEdit2.setPlainText(str(self.lickResponseTime))
        self.responseTimeLayout = QVBoxLayout()
        self.responseTimeLayout.addWidget(self.textEdit2)
        self.responseTimeLabel.setLayout(self.responseTimeLayout)
        
        #Response Period Entry (After Reward)
        self.responsePeriodLabel = QGroupBox('Response Period Time')
        self.textEdit3.setPlainText(str(self.responsePeriod))
        self.responsePeriodLayout = QVBoxLayout()
        self.responsePeriodLayout.addWidget(self.textEdit3)
        self.responsePeriodLabel.setLayout(self.responsePeriodLayout)
        
        #Movement Baseline Before Trial Requirement
        self.noMovePretrialLabel = QGroupBox('Baseline Time Requirement (Pre-Start)')
        self.textEdit4.setPlainText(str(self.noMovePreTrial))
        self.noMovePretrialLayout = QVBoxLayout()
        self.noMovePretrialLayout.addWidget(self.textEdit4)
        self.noMovePretrialLabel.setLayout(self.noMovePretrialLayout)
        
        #Time allowed to consume water
        self.consumePeriodLabel = QGroupBox('Consumption Period')
        self.textEdit5.setPlainText(str(self.consumePeriod))
        self.consumePeriodLayout = QVBoxLayout()
        self.consumePeriodLayout.addWidget(self.textEdit5)
        self.consumePeriodLabel.setLayout(self.consumePeriodLayout)
        
        #Reward Size
        self.rewSizeLabel = QGroupBox('Reward Size')
        self.textEdit6.setPlainText(str(self.rewSize))
        self.rewSizeLayout = QVBoxLayout()
        self.rewSizeLayout.addWidget(self.textEdit6)
        self.rewSizeLabel.setLayout(self.rewSizeLayout)
        
        #Autowater Boolean/True-False
        self.waitForLickLabel = QGroupBox('Wait For Lick?')
        self.textEdit7.setPlainText(str(self.waitForLickBool))
        self.waitForLickLayout = QVBoxLayout()
        self.waitForLickLayout.addWidget(self.textEdit7)
        self.waitForLickLabel.setLayout(self.waitForLickLayout)
        
        #Passive Motor Gain (BCI)
        self.motorGainLabel = QGroupBox('Motor Passive Gain')
        self.textEdit8.setPlainText(str(self.bciPassiveGain))
        self.motorGainLayout = QVBoxLayout()
        self.motorGainLayout.addWidget(self.textEdit8)
        self.motorGainLabel.setLayout(self.motorGainLayout)
        
        #Active Motor Gain (BCI)
        self.activeGainLabel = QGroupBox('Motor Active Gain')
        self.textEdit9.setPlainText(str(self.bciActiveGain))
        self.activeGainLayout = QVBoxLayout()
        self.activeGainLayout.addWidget(self.textEdit9)
        self.activeGainLabel.setLayout(self.activeGainLayout)
        
        #Threshold for movement penalty
        self.moveThreshold = QGroupBox('Movement Threshold')
        self.textEdit10.setPlainText(str(self.bciThreshold))
        self.moveThresholdLayout = QVBoxLayout()
        self.moveThresholdLayout.addWidget(self.textEdit10)
        self.moveThreshold.setLayout(self.moveThresholdLayout)
        
        #Punishment Duration
        self.punishmentDurationLabel = QGroupBox('Punishment Duration')
        self.textEdit11.setPlainText(str(self.punishmentDuration))
        self.punishmentDurationLayout = QVBoxLayout()
        self.punishmentDurationLayout.addWidget(self.textEdit11)
        self.punishmentDurationLabel.setLayout(self.punishmentDurationLayout)
        
        #Water Restriction Identifier and notes (easy name)
        self.WRnameLabel = QGroupBox('WR Name and Notes')
        self.subjectName.setPlainText(self.subjectWRID)
        self.WRnameLayout = QVBoxLayout()
        self.WRnameLayout.addWidget(self.subjectName)
        self.WRnameLabel.setLayout(self.WRnameLayout)
        
        #Mouse ID (hard name)
        self.subjectIDLabel = QGroupBox('Mouse ID')
        self.subjectID.setText(self.subjectIDentry)
        self.subjectIDLayout = QVBoxLayout()
        self.subjectIDLayout.addWidget(self.subjectID)
        self.subjectIDLabel.setLayout(self.subjectIDLayout)
        
        #Save Button
        self.saveSettingsButton = QPushButton('Save Settings', self)
        self.saveSettingsButton.clicked.connect(self.updateSettings)
        
        #Experiment Settings are row 2
        editArea1.addWidget(self.itiLabel)
        editArea1.addWidget(self.responseTimeLabel)
        editArea1.addWidget(self.responsePeriodLabel)
        editArea1.addWidget(self.noMovePretrialLabel)
        editArea1.addWidget(self.consumePeriodLabel)
        editArea1.addWidget(self.rewSizeLabel)
        editArea1.addWidget(self.waitForLickLabel)
        editArea1.addWidget(self.motorGainLabel)
        editArea1.addWidget(self.activeGainLabel)
        editArea1.addWidget(self.moveThreshold)
        editArea1.addWidget(self.punishmentDurationLabel)
        editArea1.addWidget(self.saveSettingsButton)
        
        #Mouse Data is row 1
        mouseEntryArea1.addWidget(self.WRnameLabel)
        mouseEntryArea1.addWidget(self.subjectIDLabel)
        
        #Define Buttons involved with ZMQ and bonsai
        self.startSubscriberButton = QPushButton('Subscribe to bonsai', self)
        self.startSubscriberButton.clicked.connect(self.startBonsaiSubscription)
        self.stopSubscriberButton = QPushButton('Stop bonsai subscription', self)
        self.stopSubscriberButton.clicked.connect(self.stopBonsaiSubscription)
        self.openBonsaiGUIButton = QPushButton('Open Bonsai', self)
        self.openBonsaiGUIButton.clicked.connect(self.runBonsai)
        self.resetSocketButton = QPushButton('Reset Sockets',self)
        self.resetSocketButton.clicked.connect(self.resetSocket)
        
        #Live Feed Label
        self.label = QLabel("Messages will appear here", self)
        self.triallabel = QLabel(f'Trial: 1')
        
        #Plotting of session
        self.figure, self.ax = plt.subplots()
        self.ax.set(xlabel = 'Trial', ylabel='Time')
        self.canvas = FigureCanvas(self.figure)
        
        #For File Menu
        self.mouseOptions = self.createMenu()
        layout.addWidget(self.mouseOptions)
        
        #Plot at top
        layout.addWidget(self.canvas)
        
        #Buttons for present session
        layout.addWidget(self.triallabel)
        layout.addWidget(self.startSubscriberButton)
        layout.addWidget(self.stopSubscriberButton)
        layout.addWidget(self.openBonsaiGUIButton)
        layout.addWidget(self.resetSocketButton)
        
        #first settings section
        layout.addLayout(mouseEntryArea1)
        
        #second settings section
        layout.addLayout(editArea1)
        layout.addLayout(editArea2)
        
        #live feed of experiment to verify zmq comms are working
        layout.addWidget(self.label)

        self.setLayout(layout)
        self.setWindowTitle('Bonsai Session Loader')
        self.show()
        

        
    def createMenu(self):
        options = QMenuBar()
        options.setFixedWidth(100)
        fileMenu = options.addMenu('File')
        #Action for adding new mouse
        newMouse = QAction('New Mouse', self)
        newMouse.triggered.connect(self.addMouse)
        fileMenu.addAction(newMouse)
        
        #Action for Loading Existing Mouse Settings 
        loadMouse = QAction('Load Mouse Settings', self)
        loadMouse.triggered.connect(self.loadMouse)
        fileMenu.addAction(loadMouse)
        
        #Action for loading past data
        pastData = QAction('Load Past Data', self)
        pastData.triggered.connect(self.loadMouse)
        fileMenu.addAction(pastData)
        
        #Clear Plots before session
        clearPlots = QAction('Clear Plot', self)
        clearPlots.triggered.connect(self.clearPlot)
        fileMenu.addAction(clearPlots)
        return options
    
    def clearPlot(self):
        self.outcomeArr = []
        self.data = []
        self.trialCounter = 1
        self.updatePlot()
    
    def saveData(self):
        dataDict = {}
        dataDict['RXNTimes'] = self.data
        dataDict['Outcomes'] = self.outcomeArr
        if Path(self.pathToJsonSave + '/' + str(self.subjectIDentry)).exists():
            with open(self.pathToJsonSave + '/' + str(self.subjectIDentry)+ '/data_' + today + '.json', 'w') as f:
                json.dump(dataDict, f, indent =2)
        else:
            print(str(self.subjectIDentry), ' had no saved info yet')
            
    def updateSettings(self):
        #Update App Attributes (should also save these attributes to text file in case of accidental closing or crashes)
        self.iti = float(self.textEdit1.toPlainText())
        self.lickResponseTime = float(self.textEdit2.toPlainText())
        self.responsePeriod = float(self.textEdit3.toPlainText())
        self.noMovePreTrial = float(self.textEdit4.toPlainText())
        self.consumePeriod = float(self.textEdit5.toPlainText())
        self.rewSize = float(self.textEdit6.toPlainText())
        self.waitForLickBool = bool(self.textEdit7.toPlainText())
        self.bciActiveGain = float(self.textEdit8.toPlainText())
        self.bciPassiveGain = float(self.textEdit9.toPlainText())
        self.bciThreshold = float(self.textEdit10.toPlainText())
        self.punishmentDuration = float(self.textEdit11.toPlainText())
        
        self.subjectWRID = self.subjectName.toPlainText()
        self.subjectIDentry = str(self.subjectID.toPlainText())
        


        #Running the folloing functions will write the json files for the mouse
        zaberCommands = []
        rig_settings = rig.BciNoMovementRig(
            computer_name=os.environ["COMPUTERNAME"],
            rig_name="bci-no-movement-rig",
            schema_version="0.2.0",
            describedBy="https://github.com/AllenNeuralDynamics/aind-bci-no-movement/blob/main/src/DataSchemas/bci-no-movement-rig.json",
            harp_behavior=srig.HarpBehavior(port_name="COM8"),
            harp_load_cell=srig.HarpLoadCells(port_name="COM7"),
            harp_clock=srig.HarpClockSynchronizer(port_name="COM9"),
            camera_0=srig.SpinnakerCamera(
                binning=1,
                exposure=2000,
                frame_rate=200,
                gain=0,
                serial_number="23381093",
            ),
            zaber_manipulator=rig.ZaberManipulator(
                com_port="COM10",
                velocity=9999999,
                acceleration=9999999,
                spout_axis=rig.Axis.X,
                generic_commands=zaberCommands,
                x_axis=rig.ZaberAxis(device_index=0, axis_index=1),
                y_axis=rig.ZaberAxis(device_index=0, axis_index=2),
                z_axis=rig.ZaberAxis(device_index=1, axis_index=1),
            ),
            networking=rig.Networking(
                zmq_publisher=rig.ZmqConnection(connection_string="@tcp://localhost:5556", topic="bci-no-movement"),
                zmq_subscriber=rig.ZmqConnection(connection_string="@tcp://localhost:5557", topic="bci-no-movement"),
            ),
            operation=rig.Operation(load_cell_offset=[30, 0, 0, 0, 0, 0, 0, 0], load_cell_index=0),
        )

        task_logic_settings = task_logic.BciNoMovementTaskLogic(
            schema_version="0.1.1",
            describedBy="https://github.com/AllenNeuralDynamics/aind-bci-no-movement/blob/main/src/DataSchemas/bci-no-movement-tasklogic.json",
            enable_sound_on_reward_zone_entry=True,

            #################################################################################
            ## Important Settings ##########################################################
            inter_trial_interval=self.iti,
            lick_response_time=self.lickResponseTime,
            max_trial_duration=self.responsePeriod,
            no_movement_time_before_trial=self.noMovePreTrial,
            reward_consume_time=self.consumePeriod,
            valve_open_time=self.rewSize,
            wait_for_lick=self.waitForLickBool,
            far_position_offset=10, #this will be editable soon enough...
            manipulator_reset_position=task_logic.Point3d(x=43, y=-2, z=0.26),
            wait_microscope_time=0.5,
            bci_passive_control=task_logic.Control(
                gain=self.bciPassiveGain, 
                baseline_threshold=self.bciThreshold
                ),
            #######################################
            #we will be removing no-move settings
            #######################################
            no_movement_passive_control=task_logic.Control(
                gain=1.0, 
                baseline_threshold=self.bciThreshold, 
                low_pass_cut_off=50, 
                high_pass_cut_off=0.001
                ),
            #######################################
            bci_active_control=task_logic.Control(
                gain=self.bciActiveGain, 
                baseline_threshold=1.5 #should make this an editable setting? but its also settable in slap2_AIND/scanimage.. soo....
                ),
            skip_2p_handshake=True,
            punish_on_movement_duration=self.punishmentDuration,
            delay_after_handshake=self.delayTime,
        )
        #################################################################################
        #################################################################################
        
        
        session_info = session.BciNoMovementSession(
            describedBy="https://github.com/AllenNeuralDynamics/aind-bci-no-movement/blob/main/src/DataSchemas/bci-no-movement-session.json",
            allow_dirty_repo=True,
            experiment="bci-no-movement",
            
            notes=self.subjectWRID, #DEFINED IN SETTINGS
            
            #Where to look for data locally (computer-specific)
            root_path="C:/Data/",
            remote_path="C:/DataRemote/",
            
            
            subject = str(self.subjectIDentry),  #DEFINED IN SETTINGS
            
            
            date=datetime.datetime.now(),
            experiment_version="0.0.0")
        
        BciNoMovementRig.model_validate(rig_settings)
        BciNoMovementTaskLogic.model_validate(task_logic_settings)
        BciNoMovementSession.model_validate(session_info)

        with open("C:/git/AllenNeuralDynamics/aind-bci-no-movement/local/Rigs/aind_behavior_rig_model.json", "w+") as f:
            f.write(rig_settings.model_dump_json(indent=2))
        with open("C:/git/AllenNeuralDynamics/aind-bci-no-movement/local/Subjects/aind_behavior_session_model.json", "w+") as f:
            f.write(session_info.model_dump_json(indent=2))
        with open("C:/git/AllenNeuralDynamics/aind-bci-no-movement/local/TaskLogic/aind_behavior_task_logic_model.json", "w+") as f:
            f.write(task_logic_settings.model_dump_json(indent=2)) 
   
        #Save everything as a json
        settingsDict = {
            'ITI': self.iti,
            'LickResponseTime': self.lickResponseTime,
            'ResponsePeriod': self.responsePeriod,
            'NoMovePreTrial': self.noMovePreTrial,
            'ConsumptionPeriod': self.consumePeriod,
            'RewardSize': self.rewSize,
            'Autowater': self.waitForLickBool,
            'BCIActiveGain': self.bciActiveGain,
            'BCIPassiveGain': self.bciPassiveGain,
            'BCIThreshold': self.bciThreshold,
            'PunishmentDuration': self.punishmentDuration,
            'DelayTime': self.delayTime,
            'SubjectNotes': self.subjectWRID,
            'SubjectID': self.subjectIDentry
        }
        
        with open(self.pathToJsonSave + '/' + str(self.subjectIDentry)+ '/settings.json', 'w') as f:
            json.dump(settingsDict, f, indent =2)
    
    
    
    def loadMouse(self):
        options = QFileDialog.Options()
        options |= QFileDialog.Option.DontUseNativeDialog
        fileDialog = QFileDialog()
        fileDialog.setOptions(options)
        fileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if fileDialog.exec():
            selectedFile = fileDialog.selectedFiles()
            if 'settings' in selectedFile:
                settingsFile = selectedFile[0]
                self.text_edit.setPlainText(settingsFile)
                with open(self.pathToJsonSave + '/'+ str(self.subjectIDentry)+  '/settings.json', 'r') as f:
                    settingsDict = json.load(f)
                print('Mouse Settings Loaded')
                self.textEdit1.setPlainText(str(settingsDict['ITI'] ))
                self.textEdit2.setPlainText(str(settingsDict['LickResponseTime'] ))
                self.textEdit3.setPlainText(str(settingsDict['ResponsePeriod'] ))
                self.textEdit4.setPlainText(str(settingsDict['NoMovePreTrial']))
                self.textEdit5.setPlainText(str(settingsDict['ConsumptionPeriod'] ))
                self.textEdit6.setPlainText(str(settingsDict['RewardSize'] ))
                self.textEdit7.setPlainText(str(settingsDict['Autowater']))
                self.textEdit8.setPlainText(str(settingsDict['BCIActiveGain'] ))
                self.textEdit9.setPlainText(str(settingsDict['BCIPassiveGain'] ))
                self.textEdit10.setPlainText(str(settingsDict['BCIThreshold']))
                self.textEdit11.setPlainText(str(settingsDict['PunishmentDuration'] ))
                self.subjectName.setPlainText(str(settingsDict['SubjectNotes'] ))
                self.subjectID.setText(int(settingsDict['SubjectID'] ))
            
            elif 'data' in selectedFile:
                settingsFile = selectedFile[0]
                self.text_edit.setPlainText(settingsFile)
                with open(self.pathToJsonSave + '/'+ str(self.subjectIDentry)+  '/data.json', 'r') as f:
                    dataDict = json.load(f)
                print('Past Mouse Data Loaded')
                self.data = dataDict['RXNTimes']
                self.outcomeArr = dataDict['Outcomes']
                self.trialCounter = 1
                self.updatePlot()

    def addMouse(self):
        
        #Ask for mouse ID
        mouseID, ok = QInputDialog.getText(self, 'New Mouse Entry', 'Enter 6-digit mouse ID here and press ok:')
        if ok and mouseID != '':
            try:
                self.subjectIDentry = mouseID
                self.subjectID.setText(mouseID)
                os.mkdir(self.pathToJsonSave + '/' + str(self.subjectIDentry))
                newMouse = self.subjectWRID
                print(newMouse, ' Added as New Mouse')
            except ValueError:
                err = QErrorMessage(self)
                err.showMessage('Please enter valid ID')
                err.exec()
        elif ok:
            err = QErrorMessage(self)
            err.showMessage('Please enter valid ID')
            err.exec()
            
    def resetSocket(self):
        host = 'localhost'
        port = 5556
        cmdlet = f'netstat -ano | findstr {port}'
        result = subprocess.run(cmdlet, shell=True, capture_output=True, text=True)
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if f':{port}' in line:
                    print(line)
                    parts = line.split()
                    pid = parts[-1]
                    killcmdlet = f'taskkill /PID {pid} /F'
                    os.system(killcmdlet)
                    print('I KILLED THE SOCKET! I KILLED IT IN COLD BLOOD! HOW DO I TELL MY FAMILY WHAT IVE DONE!?')
                    return
        print(f'Nothing to kill.... Socket {port} is not open')

    #currently working on this because need to fix threading issue...
    def runBonsai(self):
        if self.bonsaiThread is None or not self.bonsaiThread.isAlive():
            self.bonsaiEvent.clear()
            # self.bonsaiThread = threading.Thread(target= openCloseBonsai, args=(self.bonsaiEvent, self.openMsg))
            self.bonsaiThread = WorkerThread()
            self.bonsaiThread.finished.connect(self.resetBonsaiThread)
            self.bonsaiThread.start()
    
    def resetBonsaiThread(self):
        self.bonsaiThread = None
   
    def startBonsaiSubscription(self):
        if self.subscriberThread is None or not self.subscriberThread.is_alive():
            self.stopEvent.clear()
            self.subscriberThread = threading.Thread(target=bonsaiSubscriptionService, args=(self.stopEvent, msgQue))
            self.subscriberThread.start()
            print("Starting Amazon-Bonsai-Prime for $2000/month...")

    def stopBonsaiSubscription(self):
        if self.subscriberThread is not None and self.subscriberThread.is_alive():
            self.stopEvent.set()
            self.subscriberThread.join()
            print("Stopping Amazon-Bonsai-Prime Subscription because Im too poor to afford that...")

    def processMessages(self):
        while not msgQue.empty():
            message = msgQue.get()
            self.label.setText(f"Received message: {message}")
            print(f"Received message: {message}")
            if message['name'] == '"SuccessfulBaseline"':
                print('START FLAG')
                absTime = self.convertToAbsTime(message['SoftwareTime'])
                if self.trialCounter == 1:
                    self.sessionStartTime = absTime
                    absTime = 0 #every trial is going to be relative time
                else:
                    absTime = absTime - self.sessionStartTime
                self.trialStarting = True
                self.startTime = absTime
                # print('Time:', absTime, 'DataType:', type(absTime))
            if message['name'] == '"ResponseOutcome"':
                if message['data'] == 'true':
                    self.outcomeArr.append(1)
                else:
                    self.outcomeArr.append(0)
                self.performanceDF = self.calculatePerformanceFunc()
                
                print('END FLAG')
                absTime = self.convertToAbsTime(message['SoftwareTime'])
                absTime = absTime - self.sessionStartTime
                self.trialStarting = False
                deltaT = absTime - self.startTime
                self.data.append(deltaT)
                # print('Time series:',self.data, 'DataType:', type(self.data))
            if self.trialStarting == False:
                self.updatePlot()
                self.updateTrialLabel
                self.trialCounter += 1
                
    def updateTrialLabel(self):
        self.label.setText(f'Trial: {self.trialCounter}')


    def updatePlot(self):
        self.ax.clear()
        #turn it to dataframe to make sns scatterplot look good
        dataArr = np.array(self.data)
        dataDF = pd.DataFrame(dataArr)
        # Only one plot has a legend, thats the first entry 
        if len(self.calculatePerformance) > 1 and self.trialCounter == 1:
            self.ax = plt.scatter(dataDF.index, dataDF.values, label='RXN Time', color='lightblue')
            self.ax = plt.plot(self.performanceDF.values, color='black', label='Performance')
            plt.legend()
        else:
            self.ax = plt.scatter(dataDF.index, dataDF.values, color='lightblue')
            self.ax = plt.plot(self.performanceDF.values, color='black')

        self.figure.supxlabel('Trial')
        self.figure.supylabel('RXN Time || Performance')
        self.canvas.draw()

    def calculatePerformanceFunc(self):
        outcomes = np.array(self.outcomeArr)
        performance = np.nanmean(outcomes) *self.allowedResponseTime
        self.calculatePerformance.append(performance)
        print(self.calculatePerformance)
        return pd.DataFrame(np.array(self.calculatePerformance))
                
    def convertToAbsTime(self, timeString):
        h, m, s, ms = timeString.split(':')
        h = int(h)
        m = int(m)
        s = int(s)
        ms = int(ms)
        totalSeconds = h * 3600 + m * 60 + s + ms / 1000.0
        print(totalSeconds)
        return totalSeconds

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = sessionLoader()
    app.aboutToQuit.connect(ex.saveData)
    ex.show() #necessary?
    sys.exit(app.exec())
