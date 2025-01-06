# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'selection_form.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QSizePolicy,
                               QSpacerItem, QWidget)

from ui.components.extensions.multi_select_combobox import MultiSelectComboBox


class Ui_SelectionForm(object):
    def setupUi(self, SelectionForm):
        if not SelectionForm.objectName():
            SelectionForm.setObjectName(u"SelectionForm")
        SelectionForm.resize(1055, 43)
        self.horizontalLayout = QHBoxLayout(SelectionForm)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.shot_comboBox = QComboBox(SelectionForm)
        self.shot_comboBox.addItem("")
        self.shot_comboBox.setObjectName(u"shot_comboBox")
        self.shot_comboBox.setMinimumSize(QSize(140, 0))

        self.horizontalLayout.addWidget(self.shot_comboBox)

        self.episode_comboBox = MultiSelectComboBox('Episode', SelectionForm)
        self.episode_comboBox.addItem("")
        self.episode_comboBox.setObjectName(u"episode_comboBox")
        self.episode_comboBox.setMinimumSize(QSize(140, 0))

        self.horizontalLayout.addWidget(self.episode_comboBox)

        self.scene_comboBox = MultiSelectComboBox('Scene', SelectionForm)
        self.scene_comboBox.addItem("")
        self.scene_comboBox.setObjectName(u"scene_comboBox")
        self.scene_comboBox.setMinimumSize(QSize(140, 0))

        self.horizontalLayout.addWidget(self.scene_comboBox)

        self.task_comboBox = MultiSelectComboBox('Select Tasks', SelectionForm)
        self.task_comboBox.addItem("")
        self.task_comboBox.setObjectName(u"task_comboBox")
        self.task_comboBox.setMinimumSize(QSize(140, 0))

        self.horizontalLayout.addWidget(self.task_comboBox)

        self.status_comboBox = MultiSelectComboBox('Task Status', SelectionForm)
        self.status_comboBox.addItem("")
        self.status_comboBox.setObjectName(u"status_comboBox")
        self.status_comboBox.setMinimumSize(QSize(140, 0))

        self.horizontalLayout.addWidget(self.status_comboBox)

        self.horizontalSpacer = QSpacerItem(87, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.retranslateUi(SelectionForm)

        QMetaObject.connectSlotsByName(SelectionForm)

    # setupUi

    def retranslateUi(self, SelectionForm):
        SelectionForm.setWindowTitle(QCoreApplication.translate("SelectionForm", u"Form", None))
        self.shot_comboBox.setItemText(0, QCoreApplication.translate("SelectionForm", u"Shot", None))

        self.episode_comboBox.setItemText(0, QCoreApplication.translate("SelectionForm", u"Episode", None))

        self.scene_comboBox.setItemText(0, QCoreApplication.translate("SelectionForm", u"Scene", None))

        self.task_comboBox.setItemText(0, QCoreApplication.translate("SelectionForm", u"Select Task", None))

        self.status_comboBox.setItemText(0, QCoreApplication.translate("SelectionForm", u"Task Status", None))

    # retranslateUi
