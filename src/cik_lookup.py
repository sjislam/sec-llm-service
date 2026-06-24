import requests

class SecEdgar:
    def __init__(self, fileurl):
        self.fileurl = fileurl
        self.headers = {'user-agent': 'Shahajalal Islam sjislam27@gmail.com'}
        self.name_dict = {}
        self.ticker_dict = {}

        response = requests.get(self.fileurl, headers=self.headers)

        self.filejson = response.json()

        self._cik_json_to_dict()

    def _cik_json_to_dict(self):
        for data in self.filejson.values():
            entry = (data['cik_str'], data['title'], data['ticker'])

            self.name_dict[data['title'].upper()] = entry
            self.ticker_dict[data['ticker'].upper()] = entry

    def name_to_cik(self, company_name):
        return self.name_dict.get(company_name.upper())
    
    def ticker_to_cik(self, ticker):
        return self.ticker_dict.get(ticker.upper())
    
    def _get_company_submissions(self, cik):
        url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def _get_filings(self, cik, form_type, year, quarter):
        quarter_months = {1: "-03-", 2: "-06-", 3: "-09-"}
        data = self._get_company_submissions(cik)
        recent_filings = data['filings']['recent']

        for i in range(len(recent_filings['form'])):
            if recent_filings['form'][i] == form_type:
                match_year = recent_filings['filingDate'][i].startswith(str(year))
                match_quarter = not quarter or quarter_months.get(int(quarter)) in recent_filings['reportDate'][i]

                if match_year and match_quarter:
                    accessionNumber = recent_filings['accessionNumber'][i].replace("-", "")
                    primaryDocument = recent_filings['primaryDocument'][i]
                    url = f"https://www.sec.gov/Archives/edgar/data/{str(cik).zfill(10)}/{accessionNumber}/{primaryDocument}"
                    return accessionNumber, primaryDocument, url


    def annual_filing(self, cik, year):
        form_type = "10-K"
        return self._get_filings(cik, form_type, year, None)

    def quarterly_filing(self, cik, year, quarter):
        form_type = "10-Q"
        return self._get_filings(cik, form_type, year, quarter)


se = SecEdgar('https://www.sec.gov/files/company_tickers.json')