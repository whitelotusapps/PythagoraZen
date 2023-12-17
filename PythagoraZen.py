import importlib
import inspect
import logging
import os
import sys
import traceback

from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from framework.logging_handler import PythagoraZenLogger

pythagorazen_logger = PythagoraZenLogger()
pythagorazen_logger.create_logfile()
pythagorazen_logger.configure_logging()        

from framework.credential_database_operations import CredentialDatabaseOperations
from framework.credential_database_settings_dialog import (
    CredentialDatabaseSettingsDialog,
)
from framework.plugin_window import PluginWindow  # Import from the new plugin
from framework.signal_manager import SignalManager


os.system("clear")

# Add the parent directory of the main_app folder to the Python path
root_application_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(root_application_dir)
logging.debug(f"current_dir: {root_application_dir}")
logging.debug(f"parent_dir : {parent_dir}")
sys.path.append(parent_dir)


class PluginManager:
    def __init__(self, main_app):
        self.main_app = main_app

    def discover_plugins(self, plugin_directory):
        plugins = []
        for filename in os.listdir(plugin_directory):
            if filename.endswith(".py"):
                plugin_name = os.path.splitext(filename)[0]
                plugins.append(plugin_name)
        return plugins


class ZendeskAdminApp(QMainWindow):
    # Define plugin_windows at the class level
    plugin_windows = {}

    def __init__(self):
        super().__init__()
        self.signal_manager = SignalManager()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")        
        self.initDatabase()

        # Initialize a list to keep track of open plugin windows
        self.open_plugin_windows = []

        # Store loaded plugin instances
        self.loaded_plugins = self.load_plugins()

        self.init_ui()

    def load_plugins(self):
        # Instantiate the PluginManager and call discover_plugins to load plugins
        plugin_manager = PluginManager(self)
        plugin_names = plugin_manager.discover_plugins("pythagorazen_plugins")

        # Dynamically instantiate plugins and store references to plugin windows
        plugins = []

        for plugin_name in plugin_names:
            try:
                plugin = importlib.import_module(f"pythagorazen_plugins.{plugin_name}")
                plugin_class = getattr(plugin, "Plugin")
                plugin_instance = plugin_class(self, self.signal_manager)

                # Check if the plugin passes the criteria
                if not self.passes_criteria(plugin_instance):
                    logging.warning(
                        f"PLUGIN SKIPPED (does not pass criteria): {plugin_instance.plugin_name}"
                    )
                    continue

                # Store references to plugin windows using the name
                window_name = plugin_instance.plugin_name

                if plugin_instance.requires_plugin_window():
                    if window_name not in ZendeskAdminApp.plugin_windows:
                        # Only create a PluginWindow if it doesn't exist
                        plugin_window = PluginWindow(plugin_instance, window_name)
                        ZendeskAdminApp.plugin_windows[window_name] = plugin_window

                logging.info(f"PLUGIN LOADED: {plugin_instance.plugin_name}")
                plugins.append(plugin_instance)

            except Exception as e:
                # Log detailed traceback information
                logging.error(f"Error loading plugin '{plugin_name}': {e}")
                tb = traceback.format_exc()
                logging.error(f"Traceback:\n{tb}")

        # Now that the plugin windows are created, connect the signals
        for plugin_instance in plugins:
            try:
                plugin_name = plugin_instance.plugin_name
                if plugin_instance.requires_plugin_window():
                    plugin_window = ZendeskAdminApp.plugin_windows[plugin_name]
                    plugin_instance.update_content_signal.connect(
                        plugin_window.update_content
                    )
            except Exception as e:
                logging.error(
                    f"Error connecting signals for plugin '{plugin_name}': {e}"
                )

        return plugins

    def passes_criteria(self, plugin_instance):
        # Define your criteria functions here
        required_criteria_functions = [
            lambda plugin: plugin.supports_mongodb(),
            # Add more required criteria functions
        ]

        optional_criteria_functions = [
            lambda plugin: plugin.supports_pagination(),
            # Add optional criteria functions
        ]

        # Check if the plugin passes all required criteria functions
        required_result = all(
            criteria_func(plugin_instance)
            for criteria_func in required_criteria_functions
        )

        # Check if the plugin passes any optional criteria functions
        optional_result = any(
            criteria_func(plugin_instance)
            for criteria_func in optional_criteria_functions
        )

        # The final result is True only if it passes all required criteria and at least one optional criteria
        # result = required_result and optional_result
        result = required_result

        # Print the plugin name and the result of the criteria check
        logging.debug(f"CHECKING PLUGIN: {plugin_instance.plugin_name}")
        if required_result:
            logging.info(f"passes required criteria: {required_result}")
        else:
            logging.error(f"passes required criteria: {required_result}")

        if optional_result:
            logging.info(f"passes optional criteria: {optional_result}")
        else:
            logging.info(f"passes optional criteria: {optional_result}")

        if result:
            logging.info(f"passes overlall criteria: {result}")
        else:
            logging.error(f"passes overlall criteria: {result}")

        return result

    def initDatabase(self):
        self.database_operations = CredentialDatabaseOperations()

    def init_ui(self):
        # Create a central widget to hold the buttons
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget (e.g., QVBoxLayout)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Add a new action to the File menu
        database_settings_action = QAction("Database Settings", self)
        database_settings_action.triggered.connect(self.open_database_settings)
        file_menu.addAction(database_settings_action)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Zendesk Admin App")
        self.show()

        h = QHBoxLayout()

        # ORIGINAL CODE
        for plugin in self.loaded_plugins:
            button_text = plugin.plugin_name
            button = QPushButton(button_text)
            # Pass the plugin_name directly, not inside a lambda function
            button.pressed.connect(
                lambda plugin_name=plugin.plugin_name: self.toggle_plugin_window(
                    plugin_name
                )
            )

            h.addWidget(button)

        layout.addLayout(h)
        self.label = QLabel("")
        layout.addWidget(self.label)

    def toggle_plugin_window(self, plugin_name):
        # Case-insensitive matching
        matching_windows = [
            window
            for name, window in self.plugin_windows.items()
            if name.lower() == plugin_name.lower()
        ]

        if matching_windows:
            window = matching_windows[0]
            if window.isVisible():
                window.hide()
            else:
                # Find the plugin instance associated with the plugin_name
                plugin_instance = next(
                    (
                        plugin
                        for plugin in self.loaded_plugins
                        if plugin.plugin_name.lower() == plugin_name.lower()
                    ),
                    None,
                )
                if plugin_instance:
                    # Connect the plugin's update_content_signal to the window's update_content method
                    plugin_instance.update_content_signal.connect(window.update_content)
                    # Call the interact method of the plugin instance
                    plugin_instance.interact(window)

                # Show the window only if the plugin's show_window flag is True
                if plugin_instance.show_window:
                    window.show()
                else:
                    logging.info(f"Window remained hidden for plugin: {plugin_name}")
        else:
            logging.warning(f"No plugin window found for {plugin_name}")

    def open_database_settings(self):
        database_settings_dialog = CredentialDatabaseSettingsDialog(
            self, self.database_operations
        )
        if database_settings_dialog.exec_() == QDialog.Accepted:
            # Handle the accepted action (e.g., update UI based on new settings)
            logging.info("Database settings saved.")
            # Optionally update UI or perform other actions based on the new settings
            # For example, you could update the instance dropdown menu

            # Repopulate the instance dropdown after updating the settings
            self.populate_instance_dropdown()


def main():
    global app  # Declare 'app' as a global variable
    app = QApplication([])
    # Initialize PythagoraZen and configure logging globally

    # Set the default font size for the entire application
    default_font = app.font()
    default_font.setFamily("Verdana")
    default_font.setPointSize(12)  # Set the desired font size
    app.setFont(default_font)
    ex = ZendeskAdminApp()

    try:
        app.exec_()
    except Exception as e:
        logging.error(f"An exception occurred: {e}")
        # import traceback
        # traceback.print_exc()


if __name__ == "__main__":
    main()
