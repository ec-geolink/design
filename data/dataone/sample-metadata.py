# sample-metadata.py
# Bryce Mecum (mecum@nceas.ucsb.edu)

# Summary:
#
# Sample research objects (?) within one or more
# member nodes (MN) and save system metadata and
# object metadata to file. The purpose of this script
# is to allow metadata to be sampled randomly from within
# member nodes in order to test the quality of metadata
# across member nodes.
#
#
# Implementation details:
#
# The coordinating node (CN) is queried for all documents
# regardless of the authoritative MN.
#
#
# Command line arguments:
#
# --node: Member node identifier, e.g. urn:node:KNB TODO: NOT IMPLEMENTED
# --atleast: Return at least {atleast} objects TODO: NOT IMPLEMENTED


def getNumResults():
    query_url = ("https://cn.dataone.org/cn/v1/query/solr/"
    "?fl=identifier,authoritativeMN"
    "&q=formatType:METADATA+AND+-obsoletedBy:*"
    "&rows=0"
    "&start=0")
    request = urllib2.urlopen(query_url)
    response = request.read()
    response_xml = ET.fromstring(response)
    
    result = response_xml.findall(".//result")
    
    return int(result[0].get("numFound"))
    
def getPage(page = 1, page_size = 1000):
	print("Getting page " + str(page))
	
	identifiers = []
	authoritativeMNs = []
    
	param_rows = page_size
	param_start = (page - 1) * page_size

	query_url = "https://cn.dataone.org/cn/v1/query/solr/"\
	    "?fl=identifier,authoritativeMN"\
	    "&q=formatType:METADATA+AND+-obsoletedBy:*" \
	    "&rows="\
	    + str(param_rows) + \
	    "&start=" \
	    + str(param_start)\

	request = urllib2.urlopen(query_url)
	response = request.read()
	response_xml = ET.fromstring(response)
	docs = response_xml.findall(".//doc")

	for d in docs:
	    identifier = d.find("./str[@name='identifier']").text
	    authoritativeMN = d.find("./str[@name='authoritativeMN']").text
	    
	    identifiers.append(identifier)
	    authoritativeMNs.append(authoritativeMN)

	return (identifiers, authoritativeMNs)


def getPageRange(page_range, page_size, delay = 1):
    identifiers = []
    authoritativeMNs = []
    
    for p in page_range:
        page_result = getPage(page = p)
        
        identifiers = identifiers + page_result[0]
        authoritativeMNs = authoritativeMNs + page_result[1]  
        
	if delay is not None:
		time.sleep(delay)
		
    return (identifiers, authoritativeMNs)
 
        
def getAllPages(page_size = 1000):
	num_results = getNumResults();
	
	# pages_required = math.ceil((num_results + 0.0) / page_size)
	pages_required = 2
	range_of_pages = range(1, int(round(pages_required)))
	
	all_pages = getPageRange(range_of_pages, page_size, delay = 1)
	
	documents_df = pandas.DataFrame({
                  'identifier' : all_pages[0],
                  'authoritativeMN' : all_pages[1]})

	return documents_df

	
def sampleDocuments(documents, sample_size = 5):
	unique_mns = pandas.unique(documents['authoritativeMN'])
	sampled_documents = pandas.DataFrame({'identifier' : [], 'authoritativeMN' : []})

	for mn in unique_mns:
		df_subset = documents[documents.authoritativeMN == mn]
		nrows = df_subset.shape[0]
	
		print("  Member node " + mn + " has " + str(nrows) + " rows")

		if nrows is 0:
			continue
		elif nrows is 1:
			sampled_rows = [0]
		else:		
			if nrows > sample_size:
				rows_to_sample = range(0, nrows - 1)
				sampled_rows = numpy.random.choice(rows_to_sample, sample_size)
			else:
				sampled_rows = range(0, nrows - 1)

		df_subset_filtered = df_subset.iloc[sampled_rows,:]

		sampled_documents = pandas.concat([sampled_documents, df_subset_filtered])
	
	return sampled_documents

# NOT IMPLEMENTED FULL
def getIdentifierMetaXML(base_url, identifier):
	query_url = base_url + "/meta/" + identifier
	print(query_url)
	
	try:
		request = urllib2.urlopen(query_url)
		response = request.read()
		response_xml = ET.fromstring(response)
	except:
		response_xml = None
	
	return response_xml

# NOT IMPLEMENTED FULLY
def getIdentifierObjectXML(base_url, identifier):
	query_url = base_url + "/object/" + identifier
	print(query_url)
	try:
		request = urllib2.urlopen(query_url)
		response = request.read()
		response_xml = ET.fromstring(response)
	except:
		response_xml = None
	
	return response_xml
    
def getNodeList():
	query_url = "https://cn.dataone.org/cn/v1/node"
	request = urllib2.urlopen(query_url)
	response = request.read()
	response_xml = ET.fromstring(response)

	node_list = {}

	nodes = response_xml.findall(".//node")

	for n in nodes:
		node_identifier = n.find("identifier").text
		node_type = n.attrib["type"]
		node_base_url = n.find("baseURL").text

		node_list[node_identifier] = { "identifier" : node_identifier, "type" : node_type, "base_url" : node_base_url }

	return node_list

def getAndSaveDocuments(documents):
	nodes = getNodeList()
	
	print("Saving (" + str(documents.shape[0]) + ") documents ")
	
	for i in range(0, documents.shape[0] - 1):		
		node_identifier = documents.iloc[i, 0]
		document_identifier = documents.iloc[i, 1]
		
		# Make the subdirectories to store files
		subdirectory_path = "results/" + node_identifier + "/" + document_identifier
		
		if not os.path.exists(subdirectory_path):
			os.makedirs(subdirectory_path)
			
		mn_url = nodes[node_identifier]["base_url"]
		
		print(mn_url)
		
		meta_xml = getIdentifierMetaXML(mn_url, document_identifier)
		object_xml = getIdentifierObjectXML(mn_url, document_identifier)
		
		if meta_xml is not None:
			ET.ElementTree(meta_xml).write(subdirectory_path + "/meta.xml")

		if object_xml is not None:
			ET.ElementTree(object_xml).write(subdirectory_path + "/object.xml")
			
				
def main():
	all_documents = getAllPages()
	sampled_documents = sampleDocuments(all_documents)
	getAndSaveDocuments(sampled_documents)


if __name__ == "__main__":
	import urllib2
	import xml.etree.ElementTree as ET
	import re
	import csv
	import string
	import sys
	import math
	import pandas
	import numpy
	import time
	import os

  	try:
  		main()
  	except KeyboardInterrupt:
  		sys.exit()