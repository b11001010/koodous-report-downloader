import json
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from enum import Enum
from pathlib import Path

import requests


DEFAULT_API_TOKEN = ''
DEFAULT_OUTPUT_DIR = 'koodous_data'
DEFAULT_SEARCH_QUERY = (
    'detected:true AND analyzed:true AND is_apk: true AND rating: <-3'
)
DEFAULT_REPORT_TYPE = 'all'


class ReportType(Enum):

    All = 'all'
    Androguard = 'androguard'
    Cuckoo = 'cuckoo'
    DroidBox = 'droidbox'

    @staticmethod
    def list_():
        return [e.value for e in ReportType]


class AnalysisReportGetter:

    APKS_URL = 'https://api.koodous.com/apks'
    ANALYSIS_URL = APKS_URL + '/{sha256}/analysis'

    def __init__(self, token, output_dir, search_query, report_type):
        self.output_dir_path = Path(output_dir)
        self.output_dir_path.mkdir(exist_ok=True, parents=True)
        self.search_query = search_query
        self.headers = {'Authorization': 'Token {}'.format(token)}
        self.report_type = ReportType(report_type)
        path_gen = self.output_dir_path.glob('**/*.json')
        self.sha256_list = [report_path.stem for report_path in path_gen]

    def start(self):

        params = {'search': self.search_query}
        response = requests.get(
            url=AnalysisReportGetter.APKS_URL,
            params=params,
            headers=self.headers
        )
        next_url = self.feed_next(response)

        while next_url:
            response = requests.get(url=next_url, headers=self.headers)
            next_url = self.feed_next(response)

    def feed_next(self, response):
        data = response.json()
        self.check_error(data)

        results = data.get('results', [])
        next_url = data.get('next', None)

        for result in results:
            sha256 = result['sha256']
            if sha256 in self.sha256_list:
                print('Skip: {}'.format(sha256))
                continue

            report = self.get_analysis_report(sha256)
            if report is None:
                continue

            file_path = self.output_dir_path / '{}.json'.format(sha256)
            self.save_report(file_path, report)
            self.sha256_list.append(sha256)

            print('Saved: {}'.format(file_path))

        return next_url

    def get_analysis_report(self, sha256):
        response = requests.get(
            url=AnalysisReportGetter.ANALYSIS_URL.format(sha256=sha256),
            headers=self.headers
        )
        if response.status_code == 404:
            return None

        data = response.json()
        self.check_error(data)

        return data.get(self.report_type.value, data)

    def save_report(self, file_path, report):
        with file_path.open(mode='w') as f:
            json.dump(report, f, indent=4)

    def check_error(self, data):
        error = data.get('detail', None)
        if error:
            print('Error: {}'.format(error))
            exit()


class Main:

    def __init__(self):
        parser = ArgumentParser(
            description="Get apk's analysis reports from https://koodous.com/",
            formatter_class=ArgumentDefaultsHelpFormatter
        )
        parser.add_argument(
            '-t', '--token',
            help='Your API Token of koodous.com',
            default=DEFAULT_API_TOKEN
        )
        parser.add_argument(
            '-o', '--output_dir',
            help='Directory path to save reports',
            default=DEFAULT_OUTPUT_DIR
        )
        parser.add_argument(
            '-s', '--search_query',
            help='Query string to search target apks',
            default=DEFAULT_SEARCH_QUERY
        )
        parser.add_argument(
            '-r', '--report_type',
            help='Type of report you want',
            choices=ReportType.list_(),
            default=DEFAULT_REPORT_TYPE
        )
        self.args = parser.parse_args()

    def run(self):
        AnalysisReportGetter(
            token=self.args.token,
            output_dir=self.args.output_dir,
            search_query=self.args.search_query,
            report_type=self.args.report_type
        ).start()


if __name__ == '__main__':
    Main().run()
