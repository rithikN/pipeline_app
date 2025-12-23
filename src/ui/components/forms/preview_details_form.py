# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preview_details_form.ui'
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

class Ui_PreviewDetailsForm(object):
    def setupUi(self, PreviewDetailsForm):
        if not PreviewDetailsForm.objectName():
            PreviewDetailsForm.setObjectName(u"PreviewDetailsForm")
        PreviewDetailsForm.resize(435, 438)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PreviewDetailsForm.sizePolicy().hasHeightForWidth())
        PreviewDetailsForm.setSizePolicy(sizePolicy)
        PreviewDetailsForm.setMinimumSize(QSize(410, 225))
        self.verticalLayout_3 = QVBoxLayout(PreviewDetailsForm)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.MainContainer = QFrame(PreviewDetailsForm)
        self.MainContainer.setObjectName(u"MainContainer")
        self.MainContainer.setFrameShape(QFrame.Shape.NoFrame)
        self.MainContainer.setFrameShadow(QFrame.Shadow.Plain)
        self.MainContainer.setLineWidth(0)
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
        self.header_line.setFrameShadow(QFrame.Shadow.Plain)
        self.header_line.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayout_2.addWidget(self.header_line)

        self.main_frame = QFrame(self.MainContainer)
        self.main_frame.setObjectName(u"main_frame")
        self.main_horizontalLayout = QVBoxLayout(self.main_frame)
        self.main_horizontalLayout.setObjectName(u"main_horizontalLayout")
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
        self.preview_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.preview_frame.setFrameShadow(QFrame.Shadow.Plain)
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
        self.details_textEdit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.details_textEdit.setFrameShape(QFrame.Shape.NoFrame)
        self.details_textEdit.setFrameShadow(QFrame.Shadow.Plain)
        self.details_textEdit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.details_textEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.details_textEdit.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.details_textEdit.setUndoRedoEnabled(False)
        self.details_textEdit.setLineWrapColumnOrWidth(0)
        self.details_textEdit.setReadOnly(True)

        self.horizontalLayout.addWidget(self.details_textEdit)


        self.main_horizontalLayout.addLayout(self.horizontalLayout)

        self.button_horizontalLayout = QHBoxLayout()
        self.button_horizontalLayout.setSpacing(6)
        self.button_horizontalLayout.setObjectName(u"button_horizontalLayout")
        self.horizontalSpacer = QSpacerItem(350, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.button_horizontalLayout.addItem(self.horizontalSpacer)

        self.open_button = QPushButton(self.main_frame)
        self.open_button.setObjectName(u"open_button")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.open_button.sizePolicy().hasHeightForWidth())
        self.open_button.setSizePolicy(sizePolicy4)
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(False)
        self.open_button.setFont(font1)
        self.open_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.open_button.setStyleSheet(u"background-color: #7da7d9; color: #0b1936;\n"
"                                                            padding: 5px;\n"
"                                                        ")

        self.button_horizontalLayout.addWidget(self.open_button)

        self.explorer_button = QPushButton(self.main_frame)
        self.explorer_button.setObjectName(u"explorer_button")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.explorer_button.sizePolicy().hasHeightForWidth())
        self.explorer_button.setSizePolicy(sizePolicy5)
        self.explorer_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.explorer_button.setStyleSheet(u"background-color: #c7b299; color: #503514;\n"
"                                                            padding: 5px;\n"
"                                                        ")

        self.button_horizontalLayout.addWidget(self.explorer_button)

        self.upload_preview_button = QPushButton(self.main_frame)
        self.upload_preview_button.setObjectName(u"upload_preview_button")
        sizePolicy2.setHeightForWidth(self.upload_preview_button.sizePolicy().hasHeightForWidth())
        self.upload_preview_button.setSizePolicy(sizePolicy2)
        self.upload_preview_button.setFont(font1)
        self.upload_preview_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.upload_preview_button.setStyleSheet(u"background-color: #a3d39c; color: #173a12;\n"
"                                                            padding: 5px;\n"
"                                                        ")

        self.button_horizontalLayout.addWidget(self.upload_preview_button)


        self.main_horizontalLayout.addLayout(self.button_horizontalLayout)


        self.verticalLayout_2.addWidget(self.main_frame)


        self.verticalLayout_3.addWidget(self.MainContainer)


        self.retranslateUi(PreviewDetailsForm)

        QMetaObject.connectSlotsByName(PreviewDetailsForm)
    # setupUi

    def retranslateUi(self, PreviewDetailsForm):
        PreviewDetailsForm.setWindowTitle(QCoreApplication.translate("PreviewDetailsForm", u"Work Files Details", None))
        self.header_label.setText(QCoreApplication.translate("PreviewDetailsForm", u"Placeholder", None))
#if QT_CONFIG(accessibility)
        self.details_textEdit.setAccessibleName(QCoreApplication.translate("PreviewDetailsForm", u"v", None))
#endif // QT_CONFIG(accessibility)
        self.open_button.setText(QCoreApplication.translate("PreviewDetailsForm", u"Open File", None))
        self.explorer_button.setText("")
        self.upload_preview_button.setText(QCoreApplication.translate("PreviewDetailsForm", u"Send for Review", None))
    # retranslateUi

