import logging
from pathlib import Path
import re

from sportscraper.scraper import RequestScraper


class Scraper(RequestScraper):


    @property
    def base_url(self):
        '''
        Base URL for site

        Returns:
            str

        '''
        return 'http://www.illinoiscourts.gov/'

    @property
    def base_opinions_url(self):
        '''
        Base URL for sct/appellate opinions

        Returns:
            str

        '''
        return 'http://www.illinoiscourts.gov/Opinions/'

    @property
    def base_docket_url(self):
        '''
        Base URL for supreme court docket

        Returns:
            str

        '''
        return f'http://www.illinoiscourts.gov/SupremeCourt/Docket/'

    @property
    def docket_month_short(self):
        '''
        Gets month codes. Keys are int, vals are str.

        Returns:
            dict

        '''
        return {1: 'Jan', 3: 'Mar', 5: 'May',
                9: 'Sept', 11: 'Nov'}

    @property
    def docket_month_long(self):
        '''
        Gets month codes. Keys are int, vals are str.

        Returns:
            dict

        '''
        return {1: 'January', 3: 'March', 5: 'May',
                9: 'September', 11: 'November'}

    def archive_supreme(self, year):
        '''
        Gets recent IL supreme court page

        Args:
            year(int): year opinion was issued

        Returns:
            requests_html.HTMLResponse

        '''
        url = f'{self.base_opinions_url}SupremeCourt/{year}/default.asp'
        return self.get_htmlresponse(url)

    def docket_call(self, year, month):
        '''
        Gets call of the docket

        Args:
            month(int): month of call
            year(int): year of call

        Returns:
            requests_html.HTMLResponse

        '''


        url = (f'{self.base_docket_url}{year}/{self.docket_month_short.get(month)}/'
              f'PublicCallOfDocket.pdf')
        return self.get_htmlresponse(url)

    def get_htmlresponse(self, url):
        '''
        Gets requests_html object for parser

        Args:
            url(str):

        Returns:
            requests_html.HTMLResponse

        '''
        return self.session.get(url)

    def get_opinion(self, url, save_dir):
        '''
        Gets PDF of opinions

        Args:
            url(str): opinion URL
            save_dir(Path)

        Returns:
            str - full path of file

        '''
        file_name = Path(save_dir) / url.split('/')[-1]
        r = self.session.get(url)
        with file_name.open('wb') as f:
            f.write(r.content)

    def recent_supreme(self):
        '''
        Gets recent IL supreme court page

        Returns:
            str

        '''
        url = f'{self.base_opinions_url}recent_supreme.asp'
        return self.get_htmlresponse(url)


class Parser():

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.data = {}

    def archive_supreme(self, html_response, year):
        '''
        Parses list of recent Supreme Court decisions

        Args:
            html_response(requests_html.HTMLResponse)

        Returns:
            list (of dict)

        '''
        base_url = 'http://www.illinoiscourts.gov/Opinions/SupremeCourt'
        return [f'{base_url}/{year}/{link}' for
                 link in html_response.html.links if
                 re.search(r'^\d+\.pdf', link)]

    def docket_urls(self, html_response):
        '''
        Parses list of Supreme Court docket calls

        Args:
            html_response(requests_html.HTMLResponse)

        Returns:
            dict

        '''
        select_element = html_response.html.find('#SelectCall', first=True)

    def recent_supreme(self, html_response):
        '''
        Parses list of recent Supreme Court decisions

        Args:
            html_response(requests_html.HTMLResponse)

        Returns:
            list (of dict)

        '''
        tbl = html_response.html.find('#decisions', first=True)
        return [link for link in tbl.absolute_links
                  if re.search('Opinions/SupremeCourt', link)]


class Agent():
    '''

    '''

    def __init__(self, save_path=None):
        '''

        Args:
            save_path(pathlib.Path): where to save files

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.s = Scraper(cache_name='illcts')
        self.p = Parser()
        self.data = {}
        if save_path:
            self.save_path = save_path
        else:
            self.save_path = Path.home()

    def archive_docket_call(self, get_all=False, year=None, month=None):
        '''

        Args:
            get_all(bool): get all docket call
            year(int):
            month(int):

        Returns:
            list

        '''
        urls = []
        docket_url = f'{self.s.base_docket_url}default.asp'
        r = self.s.get_htmlresponse(docket_url)

        # parse the options in the drop-down menu
        select = r.html.find('#SelectCall', first=True)
        if get_all:
            for option in select.find('option'):
                # need to strip trailing forward slash
                url = f'{self.s.base_url[:-1]}{option.attrs.get("value")}'
                logging.info('getting %s' % url)
                urls.append(url)
                file_name = url.split('/')[-1]
                file_path = self.save_path / file_name
                if not file_path.is_file():
                    r = self.s.get_htmlresponse(url)
                    with file_path.open('wb') as f:
                        f.write(r.content)
        else:
            docket_urls_d = {option.text: option.attrs.get("value")
                        for option in select.find('option')}
            month = self.s.docket_month_long.get(month)
            datestr = f'{month} {year}'
            url = docket_urls_d.get(datestr)
            if url:
                logging.info('getting %s' % url)
                r = self.s.get_htmlresponse(url)
                file_name = url.split('/')[-1]
                file_path = self.save_path / file_name
                with file_path.open('wb') as f:
                    f.write(r.content)
                urls.append(url)
        return urls
