# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login_form.ui'
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
                               QLabel, QLineEdit, QPushButton, QScrollArea,
                               QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)


class Ui_LoginForm(object):
    def setupUi(self, LoginForm):
        if not LoginForm.objectName():
            LoginForm.setObjectName(u"LoginForm")
        LoginForm.resize(1215, 724)
        self.gridLayout = QGridLayout(LoginForm)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.header_line = QFrame(LoginForm)
        self.header_line.setObjectName(u"header_line")
        self.header_line.setFrameShape(QFrame.Shape.HLine)
        self.header_line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.header_line, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.Welcome_label = QLabel(LoginForm)
        self.Welcome_label.setObjectName(u"Welcome_label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.Welcome_label.sizePolicy().hasHeightForWidth())
        self.Welcome_label.setSizePolicy(sizePolicy)
        self.Welcome_label.setMinimumSize(QSize(600, 0))
        font = QFont()
        font.setFamilies([u"MS Shell Dlg 2"])
        font.setPointSize(24)
        font.setBold(False)
        font.setItalic(False)
        font.setKerning(False)
        self.Welcome_label.setFont(font)
        self.Welcome_label.setMouseTracking(False)
        # if QT_CONFIG(whatsthis)
        self.Welcome_label.setWhatsThis(u"")
        # endif // QT_CONFIG(whatsthis)
        # if QT_CONFIG(accessibility)
        self.Welcome_label.setAccessibleName(u"")
        # endif // QT_CONFIG(accessibility)
        # if QT_CONFIG(accessibility)
        self.Welcome_label.setAccessibleDescription(u"")
        # endif // QT_CONFIG(accessibility)
        self.Welcome_label.setStyleSheet(u"")
        self.Welcome_label.setLineWidth(0)
        self.Welcome_label.setTextFormat(Qt.PlainText)
        self.Welcome_label.setScaledContents(True)
        self.Welcome_label.setAlignment(Qt.AlignCenter)
        self.Welcome_label.setIndent(0)
        self.Welcome_label.setTextInteractionFlags(Qt.NoTextInteraction)

        self.horizontalLayout.addWidget(self.Welcome_label)

        self.right_frame = QFrame(LoginForm)
        self.right_frame.setObjectName(u"right_frame")
        self.right_frame.setStyleSheet(u"")
        self.right_frame.setFrameShape(QFrame.StyledPanel)
        self.right_frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.right_frame)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.outside_verticalSpacer_1 = QSpacerItem(20, 150, QSizePolicy.Policy.Minimum,
                                                    QSizePolicy.Policy.MinimumExpanding)

        self.gridLayout_2.addItem(self.outside_verticalSpacer_1, 0, 1, 1, 1)

        self.login_frame = QFrame(self.right_frame)
        self.login_frame.setObjectName(u"login_frame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.login_frame.sizePolicy().hasHeightForWidth())
        self.login_frame.setSizePolicy(sizePolicy1)
        self.login_frame.setStyleSheet(u"")
        self.login_frame.setFrameShape(QFrame.NoFrame)
        self.login_frame.setFrameShadow(QFrame.Plain)
        self.verticalLayout_2 = QVBoxLayout(self.login_frame)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(9, 9, 9, 9)
        self.inside_verticalSpacer_5 = QSpacerItem(20, 17, QSizePolicy.Policy.Minimum,
                                                   QSizePolicy.Policy.MinimumExpanding)

        self.verticalLayout_2.addItem(self.inside_verticalSpacer_5)

        self.label_2 = QLabel(self.login_frame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setStyleSheet(u"font: 10pt \"MS Shell Dlg 2\";")

        self.verticalLayout_2.addWidget(self.label_2)

        self.label = QLabel(self.login_frame)
        self.label.setObjectName(u"label")
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(24)
        font1.setBold(True)
        font1.setItalic(False)
        self.label.setFont(font1)
        self.label.setStyleSheet(u"")
        self.label.setLineWidth(0)
        self.label.setMargin(2)

        self.verticalLayout_2.addWidget(self.label)

        self.inside_verticalSpacer_1 = QSpacerItem(20, 35, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_2.addItem(self.inside_verticalSpacer_1)

        self.scrollArea = QScrollArea(self.login_frame)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Plain)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 133, 93))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.username_label = QLabel(self.scrollAreaWidgetContents)
        self.username_label.setObjectName(u"username_label")
        font2 = QFont()
        font2.setFamilies([u"Arial"])
        font2.setPointSize(11)
        font2.setBold(True)
        self.username_label.setFont(font2)
        self.username_label.setStyleSheet(u"")
        self.username_label.setFrameShadow(QFrame.Plain)
        self.username_label.setMargin(1)

        self.verticalLayout.addWidget(self.username_label)

        self.username_lineEdit = QLineEdit(self.scrollAreaWidgetContents)
        self.username_lineEdit.setObjectName(u"username_lineEdit")
        self.username_lineEdit.setStyleSheet(u"")

        self.verticalLayout.addWidget(self.username_lineEdit)

        self.inside_verticalSpacer_2 = QSpacerItem(16, 13, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout.addItem(self.inside_verticalSpacer_2)

        self.password_label = QLabel(self.scrollAreaWidgetContents)
        self.password_label.setObjectName(u"password_label")
        font3 = QFont()
        font3.setPointSize(11)
        font3.setBold(True)
        self.password_label.setFont(font3)
        self.password_label.setStyleSheet(u"")
        self.password_label.setMargin(1)

        self.verticalLayout.addWidget(self.password_label)

        self.password_lineEdit = QLineEdit(self.scrollAreaWidgetContents)
        self.password_lineEdit.setObjectName(u"password_lineEdit")
        self.password_lineEdit.setStyleSheet(u"")
        self.password_lineEdit.setEchoMode(QLineEdit.Password)

        self.verticalLayout.addWidget(self.password_lineEdit)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.inside_verticalSpacer_3 = QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_2.addItem(self.inside_verticalSpacer_3)

        self.login_pushButton = QPushButton(self.login_frame)
        self.login_pushButton.setObjectName(u"login_pushButton")
        self.login_pushButton.setStyleSheet(u"")

        self.verticalLayout_2.addWidget(self.login_pushButton)

        self.inside_verticalSpacer_4 = QSpacerItem(13, 16, QSizePolicy.Policy.Minimum,
                                                   QSizePolicy.Policy.MinimumExpanding)

        self.verticalLayout_2.addItem(self.inside_verticalSpacer_4)

        self.gridLayout_2.addWidget(self.login_frame, 1, 1, 1, 1)

        self.outside_horizontalSpacer_1 = QSpacerItem(150, 20, QSizePolicy.Policy.MinimumExpanding,
                                                      QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.outside_horizontalSpacer_1, 1, 0, 1, 1)

        self.outside_horizontalSpacer_2 = QSpacerItem(150, 20, QSizePolicy.Policy.MinimumExpanding,
                                                      QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.outside_horizontalSpacer_2, 1, 2, 1, 1)

        self.outside_verticalSpacer_2 = QSpacerItem(20, 150, QSizePolicy.Policy.Minimum,
                                                    QSizePolicy.Policy.MinimumExpanding)

        self.gridLayout_2.addItem(self.outside_verticalSpacer_2, 2, 1, 1, 1)

        self.horizontalLayout.addWidget(self.right_frame)

        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(LoginForm)

        QMetaObject.connectSlotsByName(LoginForm)

    # setupUi

    def retranslateUi(self, LoginForm):
        LoginForm.setWindowTitle(QCoreApplication.translate("LoginForm", u"Philmcgi Pipeline 2.0", None))
        self.Welcome_label.setText("")
        self.label_2.setText(QCoreApplication.translate("LoginForm", u"Ready To Start ?", None))
        self.label.setText(QCoreApplication.translate("LoginForm", u"Login", None))
        self.username_label.setText(QCoreApplication.translate("LoginForm", u"Username", None))
        self.username_lineEdit.setPlaceholderText(
            QCoreApplication.translate("LoginForm", u"username@philmcgi.com", None))
        self.password_label.setText(QCoreApplication.translate("LoginForm", u"Password", None))
        self.password_lineEdit.setPlaceholderText(
            QCoreApplication.translate("LoginForm", u"\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022",
                                       None))
        self.login_pushButton.setText(QCoreApplication.translate("LoginForm", u"Login", None))
    # retranslateUi
