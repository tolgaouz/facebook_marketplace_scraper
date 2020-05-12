from seleniumwire import webdriver  
import json
import urllib.request
import urllib.parse
import urllib
from selenium.webdriver.chrome.options import Options   
import boto3
import time
import pymongo
import platform
import os
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--limit', metavar='l', type=int, nargs='+',
                    help='limit of items to be scraped')
parser.add_argument('--images', metavar='i', type=bool, help='Should the images get downloaded and uploaded to S3 ?')
args = parser.parse_args()
print(args)

# Connecting MONGODB
client = pymongo.MongoClient("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
db = client.facebook_marketplace
col = db.items

# AWS CREDENTIALS
ACCESS_KEY = 'XXXXXXXXXXXXXXXXX'
SECRET_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
S3_BUCKET_URL = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' # Ex: https://bucket7474.s3.us-east-2.amazonaws.com/
S3_BUCKET_NAME = 'XXXXXXXXXXXXXXXXX' # Ex: bucket7474
MARKETPLACE_URL = 'https://www.facebook.com/marketplace/sydney/search/?query=dealership' # For Location Parameter

# Uploads images to aws
def upload_to_aws(local_file, bucket):
  s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY)

  try:
    s3.upload_file(local_file, bucket, local_file)
    print("Upload Successful")
    return True
  except FileNotFoundError:
    print("The file was not found")
    return False
  except:
    print("Credentials not available")
    return False

# Downloads the image, then uploads to s3
def handle_images(data,item_id):
  s3_image_links = []
  print('Images for item ID: '+str(item_id)+' are being downloaded.')
  for i,img_data in enumerate(data['listing_photos']):
    urllib.request.urlretrieve(img_data['image']['uri'], str(item_id)+"_"+str(i)+".jpg")
    print('Image '+str(item_id)+"_"+str(i)+".jpg"+' downloaded.')
    if upload_to_aws(str(item_id)+"_"+str(i)+".jpg",S3_BUCKET_NAME):
      s3_image_links.append(S3_BUCKET_URL+str(item_id)+"_"+str(i)+".jpg")
      os.remove(str(item_id)+"_"+str(i)+".jpg")
  return s3_image_links

def get_listing(a):
  if 'node' in a.keys():
    if 'listing' in a['node'].keys():
      if 'id' in a['node']['listing'].keys():
        return a['node']['listing']['id']
  return None

# Retrieves the next batch of data with fetch API
def get_id_batch(cursor=None,page_body=None):
  if cursor:
    page_body_dct = body_to_dict(page_body)
    variables_dct = json.loads(urllib.parse.unquote(page_body_dct['variables']))
    variables_dct['cursor'] = cursor
    variables_str = json.dumps(variables_dct)
    page_body_dct['variables'] = urllib.parse.quote(variables_str)
    page_body = dict_to_body(page_body_dct)
    pg = browser.execute_async_script(fetch,page_body,'function(dt){return dt}')
  else:
    pg = browser.execute_async_script(fetch,first_page_body.decode('ascii'),'function(dt){return dt}')
  next_cursor = pg['data']['marketplace_search']['feed_units']['page_info']['end_cursor']
  ids = [get_listing(a) for a in pg['data']['marketplace_search']['feed_units']['edges']]
  return {'next_cursor':next_cursor,'ids':ids}
        
# Gets data for given item_id
def get_item(item_request_body,item_id):
  dct = body_to_dict(item_request_body)
  product_id_dct = json.loads(urllib.parse.unquote(dct['variables']))
  product_id_dct['product_id']=item_id
  encoded_item_request_body = urllib.parse.quote(json.dumps(product_id_dct))
  dct['variables'] = encoded_item_request_body
  page_body = dict_to_body(dct)
  data = browser.execute_async_script(fetch,page_body,'function(dt){return dt}')
  return data

# Helper functions
def body_to_dict(body):
  body = body.decode('ascii')
  body_arr = body.split('&')
  dct = {}
  for b in body_arr:
      (key,val) = b.split('=')
      dct[key] = val
  return dct

def dict_to_body(dct):
  body_arr = []
  for i,(k,v) in enumerate(dct.items()):
      string = k+'='+v
      body_arr.append(string)
  return '&'.join(body_arr)

