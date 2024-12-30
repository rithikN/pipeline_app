# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'task_mancer_form.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QSizePolicy,
                               QTabWidget, QWidget)


class Ui_TaskMancer_Form(object):
    def setupUi(self, TaskMancer_Form):
        if not TaskMancer_Form.objectName():
            TaskMancer_Form.setObjectName(u"TaskMancer_Form")
        TaskMancer_Form.resize(388, 288)
        self.gridLayout = QGridLayout(TaskMancer_Form)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.header_line = QFrame(TaskMancer_Form)
        self.header_line.setObjectName(u"header_line")
        self.header_line.setMinimumSize(QSize(0, 1))
        self.header_line.setMaximumSize(QSize(16777215, 1))
        self.header_line.setFrameShadow(QFrame.Plain)
        self.header_line.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout.addWidget(self.header_line, 0, 0, 1, 1)

        self.tab_frame = QFrame(TaskMancer_Form)
        self.tab_frame.setObjectName(u"tab_frame")
        self.tab_frame.setFrameShape(QFrame.StyledPanel)
        self.tab_frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.tab_frame)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.TaskMancer_tabWidget = QTabWidget(self.tab_frame)
        self.TaskMancer_tabWidget.setObjectName(u"TaskMancer_tabWidget")

        self.gridLayout_2.addWidget(self.TaskMancer_tabWidget, 0, 0, 1, 1)

        self.gridLayout.addWidget(self.tab_frame, 1, 0, 1, 1)

        self.retranslateUi(TaskMancer_Form)

        self.TaskMancer_tabWidget.setCurrentIndex(-1)

        QMetaObject.connectSlotsByName(TaskMancer_Form)

    # setupUi

    def retranslateUi(self, TaskMancer_Form):
        TaskMancer_Form.setWindowTitle(QCoreApplication.translate("TaskMancer_Form", u"Form", None))
    # retranslateUi
