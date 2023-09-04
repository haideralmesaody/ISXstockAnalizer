import sys
from PyQt5 import QtWidgets
from MainGUI import MainGUI
from MainLogic import MainLogic
from LoggerFunction import Logger
from app_config import DEBUG

def main():
    try:
        # Initialize logging
        logger = Logger(DEBUG)
        logger.log_or_print("Main: Starting application...", level="DEBUG", module="Main")
        
        # Initialize the Qt Application
        app = QtWidgets.QApplication(sys.argv)

        # Instantiate the MainGUI and MainLogic classes
        main_gui = MainGUI()
        main_logic = MainLogic(main_gui)  # Assuming MainLogic needs a reference to MainGUI

        # It's assumed that MainLogic will handle connections between MainGUI's signals and its own slots

        # Show the GUI
        main_gui.show()
        logger.log_or_print("Main: Displayed GUI.", level="DEBUG", module="Main")

        # Start the Qt event loop
        sys.exit(app.exec_())

    except Exception as e:
        logger.log_or_print(f"An unexpected error occurred in main: {str(e)}", level="ERROR", module="Main")
        sys.exit(1)

if __name__ == "__main__":
    main()
