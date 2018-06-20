# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'image_window.ui'
#
# Created: Wed Aug 10 12:36:19 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#


from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_image_window(object):
    def setupUi(self, image_window):
        image_window.setObjectName("image_window")
        image_window.resize(1280, 768)
        #image_window.setWindowFlags(QtCore.FramelessWindowHint)
        self.image_space = QtWidgets.QGraphicsView(image_window)
        self.image_space.setGeometry(QtCore.QRect(0, 0, 1280, 768))
        self.image_space.setInteractive(False)
        self.image_space.setObjectName("image_space")
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
        image_window.setPalette(palette)
        self.retranslateUi(image_window)
        QtCore.QMetaObject.connectSlotsByName(image_window)

    def retranslateUi(self, image_window):
        image_window.setWindowTitle(QtWidgets.QApplication.translate("image_window", "Image", None))

