# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'build_window.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_BuildNewProject(object):
    def setupUi(self, BuildNewProject):
        if not BuildNewProject.objectName():
            BuildNewProject.setObjectName(u"BuildNewProject")
        BuildNewProject.resize(600, 500)
        self.verticalLayout = QVBoxLayout(BuildNewProject)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupProjectSetting = QGroupBox(BuildNewProject)
        self.groupProjectSetting.setObjectName(u"groupProjectSetting")
        self.formLayoutProject = QFormLayout(self.groupProjectSetting)
        self.formLayoutProject.setObjectName(u"formLayoutProject")
        self.labelProjectName = QLabel(self.groupProjectSetting)
        self.labelProjectName.setObjectName(u"labelProjectName")

        self.formLayoutProject.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelProjectName)

        self.line_project_name = QLineEdit(self.groupProjectSetting)
        self.line_project_name.setObjectName(u"line_project_name")
        self.line_project_name.setMinimumSize(QSize(0, 30))

        self.formLayoutProject.setWidget(0, QFormLayout.ItemRole.FieldRole, self.line_project_name)

        self.labelAlgo = QLabel(self.groupProjectSetting)
        self.labelAlgo.setObjectName(u"labelAlgo")

        self.formLayoutProject.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelAlgo)

        self.combo_algo = QComboBox(self.groupProjectSetting)
        self.combo_algo.setObjectName(u"combo_algo")

        self.formLayoutProject.setWidget(1, QFormLayout.ItemRole.FieldRole, self.combo_algo)


        self.verticalLayout.addWidget(self.groupProjectSetting)

        self.groupImagePath = QGroupBox(BuildNewProject)
        self.groupImagePath.setObjectName(u"groupImagePath")
        self.formLayoutImage = QFormLayout(self.groupImagePath)
        self.formLayoutImage.setObjectName(u"formLayoutImage")
        self.labelImgPath = QLabel(self.groupImagePath)
        self.labelImgPath.setObjectName(u"labelImgPath")

        self.formLayoutImage.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelImgPath)

        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.line_image_path = QLineEdit(self.groupImagePath)
        self.line_image_path.setObjectName(u"line_image_path")
        self.line_image_path.setMinimumSize(QSize(0, 30))

        self.hboxLayout.addWidget(self.line_image_path)

        self.btn_select_path = QPushButton(self.groupImagePath)
        self.btn_select_path.setObjectName(u"btn_select_path")
        self.btn_select_path.setMinimumSize(QSize(80, 30))

        self.hboxLayout.addWidget(self.btn_select_path)


        self.formLayoutImage.setLayout(0, QFormLayout.ItemRole.FieldRole, self.hboxLayout)


        self.verticalLayout.addWidget(self.groupImagePath)

        self.hLayoutButton = QHBoxLayout()
        self.hLayoutButton.setObjectName(u"hLayoutButton")
        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hLayoutButton.addItem(self.horizontalSpacer)

        self.btn_start_building = QPushButton(BuildNewProject)
        self.btn_start_building.setObjectName(u"btn_start_building")
        self.btn_start_building.setMinimumSize(QSize(150, 35))

        self.hLayoutButton.addWidget(self.btn_start_building)

        self.btn_stop_building = QPushButton(BuildNewProject)
        self.btn_stop_building.setObjectName(u"btn_stop_building")
        self.btn_stop_building.setEnabled(False)
        self.btn_stop_building.setMinimumSize(QSize(150, 35))

        self.hLayoutButton.addWidget(self.btn_stop_building)

        self.horizontalSpacer2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hLayoutButton.addItem(self.horizontalSpacer2)


        self.verticalLayout.addLayout(self.hLayoutButton)

        self.groupLog = QGroupBox(BuildNewProject)
        self.groupLog.setObjectName(u"groupLog")
        self.vLayoutLog = QVBoxLayout(self.groupLog)
        self.vLayoutLog.setObjectName(u"vLayoutLog")
        self.text_log = QTextEdit(self.groupLog)
        self.text_log.setObjectName(u"text_log")
        self.text_log.setReadOnly(True)

        self.vLayoutLog.addWidget(self.text_log)


        self.verticalLayout.addWidget(self.groupLog)


        self.retranslateUi(BuildNewProject)

        QMetaObject.connectSlotsByName(BuildNewProject)
    # setupUi

    def retranslateUi(self, BuildNewProject):
        BuildNewProject.setWindowTitle(QCoreApplication.translate("BuildNewProject", u"Build New Project", None))
        self.groupProjectSetting.setTitle(QCoreApplication.translate("BuildNewProject", u"Project Setting", None))
        self.labelProjectName.setText(QCoreApplication.translate("BuildNewProject", u"Project Name\uff1a", None))
        self.line_project_name.setPlaceholderText(QCoreApplication.translate("BuildNewProject", u"Enter project name...", None))
        self.labelAlgo.setText(QCoreApplication.translate("BuildNewProject", u"Algorithm\uff1a", None))
        self.groupImagePath.setTitle(QCoreApplication.translate("BuildNewProject", u"Image Path", None))
        self.labelImgPath.setText(QCoreApplication.translate("BuildNewProject", u"Image Path of New Project\uff1a", None))
        self.line_image_path.setPlaceholderText(QCoreApplication.translate("BuildNewProject", u"Select folder containing images...", None))
        self.btn_select_path.setText(QCoreApplication.translate("BuildNewProject", u"Open", None))
        self.btn_start_building.setText(QCoreApplication.translate("BuildNewProject", u"Start Building", None))
        self.btn_stop_building.setText(QCoreApplication.translate("BuildNewProject", u"Stop Building", None))
        self.groupLog.setTitle(QCoreApplication.translate("BuildNewProject", u"Log", None))
        self.text_log.setPlaceholderText(QCoreApplication.translate("BuildNewProject", u"Building process and summary will be displayed here...", None))
    # retranslateUi

