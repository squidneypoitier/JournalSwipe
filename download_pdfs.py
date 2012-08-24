"""
Library for interacting with the publication's web site to find and download 
the PDFs as individual files for later assembly.

@author: GlocktopusPrime
@version: 0.1
"""
import urllib2;

class PDFdownloader:
    """
    Class for containing a single instance of PDF downloading.
    """
    
    # Class variables
    url = '';               # URL for the table of contents
    use_mode = '';          # What method to search journal - hash key.
    download_loc = '';      # Download location TODO: Replace with default.
    
    timeout = 5;            # Timeout in seconds: TODO: pull from settings.
    def __init__(self, toc_url, use_mode):
        """
        Instantiate the class with the URL from the table of contents of the
        issue and the hash key for the use mode.
        
        @param toc_url:    String, table of contents URL.
        @param use_mode:   String, hash key to the journal settings.
        """
        
        # Open the URL
        try:
            open_url = urllib2.urlopen(toc_url, timeout=self.timeout);
            
            if(open_url == None):
                raise Exception();
        except:
            raise Exception('Failed to instantiate URL', toc_url);
        
        self.url = open_url;
        
        
                