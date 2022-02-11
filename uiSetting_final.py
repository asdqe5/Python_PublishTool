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

projectInfoJson = "{}/nuke/plugins/pythons/writeNode/projectInfo.json".format(TD_PATH)
f = open(projectInfoJson, "r")
projectInfo = json.load(f)
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
    self.ui.final_user_lineEdit.setText(getpass.getuser())
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
        
    self.ui.final_project_comboBox.clear()
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
    self.ui.final_project_comboBox.addItems([""] + newProjectList)

    self.ui.final_sequence_comboBox.clear()
    self.ui.final_shot_comboBox.clear()
    self.ui.final_task_comboBox.clear()
    self.ui.final_ext_comboBox.clear()
    self.ui.final_shotgunmov_checkBox.setChecked(False)
    self.ui.final_version_comboBox.clear()
    self.ui.final_note_textEdit.clear()
    self.ui.final_final_radioButton.setChecked(True)
    self.ui.final_publog_textEdit.clear()
    self.ui.final_publog_textEdit.setReadOnly(True)
    self.ui.final_ccGroup_lineEdit.clear()
    self.ui.final_ccGroup_lineEdit.setReadOnly(True)
    self.ui.final_ccPerson_lineEdit.clear()
    self.ui.final_ccPerson_lineEdit.setReadOnly(True)

    # 리눅스는 한글 입력을 못하니까 안내문을 띄워준다.
    if sys.platform == "linux2":
        self.ui.final_note_textEdit.setToolTip(u"<html><head/><body><p>한글 입력이 안됩니다.<br>메모장을 이용해주세요.</p></body></html>")
    elif sys.platform == "win32":
        self.ui.final_note_toolButton.setVisible(False)

    # Publish Data 테이블 설정
    self.ui.final_publish_tableWidget.setColumnCount(len(self.final_column_headers))
    self.ui.final_publish_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    self.ui.final_publish_tableWidget.setHorizontalHeaderLabels(self.final_column_headers)

def setSeqFunc(self):
    '''
    시퀀스 콤보박스를 세팅하는 함수
    '''
    self.ui.final_sequence_comboBox.clear()
    self.ui.final_shot_comboBox.clear()
    self.ui.final_task_comboBox.clear()
    self.ui.final_ext_comboBox.clear()
    self.ui.final_shotgunmov_checkBox.setChecked(False)
    self.ui.final_version_comboBox.clear()

    if self.ui.final_project_comboBox.currentText() == "":
        return
    projectName = self.ui.final_project_comboBox.currentText()

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
    
    self.ui.final_sequence_comboBox.addItems([""] + seqList)

def setShotFunc(self):
    '''
    샷 콤보박스를 세팅하는 함수
    '''
    self.ui.final_shot_comboBox.clear()
    self.ui.final_task_comboBox.clear()
    self.ui.final_ext_comboBox.clear()
    self.ui.final_shotgunmov_checkBox.setChecked(False)
    self.ui.final_version_comboBox.clear()

    projectName = self.ui.final_project_comboBox.currentText()

    if self.ui.final_sequence_comboBox.currentText() == "":
        return
    seqName = self.ui.final_sequence_comboBox.currentText()

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
    
    self.ui.final_shot_comboBox.addItems([""] + shotList)

def setTaskFunc(self):
    '''
    태스크 콤보박스를 세팅하는 함수
    '''
    self.ui.final_task_comboBox.clear()
    self.ui.final_ext_comboBox.clear()
    self.ui.final_shotgunmov_checkBox.setChecked(False)
    self.ui.final_version_comboBox.clear()

    projectName = self.ui.final_project_comboBox.currentText()
    seqName = self.ui.final_sequence_comboBox.currentText()

    if self.ui.final_shot_comboBox.currentText() == "":
        return
    shotName = self.ui.final_shot_comboBox.currentText()
    teamName = "comp"
    
    taskList, err = rdpath.tasks(projectName, seqName, shotName, teamName)

    if err != None:  # 태스크 리스트를 가져오는데 에러가 발생하면 리턴
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("{} 팀에서 태스크를 가져오는데 문제가 발생하였습니다.".format(teamName))
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
    if taskList["devl"] == None:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("{} 팀에 태스크가 존재하지 않습니다.".format(teamName))
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
    
    self.ui.final_task_comboBox.addItems([""] + taskList["devl"])

