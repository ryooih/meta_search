# -*- coding: utf-8 -*-

from django.shortcuts import render, render_to_response
from django.http import HttpResponse
import urllib
import urllib2
from bs4 import BeautifulSoup
import json
from selenium import webdriver
import re
import sys
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')

def search_api(request):
	site = request.GET.get('site', 'total')
	keyword = request.GET.get('keyword', 'None')
	sorted_by_price = request.GET.get('sort', '0')

	hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	       'Accept-Encoding': 'none',
	       'Accept-Language': 'en-US,en;q=0.8',
	       'Connection': 'keep-alive'}

	final_data = {}
	
	#홈앤쇼핑 크롤링

	results_tmp = []

	num_hns = int(0)
	if str(site) == "hns" or str(site) == "total" :  

		req_hns = urllib2.Request("http://www.hnsmall.com/search/search.do?viewtype=matrix&query="+str(keyword.encode('utf8').replace(" ", "%20"))+"&saveamt1=y&rowsPerPage=1000", headers=hdr)
		response_hns = urllib2.urlopen(req_hns)
		source_hns = response_hns.read()
		soup_hns = BeautifulSoup(source_hns, "lxml")

		
		try:
			num_hns = int(soup_hns.find("span", {"class" : "num" }).renderContents())
		except:
			pass
		result_hns = soup_hns.find_all("ul", {"class" : "goodsList imgSize220"})
		if result_hns :
			for itemrow in result_hns :
				for item in itemrow.find_all("li") :
				        tmp={}
				        tmp['mallname']="HNShopping"
				        tmp['img_src']=item.find("div", { "class" : "img"}).find("img").get("src")
				        tmp['itemName']=re.sub('<[^>]*>', '', item.find("p", { "class" : "goodsName"}).find("a").renderContents())
				        try:
				        	tmp['price']=int(re.sub("\D", "", item.find("p", { "class" : "sell"}).renderContents()))
				        except:
				        	tmp['price']=int(re.sub("\D", "", item.find("div", { "class" : "price_travel"}).renderContents()))
				        tmp['src']=item.find("p", { "class" : "goodsName"}).find("a").get("href")
				        results_tmp.append(tmp)
 						
	#CJmall 크롤링
	num_cj = int(0)
	if str(site) == "cj" or str(site) == "total" :
      
		req_cj = urllib2.Request("http://search.cjmall.com/search-web/search/cjmall/total.json?callback=callback&k="+keyword.encode('utf8').replace(" ", "%20")+"&cscg%5B%5D=TV%EC%87%BC%ED%95%91&chn=30001001&cis=100&firstSearch=TRUE&_=1476102774813")
		response_cj = urllib2.urlopen(req_cj)
		cj_list = json.loads(response_cj.read()[9:-2])

		
		for cj_results in cj_list['result'] :
			if cj_results['type'] == 'CJMALL_ITEM' and cj_results['rowCount'] > 0 :
				num_cj = cj_results['totalCount']
				for item in cj_results['rowDatas'] :
					tmp={}
					tmp['mallname'] = "CJmall"
					tmp['itemName'] =  item['itemNm']
					try : 
						tmp['price'] = int(item['pmgCustomerPrice'])
					except :
						tmp['price'] = int(0)
					tmp['img_src'] = "http://itemimage.cjmall.net/goods_images/"+str(item['coItemCd'])[:2]+"/"+str(item['coItemCd'])[-3:]+"/"+str(item['coItemCd'])+"M.jpg"
					tmp['src'] = "http://www.cjmall.com/prd/detail_cate.jsp?item_cd="+str(item['coItemCd'])
					results_tmp.append(tmp)

		#CJmall 수가 많을 경우
		if num_cj > 100 :
			for i in range((num_cj) / 100) :
				cof = (i+1) * 100
				req_cj = urllib2.Request("http://search.cjmall.com/search-web/search/cjmall/total.json?callback=callback&k="+keyword.encode('utf8').replace(" ", "%20")+"&cof="+cof+"&cscg%5B%5D=TV%EC%87%BC%ED%95%91&chn=30001001&cis=100&firstSearch=TRUE&_=1476102774813")
				response_cj = urllib2.urlopen(req_cj)
				cj_list = json.loads(response_cj.read()[9:-2])

				for cj_results in cj_list['result'] :
					if cj_results['type'] == 'CJMALL_ITEM' and cj_results['rowCount'] > 0 :
						for item in cj_results['rowDatas'] :
							tmp={}
							tmp['mallname'] = "cj"
							tmp['itemName'] =  item['itemNm']
							try : 
								tmp['price'] = int(item['pmgCustomerPrice'])
							except :
								tmp['price'] = int(0)
							tmp['img_src'] = "http://itemimage.cjmall.net/goods_images/"+str(item['coItemCd'])[:2]+"/"+str(item['coItemCd'])[-3:]+"/"+str(item['coItemCd'])+"M.jpg"
							tmp['src'] = "http://www.cjmall.com/prd/detail_cate.jsp?item_cd="+str(item['coItemCd'])
							results_tmp.append(tmp)	

	#GSeshop 크롤링    
	num_gs = 0
	if str(site) == "gs" or str(site) == "total" :

		req_gs = urllib2.Request("http://www.gsshop.com/search/main.gs?tq="+str(keyword.encode('utf8').replace(" ", "%20"))+"&lseq=390175&pt=60&cr_yn=Y&pg=1000&vt=B&is=N&ab=a#1&so=7&vt=B&pg=1000&po=0", headers=hdr)
		response_gs = urllib2.urlopen(req_gs)
		source_gs = response_gs.read()
		soup_gs = BeautifulSoup(source_gs, "lxml")
		
		try:
			num_gs = int(soup_gs.find("em", {"class" : "num"}).renderContents())
		except:
			pass
		tmp_item_gs = soup_gs.find("div", {"id" : "searchPrdList"})

		if tmp_item_gs:
			for item in tmp_item_gs.find_all("li") :
			    tmp={}
			    tmp['mallname']="GSshop"
			    tmp['img_src']=item.find("div", { "class" : "product-image-search"}).find("img").get("src")
			    tmp['itemName']=item.find("div", { "class" : "product-image-search"}).find("img").get("alt")
			    tmp['price']=int(re.sub("\D", "", item.find("span", { "class" : "set-price-search"}).renderContents()))
			    tmp['src']="http://www.gsshop.com/prd/prd.gs?prdid="+tmp['img_src'][-15:][:8]
			    results_tmp.append(tmp)

	if sorted_by_price == "1" :
		results_tmp = sorted(results_tmp, key = lambda x: x.get('price'))
	else :
		if sorted_by_price == "2" :
			results_tmp = sorted(results_tmp, key = lambda x: x.get('price'), reverse=True)

	final_data['results'] = results_tmp
	final_data['total_products_num'] = len(final_data['results'])
	final_data['keyword'] = keyword
	final_data['search_area'] = site
	final_data['num_hns'] = num_hns
	final_data['num_cj'] = num_cj
	final_data['num_gs'] = num_gs

	return HttpResponse(json.dumps(final_data, encoding='utf-8'), content_type = "application/json")


def search(request):
	site = request.GET.get('site', 'None')
	keyword = request.GET.get('keyword', 'None')
	sorted_by_price = request.GET.get('sort', '0')

	server_url = 'http://'+str(request.get_host())+"/search_api?site="+site+"&keyword="+str(keyword.replace(" ", "%20")+"&sort="+sorted_by_price)
	search_results = urllib2.urlopen(server_url)

	items = json.loads(search_results.read())
	
	if len(items) == 0 :
		return HttpResponse("No results")

	results = {'items' : items, 'host' : str(request.get_host())}
	return render(request, "finditem/search_results.html", results)


def main(request):
	return render_to_response('finditem/index.html')
