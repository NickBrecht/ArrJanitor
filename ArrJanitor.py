#!/usr/bin/python3
#noParity=true
import os 
import re
import json
import datetime
from pip._internal import main as pip


### args list ###
radarr_url = ''
radarr_api_key = ''

radarr2_url = ''
radarr2_api_key = ''

sonarr_url = ''
sonarr_api_key = ''

sonarr2_url = ''
sonarr2_api_key = ''

deluge_url = ''
deluge_password = ''

days_to_seed = 4 #days to keep torrents even if they've been replaced.

#### Arg Collecting ####

#create top level dict for holding variables in
services_dict =  {'downloaders':{}, 'arr':{}}

#should have just made this a class but whatever too late...
def services_dict_formatter(d,key, service, url, passkey):
    d[key].update({service:{}})
    d[key][service]['url'] = url
    if key == 'downloaders':
        d[key][service]['password'] = passkey
    elif key == 'arr':
        d[key][service]['api_key'] = passkey
        
if deluge_url and deluge_password:
    services_dict_formatter(services_dict,'downloaders','deluge',deluge_url,deluge_password)

if sonarr_url and sonarr_api_key:
    services_dict_formatter(services_dict,'arr','sonarr',sonarr_url,sonarr_api_key)
    
if radarr_url and radarr_api_key:
    services_dict_formatter(services_dict,'arr','radarr',radarr_url,radarr_api_key)

if sonarr2_url and sonarr2_api_key:
    services_dict_formatter(services_dict,'arr','sonarr2',sonarr_url,sonarr_api_key)
    
if radarr2_url and radarr2_api_key:
    services_dict_formatter(services_dict,'arr','radarr2',radarr_url,radarr_api_key)


#### Script ####

#install pandas & requests not found in Nerdpack's python... 
try:
    import pandas as pd
except:
    try:
        pip.main(['install','pandas'])
        import pandas as pd
    except Exception as e:
        raise Exception(f'Error importing/installing Pandas. Ensure pip is installed from Nerdpack: {e}')

try:
    import requests
except:
    try:
        pip.main(['install','requests'])
        import requests
    except Exception as e:
        raise Exception(f'Error importing/installing Requests. Ensure pip is installed from Nerdpack: {e}')

        
#deluge class
class Deluge:
    '''
    Deluge API wrapper to enable easier and more pythonic interactions with Deluge's RPC APIs.

    
    Deleveloped with Deluge 2.0.3 within python 3.8. Should work with Deluge >=1.3 & python >=3.6.
    '''
    def __init__(self, url, password,ssl=False):
        self.url = url
        self.password = password
        self.request_ = 0
        
        #create session
        self.session = requests.session()
        self.session.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        
        payload = {'id':self.request,"method": "auth.login","params":[self.password]}
        
        #authenticate      
        auth = self.session.post(f'{self.url}/json',data=json.dumps(payload), verify=ssl)
        
        #Check for errors within login. 
        if (auth.json()['error']):
            raise Exception(f"Error Authenticating: {auth.json()}")
            

    def query(self,payload:dict):
        '''Function to allow enabling free querying of deluge within the client's consturcted session. 
        
        Returns request object.'''

        payload['id'] = self.request
        data = self.session.post(f'{self.url}/json',data=json.dumps(payload))
        
        return data
        

    def remove_torrent(self,downloadid,delete=True):
        '''Method to allow deleting of torrents from within Deluge. Return boolean upon deletion attempt. 
        
            downloadid: The torrent's hash (single or list of hashes). 
            delete: bool to keep or delete the data on disk.'''
        
        #check if passed downloadid is list or str
        if isinstance(downloadid,str):
            method = 'core.remove_torrent'
        else:
            raise Exception(f'No. Pass a str ID to downloadid, not {type(downloadid)}.')
        
        #format payload
        payload = {'id':self.request,"method": method,"params":[downloadid, delete]}
        
        #issue request 
        data = self.session.post(f'{self.url}/json',data=json.dumps(payload))
        
        #status code check
        if data.status_code == 200:
            pass
        else:
            raise Exception(f"Error with request: {data.reason}")
        
        if data.json()['result']:
            return data.json()['result']
        else:
            return False
          
        
    def get_torrent(self,downloadid=None,cols:list=None):
        '''Method to get all torrents from Deluge. Pass downloadid to retrive data from individual torrent.'''
        
        if isinstance(downloadid,str):
            method = "core.get_torrent_status"
        elif downloadid == None:
            method = "core.get_torrents_status"
        
        #format payload
        payload = {'id':self.request,"method": method,"params":[downloadid or '',cols or '']}
        
        #issue request 
        data = self.session.post(f'{self.url}/json',data=json.dumps(payload))
        
        #status code check
        if data.status_code == 200:
            pass
        else:
            raise Exception(f"Error with request: {data.reason}")
            
        #convert json results to df
        df = pd.DataFrame.from_dict(data.json()['result'],orient='index')
        
        #transpose df if individual downloadid is passed. Also ensure hash(downloadid) is encoded into the index.
        if downloadid:
            df = df.transpose()
            try: 
                df.set_index('hash',drop=False,inplace=True)
            except:
                df['hash'] = downloadid
                df.set_index('hash',drop=True,inplace=True)
            
        return df

    @property
    def request(self):
        '''Counter property to track the # of requests issued to Deluge. Not sure why this is 100% needed but 
        it is mentioned within Deluge API docs.'''
        self.request_ += 1
        return self.request_

