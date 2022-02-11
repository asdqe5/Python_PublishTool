# _*_ coding: utf-8 _*_

# Comp Publish Tool
#
# Description : UI를 세팅하는 스크립트

import os
import sys
import re
import json
import getpass
import subprocess
import json

# global variables
SHOW_PATH = os.getenv("SHOW_PATH")
TD_PATH = os.getenv("TD_PATH")
PWD = os.path.dirname(os.path.abspath(__file__))
settingJson = "{}/nuke/plugins/pythons/setProjectTool/setting.json".format(TD_PATH)
f = open(settingJson, "r")
setting = json.load(f)
f.close()

from PySide2 import QtWidgets, QtCore, QtGui

if "{}/api/pathapi".format(TD_PATH) not in sys.path:
    sys.path.append("{}/api/pathapi".format(TD_PATH))
import rdpath

if "{}/api" not in sys.path:
    sys.path.append('{}/api'.format(TD_PATH))

import shotgun_api3

sg = shotgun_api3.Shotgun("https://road101.shotgunstudio.com", script_name="authentication_script", api_key="vZnk#jbmopl6oqispvodazfyn")

def initUIFunc(self):
    '''
    UI 초기 세팅
    '''
    self.ui.collect_user_lineEdit.setText(getpass.getuser())
    projectList, err = rdpath.projects()
    if err != None:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText(err)
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return

    if projectList == None:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("프로젝트가 존재하지 않습니다.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
        
    self.ui.collect_project_comboBox.clear()
    # json 파일에서 old 프로젝트 리스트를 가져옴
    f = open(self.proJson, "r")
    jsonData = json.load(f)
    f.close()
    jsonProjectList = []
    newProjectList = []
    for p in jsonData["nuke"]["projects"]:
        jsonProjectList.append(p["Name"])
    for p in projectList:
        if p not in jsonProjectList:
            newProjectList.append(p)
    self.ui.collect_project_comboBox.addItems([""] + newProjectList)

    self.ui.collect_sequence_comboBox.clear()
    self.ui.collect_shot_comboBox.clear()
    self.ui.collect_version_comboBox.clear()
    self.ui.collect_note_textEdit.clear()
    self.ui.collect_publog_textEdit.clear()
    self.ui.collect_publog_textEdit.setReadOnly(True)
    self.ui.collect_ccGroup_lineEdit.clear()
    self.ui.collect_ccGroup_lineEdit.setReadOnly(True)
    self.ui.collect_ccPerson_lineEdit.clear()
    self.ui.collect_ccPerson_lineEdit.setReadOnly(True)

    # 리눅스는 한글 입력을 못하니까 안내문을 띄워준다.
    if sys.platform == "linux2":
        self.ui.collect_note_textEdit.setToolTip(u"<html><head/><body><p>한글 입력이 안됩니다.<br>메모장을 이용해주세요.</p></body></html>")
    elif sys.platform == "win32":
        self.ui.collect_note_toolButton.setVisible(False)

    # Publish Data 테이블 설정
    self.ui.collect_publish_tableWidget.setColumnCount(len(self.collect_column_headers))
    self.ui.collect_publish_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    self.ui.collect_publish_tableWidget.setHorizontalHeaderLabels(self.collect_column_headers)

def setSeqFunc(self):
    '''
    시퀀스 콤보박스를 세팅하는 함수
    '''
    self.ui.collect_sequence_comboBox.clear()
    self.ui.collect_shot_comboBox.clear()
    self.ui.collect_version_comboBox.clear()

    if self.ui.collect_project_comboBox.currentText() == "":
        return
    projectName = self.ui.collect_project_comboBox.currentText()

    seqList, err = rdpath.seqs(projectName)
    if err != None:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("{} 프로젝트에서 시퀀스를 가져오는데 문제가 발생하였습니다.".format(projectName))
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
    if seqList == None:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("{} 프로젝트에 시퀀스가 존재하지 않습니다.".format(projectName))
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
    
    self.ui.collect_sequence_comboBox.addItems([""] + seqList)

def setShotFunc(self):
    '''
    샷 콤보박스를 세팅하는 함수
    '''
    self.ui.collect_shot_comboBox.clear()
    self.ui.collect_version_comboBox.clear()

    projectName = self.ui.collect_project_comboBox.currentText()

    if self.ui.collect_sequence_comboBox.currentText() == "":
        return
    seqName = self.ui.collect_sequence_comboBox.currentText()

    shotList, err = rdpath.shots(projectName, seqName)
    if err != None:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("{} 시퀀스에서 샷을 가져오는데 문제가 발생하였습니다.".format(seqName))
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
    if shotList == None:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("{} 시퀀스에 샷이 존재하지 않습니다.".format(seqName))
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
    
    self.ui.collect_shot_comboBox.addItems([""] + shotList)

def setVerFunc(self):
    '''
    버전 콤보박스를 세팅하는 함수
    '''
    self.ui.collect_version_comboBox.clear()

    projectName = self.ui.collect_project_comboBox.currentText()
    seqName = self.ui.collect_sequence_comboBox.currentText()
    
    if self.ui.collect_shot_comboBox.currentText() == "":
        return
    
    shotName = self.ui.collect_shot_comboBox.currentText()
    teamName = "comp"
    taskName = "comp_collect"

    path = os.path.join(SHOW_PATH, projectName, "shot", seqName, shotName, teamName, "pub", taskName)
    if os.path.exists(path):
        if not os.listdir(path):
            dial = QtWidgets.QMessageBox()
            dial.setWindowTitle("Error")
            dial.setText("{} 태스크 폴더가 비어있습니다.".format(taskName))
            ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
            dial.exec_()
            return
        
        ver = os.listdir(path)
        ver.sort()

        verList = []
        for v in ver:
            # 숨겨져 있는지 확인
            if v.startswith("."):
                continue

            # 폴더인지 확인
            if not os.path.isdir(os.path.join(path, v)):
                continue

            verList.append(v)

        self.ui.collect_version_comboBox.addItems([""] + verList)
        
    else:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("pub 폴더에 {} 태스크 폴더가 존재하지 않습니다.".format(taskName))
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return

def openEditorFunc():
    '''
    텍스트 편집기를 실행하는 함수
    '''
    if sys.platform == "linux2":
        subprocess.Popen(["gedit", "--new-window"])

def setCCGroupFunc(self):
    '''
    CC_Group line 옆 ... 버튼을 눌렀을 때
    실행하는 함수 -> CC_Group을 추가하는 list widget을 연다 
    '''
    # 버튼을 비활성화한다.
    self.ui.collect_ccGroup_pushButton.setEnabled(False)
    self.ui.collect_ccPerson_pushButton.setEnabled(False)

    # 버튼 클릭했을 때의 위젯 생성
    widget = QtWidgets.QWidget()
    widget.setWindowTitle("Shotgun CC Group")
    widget.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
    widget.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, False)
    addButton = QtWidgets.QPushButton("Add")
    cancelButton = QtWidgets.QPushButton("Cancel")
    widgetLayout = QtWidgets.QVBoxLayout()

    ccList = QtWidgets.QListWidget() # 위젯 내의 리스트 생성
    ccList.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

    # 샷건에서 CC 그룹을 가져온다.
    groups = sg.find('Group', [], ['code', 'id'])
    for g in groups:
        ccList.addItem(g['code'])

    widgetLayout.addWidget(ccList)
    widgetLayout.addWidget(addButton)
    widgetLayout.addWidget(cancelButton)
    widgetLayout.addStretch()
    
    widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
    widget.setLayout(widgetLayout)
    widget.show()

    # button signal
    addButton.clicked.connect(lambda: addCCGroupWidget(self, ccList, widget))
    cancelButton.clicked.connect(lambda: cancelCCWidget(self, widget))