def setExtFunc(self):
    '''
    확장자 콤보박스를 세팅하는 함수
    '''
    self.ui.final_ext_comboBox.clear()
    self.ui.final_shotgunmov_checkBox.setChecked(False)
    self.ui.final_version_comboBox.clear()

    projectName = self.ui.final_project_comboBox.currentText()
    seqName = self.ui.final_sequence_comboBox.currentText()
    shotName = self.ui.final_shot_comboBox.currentText()
    teamName = "comp"

    if self.ui.final_task_comboBox.currentText() == "":
        return
    
    taskName = self.ui.final_task_comboBox.currentText()

    path = os.path.join(SHOW_PATH, projectName, "shot", seqName, shotName, teamName, "devl", taskName, "render")
    if os.path.exists(path):
        if not os.listdir(path):
            dial = QtWidgets.QMessageBox()
            dial.setWindowTitle("Error")
            dial.setText("render 폴더가 비어있습니다.")
            ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
            dial.exec_()
            return
        
        ext = os.listdir(path)
        ext.sort()
        extList = []
        for e in ext:
            # 숨겨져 있는지 확인
            if e.startswith("."):
                continue

            # 폴더인지 확인
            if os.path.isdir(os.path.join(path, e)):
                # 프로젝트 예외
                if projectName == "au" and e == "mov": # au 프로젝트에서 mov 폴더를 선택할 경우
                    if os.listdir(os.path.join(path, e)):
                        aumov = os.listdir(os.path.join(path, e))
                        aumov.sort()
                        for am in aumov:
                            # 숨겨져 있는지 확인
                            if am.startswith("."):
                                continue

                            # 폴더인지 확인
                            if os.path.isdir(os.path.join(path, e, am)):
                                ame = "{}/{}".format(e, am)
                                extList.append(ame)
                else:
                    extList.append(e)
            else:
                if e.split(".")[-1] == "mov":
                    extList.append("mov")
        
        extList = list(set(extList))
        self.ui.final_ext_comboBox.addItems([""] + extList)
    else:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("render 폴더가 존재하지 않습니다.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return

def setVerFunc(self):
    '''
    버전 콤보박스를 세팅하는 함수
    '''
    self.ui.final_version_comboBox.clear()
    
    projectName = self.ui.final_project_comboBox.currentText()
    seqName = self.ui.final_sequence_comboBox.currentText()
    shotName = self.ui.final_shot_comboBox.currentText()
    teamName = "comp"
    taskName = self.ui.final_task_comboBox.currentText()
    if self.ui.final_shotgunmov_checkBox.isChecked():
        self.ui.final_confirm_radioButton.setChecked(True)
    else:
        self.ui.final_final_radioButton.setChecked(True)

    if self.ui.final_ext_comboBox.currentText() == "":
        return
    
    extName = self.ui.final_ext_comboBox.currentText()
    path = os.path.join(SHOW_PATH, projectName, "shot", seqName, shotName, teamName, "devl", taskName, "render", extName)
    if os.path.exists(path):
        if not os.listdir(path):
            dial = QtWidgets.QMessageBox()
            dial.setWindowTitle("Error")
            dial.setText("{} 확장자 폴더가 비어있습니다.".format(extName))
            ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
            dial.exec_()
            return
        
        if extName.startswith("mov"):
            if self.ui.final_shotgunmov_checkBox.isChecked():
                if extName != "mov":
                    self.ui.final_shotgunmov_checkBox.setChecked(False)
                dpath = os.path.dirname(path)
                movver = os.listdir(dpath)
                movver.sort()

                movverList = []
                for mv in movver:
                    # 숨겨져 있는지 확인
                    if mv.startswith("."):
                        continue

                    # 폴더인지 확인
                    if os.path.isdir(os.path.join(dpath, mv)):
                        continue

                    movverList.append(mv)
                
                self.ui.final_version_comboBox.addItems([""] + movverList)

            else:
                movver = os.listdir(path)
                movver.sort()

                movverList = []
                for mv in movver:
                    # 숨겨져 있는지 확인
                    if mv.startswith("."):
                        continue

                    # 폴더인지 확인
                    if os.path.isdir(os.path.join(path, mv)):
                        continue

                    movverList.append(mv)
                
                self.ui.final_version_comboBox.addItems([""] + movverList)

        else:
            if not self.ui.final_shotgunmov_checkBox.isChecked():
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

                self.ui.final_version_comboBox.addItems([""] + verList)
            else:
                self.ui.final_shotgunmov_checkBox.setChecked(False)

    else:
        if extName == "mov" and self.ui.final_shotgunmov_checkBox.isChecked(): # mov 폴더는 존재하지 않고 샷건용 mov만 존재하는 경우
            dpath = os.path.dirname(path)
            movver = os.listdir(dpath)
            movver.sort()

            movverList = []
            for mv in movver:
                # 숨겨져 있는지 확인
                if mv.startswith("."):
                    continue

                # 폴더인지 확인
                if os.path.isdir(os.path.join(dpath, mv)):
                    continue

                movverList.append(mv)
                
            self.ui.final_version_comboBox.addItems([""] + movverList)
        else:
            dial = QtWidgets.QMessageBox()
            dial.setWindowTitle("Error")
            dial.setText("render 폴더에 {} 확장자 폴더가 존재하지 않습니다.".format(extName))
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
    self.ui.final_ccGroup_pushButton.setEnabled(False)
    self.ui.final_ccPerson_pushButton.setEnabled(False)

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
    self.ui.final_ccGroup_pushButton.setEnabled(False)
    self.ui.final_ccPerson_pushButton.setEnabled(False)

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
    self.ui.final_ccGroup_lineEdit.setText(ccText)
    self.ui.final_ccGroup_pushButton.setEnabled(True)
    self.ui.final_ccPerson_pushButton.setEnabled(True)

def addCCPersonWidget(self, ccList, widget):
    '''
    선택된 CC(그룹)를 Add 하는 함수
    '''
    ccText = ""
    for cc in ccList.selectedItems():
        ccText += cc.text() + " "

    widget.close()
    self.ui.final_ccPerson_lineEdit.setText(ccText)
    self.ui.final_ccGroup_pushButton.setEnabled(True)
    self.ui.final_ccPerson_pushButton.setEnabled(True)

def cancelCCWidget(self, widget):
    '''
    CC 위젯을 닫는 함수
    '''
    widget.close()
    self.ui.final_ccGroup_pushButton.setEnabled(True)
    self.ui.final_ccPerson_pushButton.setEnabled(True)

def setPublishTableFunc(self):
    '''
    Setting 값들을 설정한 후에 Add 버튼을 눌렀을 때, Publish Data Table에
    해당 버전의 정보가 저장되는 함수이다.
    '''
    if self.ui.final_project_comboBox.currentText() == "":
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText(u"프로젝트를 선택해주세요.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return

    if self.ui.final_sequence_comboBox.currentText() == "":
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText(u"시퀀스를 선택해주세요.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return

    if self.ui.final_shot_comboBox.currentText() == "":
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText(u"샷을 선택해주세요.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return 

    if self.ui.final_task_comboBox.currentText() == "":
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText(u"태스크를 선택해주세요.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
    
    if self.ui.final_ext_comboBox.currentText() == "":
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText(u"확장자를 선택해주세요.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
    
    if self.ui.final_version_comboBox.currentText() == "":
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText(u"버전명을 선택해주세요.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return

    projectName = self.ui.final_project_comboBox.currentText()
    seqName = self.ui.final_sequence_comboBox.currentText()
    shotName = self.ui.final_shot_comboBox.currentText()
    teamName = "comp"
    taskName = self.ui.final_task_comboBox.currentText()
    extName = self.ui.final_ext_comboBox.currentText()
    verName = self.ui.final_version_comboBox.currentText()
    ccGroup = self.ui.final_ccGroup_lineEdit.text()
    ccPerson = self.ui.final_ccPerson_lineEdit.text()
    devlPath = os.path.join(SHOW_PATH, projectName, "shot", seqName, shotName, teamName, "devl", taskName)
    version = os.path.splitext(verName)[0].split('_')[-1]
    pubPath = os.path.join(SHOW_PATH, projectName, "shot", seqName, shotName, teamName, "pub", taskName)
    nukePath = os.path.join(devlPath, "nuke")
    nukeFileName = os.path.splitext(verName)[0] + ".nk"

    if self.ui.final_shotgunmov_checkBox.isChecked():
        inputPath = os.path.join(devlPath, "render", verName)
        outputPath = os.path.join(pubPath, version, "render", verName)

    else: # 프로젝트별 예외처리
        inputPath = os.path.join(devlPath, "render", extName, verName)
        outputPath = os.path.join(pubPath, version, "render", extName, verName)
        
        if projectName == "chu" and extName == "mov": # CHU 프로젝트
            fileName = re.findall("[a-z0-9]+_([A-Z]+\d{2}_[A-Z]\d{3}_\d{4})_[a-z0-9_]+_v\d{3}", os.path.splitext(nukeFileName)[0])
            fileName = fileName[0]
            epnum = fileName.split("_")[0] # EX01 or EP01
            seqnum = fileName.split("_")[1] # S001
            shotnum = fileName.split("_")[2] # 0040  -> EP: s0101_c0040 EX: s9101_c0040
            if epnum.startswith("EX"):
                newFileName = "s{}{}_c{}".format("9"+epnum[-1], seqnum[2:], shotnum)
            else:
                newFileName = "s{}{}_c{}".format(epnum[2:], seqnum[2:], shotnum)
            nukeFileName = nukeFileName.replace(fileName, newFileName)
            verName = verName.replace(fileName, newFileName)

        elif projectName == "au": # AU 프로젝트
            if not re.match("[a-z0-9]+_[st]\d{4}_c[a-z0-9]+_[a-z0-9_]+_v\d{3}", os.path.splitext(nukeFileName)[0]):
                # 파이널 샷 코드 --> RD101 샷 코드(json 파일에 정리된 샷 코드 기반)
                if projectName not in projectInfo:
                    dial = QtWidgets.QMessageBox()
                    dial.setWindowTitle("Error")
                    dial.setText(u"{} 프로젝트 세팅값이 존재하지 않아 RD101 샷 코드로 변환할 수 없습니다.".format(projectName))
                    ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
                    dial.exec_()
                    return
                auProInfo = projectInfo[projectName]
                if "publishCode" not in auProInfo:
                    dial = QtWidgets.QMessageBox()
                    dial.setWindowTitle("Error")
                    dial.setText(u"{} 프로젝트의 publishCode 세팅값이 존재하지 않아 RD101 샷 코드로 변환할 수 없습니다.".format(projectName))
                    ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
                    dial.exec_()
                    return
                auFinalCode = re.findall("(AU_\d{3}_\d{3}_\d{4})_[a-z0-9_]+_v\d{3}", os.path.splitext(nukeFileName)[0])
                if auFinalCode[0] not in auProInfo["publishCode"]:
                    dial = QtWidgets.QMessageBox()
                    dial.setWindowTitle("Error")
                    dial.setText(u"{} 프로젝트의 {}에 해당하는 파이널 샷 코드가 존재하지 않아 RD101 샷 코드로 변환할 수 없습니다.".format(projectName, auFinalCode[0]))
                    ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
                    dial.exec_()
                    return
                auRD101Code = "{}_{}".format(projectName, auProInfo["publishCode"][auFinalCode[0]])
                nukeFileName = nukeFileName.replace(auFinalCode[0], auRD101Code)
                verName = verName.replace(auFinalCode[0], auRD101Code)

    if os.path.exists(nukePath):
        if not os.listdir(nukePath):
            dial = QtWidgets.QMessageBox()
            dial.setWindowTitle("Error")
            dial.setText("nuke 폴더가 비어있습니다.")
            ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
            dial.exec_()
            return
        
        nukeFiles = os.listdir(nukePath)
        if nukeFileName in nukeFiles:
            nukeFilePath = os.path.join(nukePath, nukeFileName)
            with open(nukeFilePath, 'r') as f:
                contexts = f.read()
            root = re.findall("Root {([\n\)\(\" a-zA-Z0-9.\-/\_#%]+)", contexts)[0]

            if not re.findall("first_frame ([\d]+)", root):
                # asb 프로젝트 같은 경우 first_frame이 따로 지정되어있지 않는 경우도 있다
                first_frame = "1"

            else:
                first_frame = re.findall("first_frame ([\d]+)", root)[0]
                
            # first_frame 과 달리 last_frame은 지정되어 있다.
            if not re.findall("last_frame ([\d]+)", root):
                last_frame = "1"
            else:
                last_frame = re.findall("last_frame ([\d]+)", root)[0]
            frame_range = "{}-{}".format(first_frame, last_frame)
            duration = str(int(last_frame) - int(first_frame) + 1)

            # 프로젝트 resolution 설정
            if not projectName in setting:
                dial = QtWidgets.QMessageBox()
                dial.setWindowTitle("Error")
                dial.setText("nuke 폴더안의 setting.json 파일에서 {}프로젝트 세팅을 확인해주세요.".format(projectName))
                ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
                dial.exec_()
                return

            else:
                value = setting[projectName]
                # 납품용으로 PUB을 하는 경우
                if self.ui.final_final_radioButton.isChecked():
                    if "outputSize" in value:
                        resolution = "{}x{}".format(value["outputSize"].split()[0], value["outputSize"].split()[1])
                    else:
                        outputSize = re.findall("[^_]format \"([\d]+ [\d]+) ", root)[0]
                        resolution = "{}x{}".format(outputSize.split()[0], outputSize.split()[1])

                # 컨펌용으로 PUB을 하는 경우
                else:
                    value = setting[projectName]
                    if "confirmSize" in value:
                        resolution = "{}x{}".format(value["confirmSize"].split()[0], value["confirmSize"].split()[1])
                    else:
                        resolution = "1920x1080"

        else:
            dial = QtWidgets.QMessageBox()
            dial.setWindowTitle("Error")
            dial.setText("nuke 폴더 안에 {} 파일이 존재하지 않습니다.".format(nukeFileName))
            ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
            dial.exec_()
            return

    else:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("nuke 폴더가 존재하지 않습니다.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return

    # publish table에 이미 같은 파일이 있다면 에러처리
    tableRow = self.ui.final_publish_tableWidget.rowCount()
    tableColumn = self.ui.final_publish_tableWidget.columnCount()
    for r in range(tableRow):
        # InputPath가 일치하는지 확인
        if inputPath == self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["InputPath"]).text():
            dial = QtWidgets.QMessageBox()
            dial.setWindowTitle("Error")
            dial.setText("테이블에 이미 같은 파일이 존재합니다.")
            ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
            dial.exec_()
            return

    verName = os.path.splitext(verName)[0]
    note = self.ui.final_note_textEdit.toPlainText()
    tableData = [projectName, seqName, shotName, taskName, verName, extName, inputPath, outputPath, frame_range, duration, resolution, note, ccGroup, ccPerson]
    self.ui.final_publish_tableWidget.insertRow(tableRow)
    for j in range(tableColumn):
        item = QtWidgets.QTableWidgetItem(tableData[j])
        item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self.ui.final_publish_tableWidget.setItem(tableRow, j, item)

    self.ui.final_publish_tableWidget.resizeColumnsToContents()
    self.ui.final_publish_tableWidget.resizeRowsToContents()
    
    initUIFunc(self)

def minusPublishTableFunc(self):
    '''
    [-] 버튼을 눌렀을 때 테이블에서 현재 선택하고 있는 정보를 제거하는 함수이다.
    '''
    if self.ui.final_publish_tableWidget.rowCount() == 0:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("테이블에 제거할 데이터가 존재하지 않습니다.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
    
    if not self.ui.final_publish_tableWidget.selectedItems():
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("제거할 데이터를 선택해주세요.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
        
    tableRow = self.ui.final_publish_tableWidget.currentRow()
    self.ui.final_publish_tableWidget.removeRow(tableRow)