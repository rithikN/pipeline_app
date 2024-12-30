# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'details_form.ui'
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QFrame, QHBoxLayout,
                               QLabel, QPushButton, QSizePolicy, QSpacerItem,
                               QTextEdit, QVBoxLayout, QWidget)


class Ui_DetailsForm(object):
    def setupUi(self, DetailsForm):
        if not DetailsForm.objectName():
            DetailsForm.setObjectName(u"DetailsForm")
        DetailsForm.resize(535, 438)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DetailsForm.sizePolicy().hasHeightForWidth())
        DetailsForm.setSizePolicy(sizePolicy)
        DetailsForm.setMinimumSize(QSize(510, 225))
        self.verticalLayout_3 = QVBoxLayout(DetailsForm)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.MainContainer = QFrame(DetailsForm)
        self.MainContainer.setObjectName(u"MainContainer")
        self.MainContainer.setFrameShape(QFrame.Box)
        self.MainContainer.setFrameShadow(QFrame.Plain)
        self.verticalLayout_2 = QVBoxLayout(self.MainContainer)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, -1, -1, 6)
        self.header_label = QLabel(self.MainContainer)
        self.header_label.setObjectName(u"header_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.header_label.sizePolicy().hasHeightForWidth())
        self.header_label.setSizePolicy(sizePolicy1)
        self.header_label.setMinimumSize(QSize(0, 26))
        self.header_label.setMaximumSize(QSize(16777215, 26))

        self.verticalLayout_2.addWidget(self.header_label)

        self.header_line = QFrame(self.MainContainer)
        self.header_line.setObjectName(u"header_line")
        self.header_line.setMinimumSize(QSize(0, 1))
        self.header_line.setMaximumSize(QSize(16777215, 1))
        self.header_line.setFrameShadow(QFrame.Plain)
        self.header_line.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayout_2.addWidget(self.header_line)

        self.main_frame = QFrame(self.MainContainer)
        self.main_frame.setObjectName(u"main_frame")
        self.main_frame.setFrameShape(QFrame.NoFrame)
        self.main_frame.setFrameShadow(QFrame.Plain)
        self.main_horizontalLayout = QVBoxLayout(self.main_frame)
        self.main_horizontalLayout.setSpacing(0)
        self.main_horizontalLayout.setObjectName(u"main_horizontalLayout")
        self.main_horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.preview_frame = QFrame(self.main_frame)
        self.preview_frame.setObjectName(u"preview_frame")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.preview_frame.sizePolicy().hasHeightForWidth())
        self.preview_frame.setSizePolicy(sizePolicy2)
        self.preview_frame.setMinimumSize(QSize(238, 0))
        self.preview_frame.setFrameShape(QFrame.NoFrame)
        self.preview_frame.setFrameShadow(QFrame.Plain)
        self.preview_frame.setLineWidth(0)

        self.horizontalLayout.addWidget(self.preview_frame)

        self.details_textEdit = QTextEdit(self.main_frame)
        self.details_textEdit.setObjectName(u"details_textEdit")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.details_textEdit.sizePolicy().hasHeightForWidth())
        self.details_textEdit.setSizePolicy(sizePolicy3)
        font = QFont()
        font.setPointSize(8)
        self.details_textEdit.setFont(font)
        self.details_textEdit.setMouseTracking(False)
        self.details_textEdit.setFocusPolicy(Qt.NoFocus)
        self.details_textEdit.setFrameShape(QFrame.NoFrame)
        self.details_textEdit.setFrameShadow(QFrame.Plain)
        self.details_textEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.details_textEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.details_textEdit.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.details_textEdit.setUndoRedoEnabled(False)
        self.details_textEdit.setLineWrapColumnOrWidth(0)
        self.details_textEdit.setReadOnly(True)

        self.horizontalLayout.addWidget(self.details_textEdit)

        self.main_horizontalLayout.addLayout(self.horizontalLayout)

        self.button_horizontalLayout = QHBoxLayout()
        self.button_horizontalLayout.setSpacing(8)
        self.button_horizontalLayout.setObjectName(u"button_horizontalLayout")
        self.horizontalSpacer = QSpacerItem(200, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.button_horizontalLayout.addItem(self.horizontalSpacer)

        self.delete_button = QPushButton(self.main_frame)
        self.delete_button.setObjectName(u"delete_button")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.delete_button.sizePolicy().hasHeightForWidth())
        self.delete_button.setSizePolicy(sizePolicy4)
        self.delete_button.setStyleSheet(u"background-color: #7B0A15; color: #E1E1E8; padding: 5px;")

        self.button_horizontalLayout.addWidget(self.delete_button)

        self.explorer_button = QPushButton(self.main_frame)
        self.explorer_button.setObjectName(u"explorer_button")
        sizePolicy4.setHeightForWidth(self.explorer_button.sizePolicy().hasHeightForWidth())
        self.explorer_button.setSizePolicy(sizePolicy4)
        self.explorer_button.setStyleSheet(u"background-color: #9C521B; color: #E1E1E8; padding: 5px;")

        self.button_horizontalLayout.addWidget(self.explorer_button)

        self.open_button = QPushButton(self.main_frame)
        self.open_button.setObjectName(u"open_button")
        sizePolicy4.setHeightForWidth(self.open_button.sizePolicy().hasHeightForWidth())
        self.open_button.setSizePolicy(sizePolicy4)
        self.open_button.setStyleSheet(u"background-color: #216582; color: #E1E1E8; padding: 5px;")

        self.button_horizontalLayout.addWidget(self.open_button)

        self.main_horizontalLayout.addLayout(self.button_horizontalLayout)

        self.verticalLayout_2.addWidget(self.main_frame)

        self.verticalLayout_3.addWidget(self.MainContainer)

        self.retranslateUi(DetailsForm)

        QMetaObject.connectSlotsByName(DetailsForm)

    # setupUi

    def retranslateUi(self, DetailsForm):
        DetailsForm.setWindowTitle(QCoreApplication.translate("DetailsForm", u"Work Files Details", None))
        self.header_label.setText(QCoreApplication.translate("DetailsForm", u"Placeholder", None))
        # if QT_CONFIG(accessibility)
        self.details_textEdit.setAccessibleName(QCoreApplication.translate("DetailsForm", u"v  ", None))
        # endif // QT_CONFIG(accessibility)
        self.delete_button.setText(QCoreApplication.translate("DetailsForm", u"Delete", None))
        self.explorer_button.setText(QCoreApplication.translate("DetailsForm", u"Explorer", None))
        self.open_button.setText(QCoreApplication.translate("DetailsForm", u"Open", None))
    # retranslateUi
