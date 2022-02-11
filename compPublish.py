# _*_ coding: utf-8 _*_

# Comp Publish Tool
#
# Description : publish button을 눌렀을 때, 테이블에 있는 파일들을 Pub 하는 스크립트

import os
import sys
import shutil
from distutils.dir_util import copy_tree

from PySide2 import QtWidgets, QtGui, QtCore

TD_PATH = os.getenv("TD_PATH")

if "{}/api" not in sys.path:
    sys.path.append('{}/api'.format(TD_PATH))

import shotgun_api3

sg = shotgun_api3.Shotgun("https://road101.shotgunstudio.com", script_name="authentication_script", api_key="vZnk#jbmopl6oqispvodazfyn")

def finalPublishFunc(self):
    '''
    final publish 하는 함수
    '''
    self.ui.final_publog_textEdit.clear()
    tableRow = self.ui.final_publish_tableWidget.rowCount()
    status = self.ui.final_status_comboBox.currentText()
    artistName = self.ui.final_user_lineEdit.text()
    person = sg.find_one('HumanUser', [['login', 'is', artistName]])

    if tableRow == 0:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("Publish할 데이터가 존재하지 않습니다.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
    
    for r in range(tableRow):
        color = QtGui.QColor(255, 255, 255, 0)
        self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["Ver"]).setBackground(color)

        # publish_table에 저장된 정보
        projectName = self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["Project"]).text()
        seqName = self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["Seq"]).text()
        shotName = self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["Shot"]).text()
        shotCode = "{}_{}".format(seqName, shotName)
        taskName = self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["Task"]).text()
        verName = self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["Ver"]).text()
        ccGroup = self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["CC_Group"]).text()
        ccPerson = self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["CC_Person"]).text()

        # publish_table에 저장된 정보를 기반으로 가져오는 Shotgun 정보
        project_dict = sg.find_one('Project', [['name', 'is', projectName]])
        shot_dict = sg.find_one('Shot', [['project', 'is', project_dict], ['code', 'is', shotCode]])
        task_dict = sg.find_one('Task', [['project', 'is', project_dict], ['entity', 'is', shot_dict], ['content', 'is', taskName]])
        version_dict = sg.find_one('Version', [['project', 'is', project_dict], ['entity', 'is', shot_dict], ['sg_task', 'is', task_dict], ['code', 'is', verName], ['sg_status_list', 'is', status]], ['user'])

        if not version_dict:
            message = "{} 프로젝트에 {} 상태의 {} 버전이 Shotgun에 존재하지 않습니다.".format(projectName, status, verName)
            color = QtGui.QColor(255, 0, 0, 255)
            self.ui.final_publog_textEdit.setTextColor(color)
            self.ui.final_publog_textEdit.append(message)
            self.ui.final_publog_textEdit.repaint() # real time update final_publog_textEdit
            color = QtGui.QColor(255, 0, 0, 125)
            self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["Ver"]).setBackground(color)
            continue

        else:
            message = "{} 프로젝트에 {} 상태의 {} 버전을 publish합니다...".format(projectName, status, verName)
            color = QtGui.QColor(0, 0, 0, 255)
            self.ui.final_publog_textEdit.setTextColor(color)
            self.ui.final_publog_textEdit.append(message)
            self.ui.final_publog_textEdit.repaint() # real time update final_publog_textEdit

            inputPath = self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["InputPath"]).text()
            outputPath = self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["OutputPath"]).text()
            outputDirPath = os.path.dirname(outputPath)

            message = "{} 프로젝트에 {} 상태의 {} 버전을 Pub 폴더에 복사 준비중입니다...".format(projectName, status, verName)
            self.ui.final_publog_textEdit.append(message)
            self.ui.final_publog_textEdit.repaint() # real time update final_publog_textEdit

            # 디렉토리 경로가 없다면 경로에 맞게 디렉토리를 생성해준다
            if not os.path.isdir(outputDirPath):
                os.makedirs(outputDirPath)

            # mov는 파일을 복사하고 다른 것들은 폴더를 복사하기 때문에 경우를 나눠준다.
            if self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["Ext"]).text().startswith("mov"):
                shutil.copy(inputPath, outputDirPath)
            else:
                copy_tree(inputPath, outputPath) # shutil.copy_tree를 쓸 경우 경로가 이미 있으며 에러가 난다.
            
            message = "{} 프로젝트에 {} 상태의 {} 버전을 Pub 폴더에 복사 완료했습니다...".format(projectName, status, verName)
            self.ui.final_publog_textEdit.append(message)
            self.ui.final_publog_textEdit.repaint() # real time update final_publog_textEdit

            # shotgun에서 해당 version의 status를 update 한다.
            if status == "CT":
                sgStatus = "ctp"
            else:
                sgStatus = "dps"

            sg.update('Task', task_dict['id'], {'sg_status_list': sgStatus})
            sg.update('Version', version_dict['id'], {'sg_status_list': sgStatus})

            message = "{} 프로젝트에 {} 상태의 {} 버전을 {} 상태로 업데이트했습니다...".format(projectName, status, verName, sgStatus.upper())
            self.ui.final_publog_textEdit.append(message)
            self.ui.final_publog_textEdit.repaint() # real time update final_publog_textEdit

            # shotgun에서 해당 version에 note를 작성한다.
            subjectName = artistName + " Publish " + verName
            ver = verName.split("_")[-1]
            frameRange = self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["FrameRange"]).text()
            duration = self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["Duration"]).text()
            resolution = self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["Resolution"]).text()
            ext = self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["Ext"]).text()
            note = self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["Note"]).text()

            # note message 정리
            noteText = "[{}] {} {} Publish. ({})\n\n".format(projectName.upper(), shotCode, taskName, ver)
            noteText += "1. Frame Range : {}\n\n".format(frameRange)
            noteText += "2. Duration: {}\n\n".format(duration)
            noteText += "3. Resolution: {}\n\n".format(resolution)
            noteText += "4. Extension: {}\n\n".format(ext)
            noteText += u"5. Note: {}\n\n".format(note)
            noteText += "6. Publish Path\n"
            noteText += "Linux: {}\n".format(outputPath)
            outputWindowsPath = outputPath.replace("/", "\\")
            noteText += "Windows: \\{}\n".format(outputWindowsPath)

            if not ccGroup == "":
                ccGroupList = ccGroup.split()
                sgGroup = sg.find('Group', [['code', 'in', ccGroupList]])
            
            if not ccPerson == "":
                ccPersonList = ccPerson.split()
                loginList = []
                for p in ccPersonList:
                    loginList.append(p.split("(")[1].split(")")[0])
                sgPerson = sg.find('HumanUser', [['login', 'in', loginList]])
            
            toPerson = sg.find_one('HumanUser', [['id', 'is', version_dict['user']['id']]])
            if not ccGroup == "" and not ccPerson == "":
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson], 'addressings_cc': sgGroup + sgPerson})
            elif not ccGroup == "" and ccPerson == "":
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson],'addressings_cc': sgGroup})
            elif ccGroup == "" and not ccPerson == "":
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson],'addressings_cc': sgPerson})
            else:
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson]})

            message = "{} 프로젝트에 {} 상태의 {} 버전에 노트를 작성했습니다...".format(projectName, status, verName)
            self.ui.final_publog_textEdit.append(message)
            self.ui.final_publog_textEdit.repaint() # real time update final_publog_textEdit

            message = "{} 프로젝트에 {} 상태의 {} 버전 Publish 완료했습니다...".format(projectName, status, verName)
            self.ui.final_publog_textEdit.append(message)
            self.ui.final_publog_textEdit.repaint() # real time update final_publog_textEdit

            color = QtGui.QColor(0, 255, 0, 125)
            self.ui.final_publish_tableWidget.item(r, self.final_column_idx_lookup["Ver"]).setBackground(color)

