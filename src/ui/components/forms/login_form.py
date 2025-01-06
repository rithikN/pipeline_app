# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login_form.ui'
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

class Ui_LoginForm(object):
    def setupUi(self, LoginForm):
        if not LoginForm.objectName():
            LoginForm.setObjectName(u"LoginForm")
        LoginForm.resize(1196, 657)
        self.gridLayout = QGridLayout(LoginForm)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.logo_label = QLabel(LoginForm)
        self.logo_label.setObjectName(u"logo_label")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.logo_label.sizePolicy().hasHeightForWidth())
        self.logo_label.setSizePolicy(sizePolicy)
        self.logo_label.setMinimumSize(QSize(600, 0))
        font = QFont()
        font.setFamilies([u"MS Shell Dlg 2"])
        font.setPointSize(24)
        font.setBold(False)
        font.setItalic(False)
        font.setKerning(False)
        self.logo_label.setFont(font)
        self.logo_label.setMouseTracking(False)
#if QT_CONFIG(whatsthis)
        self.logo_label.setWhatsThis(u"")
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(accessibility)
        self.logo_label.setAccessibleName(u"")
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.logo_label.setAccessibleDescription(u"")
#endif // QT_CONFIG(accessibility)
        self.logo_label.setStyleSheet(u"")
        self.logo_label.setLineWidth(0)
        self.logo_label.setTextFormat(Qt.PlainText)
        self.logo_label.setScaledContents(True)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setIndent(0)
        self.logo_label.setTextInteractionFlags(Qt.NoTextInteraction)

        self.horizontalLayout.addWidget(self.logo_label)

        self.right_frame = QFrame(LoginForm)
        self.right_frame.setObjectName(u"right_frame")
        self.right_frame.setStyleSheet(u"")
        self.right_frame.setFrameShape(QFrame.NoFrame)
        self.right_frame.setFrameShadow(QFrame.Plain)
        self.gridLayout_2 = QGridLayout(self.right_frame)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(130, 130, 130, 130)
        self.scrollArea = QScrollArea(self.right_frame)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy1)
        self.scrollArea.setMinimumSize(QSize(0, 0))
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Plain)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 334, 254))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_2.addWidget(self.scrollArea, 2, 0, 1, 1)

        self.ready_textlabel = QLabel(self.right_frame)
        self.ready_textlabel.setObjectName(u"ready_textlabel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.ready_textlabel.sizePolicy().hasHeightForWidth())
        self.ready_textlabel.setSizePolicy(sizePolicy2)
        self.ready_textlabel.setMinimumSize(QSize(0, 25))
        self.ready_textlabel.setMaximumSize(QSize(16777215, 25))
        font1 = QFont()
        font1.setPointSize(14)
        self.ready_textlabel.setFont(font1)
        self.ready_textlabel.setStyleSheet(u"")

        self.gridLayout_2.addWidget(self.ready_textlabel, 0, 0, 1, 1)

        self.login_text_label = QLabel(self.right_frame)
        self.login_text_label.setObjectName(u"login_text_label")
        sizePolicy2.setHeightForWidth(self.login_text_label.sizePolicy().hasHeightForWidth())
        self.login_text_label.setSizePolicy(sizePolicy2)
        self.login_text_label.setMinimumSize(QSize(0, 50))
        self.login_text_label.setMaximumSize(QSize(16777215, 50))
        font2 = QFont()
        font2.setFamilies([u"Arial"])
        font2.setPointSize(30)
        font2.setBold(True)
        font2.setItalic(False)
        self.login_text_label.setFont(font2)
        self.login_text_label.setStyleSheet(u"")
        self.login_text_label.setLineWidth(0)
        self.login_text_label.setMargin(2)

        self.gridLayout_2.addWidget(self.login_text_label, 1, 0, 1, 1)

        self.login_pushButton = QPushButton(self.right_frame)
        self.login_pushButton.setObjectName(u"login_pushButton")
        sizePolicy2.setHeightForWidth(self.login_pushButton.sizePolicy().hasHeightForWidth())
        self.login_pushButton.setSizePolicy(sizePolicy2)
        self.login_pushButton.setMinimumSize(QSize(0, 45))
        font3 = QFont()
        font3.setPointSize(20)
        self.login_pushButton.setFont(font3)
        self.login_pushButton.setStyleSheet(u"")

        self.gridLayout_2.addWidget(self.login_pushButton, 3, 0, 1, 1)


        self.horizontalLayout.addWidget(self.right_frame)


        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.header_line = QFrame(LoginForm)
        self.header_line.setObjectName(u"header_line")
        self.header_line.setFrameShape(QFrame.HLine)
        self.header_line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.header_line, 0, 0, 1, 1)


        self.retranslateUi(LoginForm)

        QMetaObject.connectSlotsByName(LoginForm)
    # setupUi

    def retranslateUi(self, LoginForm):
        LoginForm.setWindowTitle(QCoreApplication.translate("LoginForm", u"Philmcgi Pipeline 2.0", None))
        self.logo_label.setText("")
        self.ready_textlabel.setText(QCoreApplication.translate("LoginForm", u"Ready To Start ?", None))
        self.login_text_label.setText(QCoreApplication.translate("LoginForm", u"Login", None))
        self.login_pushButton.setText(QCoreApplication.translate("LoginForm", u"Login", None))
    # retranslateUi

