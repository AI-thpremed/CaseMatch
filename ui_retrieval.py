# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'retrieval.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_RetrievalWindow(object):
    def setupUi(self, RetrievalWindow):
        if not RetrievalWindow.objectName():
            RetrievalWindow.setObjectName(u"RetrievalWindow")
        RetrievalWindow.resize(1200, 900)
        self.verticalLayoutMain = QVBoxLayout(RetrievalWindow)
        self.verticalLayoutMain.setObjectName(u"verticalLayoutMain")
        self.groupLoadProject = QGroupBox(RetrievalWindow)
        self.groupLoadProject.setObjectName(u"groupLoadProject")
        self.horizontalLayoutLoad = QHBoxLayout(self.groupLoadProject)
        self.horizontalLayoutLoad.setObjectName(u"horizontalLayoutLoad")
        self.labelProjectPath = QLabel(self.groupLoadProject)
        self.labelProjectPath.setObjectName(u"labelProjectPath")

        self.horizontalLayoutLoad.addWidget(self.labelProjectPath)

        self.line_project_path = QLineEdit(self.groupLoadProject)
        self.line_project_path.setObjectName(u"line_project_path")
        self.line_project_path.setMinimumSize(QSize(0, 30))

        self.horizontalLayoutLoad.addWidget(self.line_project_path)

        self.btn_load = QPushButton(self.groupLoadProject)
        self.btn_load.setObjectName(u"btn_load")
        self.btn_load.setMinimumSize(QSize(80, 30))

        self.horizontalLayoutLoad.addWidget(self.btn_load)


        self.verticalLayoutMain.addWidget(self.groupLoadProject)

        self.groupQueryImage = QGroupBox(RetrievalWindow)
        self.groupQueryImage.setObjectName(u"groupQueryImage")
        self.horizontalLayoutQuery = QHBoxLayout(self.groupQueryImage)
        self.horizontalLayoutQuery.setObjectName(u"horizontalLayoutQuery")
        self.labelQueryPath = QLabel(self.groupQueryImage)
        self.labelQueryPath.setObjectName(u"labelQueryPath")

        self.horizontalLayoutQuery.addWidget(self.labelQueryPath)

        self.line_image_path = QLineEdit(self.groupQueryImage)
        self.line_image_path.setObjectName(u"line_image_path")
        self.line_image_path.setMinimumSize(QSize(0, 30))

        self.horizontalLayoutQuery.addWidget(self.line_image_path)

        self.btn_open_image = QPushButton(self.groupQueryImage)
        self.btn_open_image.setObjectName(u"btn_open_image")
        self.btn_open_image.setMinimumSize(QSize(80, 30))

        self.horizontalLayoutQuery.addWidget(self.btn_open_image)


        self.verticalLayoutMain.addWidget(self.groupQueryImage)

        self.groupSettings = QGroupBox(RetrievalWindow)
        self.groupSettings.setObjectName(u"groupSettings")
        self.horizontalLayoutSettings = QHBoxLayout(self.groupSettings)
        self.horizontalLayoutSettings.setObjectName(u"horizontalLayoutSettings")
        self.labelTopK = QLabel(self.groupSettings)
        self.labelTopK.setObjectName(u"labelTopK")

        self.horizontalLayoutSettings.addWidget(self.labelTopK)

        self.combo_topk = QComboBox(self.groupSettings)
        self.combo_topk.addItem("")
        self.combo_topk.addItem("")
        self.combo_topk.addItem("")
        self.combo_topk.addItem("")
        self.combo_topk.setObjectName(u"combo_topk")

        self.horizontalLayoutSettings.addWidget(self.combo_topk)

        self.horizontalSpacerSettings = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutSettings.addItem(self.horizontalSpacerSettings)

        self.labelMethod = QLabel(self.groupSettings)
        self.labelMethod.setObjectName(u"labelMethod")

        self.horizontalLayoutSettings.addWidget(self.labelMethod)

        self.combo_method = QComboBox(self.groupSettings)
        self.combo_method.addItem("")
        self.combo_method.addItem("")
        self.combo_method.setObjectName(u"combo_method")

        self.horizontalLayoutSettings.addWidget(self.combo_method)


        self.verticalLayoutMain.addWidget(self.groupSettings)

        self.horizontalLayoutButtons = QHBoxLayout()
        self.horizontalLayoutButtons.setObjectName(u"horizontalLayoutButtons")
        self.horizontalSpacerButtons = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutButtons.addItem(self.horizontalSpacerButtons)

        self.btn_start_retrieval = QPushButton(RetrievalWindow)
        self.btn_start_retrieval.setObjectName(u"btn_start_retrieval")
        self.btn_start_retrieval.setMinimumSize(QSize(150, 40))

        self.horizontalLayoutButtons.addWidget(self.btn_start_retrieval)

        self.horizontalSpacerButtons2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutButtons.addItem(self.horizontalSpacerButtons2)


        self.verticalLayoutMain.addLayout(self.horizontalLayoutButtons)

        self.groupResults = QGroupBox(RetrievalWindow)
        self.groupResults.setObjectName(u"groupResults")
        self.horizontalLayoutResults = QHBoxLayout(self.groupResults)
        self.horizontalLayoutResults.setObjectName(u"horizontalLayoutResults")
        self.groupQueryDisplay = QGroupBox(self.groupResults)
        self.groupQueryDisplay.setObjectName(u"groupQueryDisplay")
        self.verticalLayoutQuery = QVBoxLayout(self.groupQueryDisplay)
        self.verticalLayoutQuery.setObjectName(u"verticalLayoutQuery")
        self.label_query_image = QLabel(self.groupQueryDisplay)
        self.label_query_image.setObjectName(u"label_query_image")
        self.label_query_image.setMinimumSize(QSize(300, 300))
        self.label_query_image.setMaximumSize(QSize(400, 400))
        self.label_query_image.setFrameShape(QFrame.Box)
        self.label_query_image.setAlignment(Qt.AlignCenter)

        self.verticalLayoutQuery.addWidget(self.label_query_image)


        self.horizontalLayoutResults.addWidget(self.groupQueryDisplay)

        self.groupRetrieved = QGroupBox(self.groupResults)
        self.groupRetrieved.setObjectName(u"groupRetrieved")
        self.verticalLayoutRetrieved = QVBoxLayout(self.groupRetrieved)
        self.verticalLayoutRetrieved.setObjectName(u"verticalLayoutRetrieved")
        self.scroll_area_results = QScrollArea(self.groupRetrieved)
        self.scroll_area_results.setObjectName(u"scroll_area_results")
        self.scroll_area_results.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 800, 400))
        self.horizontalLayoutRetrievedImages = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayoutRetrievedImages.setObjectName(u"horizontalLayoutRetrievedImages")
        self.frame_result_1 = QFrame(self.scrollAreaWidgetContents)
        self.frame_result_1.setObjectName(u"frame_result_1")
        self.frame_result_1.setFrameShape(QFrame.Box)
        self.verticalLayoutResult1 = QVBoxLayout(self.frame_result_1)
        self.verticalLayoutResult1.setObjectName(u"verticalLayoutResult1")
        self.label_result_1 = QLabel(self.frame_result_1)
        self.label_result_1.setObjectName(u"label_result_1")
        self.label_result_1.setMinimumSize(QSize(200, 200))
        self.label_result_1.setMaximumSize(QSize(250, 250))
        self.label_result_1.setAlignment(Qt.AlignCenter)

        self.verticalLayoutResult1.addWidget(self.label_result_1)

        self.label_score_1 = QLabel(self.frame_result_1)
        self.label_score_1.setObjectName(u"label_score_1")
        self.label_score_1.setAlignment(Qt.AlignCenter)

        self.verticalLayoutResult1.addWidget(self.label_score_1)


        self.horizontalLayoutRetrievedImages.addWidget(self.frame_result_1)

        self.frame_result_2 = QFrame(self.scrollAreaWidgetContents)
        self.frame_result_2.setObjectName(u"frame_result_2")
        self.frame_result_2.setFrameShape(QFrame.Box)
        self.verticalLayoutResult2 = QVBoxLayout(self.frame_result_2)
        self.verticalLayoutResult2.setObjectName(u"verticalLayoutResult2")
        self.label_result_2 = QLabel(self.frame_result_2)
        self.label_result_2.setObjectName(u"label_result_2")
        self.label_result_2.setMinimumSize(QSize(200, 200))
        self.label_result_2.setMaximumSize(QSize(250, 250))
        self.label_result_2.setAlignment(Qt.AlignCenter)

        self.verticalLayoutResult2.addWidget(self.label_result_2)

        self.label_score_2 = QLabel(self.frame_result_2)
        self.label_score_2.setObjectName(u"label_score_2")
        self.label_score_2.setAlignment(Qt.AlignCenter)

        self.verticalLayoutResult2.addWidget(self.label_score_2)


        self.horizontalLayoutRetrievedImages.addWidget(self.frame_result_2)

        self.frame_result_3 = QFrame(self.scrollAreaWidgetContents)
        self.frame_result_3.setObjectName(u"frame_result_3")
        self.frame_result_3.setFrameShape(QFrame.Box)
        self.verticalLayoutResult3 = QVBoxLayout(self.frame_result_3)
        self.verticalLayoutResult3.setObjectName(u"verticalLayoutResult3")
        self.label_result_3 = QLabel(self.frame_result_3)
        self.label_result_3.setObjectName(u"label_result_3")
        self.label_result_3.setMinimumSize(QSize(200, 200))
        self.label_result_3.setMaximumSize(QSize(250, 250))
        self.label_result_3.setAlignment(Qt.AlignCenter)

        self.verticalLayoutResult3.addWidget(self.label_result_3)

        self.label_score_3 = QLabel(self.frame_result_3)
        self.label_score_3.setObjectName(u"label_score_3")
        self.label_score_3.setAlignment(Qt.AlignCenter)

        self.verticalLayoutResult3.addWidget(self.label_score_3)


        self.horizontalLayoutRetrievedImages.addWidget(self.frame_result_3)

        self.frame_result_4 = QFrame(self.scrollAreaWidgetContents)
        self.frame_result_4.setObjectName(u"frame_result_4")
        self.frame_result_4.setFrameShape(QFrame.Box)
        self.verticalLayoutResult4 = QVBoxLayout(self.frame_result_4)
        self.verticalLayoutResult4.setObjectName(u"verticalLayoutResult4")
        self.label_result_4 = QLabel(self.frame_result_4)
        self.label_result_4.setObjectName(u"label_result_4")
        self.label_result_4.setMinimumSize(QSize(200, 200))
        self.label_result_4.setMaximumSize(QSize(250, 250))
        self.label_result_4.setAlignment(Qt.AlignCenter)

        self.verticalLayoutResult4.addWidget(self.label_result_4)

        self.label_score_4 = QLabel(self.frame_result_4)
        self.label_score_4.setObjectName(u"label_score_4")
        self.label_score_4.setAlignment(Qt.AlignCenter)

        self.verticalLayoutResult4.addWidget(self.label_score_4)


        self.horizontalLayoutRetrievedImages.addWidget(self.frame_result_4)

        self.frame_result_5 = QFrame(self.scrollAreaWidgetContents)
        self.frame_result_5.setObjectName(u"frame_result_5")
        self.frame_result_5.setFrameShape(QFrame.Box)
        self.verticalLayoutResult5 = QVBoxLayout(self.frame_result_5)
        self.verticalLayoutResult5.setObjectName(u"verticalLayoutResult5")
        self.label_result_5 = QLabel(self.frame_result_5)
        self.label_result_5.setObjectName(u"label_result_5")
        self.label_result_5.setMinimumSize(QSize(200, 200))
        self.label_result_5.setMaximumSize(QSize(250, 250))
        self.label_result_5.setAlignment(Qt.AlignCenter)

        self.verticalLayoutResult5.addWidget(self.label_result_5)

        self.label_score_5 = QLabel(self.frame_result_5)
        self.label_score_5.setObjectName(u"label_score_5")
        self.label_score_5.setAlignment(Qt.AlignCenter)

        self.verticalLayoutResult5.addWidget(self.label_score_5)


        self.horizontalLayoutRetrievedImages.addWidget(self.frame_result_5)

        self.scroll_area_results.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayoutRetrieved.addWidget(self.scroll_area_results)


        self.horizontalLayoutResults.addWidget(self.groupRetrieved)


        self.verticalLayoutMain.addWidget(self.groupResults)

        self.groupLog = QGroupBox(RetrievalWindow)
        self.groupLog.setObjectName(u"groupLog")
        self.verticalLayoutLog = QVBoxLayout(self.groupLog)
        self.verticalLayoutLog.setObjectName(u"verticalLayoutLog")
        self.text_log = QTextEdit(self.groupLog)
        self.text_log.setObjectName(u"text_log")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_log.sizePolicy().hasHeightForWidth())
        self.text_log.setSizePolicy(sizePolicy)
        self.text_log.setMinimumSize(QSize(0, 80))
        self.text_log.setReadOnly(True)

        self.verticalLayoutLog.addWidget(self.text_log)


        self.verticalLayoutMain.addWidget(self.groupLog)


        self.retranslateUi(RetrievalWindow)

        QMetaObject.connectSlotsByName(RetrievalWindow)
    # setupUi

    def retranslateUi(self, RetrievalWindow):
        RetrievalWindow.setWindowTitle(QCoreApplication.translate("RetrievalWindow", u"Image Retrieval", None))
        self.groupLoadProject.setTitle(QCoreApplication.translate("RetrievalWindow", u"Load Project", None))
        self.labelProjectPath.setText(QCoreApplication.translate("RetrievalWindow", u"Project Path\uff1a", None))
        self.line_project_path.setPlaceholderText(QCoreApplication.translate("RetrievalWindow", u"Select existing project folder...", None))
        self.btn_load.setText(QCoreApplication.translate("RetrievalWindow", u"Load", None))
        self.groupQueryImage.setTitle(QCoreApplication.translate("RetrievalWindow", u"Query Image", None))
        self.labelQueryPath.setText(QCoreApplication.translate("RetrievalWindow", u"Image Path\uff1a", None))
        self.line_image_path.setPlaceholderText(QCoreApplication.translate("RetrievalWindow", u"Select query image...", None))
        self.btn_open_image.setText(QCoreApplication.translate("RetrievalWindow", u"Open", None))
        self.groupSettings.setTitle(QCoreApplication.translate("RetrievalWindow", u"Retrieval Settings", None))
        self.labelTopK.setText(QCoreApplication.translate("RetrievalWindow", u"Top K\uff1a", None))
        self.combo_topk.setItemText(0, QCoreApplication.translate("RetrievalWindow", u"5", None))
        self.combo_topk.setItemText(1, QCoreApplication.translate("RetrievalWindow", u"10", None))
        self.combo_topk.setItemText(2, QCoreApplication.translate("RetrievalWindow", u"20", None))
        self.combo_topk.setItemText(3, QCoreApplication.translate("RetrievalWindow", u"50", None))

        self.labelMethod.setText(QCoreApplication.translate("RetrievalWindow", u"Method\uff1a", None))
        self.combo_method.setItemText(0, QCoreApplication.translate("RetrievalWindow", u"avgpool_2048", None))
        self.combo_method.setItemText(1, QCoreApplication.translate("RetrievalWindow", u"layer4_gem_2048", None))

        self.btn_start_retrieval.setText(QCoreApplication.translate("RetrievalWindow", u"Start Retrieval", None))
        self.groupResults.setTitle(QCoreApplication.translate("RetrievalWindow", u"Retrieval Results", None))
        self.groupQueryDisplay.setTitle(QCoreApplication.translate("RetrievalWindow", u"Query Image", None))
        self.label_query_image.setText(QCoreApplication.translate("RetrievalWindow", u"Query Image will appear here", None))
        self.groupRetrieved.setTitle(QCoreApplication.translate("RetrievalWindow", u"Top 5 Similar Images", None))
        self.label_result_1.setText(QCoreApplication.translate("RetrievalWindow", u"Result 1", None))
        self.label_score_1.setText(QCoreApplication.translate("RetrievalWindow", u"Similarity: --", None))
        self.label_result_2.setText(QCoreApplication.translate("RetrievalWindow", u"Result 2", None))
        self.label_score_2.setText(QCoreApplication.translate("RetrievalWindow", u"Similarity: --", None))
        self.label_result_3.setText(QCoreApplication.translate("RetrievalWindow", u"Result 3", None))
        self.label_score_3.setText(QCoreApplication.translate("RetrievalWindow", u"Similarity: --", None))
        self.label_result_4.setText(QCoreApplication.translate("RetrievalWindow", u"Result 4", None))
        self.label_score_4.setText(QCoreApplication.translate("RetrievalWindow", u"Similarity: --", None))
        self.label_result_5.setText(QCoreApplication.translate("RetrievalWindow", u"Result 5", None))
        self.label_score_5.setText(QCoreApplication.translate("RetrievalWindow", u"Similarity: --", None))
        self.groupLog.setTitle(QCoreApplication.translate("RetrievalWindow", u"Log", None))
    # retranslateUi

