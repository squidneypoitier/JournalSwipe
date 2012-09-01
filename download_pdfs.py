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
       
        # Build the step items
        
        
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
        
    def parseStep(self, step):
        '''
        This function is called recursively and is used to step through all
        the sub-branches of a given step.
        
        e.g. For a mode where Step 1 finds a list of subsections, Step 2
        has a list of articles and Step 3 has a link to the actual articles,
        the tree will look like this:
        
        Step 1      ->    Step 2a     ->   Step 3a-a
                                      ->   Step 3a-b
                                      ->   Step 3a-c
                    ->    Step 2b     ->   Step 3b-a
                                      ->   Step 3b-b
                                      ->   Step 3b-c
                        ...
        
        Since it is not known until the parsing has already been done how 
        many substeps there will be at each point, once the number of 
        substeps of a given step have been parsed, it can iterate over each
        of the substeps and flesh out the matrix structure of the tree.
        
        Since this operation is by its very nature highly parallel, we'll 
        try to do this in as threadsafe a manner as possible, to allow for
        code optimisation.
        
        @param step: A Step item telling us what we are looking for on a 
                    given step.
        @return: Returns a Branch item with information about the full tree
                substructure
        '''
        pass

            
        
                
            
