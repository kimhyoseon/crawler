# Webcrawler


## Dependency

### Download Webdriver
- http://phantomjs.org/download.html
- http://selenium-python.readthedocs.io/installation.html#drivers

### ubuntu install
- ``sudo apt-get install libfontconfig``

### pip install
- ``pip install selenium``
- ``pip install beautifulsoup4``
- ``pip install python-telegram-bot``


## How to run
- ``python start.py --chrome --second=60``  - Run the crawling with chrome browser and repeat 1minitues
- ``nohup python -u start.py --second=300 &`` - Run the crawling on background and repeat 5mininutes
