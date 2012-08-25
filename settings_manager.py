"""
Library for dealing with the various settings that come up, reading from file,
writing to file and various classes which are used to store the settings.

Settings are saved in a simple XML file.

@author: GlocktopusPrime <glocktopusprime@gmail.com>
@version: 0.1
"""

from lxml import etree;
from os import path;

from error_handling import CompatibilityException, SettingsManagerError;

current_version = 0.1; # Settings version, not program version.
dflt_settings_file = path.join(path.dirname(__file__), 'settings'+path.sep+'config.xml');

class SettingsReader:
    """
    Class for reading settings from file. These methods are generally accessed
    in a static way.
    """
    fvers = None;  # File version
    stree = None;  # Settings tree, from file.
    settings_file = dflt_settings_file;
    
    
    def __init__(self, settings_file=settings_file):
        '''
        When instantiating this class, the XML tree is parsed and set as a 
        property, and compatibility is established.
        
        @param settings_file: The location of the settings file.
        '''
        parser = etree.XMLParser();
        self.stree = etree.parse(settings_file, parser);
        self.fvers = CompatibilityHelper(self.stree.getroot());
               
    def getMode(self, mode, settings_file=settings_file):
        """
        Method for reading a specific mode from file.
        
        @param mode: String, the name of the mode.
        @param settings_file: String, location of the settings file. Optional
        @return: Returns an object of class fetchMode, containing the fetch 
                settings.
        """
        
        fvers = self.fvers;
        tree = self.stree;
        
        if(tree == None or settings_file != self.settings_file):
            return SettingsReader(settings_file).getMode(mode, settings_file);
        
        # Parse the XML file and find the "Modes" element.
        try:   
            modes = tree.find(fvers.modesTag);
            if(modes == None):
                return None;
            
            fmode = modes.find(mode); # Find the appropriate mode in the file.
            if(fmode == None):
                return None;
            
            return fetchMode(fmode);            
                        
        except:
            raise;  
        

class SettingsWriter:
    """
    Class for writing settings to a file and updating a settings file.
    """
    
    settings_file = dflt_settings_file;
    rvers = None;
    wvers = None;
    rtree = None;
    root = None;
    
    def __init__(self, settings_file=settings_file):
        """
        If settings_file exists, it will be prepared for updating, otherwise 
        a new file will be created.
        
        @param settings_file: The location of the file where you'd like to save
                              the settings.
        """
        
        self.wvers = CompatibilityHelper();
        wvers = self.wvers;
        
        
        if(path.isfile(settings_file)):
            try:
                parser = etree.XMLParser();
                self.rtree = etree.parse(settings_file, parser);
                self.root = self.rtree.getroot();
                self.fvers = CompatibilityHelper(self.root);
            except:
                raise;
            
            # TODO: Make it so that if the version is lower than the current
            # version, the file will be updated to the newest version before
            # writing.
        else:
            try:
                root = etree.Element('root');
                root.set(wvers.versionTag, wvers.version);
                self.root = root;
                self.rtree = etree.ElementTree(root);
            except:
                raise;
            
        self.settings_file = settings_file;
        
    def write(self, settings_file=settings_file):
        """
        Updates the XML file from the existing tree structure, which you have
        hopefully updated now. The file will be written to the file 
        
        @param settings_file: String, the location where you'd like to save this
                            to file. If this file exists, it will be 
                            overwritten.
        """
        
        try:
            self.rtree.write(settings_file);
        except:
            raise;
        
    def add_mode(self, fmode, auto_rename=True, modes=None, modes_list=None):
        """
        Add a fetchMode object to the settings file. This will later need to be
        saved with the SettingsReader.write() method.
        
        @param fmode: A valid fetchMode object whose name does not match a name
                    in the list of existing fetchMode objects.
        @param auto_rename: Boolean - if this is set to true, in the event of
                    a duplicate mode name, _# will be appended to the provided
                    name.
        @param modes_list: List of strings containing all the mode names.
        @raise SettingsManagerError: Error raised if a bad root is passed or if 
                auto_rename is set to False and a duplicate name is passed.
        """
        
        # Start by getting the existing mode names.
        root = self.root;
        wvers = self.wvers;
        if root == None or not etree.iselement(root):
            raise SettingsManagerError(SettingsManagerError.ERR_BAD_ROOT);
        
        if modes == None:
            modes = root.find(wvers.modesTag);
            if modes == None:
                # This means no modes exist yet, we must also create the modes root
                modes = etree.SubElement(root, wvers.modesTag);
            
            modes_list = [];
        
        if modes_list == None:    
            modes_list = [];
            for child in modes:
                modes_list.append(child.tag);
            
        # Check if the mode name is in there.
        name = fmode.name;
        if name in modes_list:
            if auto_rename:
                # Check if it's already been numbered. This will cause some 
                # weirdness in naming if you name your modes like Nature_02
                # deliberately.
                u_loc = name.rfind('_');
                u_loc += 1;
                if u_loc > 1 and name[u_loc:].isdigit():
                    num = int(name[u_loc:]);
                    num += 1;
                    name = name[0:(u_loc-1)] + '{:02}'.format(num);
                else:
                    name = name + '_01';
                
                # Call this recursively until we get a good name. Pass
                # the parsed results so we don't have to parse them for
                # every iteration.
                return self.add_mode(fmode, auto_rename, modes, modes_list);
            else:
                raise SettingsManagerError(
                            SettingsManagerError.ERR_MODE_EXISTS);
                
        # Add the mode to the list
        # TODO: Update this when a mode specification is available.
        etree.SubElement(modes, fmode.name);
        

class fetchMode:
    '''
    Class which encapsulates the various things you'd want to know about how to
    do the actual fetching from the web site.
    '''
    
    articleTag = 'article';
    linkTag = 'a';
    dflt_parser = etree.HTMLParser(remove_blank_text=True);
    
    def __init__(self, name, parser=dflt_parser):
        """
        Provide a name and various parameters to create the class object.
        
        @param name: String, the name of the mode. (e.g. "Nature")
        """
        self.name = name;
        self.parser = parser;
        
    def allTags(self, tag):
        '''
        Basically take the given tag and add .// to the beginning, for a recursive search of the 
        XML tree.
        
        @param tag: String, a given tag.
        @return: Returns the find-all-recursive version of the tag.
        '''
        
        return './/'+tag;

class CompatibilityHelper:
    """
    Helper class for dealing with settings file compatibility issues.
    """
    max_version = current_version;
    first_version = 0.1;
    
    modesTag = 'Modes';
    versionTag = 'Version';
    
    def __init__(self, version=current_version):
        """
        Instantiates a CompatibilityHelper object, which contains various 
        version-specific information that helps maintain backwards-compatibility
        with older versions of settings files.
        
        @param version: Pass the root element of the file you're going to read 
                        and its version will be read out. Alternatively, pass
                        a float, as long as that float is a valid version.
                        Default for the parameter is the current version.
        
        @raise CompatibilityException: Raised if an invalid version is passed.
        """
        if(etree.iselement(version)):           
            # Retrieve the version from the root element.
            if self.versionTag in version.attrib:
                self.version = float(version.get(self.versionTag));
                version = self.version;
            else:
                raise CompatibilityException(CompatibilityException.ERR_INVALID_VERSION);
               
        else:
            self.version = version;
        
        # When more versions are out, if the tags have changed, we'll
        # go through an if/elif control here. For now, just check for
        # invalid versions.       
        if version > self.max_version:
            raise CompatibilityException(CompatibilityException.ERR_FUTURE);
        elif version < self.first_version:
            raise CompatibilityException(CompatibilityException.ERR_INVALID_VERSION);
            