# _*_ coding: utf-8 _*_

# Comp Publish Tool
#
# Description : Comp 팀에서 Pub하는 툴

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import comppubtool
import uiSetting_final
import uiSetting_team
import uiSetting_collect
import uiSetting_retime
import compPublish

# global variables
OPT_PATH = os.getenv("OPT_PATH")

PWD = os.path.dirname(os.path.abspath(__file__))
uiFileName = "{}/compPublishTool.ui".format(PWD)

from PySide2 import QtWidgets, QtUiTools, QtCore

class CompPublishTool():
    def __init__(self):
        self.ui = QtUiTools.QUiLoader().load(uiFileName, None)
        self.ui.show()

        self.version = comppubtool.__version__ # 버전
        self.proJson = "{}/TD/sceneopener/code/openersetCopy/teamInfo.json".format(OPT_PATH)
        self.final_column_headers = ["Project", "Seq", "Shot", "Task", "Ver", "Ext", "InputPath", "OutputPath", "FrameRange", "Duration", "Resolution", "Note", "CC_Group", "CC_Person"]
        self.team_column_headers = ["Project", "Seq", "Shot", "Task", "Ver", "Ext", "PubRenderPath", "PubNukePath", "DevlRenderPath", "DevlNukePath", "FrameRange", "Duration", "Resolution", "Note", "CC_Group", "CC_Person"]
        self.collect_column_headers = ["Project", "Seq", "Shot", "Task", "Ver", "PubCollectPath", "Note", "CC_Group", "CC_Person"]
        self.retime_column_headers = ["Project", "Seq", "Shot", "Task", "PlateVer", "Ver", "PlatePath", "FrameRange", "Duration", "Resolution", "Note", "CC_Group", "CC_Person"]

        self.final_column_idx_lookup = {"Project": 0, "Seq": 1, "Shot": 2, "Task": 3, "Ver": 4, "Ext": 5, "InputPath": 6, "OutputPath": 7, "FrameRange": 8, "Duration": 9, "Resolution": 10, "Note": 11, "CC_Group": 12, "CC_Person": 13}
        self.team_column_idx_lookup = {"Project": 0, "Seq": 1, "Shot": 2, "Task": 3, "Ver": 4, "Ext": 5, "PubRenderPath": 6, "PubNukePath": 7, "DevlRenderPath": 8, "DevlNukePath": 9, "FrameRange": 10, "Duration": 11, "Resolution": 12, "Note": 13, "CC_Group": 14, "CC_Person": 15}
        self.collect_column_idx_lookup = {"Project": 0, "Seq": 1, "Shot": 2, "Task": 3, "Ver": 4, "PubCollectPath": 5, "Note": 6, "CC_Group": 7, "CC_Person": 8}
        self.retime_column_idx_lookup = {"Project": 0, "Seq": 1, "Shot": 2, "Task": 3, "PlateVer": 4, "Ver": 5, "PlatePath": 6, "FrameRange": 7, "Duration": 8, "Resolution": 9, "Note": 10, "CC_Group": 11, "CC_Person": 12}

        # ui 초기화
        self.ui.version_label.setText(self.version)
        uiSetting_final.initUIFunc(self)
        uiSetting_team.initUIFunc(self)
        uiSetting_collect.initUIFunc(self)
        uiSetting_retime.initUIFunc(self)

        # final pub tab signals
        self.ui.final_project_comboBox.currentIndexChanged.connect(lambda: uiSetting_final.setSeqFunc(self))
        self.ui.final_sequence_comboBox.currentIndexChanged.connect(lambda: uiSetting_final.setShotFunc(self))
        self.ui.final_shot_comboBox.currentIndexChanged.connect(lambda: uiSetting_final.setTaskFunc(self))
        self.ui.final_task_comboBox.currentIndexChanged.connect(lambda: uiSetting_final.setExtFunc(self))
        self.ui.final_ext_comboBox.currentIndexChanged.connect(lambda: uiSetting_final.setVerFunc(self))
        self.ui.final_shotgunmov_checkBox.stateChanged.connect(lambda: uiSetting_final.setVerFunc(self))
        self.ui.final_note_toolButton.pressed.connect(lambda: uiSetting_final.openEditorFunc())
        self.ui.final_ccGroup_pushButton.pressed.connect(lambda: uiSetting_final.setCCGroupFunc(self))
        self.ui.final_ccPerson_pushButton.pressed.connect(lambda: uiSetting_final.setCCPersonFunc(self))
        self.ui.final_add_btn.pressed.connect(lambda: uiSetting_final.setPublishTableFunc(self))
        self.ui.final_minus_btn.pressed.connect(lambda: uiSetting_final.minusPublishTableFunc(self))
        self.ui.final_publish_btn.pressed.connect(lambda: compPublish.finalPublishFunc(self))
        self.ui.final_cancel_btn.pressed.connect(lambda: self.ui.close())

        # team pub tab signals
        self.ui.team_pubTeam_comboBox.currentIndexChanged.connect(lambda: uiSetting_team.initUIFunc(self))
        self.ui.team_pubFile_comboBox.currentIndexChanged.connect(lambda: uiSetting_team.initUIFunc((self)))
        self.ui.team_project_comboBox.currentIndexChanged.connect(lambda: uiSetting_team.setSeqFunc(self))
        self.ui.team_sequence_comboBox.currentIndexChanged.connect(lambda: uiSetting_team.setShotFunc(self))
        self.ui.team_shot_comboBox.currentIndexChanged.connect(lambda: uiSetting_team.setTaskFunc(self))
        self.ui.team_task_comboBox.currentIndexChanged.connect(lambda: uiSetting_team.setCheckFunc(self))
        self.ui.team_ext_comboBox.currentIndexChanged.connect(lambda: uiSetting_team.setVerFunc(self))
        self.ui.team_shotgunmov_checkBox.stateChanged.connect(lambda: uiSetting_team.setVerFunc(self))
        self.ui.team_note_toolButton.pressed.connect(lambda: uiSetting_team.openEditorFunc())
        self.ui.team_ccGroup_pushButton.pressed.connect(lambda: uiSetting_team.setCCGroupFunc(self))
        self.ui.team_ccPerson_pushButton.pressed.connect(lambda: uiSetting_team.setCCPersonFunc(self))
        self.ui.team_add_btn.pressed.connect(lambda: uiSetting_team.setPublishTableFunc(self))
        self.ui.team_minus_btn.pressed.connect(lambda: uiSetting_team.minusPublishTableFunc(self))
        self.ui.team_publish_btn.pressed.connect(lambda: compPublish.teamPublishFunc(self))
        self.ui.team_cancel_btn.pressed.connect(lambda: self.ui.close())

        # collect pub table signals
        self.ui.collect_project_comboBox.currentIndexChanged.connect(lambda: uiSetting_collect.setSeqFunc(self))
        self.ui.collect_sequence_comboBox.currentIndexChanged.connect(lambda: uiSetting_collect.setShotFunc(self))
        self.ui.collect_shot_comboBox.currentIndexChanged.connect(lambda: uiSetting_collect.setVerFunc(self))
        self.ui.collect_note_toolButton.pressed.connect(lambda: uiSetting_collect.openEditorFunc())
        self.ui.collect_ccGroup_pushButton.pressed.connect(lambda: uiSetting_collect.setCCGroupFunc(self))
        self.ui.collect_ccPerson_pushButton.pressed.connect(lambda: uiSetting_collect.setCCPersonFunc(self))
        self.ui.collect_add_btn.pressed.connect(lambda: uiSetting_collect.setPublishTableFunc(self))
        self.ui.collect_minus_btn.pressed.connect(lambda: uiSetting_collect.minusPublishTableFunc(self))
        self.ui.collect_publish_btn.pressed.connect(lambda: compPublish.collectPublishFunc(self))
        self.ui.collect_cancel_btn.pressed.connect(lambda: self.ui.close())

        # retime pub table signals
        self.ui.retime_project_comboBox.currentIndexChanged.connect(lambda: uiSetting_retime.setSeqFunc(self))
        self.ui.retime_sequence_comboBox.currentIndexChanged.connect(lambda: uiSetting_retime.setShotFunc(self))
        self.ui.retime_shot_comboBox.currentIndexChanged.connect(lambda: uiSetting_retime.setTaskFunc(self))
        self.ui.retime_task_comboBox.currentIndexChanged.connect(lambda: uiSetting_retime.setVerFunc(self))
        self.ui.retime_note_toolButton.pressed.connect(lambda: uiSetting_retime.openEditorFunc())
        self.ui.retime_ccGroup_pushButton.pressed.connect(lambda: uiSetting_retime.setCCGroupFunc(self))
        self.ui.retime_ccPerson_pushButton.pressed.connect(lambda: uiSetting_retime.setCCPersonFunc(self))
        self.ui.retime_add_btn.pressed.connect(lambda: uiSetting_retime.setPublishTableFunc(self))
        self.ui.retime_minus_btn.pressed.connect(lambda: uiSetting_retime.minusPublishTableFunc(self))
        self.ui.retime_publish_btn.pressed.connect(lambda: compPublish.retimePublishFunc(self))
        self.ui.retime_cancel_btn.pressed.connect(lambda: self.ui.close())

if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    win = CompPublishTool()
    sys.exit(app.exec_())