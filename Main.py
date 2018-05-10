# coding:utf-8

import sys, os
from PyQt4 import QtGui
import numpy as np
from texture import tex, postProcedure
import time
from conv_fliter import main_function
from ma_fn import main_mabaod, obtain_data
import matplotlib.pyplot as plt


class MyWindow(QtGui.QWidget):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.fname = 'd:/'
        self.outFile = {}
        self.initUI()
        self.pP = postProcedure()

    def initUI(self):

        self.EWIEdit = QtGui.QLineEdit()
        self.V_0_Edit = QtGui.QLineEdit()
        self.ExtraEdit = QtGui.QLineEdit()
        # self.V_1_Edit = QtGui.QLineEdit()
        # self.H_0_Edit = QtGui.QLineEdit()
        # self.H_1_Edit = QtGui.QLineEdit()
        # self.threshold = QtGui.QLineEdit()

        EWIAction = QtGui.QPushButton('B2 NIR')
        V_0_Action = QtGui.QPushButton('B4 Green')
        Extra = QtGui.QPushButton('B5/6 SWIR1')
        # H_0_Action = QtGui.QPushButton('180')
        # V_1_Action = QtGui.QPushButton('90')
        # H_1_Action = QtGui.QPushButton('0')
        # self.ok_Action = QtGui.QPushButton('threshold ok')
        self.progressBar = QtGui.QProgressBar()

        # Action1 = QtGui.QPushButton('Angle 270',self)
        # Action2 = QtGui.QPushButton('Angle 180',self)
        about = QtGui.QPushButton('Read ME', self)
        execu = QtGui.QPushButton('Run', self)

        grid = QtGui.QGridLayout()
        grid.setSpacing(5)

        grid.addWidget(self.EWIEdit, 1, 0)
        grid.addWidget(EWIAction, 1, 1)

        grid.addWidget(self.V_0_Edit, 2, 0)
        grid.addWidget(V_0_Action, 2, 1)

        grid.addWidget(self.ExtraEdit, 3, 0)
        grid.addWidget(Extra, 3, 1)
        #
        # grid.addWidget(self.H_0_Edit, 4, 0)
        # grid.addWidget(H_0_Action, 4, 1)
        #
        # grid.addWidget(self.H_1_Edit, 5, 0)
        # grid.addWidget(H_1_Action, 5, 1)

        # grid.addWidget(self.threshold, 6, 0)
        # grid.addWidget(self.ok_Action, 6, 1)

        grid.addWidget(self.progressBar, 7, 0, 1, 2)
        grid.addWidget(execu, 8, 0)
        grid.addWidget(about, 8, 1)
        self.setLayout(grid)

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(4)

        EWIAction.clicked.connect(self.openImg)
        V_0_Action.clicked.connect(self.openImg)
        Extra.clicked.connect(self.openImg)
        # H_0_Action.clicked.connect(self.openImg)
        # V_1_Action.clicked.connect(self.openImg)
        # H_1_Action.clicked.connect(self.openImg)

        # Action1.clicked.connect(self.on_about)
        # Action2.clicked.connect(self.on_about)
        about.clicked.connect(self.on_about)
        execu.clicked.connect(self.execute)

        self.setGeometry(300, 300, 370, 400)
        # Action1.move(self.width()*0.15, self.height()*0.85)
        # Action2.move(self.width()*0.55, self.height()*0.85)
        # execu.move(self.width()*0.55, self.height()*0.9)
        # about.move(self.width()*0.15, self.height()*0.9)
        self.setFixedSize(self.width(), self.height())

        self.setWindowTitle('Adjacent effect towards inland water')
        self.show()

    def openImg(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', self.fname, "*.tif")
        b = filename.__str__()
        self.fname = b  # .encode("utf-8")
        sender = self.sender()
        t = sender.text()
        if t == 'B2 NIR':  # EWI
            self.EWIEdit.setText(self.fname)
        elif t == 'B4 Green':  # 270
            self.V_0_Edit.setText(self.fname)
        elif t == 'B5/6 SWIR1':
            self.ExtraEdit.setText(self.fname)
        # elif t == '0':
        #     self.H_1_Edit.setText(self.fname)
        # else:
        #     self.H_0_Edit.setText(self.fname)

    def on_about(self):
        msg = "Adjacent effect can influence the reflectance value of inland water, " \
              "it is of great importance to remove such effect before unmixing method being applied.\n" \
              "The process was used for modis 09A1 dataset.\n\n" \
              "If the quality of image is ok, ndwi will be used for calculating," \
              "just band 2 & band 4 is alright (NIR, Green), otherwise," \
              "EWI is better which need extra "
        QtGui.QMessageBox.about(self, "About", msg)

    def execute(self):
        dataFile = {}
        dataFile[0] = self.EWIEdit.text()  # .toUtf8()
        dataFile[1] = self.V_0_Edit.text()  # .toUtf8()
        dataFile[2] = self.ExtraEdit.text()
        # dataFile[180] = self.H_0_Edit.text()  # .toUtf8()
        # dataFile[90] = self.V_1_Edit.text()  # .toUtf8()
        # dataFile[0] = self.H_1_Edit.text()  # .toUtf8()
        valuable = []
        for k, v in dataFile.items():
            if v != '':
                # QtGui.QMessageBox.about(self, "Warning", 'please select all directional fileter images and EWI')
                # return 0
                valuable.append(k)
        if len(valuable) == 2:
            data_nir, sv = obtain_data(dataFile[0])
            data_green, _ = obtain_data(dataFile[1])
            WI = (data_green - data_nir) / (data_green + data_nir)
        else:
            data_nir, sv = obtain_data(dataFile[0])
            data_green, _ = obtain_data(dataFile[1])
            data_swir, _ = obtain_data(dataFile[2])
            WI = (data_green - data_nir - data_swir) / (data_green + data_nir + data_swir)
        WI = np.where(WI > 1, 1, WI)
        WI = np.where(WI < -1, -1, WI)
        temp = dataFile[0][:-4] + '_ndwi.tif'
        sv(WI, temp)
        # remove adjacent effect by proposed method
        main_function(temp)
        # method introduced by ma baodong
        # main_mabaod(temp)
        # os.remove(temp)
        # QtGui.QMessageBox.about(self, "Assert",
        #                         'The processor will be carried on. Please make sure all images properly selected ! ')

        # ewi = dataFile.pop('ewi')
        # out = []  # save temp image resptively
        #
        # while (len(dataFile)):
        #     dir, file = dataFile.popitem()
        #     print(dir, file)
        #     texture = tex(file, ewi, dir)
        #     out.append(texture.out)
        #     self.timeBar(4 - len(dataFile))
        # self.pP.finalImage(out)
        # self.ok_Action.clicked.connect(self.on_threshold)

    # def on_threshold(self):
    #     tsh = self.threshold.text()
    #     try:
    #         tsh = float(tsh)
    #     except:
    #         QtGui.QMessageBox.about(self, "waring", 'Please input a float number ! ')
    #         return 0
    #     print(tsh)
    #     self.pP.thres(tsh)

    def timeBar(self, step):
        self.progressBar.setValue(step)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = MyWindow()
    sys.exit(app.exec_())
