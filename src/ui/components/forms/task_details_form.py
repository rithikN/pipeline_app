# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'task_details_form.ui'
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QFrame, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_TaskDetailsForm(object):
    def setupUi(self, TaskDetailsForm):
        if not TaskDetailsForm.objectName():
            TaskDetailsForm.setObjectName(u"TaskDetailsForm")
        TaskDetailsForm.resize(670, 590)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TaskDetailsForm.sizePolicy().hasHeightForWidth())
        TaskDetailsForm.setSizePolicy(sizePolicy)
        TaskDetailsForm.setMinimumSize(QSize(670, 0))
        self.horizontalLayout_2 = QHBoxLayout(TaskDetailsForm)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 9, -1, -1)
        self.MainContainer = QFrame(TaskDetailsForm)
        self.MainContainer.setObjectName(u"MainContainer")
        self.MainContainer.setFrameShape(QFrame.NoFrame)
        self.MainContainer.setFrameShadow(QFrame.Plain)
        self.verticalLayout_2 = QVBoxLayout(self.MainContainer)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(9, 0, 9, 9)
        self.header_label = QLabel(self.MainContainer)
        self.header_label.setObjectName(u"header_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.header_label.sizePolicy().hasHeightForWidth())
        self.header_label.setSizePolicy(sizePolicy1)
        self.header_label.setMinimumSize(QSize(0, 40))
        self.header_label.setMaximumSize(QSize(16777215, 38))

        self.verticalLayout_2.addWidget(self.header_label)

        self.header_line = QFrame(self.MainContainer)
        self.header_line.setObjectName(u"header_line")
        self.header_line.setMinimumSize(QSize(0, 1))
        self.header_line.setMaximumSize(QSize(16777215, 1))
        self.header_line.setFrameShadow(QFrame.Plain)
        self.header_line.setLineWidth(0)
        self.header_line.setFrameShape(QFrame.HLine)

        self.verticalLayout_2.addWidget(self.header_line)

        self.main_frame = QFrame(self.MainContainer)
        self.main_frame.setObjectName(u"main_frame")
        self.main_frame.setFrameShape(QFrame.NoFrame)
        self.main_frame.setFrameShadow(QFrame.Plain)
        self.verticalLayout_3 = QVBoxLayout(self.main_frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.preview_frame = QFrame(self.main_frame)
        self.preview_frame.setObjectName(u"preview_frame")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.preview_frame.sizePolicy().hasHeightForWidth())
        self.preview_frame.setSizePolicy(sizePolicy2)
        self.preview_frame.setMinimumSize(QSize(198, 0))
        self.preview_frame.setFrameShape(QFrame.NoFrame)
        self.preview_frame.setFrameShadow(QFrame.Plain)

        self.horizontalLayout_3.addWidget(self.preview_frame)

        self.task_details_textEdit = QTextEdit(self.main_frame)
        self.task_details_textEdit.setObjectName(u"task_details_textEdit")
        sizePolicy.setHeightForWidth(self.task_details_textEdit.sizePolicy().hasHeightForWidth())
        self.task_details_textEdit.setSizePolicy(sizePolicy)
        self.task_details_textEdit.setMinimumSize(QSize(470, 0))
        font = QFont()
        font.setPointSize(8)
        self.task_details_textEdit.setFont(font)
        self.task_details_textEdit.setMouseTracking(False)
        self.task_details_textEdit.setFocusPolicy(Qt.NoFocus)
        self.task_details_textEdit.setFrameShape(QFrame.NoFrame)
        self.task_details_textEdit.setFrameShadow(QFrame.Plain)
        self.task_details_textEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.task_details_textEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.task_details_textEdit.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.task_details_textEdit.setUndoRedoEnabled(False)
        self.task_details_textEdit.setLineWrapColumnOrWidth(0)
        self.task_details_textEdit.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.task_details_textEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.open_button = QPushButton(self.main_frame)
        self.open_button.setObjectName(u"open_button")
        self.open_button.setMinimumSize(QSize(0, 0))
        self.open_button.setStyleSheet(u"background-color: #216582; color:\n"
"                                                                    #E1E1E8; padding: 5px;\n"
"                                                                ")

        self.horizontalLayout.addWidget(self.open_button)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.log_line = QFrame(self.main_frame)
        self.log_line.setObjectName(u"log_line")
        self.log_line.setMinimumSize(QSize(0, 1))
        self.log_line.setMaximumSize(QSize(16777215, 1))
        self.log_line.setFrameShadow(QFrame.Plain)
        self.log_line.setFrameShape(QFrame.HLine)

        self.verticalLayout_3.addWidget(self.log_line)

        self.taskLog_frame = QFrame(self.main_frame)
        self.taskLog_frame.setObjectName(u"taskLog_frame")
        self.taskLog_frame.setMinimumSize(QSize(0, 320))
        self.taskLog_frame.setFrameShape(QFrame.NoFrame)
        self.taskLog_frame.setFrameShadow(QFrame.Plain)

        self.verticalLayout_3.addWidget(self.taskLog_frame)


        self.verticalLayout_2.addWidget(self.main_frame)


        self.horizontalLayout_2.addWidget(self.MainContainer)


        self.retranslateUi(TaskDetailsForm)

        QMetaObject.connectSlotsByName(TaskDetailsForm)
    # setupUi

    def retranslateUi(self, TaskDetailsForm):
        TaskDetailsForm.setWindowTitle(QCoreApplication.translate("TaskDetailsForm", u"Work Files Details", None))
        self.header_label.setText(QCoreApplication.translate("TaskDetailsForm", u"Placeholder", None))
#if QT_CONFIG(accessibility)
        self.task_details_textEdit.setAccessibleName(QCoreApplication.translate("TaskDetailsForm", u"v", None))
#endif // QT_CONFIG(accessibility)
        self.open_button.setText(QCoreApplication.translate("TaskDetailsForm", u"Open On Kitsu", None))
    # retranslateUi

