import json
import os
from django.utils import timezone

class GroupStatistics:
    def __init__(self,id,exist = True):
        from django.conf import settings
        self.folderName = 'group'+str(id)
        self.dirPath = str(settings.BASE_DIR) + (str('/main/data/')+self.folderName)
        self.subDir = self.dirPath + '/subscribers/'
        self.reactDir = self.dirPath + '/reactions/'
        if not os.path.exists(self.dirPath):
          try:
              os.makedirs(os.path.dirname(self.dirPath), exist_ok=True)
              os.makedirs(os.path.dirname(self.subDir),exist_ok=True)
              os.makedirs(os.path.dirname(self.reactDir),exist_ok=True)
          except Exception as e:
              print('Error: ' + str(e))
              raise e

    def readFileJson(self,file):
        with open(file, 'r',encoding='utf-8') as f:
            data = json.load(f)
        return data
    def findUser(self,user_id,file,type):
        with open(file,'r',encoding='utf-8') as f:
            try:
                data = json.load(f)
                for hour in data:
                    for k in data[hour]:
                        event = data[hour][k]
                        if event['user_id'] == user_id and event['type'] == type:
                            return [hour,k]
            except Exception as e:
                print('Error: ' + str(e))
        return -1
    def logEvent(self,type,event,total=None):
        name = str(timezone.now().year)+'-'+str(timezone.now().month)+'-'+str(timezone.now().day)+'.json'
        if type == 0:
            file = self.subDir+name
        else:
            file = self.reactDir+name
        if(not os.path.isfile(file)):
            with open(file,'w+', encoding='utf-8') as f:
                data = {}
                for i in range (0,24):
                    data[str(i)] = {}
                json.dump(data,f,ensure_ascii=False, indent=4)
        data = self.readFileJson(file)
        user_exist = self.findUser(event['user_id'], file, event['type'])
        with open(file, 'w', encoding='utf-8') as f:
            if(type == 0 and total):
                data[str(timezone.now().hour)]['total'] = total
            if(user_exist != -1):
                data[user_exist[0]][user_exist[1]]['count'] = event['count']
                try:
                    data[user_exist[0]][user_exist[1]]['text'] = event['text']
                except:
                    pass
            else:
                data_hour_size = len(data[str(timezone.now().hour)])
                data[str(timezone.now().hour)][data_hour_size] = event
            json.dump(data, f,ensure_ascii=False, indent=4)

    def getDayliSubs(self,day):
        name = str(timezone.now().year)+'-'+str(timezone.now().month)+'-'+str(day)+'.json'
        file = self.subDir+name
        if not os.path.isfile(file):
            return {
                'total': 0
            }
        res = {}
        with open(file,'r') as f:
            data = json.load(f)
            total = 0
            for hour in data:
                res[str(hour)] = 0
                for sub in hour:
                    total += sub['count']
                    res[str(hour)] += sub['count']
            res['total'] = total
        return res

    def getDayliReact(self,day):
        name = str(timezone.now().year)+'-'+str(timezone.now().month)+'-'+str(day)+'.json'
        file = self.reactDir+name
        if not os.path.isfile(file):
            return {
                'total': 0
            }
        res = {}
        with open(file,'r') as f:
            data = json.load(f)
            total = 0
            for hour in data:
                res[str(hour)] = 0
                for sub in hour:
                    total += sub['count']
                    res[str(hour)] += sub['count']
            res['total'] = total
        return res