import os
from .HarmoniAPI import HarmonyAPI
from hashlib import md5
from time import sleep

class Connector(object):
    
    def __init__(self,mainPath, clientID, secretID, url):
        self.harmonyApi = HarmonyAPI(clientID, secretID, url)
        self.pathes = None
        self.mainPath = mainPath
        self.__setEnv__()
        
    def __pathes__(self):
        self.pathes = {
            'main': self.mainPath,
            'emailAndCollaboration': os.path.join(self.mainPath,'emailAndCollaboration')
        }
        
        
    def __setEnv__(self):
        self.__pathes__()
        if  not os.path.exists(self.pathes['main']):
            os.mkdir(self.pathes['main'])
        if  not os.path.exists(
            self.pathes['emailAndCollaboration']
        ):
            os.mkdir(self.pathes['emailAndCollaboration'])
        return self.pathes['main']
    
    
    def __parseToCef__(self,logs):
        return '\n'.join(
            ' '.join(f'"{n}"="{log[n]}"' for n in log.keys()) for log in logs
        ).encode()

    def __writeToFile__(self,logs,logType):
        path =  os.path.join(self.pathes[logType],f"{md5(logs).hexdigest()}.cef")
        with open(path,'wb') as f:
            f.write(logs)
        f.close()


    def startMonitoring(self):
        start_date = None
        while True:
            logs = self.harmonyApi.queryEvent(start_date=start_date)
            start_date = logs['untiTime']
            logs = self.__parseToCef__(logs['logs'])
            if not logs: continue
            print(len(logs))
            self.__writeToFile__(logs,'emailAndCollaboration')
            sleep(5)