def teamPublishFunc(self):
    '''
    team publish 하는 함수
    '''
    self.ui.team_publog_textEdit.clear()
    tableRow = self.ui.team_publish_tableWidget.rowCount()
    pubTeam = self.ui.team_pubTeam_comboBox.currentText() # publish 하려는 팀
    pubFile = self.ui.team_pubFile_comboBox.currentText() # publish 하려는 파일
    artistName = self.ui.team_user_lineEdit.text()
    person = sg.find_one('HumanUser', [['login', 'is', artistName]])

    if tableRow == 0:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("Publish할 데이터가 존재하지 않습니다.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
    
    for r in range(tableRow):
        color = QtGui.QColor(255, 255, 255, 0)
        self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["Ver"]).setBackground(color)

        # publish_table에 저장된 정보
        projectName = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["Project"]).text()
        seqName = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["Seq"]).text()
        shotName = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["Shot"]).text()
        shotCode = "{}_{}".format(seqName, shotName)
        taskName = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["Task"]).text()
        verName = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["Ver"]).text()
        ccGroup = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["CC_Group"]).text()
        ccPerson = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["CC_Person"]).text()

        # publish_table에 저장된 정보를 기반으로 가져오는 Shotgun 정보
        project_dict = sg.find_one('Project', [['name', 'is', projectName]])
        shot_dict = sg.find_one('Shot', [['project', 'is', project_dict], ['code', 'is', shotCode]])
        task_dict = sg.find_one('Task', [['project', 'is', project_dict], ['entity', 'is', shot_dict], ['content', 'is', taskName]])
        version_dict = sg.find_one('Version', [['project', 'is', project_dict], ['entity', 'is', shot_dict], ['sg_task', 'is', task_dict], ['code', 'is', verName]], ['user'])

        if not version_dict:
            message = "{} 프로젝트에 {} 버전이 Shotgun에 존재하지 않습니다.".format(projectName, verName)
            color = QtGui.QColor(255, 0, 0, 255)
            self.ui.team_publog_textEdit.setTextColor(color)
            self.ui.team_publog_textEdit.append(message)
            self.ui.team_publog_textEdit.repaint() # real time update team_publog_textEdit
            color = QtGui.QColor(255, 0, 0, 125)
            self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["Ver"]).setBackground(color)
            continue

        else:
            message = "{} 프로젝트에 {} 버전을 {} 팀으로 publish합니다...".format(projectName, verName, pubTeam)
            color = QtGui.QColor(0, 0, 0, 255)
            self.ui.team_publog_textEdit.setTextColor(color)
            self.ui.team_publog_textEdit.append(message)
            self.ui.team_publog_textEdit.repaint() # real time update team_publog_textEdit

            # publish 하려는 파일에 맞게 경로 설정
            if pubFile == "Only Nuke":
                pubNukePath = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["PubNukePath"]).text()
                devlNukePath = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["DevlNukePath"]).text()
                
                pubNukeDirPath = os.path.dirname(pubNukePath)

                message = "{} 프로젝트에 {} 버전을 Pub 폴더에 복사 준비중입니다...".format(projectName, verName)
                self.ui.team_publog_textEdit.append(message)
                self.ui.team_publog_textEdit.repaint() # real time update team_publog_textEdit

                # 디렉토리 경로가 없다면 경로에 맞게 디렉토리를 생성해준다.
                if not os.path.isdir(pubNukeDirPath):
                    os.makedirs(pubNukeDirPath)
                
                # nuke 파일을 pub 경로에 복사한다.
                shutil.copy(devlNukePath, pubNukePath)

            elif pubFile == "Only Render":
                pubRenderPath = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["PubRenderPath"]).text()
                devlRenderPath = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["DevlRenderPath"]).text()

                pubRenderDirPath = os.path.dirname(pubRenderPath)

                message = "{} 프로젝트에 {} 버전을 Pub 폴더에 복사 준비중입니다...".format(projectName, verName)
                self.ui.team_publog_textEdit.append(message)
                self.ui.team_publog_textEdit.repaint() # real time update team_publog_textEdit

                # 디렉토리 경로가 없다면 경로에 맞게 디렉토리를 생성해준다
                if not os.path.isdir(pubRenderDirPath):
                    os.makedirs(pubRenderDirPath)
                    
                # Render 폴더를 pub 경로에 복사한다.
                if self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["Ext"]).text().startswith("mov"):
                    shutil.copy(devlRenderPath, pubRenderPath)
                else:
                    copy_tree(devlRenderPath, pubRenderPath) # shutil.copy_tree를 쓸 경우 경로가 이미 있으며 에러가 난다.

            else:
                pubNukePath = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["PubNukePath"]).text()
                devlNukePath = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["DevlNukePath"]).text()
                pubRenderPath = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["PubRenderPath"]).text()
                devlRenderPath = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["DevlRenderPath"]).text()

                pubNukeDirPath = os.path.dirname(pubNukePath)
                pubRenderDirPath = os.path.dirname(pubRenderPath)

                message = "{} 프로젝트에 {} 버전을 Pub 폴더에 복사 준비중입니다...".format(projectName, verName)
                self.ui.team_publog_textEdit.append(message)
                self.ui.team_publog_textEdit.repaint() # real time update team_publog_textEdit

                # 디렉토리 경로가 없다면 경로에 맞게 디렉토리를 생성해준다.
                if not os.path.isdir(pubNukeDirPath):
                    os.makedirs(pubNukeDirPath)

                # 디렉토리 경로가 없다면 경로에 맞게 디렉토리를 생성해준다
                if not os.path.isdir(pubRenderDirPath):
                    os.makedirs(pubRenderDirPath)
                
                # nuke 파일과 Render 폴더를 pub 경로에 복사한다.
                shutil.copy(devlNukePath, pubNukePath)

                # Render 폴더를 pub 경로에 복사한다.
                if self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["Ext"]).text().startswith("mov"):
                    shutil.copy(devlRenderPath, pubRenderPath)
                else:
                    copy_tree(devlRenderPath, pubRenderPath) # shutil.copy_tree를 쓸 경우 경로가 이미 있으며 에러가 난다.  
                      
            message = "{} 프로젝트에 {} 버전을 Pub 폴더에 복사 완료했습니다...".format(projectName, verName)
            self.ui.team_publog_textEdit.append(message)
            self.ui.team_publog_textEdit.repaint() # real time update team_publog_textEdit

            # shotgun에 task, version status 변경
            sgStatus = "ps"

            sg.update('Task', task_dict['id'], {'sg_status_list': sgStatus})
            sg.update('Version', version_dict['id'], {'sg_status_list': sgStatus})

            message = "{} 프로젝트에 {} 버전을 {} 상태로 업데이트했습니다...".format(projectName, verName, sgStatus.upper())
            self.ui.team_publog_textEdit.append(message)
            self.ui.team_publog_textEdit.repaint() # real time update team_publog_textEdit

            # shotgun에서 해당 version에 note를 작성한다.
            subjectName = artistName + " Publish " + verName
            ver = verName.split("_")[-1]
            frameRange = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["FrameRange"]).text()
            duration = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["Duration"]).text()
            resolution = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["Resolution"]).text()
            ext = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["Ext"]).text()
            note = self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["Note"]).text()

            # note message 정리
            noteText = u"[검수팀: {} ({})]\n\n".format(pubTeam, pubFile)
            noteText += "[{}] {} {} Publish. ({})\n\n".format(projectName.upper(), shotCode, taskName, ver)
            noteText += "1. Frame Range : {}\n\n".format(frameRange)
            noteText += "2. Duration: {}\n\n".format(duration)
            noteText += "3. Resolution: {}\n\n".format(resolution)
            noteText += "4. Extension: {}\n\n".format(ext)
            noteText += u"5. Note: {}\n\n".format(note)
            noteText += "6. Publish Path\n"

            if pubFile == "Only Nuke":
                noteText += "NukePath(Linux): {}\n".format(pubNukePath)
                pubNukeWindowsPath = pubNukePath.replace("/","\\")
                noteText += u"NukePath(Windows): \\{}\n".format(pubNukeWindowsPath)

            elif pubFile == "Only Render":
                noteText += "RenderPath(Linux): {}\n".format(pubRenderPath)
                pubRenderWindowsPath = pubRenderPath.replace("/", "\\")
                noteText += u"RenderPath(Windows): \\{}\n".format(pubRenderWindowsPath)

            else:
                noteText += "NukePath(Linux): {}\n".format(pubNukePath)
                pubNukeWindowsPath = pubNukePath.replace("/","\\")
                noteText += u"NukePath(Windows): \\{}\n\n".format(pubNukeWindowsPath)

                noteText += "\tRenderPath(Linux): {}\n".format(pubRenderPath)
                pubRenderWindowsPath = pubRenderPath.replace("/", "\\")
                noteText += u"RenderPath(Windows): \\{}\n".format(pubRenderWindowsPath)

            if not ccGroup == "":
                ccGroupList = ccGroup.split()
                sgGroup = sg.find('Group', [['code', 'in', ccGroupList]])
            
            if not ccPerson == "":
                ccPersonList = ccPerson.split()
                loginList = []
                for p in ccPersonList:
                    loginList.append(p.split("(")[1].split(")")[0])
                sgPerson = sg.find('HumanUser', [['login', 'in', loginList]])
            
            toPerson = sg.find_one('HumanUser', [['id', 'is', version_dict['user']['id']]])
            if not ccGroup == "" and not ccPerson == "":
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson], 'addressings_cc': sgGroup + sgPerson})
            
            elif not ccGroup == "" and ccPerson == "":
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson],'addressings_cc': sgGroup})
            
            elif ccGroup == "" and not ccPerson == "":
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson],'addressings_cc': sgPerson})
            
            else:
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson]})

            message = "{} 프로젝트에 {} 버전에 노트를 작성했습니다...".format(projectName, verName)
            self.ui.team_publog_textEdit.append(message)
            self.ui.team_publog_textEdit.repaint() # real time update team_publog_textEdit

            message = "{} 프로젝트에 {} 버전 Publish 완료했습니다...".format(projectName, verName)
            self.ui.team_publog_textEdit.append(message)
            self.ui.team_publog_textEdit.repaint() # real time update team_publog_textEdit

            color = QtGui.QColor(0, 255, 0, 125)
            self.ui.team_publish_tableWidget.item(r, self.team_column_idx_lookup["Ver"]).setBackground(color)