def get_item_request_body():
    item_request_body = None
    counter = 0
    time.sleep(5)
    while(counter<10):
        del browser.requests
        browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]').click()
        for request in browser.requests:
            item_request_body = request.body
        time.sleep(3)
        browser.find_element_by_css_selector('button[title="Close"]').click()
        if item_request_body: 
            return item_request_body
        else:
            counter+=1
    return None

# API Fetchers

# Fetchs first page of items
fetch = """
    console.log(arguments)
    let get_data = async ()=>{
        let x = await fetch("https://www.facebook.com/api/graphql/", {
              "headers": {
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/x-www-form-urlencoded",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin"
              },
              "referrer": "https://www.facebook.com/marketplace/item/3737004949707889/",
              "referrerPolicy": "origin-when-cross-origin",
              "body": arguments[0],
              "method": "POST",
              "mode": "cors",
              "credentials": "include"
            })
        return x.json()
        }
    get_data().then(dt=>{arguments[2](dt)})
    """
# Main Frame

if __name__=="__main__":
  chrome_options = Options()
  #chrome_options.add_argument("--headless") 
  #chrome_options.add_argument('--disable-dev-shm-usage')
  #chrome_options.add_argument('--no-sandbox')
  #chrome_options.add_argument("window-size=1920,1080")
  if platform.system()=='Darwin' or platform.system()=='Linux':
    browser = webdriver.Chrome(chrome_options=chrome_options)
  else:
    browser = webdriver.Chrome(executable_path='chromedriver.exe',chrome_options=chrome_options)
  print('Opening up chrome...')
  browser.get(MARKETPLACE_URL)
  with open('cookies.json') as json_file:
    data = json.load(json_file)
    for d in data['cookies']:
      if d['domain'][1:] in "https://facebook.com":
        cookie = {}
        for k,v in d.items():
          if k=='expirationDate':
            key = 'expiry'
            v = 3333333333
          else:
            key = k
          if key in ['name','domain','value','expiry','path','secure']:
            cookie[key] = v
        browser.add_cookie(cookie)
  browser.get(MARKETPLACE_URL)
  print('Successfully loaded cookies')

  # Access requests via the `requests` attribute
  cnt=0
  for request in browser.requests:
      if request.response and request.method=='POST' and ("/api/graphql/" in request.path):
          try:
              a = json.loads(request.response.body)
          except:
              pass
          if 'marketplace_search' in a['data'].keys():
              if 'MarketplaceSearchResultsPageContainerNewQuery' in request.body.decode('ascii'):
                  first_page_body = request.body
              elif 'MarketplaceNewSearchFeedPaginationQuery' in request.body.decode('ascii'):
                  page_body = request.body

  item_request_body = get_item_request_body()
  if item_request_body:
    counter = 0
    total_scraped = args.limit[0] if args.limit[0] else 30
    data = get_id_batch()
    print('Retrieved data for first batch')
    ids = data['ids']
    next_cursor = data['next_cursor']
    while(counter<total_scraped):
      print('This batch has total of',len(ids),'items to be scraped.')
      for i in range(len(ids)):
        item_id = ids[i]
        if item_id:
          if(col.find_one({'_id':item_id})): # If the id is already in DB, pass.
            print('This item_id is already in database, passing.')
            continue
          try:
            print('Scraping data for '+str(item_id))
            data = get_item(item_request_body,item_id)['data']['listingRenderable']
            print(data)
            print('Retrieved data for '+str(item_id))
            if args.images: # If images are set to True retrieve images as well.
              s3_image_links = handle_images(data,item_id)
            else:
              s3_image_links = []
            mongo_data = {'_id':item_id,
                      'data':data,
                      's3_image_links':s3_image_links}
            col.insert_one(mongo_data)
          except Exception as e:
            print(e)
            continue
          counter+=1
          print('Scraped data count:',counter)
        else:
          print('This item id was returned NULL, passing.')
      print('Retrieving new batch of data..')
      next_data = get_id_batch(next_cursor,page_body)
      ids = next_data['ids']
      print(ids)
      next_cursor = next_data['next_cursor']
  else:
    print("Couldn't retrieve data for item requests, please try again later or contact tolgaouzz@gmail.com")
  browser.close()
  exit()
    