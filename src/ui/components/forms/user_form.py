# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'user_form.ui'
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
                               QLabel, QPushButton, QScrollArea, QSizePolicy,
                               QSpacerItem, QVBoxLayout, QWidget)


class Ui_UserForm(object):
    def setupUi(self, UserForm):
        if not UserForm.objectName():
            UserForm.setObjectName(u"UserForm")
        UserForm.resize(1364, 778)
        self.verticalLayout = QVBoxLayout(UserForm)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.header_line = QFrame(UserForm)
        self.header_line.setObjectName(u"header_line")
        self.header_line.setFrameShape(QFrame.Shape.HLine)
        self.header_line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.header_line)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.Welcome_label = QLabel(UserForm)
        self.Welcome_label.setObjectName(u"Welcome_label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.Welcome_label.sizePolicy().hasHeightForWidth())
        self.Welcome_label.setSizePolicy(sizePolicy)
        self.Welcome_label.setMinimumSize(QSize(600, 0))
        self.Welcome_label.setPixmap(QPixmap(u"../../../../../../../../resources/logo.png"))
        self.Welcome_label.setScaledContents(True)
        self.Welcome_label.setAlignment(Qt.AlignCenter)
        self.Welcome_label.setIndent(0)

        self.horizontalLayout.addWidget(self.Welcome_label)

        self.right_frame = QFrame(UserForm)
        self.right_frame.setObjectName(u"right_frame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.right_frame.sizePolicy().hasHeightForWidth())
        self.right_frame.setSizePolicy(sizePolicy1)
        self.right_frame.setStyleSheet(u"")
        self.right_frame.setFrameShape(QFrame.StyledPanel)
        self.right_frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.right_frame)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalSpacer = QSpacerItem(20, 150, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 0, 1, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(150, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_3, 1, 0, 1, 1)

        self.main_frame = QFrame(self.right_frame)
        self.main_frame.setObjectName(u"main_frame")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.main_frame.sizePolicy().hasHeightForWidth())
        self.main_frame.setSizePolicy(sizePolicy2)
        self.main_frame.setMinimumSize(QSize(0, 0))
        self.main_frame.setStyleSheet(u"")
        self.main_frame.setFrameShape(QFrame.NoFrame)
        self.main_frame.setFrameShadow(QFrame.Plain)
        self.gridLayout = QGridLayout(self.main_frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.form_scrollArea = QScrollArea(self.main_frame)
        self.form_scrollArea.setObjectName(u"form_scrollArea")
        self.form_scrollArea.setFrameShape(QFrame.NoFrame)
        self.form_scrollArea.setFrameShadow(QFrame.Plain)
        self.form_scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 158, 89))
        self.form_scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.form_scrollArea, 4, 0, 1, 1)

        self.inside_verticalSpacer_5 = QSpacerItem(20, 17, QSizePolicy.Policy.Minimum,
                                                   QSizePolicy.Policy.MinimumExpanding)

        self.gridLayout.addItem(self.inside_verticalSpacer_5, 0, 0, 1, 1)

        self.inside_verticalSpacer_3 = QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.gridLayout.addItem(self.inside_verticalSpacer_3, 5, 0, 1, 1)

        self.inside_verticalSpacer_1 = QSpacerItem(20, 35, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.gridLayout.addItem(self.inside_verticalSpacer_1, 3, 0, 1, 1)

        self.user_label = QLabel(self.main_frame)
        self.user_label.setObjectName(u"user_label")
        self.user_label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.gridLayout.addWidget(self.user_label, 2, 0, 1, 1)

        self.welcome_label = QLabel(self.main_frame)
        self.welcome_label.setObjectName(u"welcome_label")

        self.gridLayout.addWidget(self.welcome_label, 1, 0, 1, 1)

        self.button_Layout = QHBoxLayout()
        self.button_Layout.setObjectName(u"button_Layout")
        self.previous_button = QPushButton(self.main_frame)
        self.previous_button.setObjectName(u"previous_button")

        self.button_Layout.addWidget(self.previous_button)

        self.next_button = QPushButton(self.main_frame)
        self.next_button.setObjectName(u"next_button")
        sizePolicy1.setHeightForWidth(self.next_button.sizePolicy().hasHeightForWidth())
        self.next_button.setSizePolicy(sizePolicy1)
        self.next_button.setStyleSheet(u"")

        self.button_Layout.addWidget(self.next_button)

        self.gridLayout.addLayout(self.button_Layout, 6, 0, 1, 1)

        self.inside_verticalSpacer_4 = QSpacerItem(20, 14, QSizePolicy.Policy.Minimum,
                                                   QSizePolicy.Policy.MinimumExpanding)

        self.gridLayout.addItem(self.inside_verticalSpacer_4, 7, 0, 1, 1)

        self.gridLayout_2.addWidget(self.main_frame, 1, 1, 1, 2)

        self.horizontalSpacer_4 = QSpacerItem(150, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_4, 1, 3, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 150, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)

        self.gridLayout_2.addItem(self.verticalSpacer_2, 2, 2, 1, 1)

        self.horizontalLayout.addWidget(self.right_frame)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(UserForm)

        QMetaObject.connectSlotsByName(UserForm)

    # setupUi

    def retranslateUi(self, UserForm):
        UserForm.setWindowTitle(QCoreApplication.translate("UserForm", u"Philmcgi Pipeline 2.0", None))
        self.Welcome_label.setStyleSheet(
            QCoreApplication.translate("UserForm", u"font: 75 24pt \"MS Shell Dlg 2\";", None))
        self.Welcome_label.setText("")
        self.user_label.setText(QCoreApplication.translate("UserForm", u"TextLabel", None))
        self.welcome_label.setText(QCoreApplication.translate("UserForm", u"Welcome Back!", None))
        self.previous_button.setText(QCoreApplication.translate("UserForm", u"Back", None))
        self.next_button.setText(QCoreApplication.translate("UserForm", u"Next", None))
    # retranslateUi
