"""

  This code is released under the GNU Affero General Public License.
  
  OpenEnergyMonitor project:
  http://openenergymonitor.org

"""

import urllib2
import time
import logging
import csv
import urlparse
from configobj import ConfigObj

"""class EmonHubInterface

User interface to communicate with the hub.

The settings attribute stores the settings of the hub. It is a
dictionnary with the following keys:

        'hub': a dictionary containing the hub settings
        'listeners': a dictionary containing the listeners
        'dispatchers': a dictionary containing the dispatchers

        The hub settings are:
        'loglevel': the logging level
        
        Listeners and dispatchers are dictionaries with the folowing keys:
        'type': class name
        'init_settings': dictionary with initialization settings
        'runtime_settings': dictionary with runtime settings
        Initialization and runtime settings depend on the listener and
        dispatcher type.

The run() method is supposed to be run regularly by the instanciater, to
perform regular communication tasks.

The check_settings() method is run regularly as well. It checks the settings 
and returns True is settings were changed.

This almost empty class is meant to be inherited by subclasses specific to
each user interface.

"""
class EmonHubInterface(object):

    def __init__(self):
        
        # Initialize logger
        self._log = logging.getLogger("EmonHub")
        
        # Initialize settings
        self.settings = None

    def run(self):
        """Run in background. 
        
        To be implemented in child class.

        """
        pass

    def check_settings(self):
        """Check settings
        
        Update attribute settings and return True if modified.
        
        To be implemented in child class.
        
        """
    
    def get_settings(self):
        """Get settings
        
        Returns None if settings couldn't be obtained.

        To be implemented in child class.
        
        """
        pass

class EmonHubFileInterface(EmonHubInterface):

    def __init__(self, filename):
        
        # Initialization
        super(EmonHubFileInterface, self).__init__()

        # Initialize update timestamp
        self._settings_update_timestamp = 0
        self._retry_time_interval = 60

        # Initialize attribute settings as a ConfigObj instance
        try:
            self.settings = ConfigObj(filename, file_error=True)
        except IOError as e:
            raise EmonHubInterfaceInitError(e)
        except SyntaxError as e:
            raise EmonHubInterfaceInitError( \
                'Error parsing config file \"%s\": ' % filename + str(e))

    def check_settings(self):
        """Check settings
        
        Update attribute settings and return True if modified.
        
        """
        
        # Check settings only once per second
        now = time.time()
        if (now - self._settings_update_timestamp < 1):
            return
        # Update timestamp
        self._settings_update_timestamp = now
        
        # Backup settings
        settings = dict(self.settings)
        
        # Get settings from file
        try:
            self.settings.reload()
        except IOError as e:
            self._log.warning('Could not get settings: ' + str(e))
            self._settings_update_timestamp = now + self._retry_time_interval
            return
        except SyntaxError as e:
            self._log.warning('Could not get settings: ' + 
                              'Error parsing config file: ' + str(e))
            self._settings_update_timestamp = now + self._retry_time_interval
            return
        except Exception:
            import traceback
            self._log.warning("Couldn't get settings, Exception: " + 
                traceback.format_exc())
            self._settings_update_timestamp = now + self._retry_time_interval
            return
        
        if self.settings != settings:
            return True

"""class EmonHubInterfaceInitError

Raise this when init fails.

"""
class EmonHubInterfaceInitError(Exception):
    pass