def setCCPersonFunc(self):
    '''
    CC_Person line 옆 ... 버튼을 눌렀을 때
    실행하는 함수 -> CC_Person을 추가하는 list widget을 연다
    '''
    # 버튼을 비활성화한다.
    self.ui.collect_ccGroup_pushButton.setEnabled(False)
    self.ui.collect_ccPerson_pushButton.setEnabled(False)

    # 버튼 클릭했을 때 위젯 생성
    widget = QtWidgets.QWidget()
    widget.setWindowTitle("Shotgun CC Person")
    widget.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
    widget.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, False)
    addButton = QtWidgets.QPushButton("Add")
    cancelButton = QtWidgets.QPushButton("Cancel")
    widgetLayout = QtWidgets.QVBoxLayout()

    ccList = QtWidgets.QListWidget()
    ccList.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

    # 샷건에서 CC Person을 가져온다.
    people = sg.find('HumanUser', [['sg_status_list', 'is', 'act']], ['name', 'login'])
    for p in people:
        ccList.addItem("{}({})".format(p['name'], p['login']))
    
    widgetLayout.addWidget(ccList)
    widgetLayout.addWidget(addButton)
    widgetLayout.addWidget(cancelButton)
    widgetLayout.addStretch()
    
    widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
    widget.setLayout(widgetLayout)
    widget.show()

    # button signal
    addButton.clicked.connect(lambda: addCCPersonWidget(self, ccList, widget))
    cancelButton.clicked.connect(lambda: cancelCCWidget(self, widget))

