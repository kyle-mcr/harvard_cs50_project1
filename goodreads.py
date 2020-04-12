import os,requests,xmltodict
API_KEY = os.environ["API_KEY"]

url = "https://www.goodreads.com/search/index.xml"
def make_request(param):
	res =requests.get(url,params={'key':API_KEY,'q':param})
	res = xmltodict.parse(res.content)
	doc = res["GoodreadsResponse"]['search']['results']['work']
	return doc

def get_reviews(book_id):
	res = requests.get("https://www.goodreads.com/book/show/{}.xml".format(book_id),\
							params={'key':API_KEY})
	res = xmltodict.parse(res.content)
	doc = res["GoodreadsResponse"]["book"]
	return doc