import requests

class SecEdgar:
    def __init__(self, fileurl):
        self.fileurl = fileurl
        self.headers = {'user-agent': 'Shahajalal Islam sjislam27@gmail.com'}
        self.name_dict = {}
        self.ticker_dict = {}

        response = requests.get(self.fileurl, headers=self.headers, timeout=10)
        response.raise_for_status()

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
        url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def _fiscal_year_and_quarter(self, report_date, fiscal_year_end):
        fiscal_end_month = int(fiscal_year_end[:2])

        date_parts = report_date.split("-")
        report_year = int(date_parts[0])
        report_month = int(date_parts[1])

        fiscal_start_month = (fiscal_end_month % 12) + 1
        months_since_fiscal_start = (report_month - fiscal_start_month) % 12
        quarter = (months_since_fiscal_start // 3) + 1

        if report_month <= fiscal_end_month:
            fiscal_year = report_year
        else:
            fiscal_year = report_year + 1

        return fiscal_year, quarter

    def _get_filings(self, cik, form_type, year, quarter):
        data = self._get_company_submissions(cik)
        fiscal_year_end = data['fiscalYearEnd']
        recent_filings = data['filings']['recent']

        for i in range(len(recent_filings['form'])):
            if recent_filings['form'][i] != form_type:
                continue

            report_date = recent_filings['reportDate'][i]
            filing_year, filing_quarter = self._fiscal_year_and_quarter(report_date, fiscal_year_end)

            match_year = filing_year == int(year)
            match_quarter = not quarter or filing_quarter == int(quarter)

            if match_year and match_quarter:
                accessionNumber = recent_filings['accessionNumber'][i].replace("-", "")
                primaryDocument = recent_filings['primaryDocument'][i]
                url = f"https://www.sec.gov/Archives/edgar/data/{str(cik).zfill(10)}/{accessionNumber}/{primaryDocument}"
                return accessionNumber, primaryDocument, url

        return None

    def annual_filing(self, cik, year):
        form_type = "10-K"
        return self._get_filings(cik, form_type, year, None)

    def quarterly_filing(self, cik, year, quarter):
        form_type = "10-Q"
        return self._get_filings(cik, form_type, year, quarter)


se = SecEdgar('https://www.sec.gov/files/company_tickers.json')