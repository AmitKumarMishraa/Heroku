import requests,pprint
import configparser
import json

config = configparser.ConfigParser()
config.read('config.ini')

#fetching the latest available reviews
last_modified=int(config['User-Info']['lastModified'])

print 'latest reviews stored'
print 'updated ' + str(last_modified) + ' seconds ago'

#generating access token

refresh_token=config['DEFAULT']['refresh_token']
client_id=config['DEFAULT']['client_id']
client_secret=config['DEFAULT']['client_secret']
app_id=config['DEFAULT']['app_id']
shop_id=config['DEFAULT']['shop_id']



maxResults = config['DEFAULT']['maxResults']
URL = "https://accounts.google.com/o/oauth2/token?refresh_token="+refresh_token+"&client_id="+client_id+"&client_secret="+client_secret+"&grant_type=refresh_token"
refresh_token_response = requests.post(url=URL)
data = refresh_token_response.json()
access_token = data['access_token']
url2 = config['DEFAULT']['url']
headers = {
        'Content-Type': 'application/json',
    }

#getting google reviews
#try:
URL = "https://www.googleapis.com/androidpublisher/v2/applications/"+app_id+"/reviews?access_token="+str(access_token)+"&maxResults="+maxResults
temp1_reviews_page = requests.get(url=URL)
reviews_page = temp1_reviews_page.json()
x = reviews_page['reviews']

#filtering review fields

y = {}
a = {}
y = x[0]
a = {'authorName': y['authorName']}
a['reviewId'] = y['reviewId']
z = y['comments']
for r in z:
	p = {'comments':r}
	a.update(p['comments'])
reviews_dict = {'review': {
'shop_id': shop_id,
'rating': a['userComment']['starRating'],
'rating_parameter':[{
	'field_id':'primary_rating',
	'question_type':'rating',
	'component_type':'Itms-emoticon-rater',
	'rating': a['userComment']['starRating']
}],
'comments':a['userComment']['text'],
'user_info':{
	'name': a['authorName'],
	'customer_id': a['reviewId']
},
'tag_review_id': a['reviewId'],
'tag_review_id': a['reviewId'],
'tag_device': a['userComment']['device'],
'tag_android_os_version': a['userComment']['androidOsVersion'],
'tag_app_version_code': a['userComment']['appVersionCode'],
'tag_app_version_name': a['userComment']['appVersionName'],
'tag_likes': a['userComment']['thumbsUpCount'],
'tag_dislikes': a['userComment']['thumbsDownCount'],
'tag_product_name': a['userComment']['deviceMetadata']['productName']

}}
if 'developerComment' in a:
			reviews_dict['review'].update({'developerComment': a['developerComment']['text']})	
#pprint.pprint(reviews_dict)

data = reviews_dict['review']
#pprint.pprint(data)
#checking for the redundent review
 

last_modified_response_temp=a['userComment']['lastModified']['seconds']
last_modified_response=int(a['userComment']['lastModified']['seconds'])

print 'new fetched reviews'
print 'review updated '+str(last_modified_response)+' seconds ago'
if last_modified < last_modified_response:
	print 'new reviews are added'
	response = requests.post(url=url2,headers=headers, data=json.dumps(data))
	response_j = response.json()
	pprint.pprint(response_j)
	print 'review posted'
#except KeyError as error:
		#print "No review available"

#getting the reviews on next page
	while "tokenPagination" in reviews_page:
		
		next_page_token = reviews_page["tokenPagination"]["nextPageToken"]
		del reviews_page["tokenPagination"]
		next_page_request = URL+"&token="+next_page_token	
		temp2_reviews_page = requests.get(url=next_page_request)
		reviews_page = temp2_reviews_page.json()
		
		#filtering reviews fields
		
		try:
		
			x = reviews_page['reviews']#['reviewId']
			y = {}
			a = {}
			y = x[0]
			a = {'authorName': y['authorName']}
			a['reviewId']= y['reviewId']
			z = y['comments']
			for r in z:
				p = {'comments':r}
				a.update(p['comments'])
				reviews_dict = {'review': {
				'shop_id': shop_id,
				'rating': a['userComment']['starRating'],
				'rating_parameter':[{
				'field_id':'primary_rating',
				'question_type':'rating',
				'component_type':'Itms-emoticon-rater',
				'rating': a['userComment']['starRating']
				}],
				'comments':a['userComment']['text'],
				'user_info':{

				'name': a['authorName'],
				'customer_id': a['reviewId']
				},
			'tag_review_id': a['reviewId'],
			'tag_review_id': a['reviewId'],
			'tag_device': a['userComment']['device'],
			'tag_android_os_version': a['userComment']['androidOsVersion'],
			'tag_app_version_code': a['userComment']['appVersionCode'],
			'tag_app_version_name': a['userComment']['appVersionName'],
			'tag_thunps_up_count': a['userComment']['thumbsUpCount'],
			'tag_thumps_down_count': a['userComment']['thumbsDownCount'],
			'tag_product_name': a['userComment']['deviceMetadata']['productName']

			}}
				if 'developerComment' in a:
					reviews_dict['review'].update({'developerComment': a['developerComment']['text']})	
			print "next page---------------------------------------------------------------------------------------------------------------"
			#pprint.pprint(reviews_dict)
			data = reviews_dict['review']
			#pprint.pprint(data)
			
			
			last_modified_response=int(a['userComment']['lastModified']['seconds'])
			print 'new fetched reviews'
			print 'review updated '+str(last_modified_response)+' seconds ago'

			if last_modified < last_modified_response:
				print 'new reviews are added'
				response = requests.post(url=url2,headers=headers, data=json.dumps(data))
				response_j = response.json()
				pprint.pprint(response_j)
				print 'review posted'
			else:
				print 'Review already exists'
		except KeyError as error:
			print "End of page"
	config.set('User-Info', 'lastModified', last_modified_response_temp)
	with open('config.ini','w') as configfile:
		config.write(configfile)		
	print 'new reviews are added to the config'	
else:
	print 'No new review found'
#print '---------------------------------------------------------------------------------NEXT--------------------------------------------------------------------------------'