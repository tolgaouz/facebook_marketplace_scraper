Facebook Scraping

# How to obtain cookie.json file #
1-) Download firefox if you don't have already.

2-) Add the extension https://addons.mozilla.org/tr/firefox/addon/a-cookie-manager/ here

3-) Go to Facebook and login with the account that the scraper will work with

4-) Open Cookie Manager from top right corner of firefox browser

5-) Input "Facebook.com" to the filter by url or domain area.

6-) Search cookies

7-) Select all from bottom left

8-) Click More Actions dropdown, Export Selected Cookies

9-) Output Format : JSON, Export as file.

10-) put cookie.json in the same directory with script.



# How to get chrome driver #

1-) go to the link:https://chromedriver.chromium.org

2-) Download current stable release

3-) Put the downloaded chromedriver.exe inside same directory with script.

P.S: Contact me if you're going to use the script on MacOS because there are additional steps.



# How to install Python and dependencies #

1-) https://www.python.org/downloads/release/python-365/, download from here,

2-) After download, open a cmd in the directory of script

3-) Run this command, 'pip install selenium boto3 pymongo'


# How to run Script after all installations #
1-) Open a cmd in the same directory with script
2-) run this command 'python marketplace_worker.py --limit 50' # I set limit 50 here you can set whatever you wish

P.S: Make sure you put in your credentials to .py file, such as AWS Secret Key and Access Key, MongoDB url etc.
