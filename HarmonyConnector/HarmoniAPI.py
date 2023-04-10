import requests
from time import time
from uuid import uuid4
import datetime


class HarmonyAPI(object):
    
    def __init__(self,client_id,secret_key,urlAuto,apiVersion='v1.0'):
        self.client_id = client_id
        self.secret_key = secret_key
        self.urlAuto = urlAuto
        self.apiVersion = apiVersion
        self.url = self.__genUrl__()
        self.jsonRes = None
        self.expTime = None
        self.token = self.get_token(isauto=False)
        self.scop = self.getScopes()
        self.lastRequestId = None
        
        
    def __genUrl__(self):
        return "https://" + self.urlAuto.replace(
            "https://",''
        ).split('/')[0]+f"/app/hec-api/{self.apiVersion}/"
        
    def get_token(self,isauto=True):
        if self.__isTokevnValid__(isauto): return self.token
        payload = {
            'clientId': self.client_id,
            'accessKey': self.secret_key
        }
        r = requests.post(self.urlAuto, json=payload)
        assert(r.status_code == 200)
        self.jsonRes = r.json()['data']
        self.token = self.jsonRes['token']
        self.expTime = self.__getDateExpUnix__()
        return self.token
        
    def __isTokevnValid__(self,isauto=True):
        if not isauto: 
            return isauto
        return time() <= self.__getDateExpUnix__()
        
    def __getDateExpUnix__(self):
        if not self.expTime: return self.jsonRes['expiresIn'] + time()
        return self.expTime
    
    def header(self):
        token = self.get_token()
        self.lastRequestId = str(uuid4())
        return {
            'Authorization': f'Bearer {token}',
            'x-av-req-id': self.lastRequestId
        }
 
    def __genRequestedUrl__(self,*actions):
        return f"{self.url}{'/'.join(actions)}"
    
    def getScopes(self):
        url = self.__genRequestedUrl__('scopes')
        r = requests.get(url,headers=self.header())
        return r.json()['responseData']
    
    
    def noneRemove(self,payload):
        return {
            i:payload[i] for i in payload.keys() if payload[i]!=None
        }
    
    
    def getTimeFormat(self, num=24, Type='h', start_time=None):
        def getnum(num,Type):
            multip = {
                'm': num/60,
                'h': num,
                'd': 24*num
            }
            return multip[Type]
        if not start_time:
            s = (datetime.datetime.now() - datetime.timedelta(
                    hours=getnum(num=num,Type=Type))).strftime("%Y-%m-%dT%H:%M:%SZ")
        else: s = start_time
        e = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        return {
            'start_date': s,
            'end_date': e
        }
        
        
    def queryEvent(self,start_date=None,end_date=None,scopes=None,event_types=None,event_states=None,
                  severities=None,saas=None,description=None,event_ids=None,scroll_id=None):
        if not scopes: scopes = self.scop
        if not start_date or not end_date:
            d = self.getTimeFormat(start_time=start_date)
            start_date, end_date = d['start_date'], d['end_date']
        payload = {
            'requestData': self.noneRemove({
                    'scopes': scopes,
                    'eventTypes': event_types,
                    'eventStates': event_states,
                    'severities': severities,
                    'startDate': start_date,
                    'endDate': end_date,
                    'saas': saas,
                    'description': description,
                    'eventIds': event_ids,
                    'scrollId': scroll_id
                }
            ) 
        }
        url = self.__genRequestedUrl__('event','query')
        r = requests.post(url,headers=self.header(),json=payload)
        if r.status_code != 200:
            return False
        return {
            "untiTime": end_date,
            'logs': r.json()['responseData']
        }
        