def arr_request(url,api_key,event_type):
    '''Quick helper function to format and issue GET requests against the targeted service'''
    response = requests.get(f'{url}/api/history?pageSize=1000000&filterKey=eventType&filterValue={event_type}&apikey={api_key}')
    return response

def arr_frame_formatter(r,cols=None,dupes=True):
    '''Function to take response object and return df of select columns excluding recent downloads.'''

    #convert json to df
    df = pd.DataFrame(r.json()['records'])

    if isinstance(cols,list):
        df = df[cols]

    if 'date' in df.columns:
        #properly convert date to pd datetime
        df['date'] = pd.to_datetime(df['date'])

    if dupes == False:
        if 'downloadId' in df.columns:
            df.drop_duplicates('downloadId',inplace=True)
        else:
            raise Exception('downloadId not within Columns. ID is needed to remove duplicates.')
    return df


if __name__ == "__main__":

    #create deluge client sessions...
    client = Deluge(deluge_url,deluge_password)

    days_to_seed_dt = datetime.date.today() - datetime.timedelta(days =days_to_seed)

    master_arr_media = pd.DataFrame() #create dataframe to hold data from sonarr & radarr.

    for k, v in services_dict['arr'].items():
        url = v['url']
        api_key = v['api_key']
        
        initial_grab_response = arr_request(url=url,api_key=api_key,event_type=1)
        
        #creation of service specific media important to allow users to have a 1080p & 4k verson (as in the usecase of user running radarr4k). 
        if 'radarr' in k.lower():
            df = arr_frame_formatter(initial_grab_response,dupes=False
                                    ).sort_values(['date'], ascending=True)
            #generate service specific media ID
            df['media_id'] = df['movieId'].astype(str) + '-' + str(k)
            df.drop(columns=['movieId','movie'],inplace=True)
            
            
        elif 'sonarr' in k.lower():
            df = arr_frame_formatter(initial_grab_response,dupes=False
                                    ).sort_values(['date'],ascending=True)      
            #generate service specific media ID
            df['media_id'] = df['seriesId'].astype(str) +'-'+ df['episodeId'].astype(str) + '-' + str(k)
            #drop sonarr specific columns
            df.drop(columns=['series','episodeId','episode','seriesId'],inplace=True)

        
        #Looks like Sonarr/Radarr return hash capitalized?
        df['downloadId'] = df['downloadId'].str.lower()
    
        #save the service for traceability.
        df['service'] = k 
        
        #concat the data within the master df.
        master_arr_media = pd.concat([master_arr_media,df]).reset_index(drop=True)
        
     
    try:
        
        #grab all current torrents in session
        current_torrents = client.get_torrent(cols=['name','hash','total_size','completed_time'])
        
        #filter out 0s (uncompleted torrents)
        current_torrents = current_torrents[current_torrents['completed_time'] > 0]
        
        #format dt col
        current_torrents['completed_time'] = pd.to_datetime(current_torrents['completed_time'],unit='s')
        
    except KeyError as e:
        raise Exception('KeyError - ArrJanitor does not support Deluge 1.3.')


    #combine target media & current torrents to generate list of torrents that need to be deleted. 
    combined_df = pd.merge(master_arr_media, current_torrents, how='left',left_on=['downloadId'], right_index=True)

    combined_df.dropna(inplace=True)

    #find replaced media
    combined_df['replaced'] = combined_df.duplicated(subset=['media_id'],keep=False)

    replaced_media_df = combined_df[combined_df['replaced']==True].copy()

    #generate the list of hashs to keep (the most recently downloaded version)
    media_to_keep = replaced_media_df.drop_duplicates(subset='media_id',keep='last')['hash'].tolist()

    #finalize media to be deleted by excluding the most recent verson & any torrents within the days to keep range.
    media_to_delete = replaced_media_df[~replaced_media_df['hash'].isin(media_to_keep) 
                                        & (replaced_media_df['date'].dt.date < days_to_seed_dt)].copy()


    #check if there is media to delete

    if len(media_to_delete) > 0:
        media_to_delete['deleted'] = media_to_delete.apply(lambda download : client.remove_torrent(download['hash']),axis=1)

        #print out if someone is watching...
        print(f"ArrJanitor finished: {media_to_delete['deleted'].sum()} torrents have been deleted.")  
        for index, row in media_to_delete.iterrows():
            print (f"{row['name']} : {round(row['total_size']/1073741824,2)} GB(s)")
    else:
        print('Script complete with no deletions')
