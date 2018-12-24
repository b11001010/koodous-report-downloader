# APK-Malware-Analysis
Get apk's analysis report from https://koodous.com/

## Requirement

requests

## Usage

```
$ python analysis_report_getter.py -h
usage: analysis_report_getter.py [-h] [-t TOKEN] [-o OUTPUT_DIR]
                                 [-s SEARCH_QUERY]
                                 [-r {all,androguard,cuckoo,droidbox}]

Get apk's analysis reports from https://koodous.com/

optional arguments:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        Your API Token of koodous.com (default: )
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Directory path to save reports (default: koodous_data)
  -s SEARCH_QUERY, --search_query SEARCH_QUERY
                        Query string to search target apks (default:
                        detected:true AND analyzed:true AND is_apk: true AND
                        rating: <-3)
  -r {all,androguard,cuckoo,droidbox}, --report_type {all,androguard,cuckoo,droidbox}
                        Type of report you want (default: all)
```