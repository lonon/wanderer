#!/usr/bin/env python

import hashlib
import ipaddress
import csv
import socket
import re
from urllib.parse import urlparse


#LOTS OF UNNECESSARY FUNCTIONS HERE

def generate_md5_hash(host):
    """
    Function that takes host ip address and returns md5 hash of said ip
    """

    host_bytes = host.encode('utf-8')
    
    return hashlib.md5(host_bytes).hexdigest()


def ip_to_number(ip_address):
    '''
    Function takes an ip address and returns ip number.
    '''
    try:
        ip = ipaddress.IPv4Address(ip_address)
        return int(ip)
    except ipaddress.AddressValueError as e:
        print(f"Error: {e}")
        return None


def csv_to_list_of_dicts(csv_file_path):
    '''
    Function takes path name to csv file. Returns a list of dictionary elements containing
    the csv contents. Dictionary keys defined by first line of csv file.
    '''
    data_list = []

    with open(csv_file_path, 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        
        # Assuming the first row of the CSV file contains headers
        headers = next(csv_reader)

        for row in csv_reader:
            data_dict = {}

            for header, value in zip(headers, row):
                # Replace blank data with 'empty'
                value = 'empty' if not value else value
                data_dict[header] = value

            data_list.append(data_dict)

    return data_list

def resolve_hostname(hostname):
    '''
    Function takes a host name e.g. google.com and returns a list corresponding ip address(es).
    '''
    try:
        if hostname != '':
            ip_addresses = socket.gethostbyname_ex(extract_domain(hostname))[2]
            return ip_addresses
    except socket.gaierror as err:
        print('Error! Check hostname: {}\n{}'.format(hostname, err))
    except socket.herror as err:
        print('Error! Check hostname: {}\n{}'.format(hostname, err))


def clean_host_name(hostname):
    if is_valid_hostname(hostname) == True:

        # Define a regular expression pattern for a valid hostname
        valid_pattern = r'^[a-zA-Z0-9.-]+$'

        # Use regex to check if the hostname contains only valid characters
        if re.match(valid_pattern, hostname):
            # Remove any invalid characters (characters that do not match the pattern)
            cleaned_hostname = ''.join(re.findall(valid_pattern, hostname))
            
            # Remove leading and trailing dots
            cleaned_hostname = cleaned_hostname.strip('.')
            
            return extract_domain(cleaned_hostname)
    else:
        return 'google.com'  #FIIIIIIIX Invalid hostname, return None or raise an exception as needed
    

def is_valid_hostname(hostname):
    # Define a regular expression pattern for a valid host name
    pattern = r'^[a-zA-Z0-9\-\.]+$'
    
    # Use re.match to check if the input matches the pattern
    if re.match(pattern, hostname):
        return True
    else:
        return False
    
def extract_domain(url):
    '''
    Function to get domain name from full path, example: google.com/staff/unique to just google.com
    '''
    # Define a regular expression pattern to match domain names
    pattern = r'^(?:https?://)?(?:www\d*\.)?([a-zA-Z0-9.-]+)'
    
    # Use re.search to find the first match in the URL
    match = re.search(pattern, url)
    
    if match:
        # Extract the matched domain name from the regex match
        domain = match.group(1)
        return domain
    else:
        return None




#def fn_to_update_geo():
    #manage = Managedata(session)

   # iploc  = ip2location_data(ip2locationsession)

    #hosts = manage.get_all_hosts()
    #print(hosts)

    #for host in hosts:
        #poss = iploc.get_possible_iplocations(ip_to_number(host))
        #location = iploc.most_accurate_range(poss,ip_to_number(host))
        #manage.add_geolocation_data(generate_md5_hash(host), location)

    #print('Done updating geo data')

