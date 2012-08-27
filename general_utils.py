'''
Library containing various general utilities that can be used out of convenience.

@author: SquidneyPoitier <squidney.poitier@gmail.com>
@version: 0.1
'''

def boolString(val):
    '''
    If you pass a string to this, it checks against common values that should evaluate to 'true'
    
    The relevant values are (case-insensitive):
        true
        t
        1
        yes
        y
        
    @param val: String whose truth value you'd be interested in.
    @return: Boolean of whether or not it's true.
    '''
    
    return val.lower() in ['true', 't', '1', 'yes', 'y'];