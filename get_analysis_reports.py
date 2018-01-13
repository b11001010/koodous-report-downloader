import json
import requests
import glob

def main():
    directory_path = 'koodous_data'
    params = {'search': 'detected:true AND analyzed:true AND rating: <-3'}
    
    sha256_list = [r.split('/')[-1].split('.json')[0] for r in glob.glob(directory_path+'/*.json')]
    page_count = 0
    next_url = 'First'

    while next_url != None:
        print('%s:' % page_count)
        
        if next_url == 'First':
            r = requests.get(url="https://api.koodous.com/apks", params=params)
        else:
            r = requests.get(url=next_url)
            
        results = r.json()['results']
        next_url = r.json()['next']
        for result in results:
            sha256 = result['sha256']
            
            if sha256 in sha256_list:
                continue
            
            url_koodous = "https://api.koodous.com/apks/%s/analysis" % sha256
            r = requests.get(url=url_koodous)
            if r.json()['androguard'] != None: # androguardによる解析結果があるか
                f = open(directory_path + '/' + sha256 + '.json', 'w')
                json.dump(r.json(), f, indent=4)
                f.close()
                print(sha256)
        
        page_count += 1


if __name__ == '__main__':
    main()