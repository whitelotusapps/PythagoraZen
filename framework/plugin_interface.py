import inspect
import os


class PluginInterface:
    """
    def initialize(self):
        pass
    """

    def interact(self, main_app):
        pass

    def cleanup(self):
        pass

    def supports_pagination(self):
        return False  # By default, plugins do not support pagination

    def filename(self):
        # Get the filename of the calling file, excluding plugin_interface.py
        calling_frame = inspect.stack()[1]
        calling_filename = os.path.basename(calling_frame[0].f_code.co_filename)

        print(f"\nFILE: {calling_filename}")
