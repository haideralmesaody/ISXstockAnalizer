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

        # Initialize the Qt Application
        app = QtWidgets.QApplication(sys.argv)

        # Instantiate the MainGUI and MainLogic classes
        main_gui = MainGUI()
        # Assuming MainLogic needs a reference to MainGUI
        main_logic = MainLogic(main_gui)

        # It's assumed that MainLogic will handle connections between MainGUI's signals and its own slots

        # Show the GUI
        main_gui.show()

        # Start the Qt event loop
        sys.exit(app.exec_())

    except Exception as e:

        sys.exit(1)


if __name__ == "__main__":
    main()
