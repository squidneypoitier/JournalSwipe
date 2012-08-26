'''
Module for dealing with error handling in the various packages.

@author: SquidneyPoitier <squidney.poitier@gmail.com>
@version: 0.1
'''

class JSError(Exception):
    '''
    Base class for exceptions in JournalSwipe. When subclassing this, one can set as properties a 
    number of error codes, with integer values != -1. 
    
    Instantiate the subclasses either with an integer error code, a message or an integer error
    code and a custom message. There are default messages for each error code.
    '''
    
    ERR_UNKNOWN = -1;
    
    @property
    def __dflt_err_strings(self):
        return {self.ERR_UNKNOWN: "An unknown exception has occurred."};
    
    __err_strings = property(__dflt_err_strings);
    _err_strings = {};
    
    def __init__(self, value=ERR_UNKNOWN, message=None):       
        if(isinstance(value, str)):
            message = value;
            value = self.ERR_UNKNOWN;
        
        if(message == None):
            message = self.err_string(value);
        
        self.err_code = value;
        self.value = message;
        
    def __str__(self):
        return repr(self.value);
    
    def err_string(self, code):
        es = dict(self.__dflt_err_strings.items() + self._err_strings.items());
         
        return es[code];

class SettingsManagerError(JSError):
    '''
    Class for errors in SettingsManager.SettingsReader and SettingsManager.SettingsWriter.
    '''
    
    ERR_BAD_TREE = -2;
    ERR_BAD_ROOT = -3;
    ERR_MODE_EXISTS = -4;
    
    _err_strings = {
        ERR_BAD_TREE : "A bad element tree was passed to the writer.",
        ERR_BAD_ROOT : "A bad root element was passed to the writer.",
        ERR_MODE_EXISTS: "The specified mode named already exists."
    };

class CompatibilityException(JSError):
    '''
    Class for version errors.
    '''
    
    ERR_FUTURE = -2;
    ERR_INVALID_VERSION = -3;
    
    _err_strings = {
         ERR_FUTURE : "The version value provided is a future version, compatibility is not guaranteed",
         ERR_INVALID_VERSION : "An invalid version was provided."
         };      
         
class ModeException(JSError):
    ''' 
    Class for errors in mode fetching.
    '''
    
    ERR_NO_LINK = -2;
    ERR_NO_TAG = -3;
    
    _err_strings = {
        ERR_NO_LINK : "Link locations must be specified from the first link to the page containing the PDF.",
        ERR_NO_TAG : "No tag was specified in a Mode XML location list."
                    };  
         
