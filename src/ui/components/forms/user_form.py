# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'user_form.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QSizePolicy,
    QWidget)

class Ui_UserForm(object):
    def setupUi(self, UserForm):
        if not UserForm.objectName():
            UserForm.setObjectName(u"UserForm")
        UserForm.resize(1034, 706)
        self.gridLayout_2 = QGridLayout(UserForm)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.header_line = QFrame(UserForm)
        self.header_line.setObjectName(u"header_line")
        self.header_line.setFrameShape(QFrame.HLine)
        self.header_line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.header_line, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.logo_label = QLabel(UserForm)
        self.logo_label.setObjectName(u"logo_label")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.logo_label.sizePolicy().hasHeightForWidth())
        self.logo_label.setSizePolicy(sizePolicy)
        self.logo_label.setMinimumSize(QSize(600, 0))
        self.logo_label.setPixmap(QPixmap(u"../../../../../../../../resources/logo.png"))
        self.logo_label.setScaledContents(True)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setIndent(0)

        self.horizontalLayout.addWidget(self.logo_label)

        self.right_frame = QFrame(UserForm)
        self.right_frame.setObjectName(u"right_frame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.right_frame.sizePolicy().hasHeightForWidth())
        self.right_frame.setSizePolicy(sizePolicy1)
        self.right_frame.setStyleSheet(u"")
        self.right_frame.setFrameShape(QFrame.NoFrame)
        self.right_frame.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.right_frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(130, 130, 130, 130)
        self.welcome_test_label = QLabel(self.right_frame)
        self.welcome_test_label.setObjectName(u"welcome_test_label")
        self.welcome_test_label.setMinimumSize(QSize(0, 25))
        self.welcome_test_label.setMaximumSize(QSize(16777215, 25))
        font = QFont()
        font.setPointSize(14)
        self.welcome_test_label.setFont(font)

        self.gridLayout.addWidget(self.welcome_test_label, 0, 0, 1, 1)

        self.user_text_label = QLabel(self.right_frame)
        self.user_text_label.setObjectName(u"user_text_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.user_text_label.sizePolicy().hasHeightForWidth())
        self.user_text_label.setSizePolicy(sizePolicy2)
        self.user_text_label.setMinimumSize(QSize(0, 50))
        self.user_text_label.setMaximumSize(QSize(16777215, 50))
        font1 = QFont()
        font1.setPointSize(30)
        self.user_text_label.setFont(font1)
        self.user_text_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.user_text_label, 1, 0, 1, 1)

        self.scrollArea = QScrollArea(self.right_frame)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Plain)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 172, 301))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 2, 0, 1, 1)

        self.button_Layout = QHBoxLayout()
        self.button_Layout.setSpacing(12)
        self.button_Layout.setObjectName(u"button_Layout")
        self.button_Layout.setContentsMargins(-1, 0, -1, -1)
        self.previous_button = QPushButton(self.right_frame)
        self.previous_button.setObjectName(u"previous_button")
        sizePolicy2.setHeightForWidth(self.previous_button.sizePolicy().hasHeightForWidth())
        self.previous_button.setSizePolicy(sizePolicy2)
        self.previous_button.setMinimumSize(QSize(0, 45))
        font2 = QFont()
        font2.setPointSize(20)
        self.previous_button.setFont(font2)

        self.button_Layout.addWidget(self.previous_button)

        self.next_button = QPushButton(self.right_frame)
        self.next_button.setObjectName(u"next_button")
        sizePolicy2.setHeightForWidth(self.next_button.sizePolicy().hasHeightForWidth())
        self.next_button.setSizePolicy(sizePolicy2)
        self.next_button.setMinimumSize(QSize(0, 45))
        self.next_button.setBaseSize(QSize(0, 0))
        self.next_button.setFont(font2)
        self.next_button.setStyleSheet(u"")

        self.button_Layout.addWidget(self.next_button)


        self.gridLayout.addLayout(self.button_Layout, 3, 0, 1, 1)


        self.horizontalLayout.addWidget(self.right_frame)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)


        self.retranslateUi(UserForm)

        QMetaObject.connectSlotsByName(UserForm)
    # setupUi

    def retranslateUi(self, UserForm):
        UserForm.setWindowTitle(QCoreApplication.translate("UserForm", u"Philmcgi Pipeline 2.0", None))
        self.logo_label.setStyleSheet(QCoreApplication.translate("UserForm", u"font: 75 24pt \"MS Shell Dlg 2\";", None))
        self.logo_label.setText("")
        self.welcome_test_label.setText(QCoreApplication.translate("UserForm", u"Welcome Back!", None))
        self.user_text_label.setText(QCoreApplication.translate("UserForm", u"TextLabel", None))
        self.previous_button.setText(QCoreApplication.translate("UserForm", u"Back", None))
        self.next_button.setText(QCoreApplication.translate("UserForm", u"Next", None))
    # retranslateUi

