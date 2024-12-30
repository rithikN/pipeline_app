# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'work_files_form.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QListWidget,
                               QListWidgetItem, QSizePolicy, QVBoxLayout, QWidget)


class Ui_WorkFilesForm(object):
    def setupUi(self, WorkFilesForm):
        if not WorkFilesForm.objectName():
            WorkFilesForm.setObjectName(u"WorkFilesForm")
        WorkFilesForm.resize(112, 300)
        self.verticalLayout_2 = QVBoxLayout(WorkFilesForm)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.MainContainer = QFrame(WorkFilesForm)
        self.MainContainer.setObjectName(u"MainContainer")
        self.MainContainer.setFrameShape(QFrame.NoFrame)
        self.MainContainer.setFrameShadow(QFrame.Plain)
        self.verticalLayout = QVBoxLayout(self.MainContainer)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.sort_comboBox = QComboBox(self.MainContainer)
        self.sort_comboBox.setObjectName(u"sort_comboBox")

        self.verticalLayout.addWidget(self.sort_comboBox)

        self.header_line = QFrame(self.MainContainer)
        self.header_line.setObjectName(u"header_line")
        self.header_line.setMinimumSize(QSize(0, 1))
        self.header_line.setMaximumSize(QSize(16777215, 1))
        self.header_line.setFrameShape(QFrame.Shape.HLine)
        self.header_line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.header_line)

        self.workFiles_listWidget = QListWidget(self.MainContainer)
        self.workFiles_listWidget.setObjectName(u"workFiles_listWidget")

        self.verticalLayout.addWidget(self.workFiles_listWidget)

        self.verticalLayout_2.addWidget(self.MainContainer)

        self.retranslateUi(WorkFilesForm)

        QMetaObject.connectSlotsByName(WorkFilesForm)

    # setupUi

    def retranslateUi(self, WorkFilesForm):
        WorkFilesForm.setWindowTitle(QCoreApplication.translate("WorkFilesForm", u"Form", None))
    # retranslateUi
