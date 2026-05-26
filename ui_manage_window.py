# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'manage_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QTextEdit, QVBoxLayout, QWidget)

class Ui_ManageProject(object):
    def setupUi(self, ManageProject):
        if not ManageProject.objectName():
            ManageProject.setObjectName(u"ManageProject")
        ManageProject.resize(600, 500)
        self.verticalLayout = QVBoxLayout(ManageProject)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupLoadProject = QGroupBox(ManageProject)
        self.groupLoadProject.setObjectName(u"groupLoadProject")
        self.formLayoutLoad = QFormLayout(self.groupLoadProject)
        self.formLayoutLoad.setObjectName(u"formLayoutLoad")
        self.labelProjectPath = QLabel(self.groupLoadProject)
        self.labelProjectPath.setObjectName(u"labelProjectPath")

        self.formLayoutLoad.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelProjectPath)

        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.line_project_path = QLineEdit(self.groupLoadProject)
        self.line_project_path.setObjectName(u"line_project_path")
        self.line_project_path.setMinimumSize(QSize(0, 30))

        self.hboxLayout.addWidget(self.line_project_path)

        self.btn_load = QPushButton(self.groupLoadProject)
        self.btn_load.setObjectName(u"btn_load")
        self.btn_load.setMinimumSize(QSize(80, 30))

        self.hboxLayout.addWidget(self.btn_load)


        self.formLayoutLoad.setLayout(0, QFormLayout.ItemRole.FieldRole, self.hboxLayout)


        self.verticalLayout.addWidget(self.groupLoadProject)

        self.horizontalLayoutButtons = QHBoxLayout()
        self.horizontalLayoutButtons.setObjectName(u"horizontalLayoutButtons")
        self.horizontalSpacerButtons = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutButtons.addItem(self.horizontalSpacerButtons)

        self.btn_update_index = QPushButton(ManageProject)
        self.btn_update_index.setObjectName(u"btn_update_index")
        self.btn_update_index.setMinimumSize(QSize(150, 40))

        self.horizontalLayoutButtons.addWidget(self.btn_update_index)

        self.horizontalSpacerButtons2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutButtons.addItem(self.horizontalSpacerButtons2)


        self.verticalLayout.addLayout(self.horizontalLayoutButtons)

        self.groupLog = QGroupBox(ManageProject)
        self.groupLog.setObjectName(u"groupLog")
        self.vLayoutLog = QVBoxLayout(self.groupLog)
        self.vLayoutLog.setObjectName(u"vLayoutLog")
        self.text_log = QTextEdit(self.groupLog)
        self.text_log.setObjectName(u"text_log")
        self.text_log.setReadOnly(True)

        self.vLayoutLog.addWidget(self.text_log)


        self.verticalLayout.addWidget(self.groupLog)


        self.retranslateUi(ManageProject)

        QMetaObject.connectSlotsByName(ManageProject)
    # setupUi

    def retranslateUi(self, ManageProject):
        ManageProject.setWindowTitle(QCoreApplication.translate("ManageProject", u"Manage Project", None))
        self.groupLoadProject.setTitle(QCoreApplication.translate("ManageProject", u"Load Project", None))
        self.labelProjectPath.setText(QCoreApplication.translate("ManageProject", u"Project Path\uff1a", None))
        self.line_project_path.setPlaceholderText(QCoreApplication.translate("ManageProject", u"Select existing project folder...", None))
        self.btn_load.setText(QCoreApplication.translate("ManageProject", u"Load", None))
        self.btn_update_index.setText(QCoreApplication.translate("ManageProject", u"Quick Update", None))
        self.groupLog.setTitle(QCoreApplication.translate("ManageProject", u"Log", None))
        self.text_log.setPlaceholderText(QCoreApplication.translate("ManageProject", u"Index management operations log will be displayed here...", None))
    # retranslateUi

