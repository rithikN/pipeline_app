# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'project_form.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
                               QHeaderView, QLabel, QPushButton, QSizePolicy,
                               QSpacerItem, QTableWidget, QTableWidgetItem, QWidget)


class Ui_ProjectForm(object):
    def setupUi(self, ProjectForm):
        if not ProjectForm.objectName():
            ProjectForm.setObjectName(u"ProjectForm")
        ProjectForm.resize(645, 487)
        ProjectForm.setAutoFillBackground(False)
        self.gridLayout_3 = QGridLayout(ProjectForm)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.bottom_frame = QFrame(ProjectForm)
        self.bottom_frame.setObjectName(u"bottom_frame")
        self.bottom_frame.setFrameShape(QFrame.StyledPanel)
        self.bottom_frame.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.bottom_frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.previous_pushButton = QPushButton(self.bottom_frame)
        self.previous_pushButton.setObjectName(u"previous_pushButton")

        self.horizontalLayout_2.addWidget(self.previous_pushButton)

        self.next_pushButton = QPushButton(self.bottom_frame)
        self.next_pushButton.setObjectName(u"next_pushButton")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.next_pushButton.sizePolicy().hasHeightForWidth())
        self.next_pushButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.next_pushButton)

        self.gridLayout.addLayout(self.horizontalLayout_2, 3, 0, 1, 1)

        self.project_tableWidget = QTableWidget(self.bottom_frame)
        self.project_tableWidget.setObjectName(u"project_tableWidget")
        self.project_tableWidget.setFrameShape(QFrame.NoFrame)
        self.project_tableWidget.setFrameShadow(QFrame.Plain)
        self.project_tableWidget.setLineWidth(0)
        self.project_tableWidget.setDragDropOverwriteMode(False)
        self.project_tableWidget.setShowGrid(False)
        self.project_tableWidget.setCornerButtonEnabled(False)

        self.gridLayout.addWidget(self.project_tableWidget, 2, 0, 1, 1)

        self.selectProject_label = QLabel(self.bottom_frame)
        self.selectProject_label.setObjectName(u"selectProject_label")
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        font.setBold(True)
        self.selectProject_label.setFont(font)
        self.selectProject_label.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.gridLayout.addWidget(self.selectProject_label, 1, 0, 1, 1)

        self.line = QFrame(self.bottom_frame)
        self.line.setObjectName(u"line")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy1)
        self.line.setMinimumSize(QSize(0, 1))
        self.line.setMaximumSize(QSize(16777215, 1))
        font1 = QFont()
        font1.setPointSize(6)
        font1.setKerning(False)
        self.line.setFont(font1)
        self.line.setStyleSheet(u"color: rgb(255, 255, 255);\n"
                                "background-color: rgb(255, 255, 255);")
        self.line.setFrameShadow(QFrame.Plain)
        self.line.setLineWidth(1)
        self.line.setFrameShape(QFrame.Shape.HLine)

        self.gridLayout.addWidget(self.line, 0, 0, 1, 1)

        self.gridLayout_3.addWidget(self.bottom_frame, 0, 0, 1, 1)

        self.retranslateUi(ProjectForm)

        QMetaObject.connectSlotsByName(ProjectForm)

    # setupUi

    def retranslateUi(self, ProjectForm):
        self.previous_pushButton.setText(QCoreApplication.translate("ProjectForm", u"Previous", None))
        self.next_pushButton.setText(QCoreApplication.translate("ProjectForm", u"Next", None))
        self.selectProject_label.setText(QCoreApplication.translate("ProjectForm", u"Select Project:", None))
        pass
    # retranslateUi
