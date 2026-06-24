import requests

class SecEdgar:
    def __init__(self, fileurl):
        self.fileurl = fileurl
        self.name_dict = {}
        self.ticker_dict = {}

        headers = {'user-agent': 'Shahajalal Islam sjislam27@gmail.com'}

        r = requests.get(self.fileurl, headers=headers)

        self.filejson = r.json()

        self.cik_json_to_dict()

    def cik_json_to_dict(self):
        for data in self.filejson.values():
            entry = (data['cik_str'], data['title'], data['ticker'])

            self.name_dict[data['title'].upper()] = entry
            self.ticker_dict[data['ticker'].upper()] = entry

    def name_to_cik(self, company_name):
        return self.name_dict.get(company_name.upper())
    
    def ticker_to_cik(self, ticker):
        return self.ticker_dict.get(ticker.upper())
    
se = SecEdgar('https://www.sec.gov/files/company_tickers.json')
