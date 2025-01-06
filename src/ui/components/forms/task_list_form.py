# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'task_list_form.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
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
from PySide6.QtWidgets import (QApplication, QFrame, QLineEdit, QListView,
    QListWidget, QListWidgetItem, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_TaskListForm(object):
    def setupUi(self, TaskListForm):
        if not TaskListForm.objectName():
            TaskListForm.setObjectName(u"TaskListForm")
        TaskListForm.resize(292, 477)
        TaskListForm.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(TaskListForm)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.MainContainer = QFrame(TaskListForm)
        self.MainContainer.setObjectName(u"MainContainer")
        self.MainContainer.setFrameShape(QFrame.NoFrame)
        self.MainContainer.setFrameShadow(QFrame.Plain)
        self.verticalLayout = QVBoxLayout(self.MainContainer)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.search_lineEdit = QLineEdit(self.MainContainer)
        self.search_lineEdit.setObjectName(u"search_lineEdit")
        self.search_lineEdit.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_lineEdit.sizePolicy().hasHeightForWidth())
        self.search_lineEdit.setSizePolicy(sizePolicy)
        self.search_lineEdit.setMinimumSize(QSize(0, 0))
        self.search_lineEdit.setMaximumSize(QSize(16777215, 25))
        self.search_lineEdit.setFrame(False)
        self.search_lineEdit.setCursorMoveStyle(Qt.LogicalMoveStyle)

        self.verticalLayout.addWidget(self.search_lineEdit)

        self.header_line = QFrame(self.MainContainer)
        self.header_line.setObjectName(u"header_line")
        self.header_line.setMinimumSize(QSize(0, 0))
        self.header_line.setMaximumSize(QSize(16777215, 1))
        self.header_line.setFrameShadow(QFrame.Plain)
        self.header_line.setFrameShape(QFrame.HLine)

        self.verticalLayout.addWidget(self.header_line)

        self.task_listWidget = QListWidget(self.MainContainer)
        self.task_listWidget.setObjectName(u"task_listWidget")
        self.task_listWidget.setFrameShape(QFrame.NoFrame)
        self.task_listWidget.setFrameShadow(QFrame.Plain)
        self.task_listWidget.setSpacing(0)
        self.task_listWidget.setViewMode(QListView.ListMode)

        self.verticalLayout.addWidget(self.task_listWidget)


        self.verticalLayout_2.addWidget(self.MainContainer)


        self.retranslateUi(TaskListForm)

        QMetaObject.connectSlotsByName(TaskListForm)
    # setupUi

    def retranslateUi(self, TaskListForm):
        TaskListForm.setWindowTitle(QCoreApplication.translate("TaskListForm", u"Form", None))
        self.search_lineEdit.setPlaceholderText(QCoreApplication.translate("TaskListForm", u"Search Task...", None))
    # retranslateUi

