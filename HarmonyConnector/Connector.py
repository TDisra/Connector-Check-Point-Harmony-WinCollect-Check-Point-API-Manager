import os
from HarmoniAPI import HarmonyAPI
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

if __name__ == '__main__':
    c = Connector(
        mainPath=r"C:\HarmonyConnector",
        clientID="7fb3f837277c477da294e87fb33b2f19",
        secretID="53e2d2e20c4244acb29d815cb6f015e6",
        url="https://cloudinfra-gw.portal.checkpoint.com/auth/external"
    )
    c.startMonitoring()