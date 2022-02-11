# Comp Pub Tool
<br>

#### [소스 코드]

##### 메인 코드
- [basic.py](../basic.py) : CompPublishTool 클래스가 구현되어 있는 메인 코드
   - 기본적으로 실행을 할 때, ui 파일을 로드하여 보여준다.
   - UI 테이블을 구성하기 위한 컬럼에 대한 정의가 되어있다. final, team, collect, retime 각각 따로 정의가 되어있다.
   ```
   self.final_column_headers = ["Project", "Seq", "Shot", "Task", "Ver", "Ext", "InputPath", "OutputPath", "FrameRange", "Duration", "Resolution", "Note", "CC_Group", "CC_Person"]
   
   self.final_column_idx_lookup = {"Project": 0, "Seq": 1, "Shot": 2, "Task": 3, "Ver": 4, "Ext": 5, "InputPath": 6, "OutputPath": 7, "FrameRange": 8, "Duration": 9, "Resolution": 10, "Note": 11, "CC_Group": 12, "CC_Person": 13}
   ```
   - final, team, collect, retime 각각 UI 별로 버튼 클릭, radio 버튼 토글 변경, 콤보 박스 변경에 따른 시그널 함수들이 정의되어 있다.

##### 서브 코드
- [uiSetting_final.py](../uiSetting_final.py) : Final Pulish 탭의 UI를 세팅하는 코드
  - resolution, fps 등의 프로젝트 정보는 nuke 레포지터리의 setting.json에서 가져온다.
  - au 프로젝트의 샷코드 변환을 위해서 nuke 레포지터리의 projectInfo.json을 가져온다.
  - CC를 위해 shotgun api를 사용한다.
  ```
  # 샷건에서 CC 그룹을 가져온다.
    groups = sg.find('Group', [], ['code', 'id'])
    for g in groups:
        ccList.addItem(g['code'])
  
  # 샷건에서 CC Person을 가져온다.
    people = sg.find('HumanUser', [['sg_status_list', 'is', 'act']], ['name', 'login'])
    for p in people:
        ccList.addItem("{}({})".format(p['name'], p['login']))
  ```
  - nuke 파일을 텍스트로 읽어서 frame 정보를 가져온다.
  ```
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
  ```


- [uiSetting_team.py](../uiSetting_team.py) : Team Pulish 탭의 UI를 세팅하는 코드
  - render 파일만 pub을 하거나, nuke 파일만 pub을 하거나 혹은 둘다 pub을 하거나의 상황에 따라서 지정하는 경로에 차이가 있다.

- [uiSetting_collect.py](../uiSetting_collect.py) : Collect Pulish 탭의 UI를 세팅하는 코드
- [uiSetting_retime.py](../uiSetting_retime.py) : Retime Pulish 탭의 UI를 세팅하는 코드


- [compPublish.py](../compPublish.py) : 세팅된 테이블 데이터를 기준으로 Publish를 실제로 하는 코드
  - finalPublishFunc: final Publish / teamPublishFunc: team Publish / collectPublishFunc: collect Publish / retimePublishFunc: retime Publish
  - 폴더 및 파일 복사를 위해서 shutil, copy_tree를 사용한다.
  - Shotgun에서 정보를 가져온다.
  ```
  project_dict = sg.find_one('Project', [['name', 'is', projectName]])

  shot_dict = sg.find_one('Shot', [['project', 'is', project_dict], ['code', 'is', shotCode]])
  
  task_dict = sg.find_one('Task', [['project', 'is', project_dict], ['entity', 'is', shot_dict], ['content', 'is', taskName]])
  
  version_dict = sg.find_one('Version', [['project', 'is', project_dict], ['entity', 'is', shot_dict], ['sg_task', 'is', task_dict], ['code', 'is', verName], ['sg_status_list', 'is', status]], ['user'])
  ```
  - Shotgun 정보(Status)를 업데이트한다.
  ```
  sg.update('Task', task_dict['id'], {'sg_status_list': sgStatus})
  sg.update('Version', version_dict['id'], {'sg_status_list': sgStatus})
  ```
  - Shotgun에 노트를 남긴다.
  ```
  toPerson = sg.find_one('HumanUser', [['id', 'is', version_dict['user']['id']]])
  if not ccGroup == "" and not ccPerson == "":
      sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson], 'addressings_cc': sgGroup + sgPerson})
  
  elif not ccGroup == "" and ccPerson == "":
      sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson],'addressings_cc': sgGroup})
            
  elif ccGroup == "" and not ccPerson == "":
      sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson],'addressings_cc': sgPerson})
  else:
      sg.create('Note', {'user': person, 'project': project_dict, 'note_links': [version_dict, shot_dict], 'subject': subjectName, 'content': noteText, 'tasks': [task_dict], 'addressings_to': [toPerson]})
  ```
  - collect, retime publish의 경우 따로 파일 및 폴더를 복사하지 않고 Shotgun에 노트만 남기는 기능을 한다.