def collectPublishFunc(self):
    '''
    collect publish 하는 함수
    '''
    self.ui.collect_publog_textEdit.clear()
    tableRow = self.ui.collect_publish_tableWidget.rowCount()
    artistName = self.ui.collect_user_lineEdit.text()
    person = sg.find_one('HumanUser', [['login', 'is', artistName]])

    if tableRow == 0:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("Publish할 데이터가 존재하지 않습니다.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return

    for r in range(tableRow):
        color = QtGui.QColor(255, 255, 255, 0)
        self.ui.collect_publish_tableWidget.item(r, self.collect_column_idx_lookup["Ver"]).setBackground(color)

        # publish_table에 저장된 정보
        projectName = self.ui.collect_publish_tableWidget.item(r, self.collect_column_idx_lookup["Project"]).text()
        seqName = self.ui.collect_publish_tableWidget.item(r, self.collect_column_idx_lookup["Seq"]).text()
        shotName = self.ui.collect_publish_tableWidget.item(r, self.collect_column_idx_lookup["Shot"]).text()
        shotCode = "{}_{}".format(seqName, shotName)
        taskName = self.ui.collect_publish_tableWidget.item(r, self.collect_column_idx_lookup["Task"]).text()
        verName = self.ui.collect_publish_tableWidget.item(r, self.collect_column_idx_lookup["Ver"]).text()
        ccGroup = self.ui.collect_publish_tableWidget.item(r, self.collect_column_idx_lookup["CC_Group"]).text()
        ccPerson = self.ui.collect_publish_tableWidget.item(r, self.collect_column_idx_lookup["CC_Person"]).text()

        # publish_table에 저장된 정보를 기반으로 가져오는 Shotgun 정보
        project_dict = sg.find_one('Project', [['name', 'is', projectName]])
        shot_dict = sg.find_one('Shot', [['project', 'is', project_dict], ['code', 'is', shotCode]])
        task_dict = sg.find_one('Task', [['project', 'is', project_dict], ['entity', 'is', shot_dict], ['content', 'is', taskName]])
        version_dict = sg.find_one('Version', [['project', 'is', project_dict], ['entity', 'is', shot_dict], ['sg_task', 'is', task_dict], ['code', 'is', verName]], ['user'])

        if not version_dict:
            message = "{} 프로젝트에 {} 버전이 Shotgun에 존재하지 않습니다.".format(projectName, verName)
            color = QtGui.QColor(255, 0, 0, 255)
            self.ui.collect_publog_textEdit.setTextColor(color)
            self.ui.collect_publog_textEdit.append(message)
            self.ui.collect_publog_textEdit.repaint() # real time update collect_publog_textEdit
            color = QtGui.QColor(255, 0, 0, 125)
            self.ui.collect_publish_tableWidget.item(r, self.collect_column_idx_lookup["Ver"]).setBackground(color)
            continue

        else:
            message = "{} 프로젝트에 {} 버전을 publish합니다...".format(projectName, verName)
            color = QtGui.QColor(0, 0, 0, 255)
            self.ui.collect_publog_textEdit.setTextColor(color)
            self.ui.collect_publog_textEdit.append(message)
            self.ui.collect_publog_textEdit.repaint() # real time update collect_publog_textEdit

            pubCollectPath = self.ui.collect_publish_tableWidget.item(r, self.collect_column_idx_lookup["PubCollectPath"]).text()

            # shotgun에서 해당 version의 status를 update 한다.
            sgStatus = "ps"

            sg.update('Task', task_dict['id'], {'sg_status_list': sgStatus})
            sg.update('Version', version_dict['id'], {'sg_status_list': sgStatus})

            message = "{} 프로젝트에 {} 버전을 {} 상태로 업데이트했습니다...".format(projectName, verName, sgStatus.upper())
            self.ui.collect_publog_textEdit.append(message)
            self.ui.collect_publog_textEdit.repaint() # real time update collect_publog_textEdit

            # shotgun에서 해당 version에 note를 작성한다.
            subjectName = artistName + " Publish " + verName
            ver = verName.split("_")[-1]
            note = self.ui.collect_publish_tableWidget.item(r, self.collect_column_idx_lookup["Note"]).text()

            # note message 정리
            noteText = u"[검수팀: PD팀]\n\n"
            noteText += "[{}] {} {} Publish. ({})\n\n".format(projectName.upper(), shotCode, taskName, ver)
            noteText += u"1. Note: {}\n\n".format(note)
            noteText += "2. Publish Path\n"
            noteText += "Linux: {}\n".format(pubCollectPath)
            outputWindowsPath = pubCollectPath.replace("/", "\\")
            noteText += "Windows: \\{}\n".format(outputWindowsPath)

            if not ccGroup == "":
                ccGroupList = ccGroup.split()
                sgGroup = sg.find('Group', [['code', 'in', ccGroupList]])
            
            if not ccPerson == "":
                ccPersonList = ccPerson.split()
                loginList = []
                for p in ccPersonList:
                    loginList.append(p.split("(")[1].split(")")[0])
                sgPerson = sg.find('HumanUser', [['login', 'in', loginList]])
            
            toPerson = sg.find_one('HumanUser', [['id', 'is', version_dict['user']['id']]])
            if not ccGroup == "" and not ccPerson == "":
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson], 'addressings_cc': sgGroup + sgPerson})
            elif not ccGroup == "" and ccPerson == "":
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson],'addressings_cc': sgGroup})
            elif ccGroup == "" and not ccPerson == "":
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson],'addressings_cc': sgPerson})
            else:
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson]})

            message = "{} 프로젝트에 {} 버전에 노트를 작성했습니다...".format(projectName, verName)
            self.ui.collect_publog_textEdit.append(message)
            self.ui.collect_publog_textEdit.repaint() # real time update collect_publog_textEdit

            message = "{} 프로젝트에 {} 버전을 Publish 완료했습니다...".format(projectName, verName)
            self.ui.collect_publog_textEdit.append(message)
            self.ui.collect_publog_textEdit.repaint() # real time update collect_publog_textEdit

            color = QtGui.QColor(0, 255, 0, 125)
            self.ui.collect_publish_tableWidget.item(r, self.collect_column_idx_lookup["Ver"]).setBackground(color)

