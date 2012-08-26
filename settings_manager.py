"""
Library for dealing with the various settings that come up, reading from file,
writing to file and various classes which are used to store the settings.

Settings are saved in a simple XML file.

@author: SquidneyPoitier <squidney.poitier@gmail.com>
@version: 0.1
"""

from lxml import etree;
from os import path;
from general_utils import *;

from error_handling import CompatibilityException, SettingsManagerError, ModeException;

current_version = 0.1; # Settings version, not program version.
dflt_settings_file = path.join(path.dirname(__file__), 'settings'+path.sep+'config.xml');
dflt_modes_location = path.join(path.dirname(__file__), 'modes');

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
            if(fmode == None or not fvers.modeLocAttrib in fmode.attrib):
                return None;
            
            fileLoc = fmode.attrib[fvers.modeLocAttrib];
            if(fileLoc == None):
                return None;
            
            # By default, file locations that are not absolute locations are taken to be relative 
            # to the default 'modes' location.
            if(not path.isabs(fileLoc)):
                fileLoc = path.join(dflt_modes_location, fileLoc);
            
            return fetchMode(fileLoc);            
                        
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
    
    modeparser = etree.XMLParser(remove_blank_text=True,remove_comments=True);
    parsers = {
               'HTML' : etree.HTMLParser(),
               'XML' : etree.XMLParser()
               };
    
    titleLoc = None;
    authorLoc = None;
    citeLoc = {
               'journal' : None,
               'volume' : None,
               'issue' : None,
               'pages' : None,
               'doi' : None,
               'year' : None
               };
               
    suppInfo = {
                'title' : None,
                'pdf' : None,
                'desc' : None
                };
    
    def __init__(self, modeFile):
        """
        Provide a name and various parameters to create the class object.
        
        @param modeFile: String which is the absolute path pointing to the xml file containing the
                        mode specifications.
        """
                
        tree = etree.parse(modeFile, self.modeparser);
        root = tree.getroot();
        
        fvers = self.fvers = CompatibilityHelper(root);
        
        self.name = root.attrib[fvers.ModeXML.name];
        self.nsteps = int(root.attrib[fvers.ModeXML.nsteps]);
        
        # Parse out the steps
        sparsers = [None]*self.nsteps;
        links = [None]*(self.nsteps-1);
        
        for step in root.findall(fvers.ModeXML.step):
            i = int(step.attrib[fvers.ModeXML.num]);
            print(step.attrib[fvers.ModeXML.parser]);
            sparsers[i] = self.parsers[step.attrib[fvers.ModeXML.parser]];
        
            # Parse out the steps we need - start with the links.
            ll = step.find(fvers.ModeXML.linkLoc);
            if i != self.nsteps-1 and ll == None:
                raise ModeException(ModeException.ERR_NO_LINK);
            elif ll != None:
                links[i] = self.parseLoc(ll);
                if fvers.ModeXML.articleLink in ll.attrib and \
                    boolString(ll.attrib[fvers.ModeXML.articleLink]):
                    self.aLinkStep = i;
            
            # Check for the title
            if self.titleLoc == None:
                tl = step.find(fvers.ModeXML.titleLoc);
                if tl != None:
                    if fvers.ModeXML.useLinkText in tl.attrib and \
                    boolString(tl.attrib[fvers.ModeXML.useLinkText]):
                        titleLoc = links[i];
                        titleLoc[-1].set_at(None);
                        self.titleLoc = self.Loc(titleLoc, i);
                    else:
                        self.titleLoc = self.Loc(self.parseLoc(tl), i);
            
            # Check for the author list
            if self.authorLoc == None:
                al = step.find(fvers.ModeXML.authorLoc);
                if al != None:
                    self.authorLoc = self.Loc(self.parseLoc(al), i);
            
            # Check for a citation location.
            cl = step.find(fvers.ModeXML.citeLoc);
            if(cl != None):
                jl = cl.find(fvers.ModeXML.journalName);
                if(jl != None):
                    self.citeLoc['journal'] = self.Loc(self.parseLoc(jl), i);
                
                vl = cl.find(fvers.ModeXML.volume);
                if(vl != None):
                    self.citeLoc['volume'] = self.Loc(self.parseLoc(vl), i);
                
                il = cl.find(fvers.ModeXML.issue);
                if(il != None):
                    self.citeLoc['issue'] = self.Loc(self.parseLoc(il), i);
                
                pl = cl.find(fvers.ModeXML.pages);
                if(pl != None):
                    self.citeLoc['pages'] = self.Loc(self.parseLoc(pl), i);
                
                dl = cl.find(fvers.ModeXML.doi);
                if(dl != None):
                    self.citeLoc['doi'] = self.Loc(self.parseLoc(dl), i);
                
                yl = cl.find(fvers.ModeXML.year);
                if(yl != None):
                    self.citeLoc['year'] = self.Loc(self.parseLoc(yl), i);
            
            # Find supplementary information
            if self.suppInfo == None:
                sl = step.find(fvers.ModeXML.suppInfo);
                if(sl != None):
                    slp = self.parseTag(sl);
                    
                    tl = step.find(fvers.ModeXML.title);
                    if(tl != None):
                        self.suppInfo['title'] = self.Loc(self.parseLoc(tl, slp), i);
                    
                    pl = step.find(fvers.ModeXML.pdf);
                    if(pl != None):
                        self.suppInfo['pdf'] = self.Loc(self.parseLoc(pl, slp), i);
                    
                    dl = step.find(fvers.ModeXML.desc);
                    if(dl != None):
                        self.suppInfo['desc'] = self.Loc(self.parseLoc(dl, slp), i);
            
        self.sparsers = sparsers;        
        self.links = links;
        
    def parseLoc(self, element, parent=None):
        '''
        Give an element in the tree that is of the 'Loc' type, and this will parse it into a list
        of the nested tags where you can find the object.
        
        @param element: The element you're interested in.
        @param parent: The parent element of the list. Pass None to detect from the tag itself.
        @return: Returns a list of tags.
        '''
        
        fvers = self.fvers;
        if(parent == None):
            parent = self.parseTag(element);
           
        tags = [parent];
        for child in element:
            tags.append(self.parseTag(child));
                    
        # Check if the final tag has an 'at' attribute.
        child = element[-1];
        if(fvers.ModeXML.attrib in child.attrib):
            tags[-1].set_at(child.attrib[fvers.ModeXML.attrib]);
        
        return tags;
    
    def parseTag(self, element):
        '''
        Called to parse a given tag in the list of the 'Loc' type things. They can have a tag named
        'tag' to specify the name, otherwise the text itself specifies the name.
        
        @param element: The element in the tree.
        @return: Returns a Tag item.
        @raise ModeException:  Raises this in the event of no specified name. 
        '''
        
        fvers = self.fvers;
        
        if fvers.ModeXML.tag in element.attrib:             
            tag = element.attrib[fvers.ModeXML.tag];
        elif element.text != None:
            tag = element.text;
        else:
            raise ModeException(ModeException.ERR_NO_TAG);
        
        if(fvers.ModeXML._class in element.attrib):
            _class = element.attrib[fvers.ModeXML._class];
        else:
            _class = None;
          
        if(fvers.ModeXML._id in element.attrib):
            _id = element.attrib[fvers.ModeXML._id];
        else:
            _id = None;
            
        return self.Tag(tag, _class, _id);        
                    
    def allTags(self, tag):
        '''
        Basically take the given tag and add .// to the beginning, for a recursive search of the 
        XML tree.
        
        @param tag: String, a given tag.
        @return: Returns the find-all-recursive version of the tag.
        '''
        
        return './/'+tag;
    
    class Loc:
        '''
        Class for specifying locations and such.
        '''
        
        def __init__(self, tags, step):
            '''
            Instantiate the class with a list of tags locating the relevant information and the 
            step number that it's in (0-based index.);
            
            @param tags: List of Tag items.
            @param step: int, the step it's on.
            '''
            self.tags = tags;
            self.step = step;
    
    class Tag:
        '''
        Class for specifying a kind of tag.
        '''
        
        name = None;
        _class = None;
        _id = None;
        _at = None;
        
        def __init__(self, name, _class=None, _id=None, _at=None):
            '''
            Instantiate the class with the name, and, optionally, the class and id.
            
            @param name: The name of the tag (e.g. 'a', 'div', etc.)
            @param _class: The class of the tag (css, etc)
            @param _id: The id of the tag.
            @param _at: The attribute to use (final tags only)
            '''
            
            self.name = name;
            self._class = _class;
            self._id = _id;
        
        def has_id(self):
            return (not self._id == None);
        
        def has_class(self):
            return (not self._class == None);
        
        def use_at(self):
            return (not self._at == None);
        
        def get_class(self):
            return self._class;
        
        def get_id(self):
            return self._id;
        
        def get_at(self):
            return self._at;
        
        def set_id(self, val):
            self._id = val;
        
        def set_class(self, val):
            self._class = val;
        
        def set_at(self, val):
            self._at = val;
            

