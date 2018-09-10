#!/usr/bin/env python
"""
Created on May 10 2016

@author: Sage Lichtenwalner
@modified: Lori Garzio on Sep 10 2018
Script to download netCDF, provenance, and annotation files from a THREDDS directory to local machine.

sDir: local directory to which files are saved
thredds_urls: file or list containing THREDDS directories containing .nc files to download to a local machine.
"""


from xml.dom import minidom
import urllib2
import urllib
import pandas as pd
import os
import requests
import time
import data_request_tools


def get_elements(url, tag_name, attribute_name):
    """Get elements from an XML file"""
    usock = urllib2.urlopen(url)
    xmldoc = minidom.parse(usock)
    usock.close()
    tags = xmldoc.getElementsByTagName(tag_name)
    attributes=[]
    for tag in tags:
        attribute = tag.getAttribute(attribute_name)
        attributes.append(attribute)
    return attributes


def main(sDir, thredds_urls):
    server_url = 'https://opendap.oceanobservatories.org'
    data_request_tools.create_dir(sDir)
    if type(thredds_urls) == list:
        thredds_list = thredds_urls
    else:
        thredds_file = pd.read_csv(os.path.join(sDir, thredds_urls))
        thredds_list = thredds_file['outputUrl'].tolist()

    for t in thredds_list:
        print t

        # Check that the data request has been fulfilled
        check_complete = t.replace('/catalog/', '/fileServer/')
        check_complete = check_complete.replace('/catalog.html', '/status.txt')

        session = requests.session()
        r = session.get(check_complete)
        while r.status_code != requests.codes.ok:
            print 'Data request is still fulfilling. Trying again in 1 minute.'
            time.sleep(60)
            r = session.get(check_complete)

        # Create local folders and download files
        print 'Downloading files'
        folder = t.split('/')[-2]
        subsite = folder.split('-')[1]
        refdes = '-'.join((subsite, folder.split('-')[2], folder.split('-')[3], folder.split('-')[4]))
        output_dir = os.path.join(sDir, subsite, refdes, folder)
        data_request_tools.create_dir(output_dir)

        catalog_url = t.replace('.html', '.xml')
        files = []
        datasets = get_elements(catalog_url, 'dataset', 'urlPath')
        for d in datasets:
            if d.endswith(('_provenance.json', '_annotations.json', '.nc')):
                files.append(d)
        count = 0
        for f in files:
            count += 1
            file_url = '/'.join((server_url, 'thredds/fileServer', f))
            file_name = '/'.join((output_dir, file_url.split('/')[-1]))
            urllib.urlretrieve(file_url, file_name)


if __name__ == '__main__':
    sDir = '/Users/lgarzio/Documents/OOI'
    thredds_urls = 'data_request_summary_20180910T1200.csv'
    main(sDir, thredds_urls)