def retimePublishFunc(self):
    '''
    retime publish 하는 함수
    '''
    self.ui.retime_publog_textEdit.clear()
    tableRow = self.ui.retime_publish_tableWidget.rowCount()
    pubTeam = self.ui.retime_pubTeam_comboBox.currentText() # publish 하려는 팀
    artistName = self.ui.retime_user_lineEdit.text()
    person = sg.find_one('HumanUser', [['login', 'is', artistName]])

    if tableRow == 0:
        dial = QtWidgets.QMessageBox()
        dial.setWindowTitle("Error")
        dial.setText("Publish할 데이터가 존재하지 않습니다.")
        ok_btn = dial.addButton("OK", QtWidgets.QMessageBox.YesRole)
        dial.exec_()
        return
    
    for r in range(tableRow):
        color = QtGui.QColor(255, 255, 255, 0)
        self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["Ver"]).setBackground(color)
        QtCore.QCoreApplication.processEvents()

        # publish_table에 저장된 정보
        projectName = self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["Project"]).text()
        seqName = self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["Seq"]).text()
        shotName = self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["Shot"]).text()
        shotCode = "{}_{}".format(seqName, shotName)
        taskName = self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["Task"]).text()
        plateVerName = self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["PlateVer"]).text()
        verName = self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["Ver"]).text()
        platePath = self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["PlatePath"]).text()
        ccGroup = self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["CC_Group"]).text()
        ccPerson = self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["CC_Person"]).text()

        # publish_table에 저장된 정보를 기반으로 가져오는 Shotgun 정보
        project_dict = sg.find_one('Project', [['name', 'is', projectName]])
        shot_dict = sg.find_one('Shot', [['project', 'is', project_dict], ['code', 'is', shotCode]])
        task_dict = sg.find_one('Task', [['project', 'is', project_dict], ['entity', 'is', shot_dict], ['content', 'is', taskName]])
        version_dict = sg.find_one('Version', [['project', 'is', project_dict], ['entity', 'is', shot_dict], ['sg_task', 'is', task_dict], ['code', 'is', verName]], ['user'])

        if not version_dict:
            message = "{} 프로젝트에 {} 버전이 Shotgun에 존재하지 않습니다.".format(projectName, verName)
            color = QtGui.QColor(255, 0, 0, 255)
            self.ui.retime_publog_textEdit.setTextColor(color)
            self.ui.retime_publog_textEdit.append(message)
            color = QtGui.QColor(255, 0, 0, 125)
            self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["Ver"]).setBackground(color)
            QtCore.QCoreApplication.processEvents()
            continue

        else:
            message = "{} 프로젝트에 {} 버전을 {} 팀으로 publish합니다...".format(projectName, verName, pubTeam)
            color = QtGui.QColor(0, 0, 0, 255)
            self.ui.retime_publog_textEdit.setTextColor(color)
            self.ui.retime_publog_textEdit.append(message)
            QtCore.QCoreApplication.processEvents()

            # shotgun에 task, version status 변경
            sgStatus = "ps"

            sg.update('Task', task_dict['id'], {'sg_status_list': sgStatus})
            sg.update('Version', version_dict['id'], {'sg_status_list': sgStatus})

            message = "{} 프로젝트에 {} 버전을 {} 상태로 업데이트했습니다...".format(projectName, verName, sgStatus.upper())
            self.ui.retime_publog_textEdit.append(message)
            QtCore.QCoreApplication.processEvents()

            # shotgun에서 해당 version에 note를 작성한다.
            subjectName = artistName + " Publish " + verName
            ver = verName.split("_")[-1]
            frameRange = self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["FrameRange"]).text()
            duration = self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["Duration"]).text()
            resolution = self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["Resolution"]).text()
            note = self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["Note"]).text()

            # note message 정리
            noteText = u"[검수팀: {} ({})]\n\n".format(pubTeam, "Retime")
            noteText += "[{}] {} {} Publish. ({})\n\n".format(projectName.upper(), shotCode, taskName, ver)
            noteText += "1. Plate Version : {}\n\n".format(plateVerName)
            noteText += "2. Frame Range : {}\n\n".format(frameRange)
            noteText += "3. Duration: {}\n\n".format(duration)
            noteText += "4. Resolution: {}\n\n".format(resolution)
            noteText += u"5. Note: {}\n\n".format(note)
            noteText += "6. Publish Path\n"

            noteText += "PlatePath(Linux): {}\n".format(platePath)
            plateWindowsPath = platePath.replace("/", "\\")
            noteText += u"PlatePath(Windows): \\{}\n".format(plateWindowsPath)

            if not ccGroup == "":
                ccGroupList = ccGroup.split()
                sgGroup = sg.find('Group', [['code', 'in', ccGroupList]])
            
            if not ccPerson == "":
                ccPersonList = ccPerson.split()
                loginList = []
                for p in ccPersonList:
                    loginList.append(p.split("(")[1].split(")")[0])
                sgPerson = sg.find('HumanUser', [['login', 'in', loginList]])
            
            toPerson = sg.find_one('HumanUser', [['id', 'is', version_dict['user']['id']]])
            if not ccGroup == "" and not ccPerson == "":
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson], 'addressings_cc': sgGroup + sgPerson})
            
            elif not ccGroup == "" and ccPerson == "":
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson],'addressings_cc': sgGroup})
            
            elif ccGroup == "" and not ccPerson == "":
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson],'addressings_cc': sgPerson})
            
            else:
                sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson]})
            
            message = "{} 프로젝트에 {} 버전에 노트를 작성했습니다...".format(projectName, verName)
            self.ui.retime_publog_textEdit.append(message)

            message = "{} 프로젝트에 {} 버전 Publish 완료했습니다...".format(projectName, verName)
            self.ui.retime_publog_textEdit.append(message)

            color = QtGui.QColor(0, 255, 0, 125)
            self.ui.retime_publish_tableWidget.item(r, self.retime_column_idx_lookup["Ver"]).setBackground(color)
            QtCore.QCoreApplication.processEvents()