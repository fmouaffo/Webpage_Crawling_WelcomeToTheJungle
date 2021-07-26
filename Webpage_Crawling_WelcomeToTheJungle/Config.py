import os # import os package which will be used for path jointure

#Configuration file
HOME_FOLDER = os.path.join('.')     # provide the local directory where the driver is located
DRIVER_NAME = 'chromedriver.exe'    # give the driver name
DRIVER_TYPE = 'Chrome'              # give the driver path
DRIVER_PATH = os.path.join(HOME_FOLDER, DRIVER_NAME)

Language = 'french'  # choose between french and english