def addCCGroupWidget(self, ccList, widget):
    '''
    선택된 CC(그룹)를 Add 하는 함수
    '''
    ccText = ""
    for cc in ccList.selectedItems():
        ccText += cc.text() + " "

    widget.close()
    self.ui.collect_ccGroup_lineEdit.setText(ccText)
    self.ui.collect_ccGroup_pushButton.setEnabled(True)
    self.ui.collect_ccPerson_pushButton.setEnabled(True)

def addCCPersonWidget(self, ccList, widget):
    '''
    선택된 CC(그룹)를 Add 하는 함수
    '''
    ccText = ""
    for cc in ccList.selectedItems():
        ccText += cc.text() + " "

    widget.close()
    self.ui.collect_ccPerson_lineEdit.setText(ccText)
    self.ui.collect_ccGroup_pushButton.setEnabled(True)
    self.ui.collect_ccPerson_pushButton.setEnabled(True)

def cancelCCWidget(self, widget):
    '''
    CC 위젯을 닫는 함수
    '''
    widget.close()
    self.ui.collect_ccGroup_pushButton.setEnabled(True)
    self.ui.collect_ccPerson_pushButton.setEnabled(True)

def setPublishTableFunc(self):
    '''
    Setting 값들을 설정한 후에 Add 버튼을 눌렀을 때, Publish Data Table에
    해당 버전의 정보가 저장되는 함수이다.
    '''
    if self.ui.collect_project_comboBox.currentText() == "":
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText(u"프로젝트를 선택해주세요.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return

    if self.ui.collect_sequence_comboBox.currentText() == "":
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText(u"시퀀스를 선택해주세요.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return

    if self.ui.collect_shot_comboBox.currentText() == "":
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText(u"샷을 선택해주세요.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return 
    
    if self.ui.collect_version_comboBox.currentText() == "":
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText(u"버전명을 선택해주세요.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return

    projectName = self.ui.collect_project_comboBox.currentText()
    seqName = self.ui.collect_sequence_comboBox.currentText()
    shotName = self.ui.collect_shot_comboBox.currentText()
    teamName = "comp"
    taskName = "comp_collect"
    verName = self.ui.collect_version_comboBox.currentText()
    ccGroup = self.ui.collect_ccGroup_lineEdit.text()
    ccPerson = self.ui.collect_ccPerson_lineEdit.text()
    pubPath = os.path.join(SHOW_PATH, projectName, "shot", seqName, shotName, teamName, "pub", taskName, verName)

    # publish table에 이미 같은 파일이 있다면 에러처리
    tableRow = self.ui.collect_publish_tableWidget.rowCount()
    tableColumn = self.ui.collect_publish_tableWidget.columnCount()
    for r in range(tableRow):
        # InputPath가 일치하는지 확인
        if pubPath == self.ui.collect_publish_tableWidget.item(r, self.collect_column_idx_lookup["PubCollectPath"]).text():
            dial = QtWidgets.QMessageBox()
            dial.setWindowTitle("Error")
            dial.setText("테이블에 이미 같은 파일이 존재합니다.")
            ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
            dial.exec_()
            return

    verName = os.path.splitext(verName)[0]
    note = self.ui.collect_note_textEdit.toPlainText()
    tableData = [projectName, seqName, shotName, taskName, verName, pubPath, note, ccGroup, ccPerson]
    self.ui.collect_publish_tableWidget.insertRow(tableRow)
    for j in range(tableColumn):
        item = QtWidgets.QTableWidgetItem(tableData[j])
        item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self.ui.collect_publish_tableWidget.setItem(tableRow, j, item)

    self.ui.collect_publish_tableWidget.resizeColumnsToContents()
    self.ui.collect_publish_tableWidget.resizeRowsToContents()
    
    initUIFunc(self)

def minusPublishTableFunc(self):
    '''
    [-] 버튼을 눌렀을 때 테이블에서 현재 선택하고 있는 정보를 제거하는 함수이다.
    '''
    if self.ui.collect_publish_tableWidget.rowCount() == 0:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("테이블에 제거할 데이터가 존재하지 않습니다.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
    
    if not self.ui.collect_publish_tableWidget.selectedItems():
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("제거할 데이터를 선택해주세요.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
        
    tableRow = self.ui.collect_publish_tableWidget.currentRow()
    self.ui.collect_publish_tableWidget.removeRow(tableRow)