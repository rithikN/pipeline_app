# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'project_card_form.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
                               QSizePolicy, QWidget)


class Ui_ProjectCard(object):
    def setupUi(self, ProjectCard):
        if not ProjectCard.objectName():
            ProjectCard.setObjectName(u"ProjectCard")
        ProjectCard.resize(392, 256)
        self.gridLayout = QGridLayout(ProjectCard)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.thumbnailLabel = QLabel(ProjectCard)
        self.thumbnailLabel.setObjectName(u"thumbnailLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.thumbnailLabel.sizePolicy().hasHeightForWidth())
        self.thumbnailLabel.setSizePolicy(sizePolicy)
        self.thumbnailLabel.setMinimumSize(QSize(0, 120))
        self.thumbnailLabel.setPixmap(QPixmap(u"../../../resources/empty_project.png"))
        self.thumbnailLabel.setScaledContents(True)
        self.thumbnailLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.thumbnailLabel, 0, 0, 1, 1)

        self.titleLabel = QLabel(ProjectCard)
        self.titleLabel.setObjectName(u"titleLabel")
        font = QFont()
        font.setBold(True)
        self.titleLabel.setFont(font)
        self.titleLabel.setLineWidth(0)
        self.titleLabel.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.titleLabel.setMargin(2)
        self.titleLabel.setIndent(5)
        self.titleLabel.setTextInteractionFlags(Qt.NoTextInteraction)

        self.gridLayout.addWidget(self.titleLabel, 1, 0, 1, 1)

        self.authorLabel = QLabel(ProjectCard)
        self.authorLabel.setObjectName(u"authorLabel")
        self.authorLabel.setMinimumSize(QSize(0, 25))
        self.authorLabel.setFrameShadow(QFrame.Plain)
        self.authorLabel.setLineWidth(0)
        self.authorLabel.setScaledContents(False)
        self.authorLabel.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
        self.authorLabel.setWordWrap(False)
        self.authorLabel.setMargin(1)
        self.authorLabel.setIndent(5)
        self.authorLabel.setTextInteractionFlags(Qt.NoTextInteraction)

        self.gridLayout.addWidget(self.authorLabel, 2, 0, 1, 1)

        self.emptyLabel = QLabel(ProjectCard)
        self.emptyLabel.setObjectName(u"emptyLabel")

        self.gridLayout.addWidget(self.emptyLabel, 3, 0, 1, 1)

        self.retranslateUi(ProjectCard)

        QMetaObject.connectSlotsByName(ProjectCard)

    # setupUi

    def retranslateUi(self, ProjectCard):
        self.thumbnailLabel.setStyleSheet(
            QCoreApplication.translate("ProjectCard", u"background-color: lightgray; border: 1px solid gray;", None))
        self.thumbnailLabel.setText("")
        self.titleLabel.setText(QCoreApplication.translate("ProjectCard", u"Project Title", None))
        self.authorLabel.setText(QCoreApplication.translate("ProjectCard", u"Director: John Doe", None))
        self.emptyLabel.setText("")
        pass
    # retranslateUi