class CompatibilityHelper:
    """
    Helper class for dealing with settings file compatibility issues.
    """
    max_version = current_version;
    first_version = 0.1;
    
    modesTag = 'Modes';
    versionTag = 'version';
    
    modeLocAttrib = 'location';
    
    
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
    
    
    class ModeXML:
        '''
        Subclass containing information about how to parse Mode XML files. Put in this subclass 
        to isolate the namespaces.
        '''
        
        # Tags
        step = 'Step';   # Tag for each given step
        
        titleLoc = 'titleLoc';  
        linkLoc = 'linkLoc';    
        authorLoc = 'authorLoc';
        pdfLoc = 'pdfLoc';
        citeLoc = 'citeLoc';
        suppInfo = 'suppInfo';
        
        # Citation-specific tags        
        journalName='journalName';
        volume = 'volume';
        pages = 'pages';
        doi = 'doi';
        issue = 'issue';
        year = 'year';
        
        # Supplemental Information-specific tags
        pdf = 'pdf';
        desc = 'desc';
        title = 'title';
        
        # Attributes
        name = 'name';      # For the name of a given object, mode, etc.
        nsteps = 'nsteps';
        num = 'n';          # For ordering steps
        parser = 'parser';
        _class = 'class';
        tag = 'tag';
        _id = 'id';
        attrib = 'at';
        
        # Specific sub-tags.
        useLinkText = 'useLinkText';
        articleLink = 'articleLink';