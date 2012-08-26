"""
Library for interacting with the publication's web site to find and download the PDFs as individual 
files for later assembly.

@author: SquidneyPoitier <squidney.poitier@gmail.com>
@version: 0.1
"""
import settings_manager as SettingsManager;
from lxml import etree;
import urlparse;

class PDFDownloader:
    """
    Class for containing a single instance of PDF downloading.
    """
    
    # Class variables
    url = '';               # URL for the table of contents
    use_mode = '';          # What method to search journal - hash key.
    download_loc = '';      # Download location TODO: Replace with default.
    fmode = None;
    
    def __init__(self, toc_url, use_mode):
        '''
        Instantiate the class with the URL from the table of contents of the
        issue and the hash key for the use mode.
        
        @param toc_url:    String, table of contents URL.
        @param use_mode:   String, hash key to the journal settings.
        '''
        
        # Get the use mode.
        sr = SettingsManager.SettingsReader();
        try:
            self.fmode = sr.getMode(use_mode);
            fmode = self.fmode;
        except:
            raise;
        
        self.url = toc_url;
        url = self.url;
        
        self.base_url = urlparse.urlparse(url).netloc;
        base_url = self.base_url;
       
        # Execute the steps, in order, and capture things.
        
        
        # Build the tables of contents from the URL.
       
        ''' 
        Invalid code, for the moment.
       
        tree = etree.parse(url, parser=parser, base_url=base_url);
        
        all_articles = tree.findall(fmode.allTags(fmode.articleTag));
        
        # Null-initialization of these tables.
        nArticles = len(all_articles);
        self.nArticles = nArticles;
        self.titles = ['']*nArticles;
        self.links = ['']*nArticles;        
        self.authors = [['']]*nArticles;
        self.abstract = ['']*nArticles;
        
        # Iterate through the table of contents and generate the table.
        for i, article in enumerate(all_articles):
            link = article.find('.//a');
            if(link == None):
                print(etree.tounicode(article));
                continue;
                
            self.titles[i] = link.text;
            self.links[i] = link.get('href');
        '''
        
        
        
