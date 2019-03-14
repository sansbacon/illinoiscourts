import logging
from pathlib import Path
import re

from sportscraper.scraper import RequestScraper


class Scraper(RequestScraper):
    
    @property
    def base_url(self):
        '''
        
        '''
        return 'http://www.illinoiscourts.gov/Opinions/'

    def archive_supreme(self, year):
        '''
        Gets recent IL supreme court page
        
        Args:
            year(int): year opinion was issued
            
        Returns:
            requests_html.HTMLResponse
            
        '''
        url = f'{self.base_url}SupremeCourt/{year}/default.asp'
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
        url = f'{self.base_url}recent_supreme.asp'
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
            
