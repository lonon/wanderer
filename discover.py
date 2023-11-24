#!/usr/bin/env python

####
'''
Todo:
handling connection time out on requests
'''

import json
import nmap
import random
import requests

import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor

from requests.exceptions import SSLError

import time #this is only for testing, delete later

#######
geo_api_key = 'f2e84010-e1e9-11ed-b2f8-6b70106be3c8'
import numpy as np #testing function for now
import os
#########


class Discover():
    def __init__(self):
        pass
    
    def host_up(self, host):
        """
        This function returns True if the provided host is online/up.
        Host is in the form of an IPv4 address.
        """

        command  = ["ping", "-c", "1", host]
        try:
            result  = subprocess.check_output(command)
            return "0% packet loss" in result.decode("utf-8")
        except subprocess.CalledProcessError as err:
            pass

    # Uses nmap random suite
    def generate_random_ips(self, num_addresses):
        """
        Function generates random number of IPv4 addresses. Returns them in a list.
        Just how random random.randint() is, is up for further research.
        """
        if num_addresses <= 0:
            return []

        # Generate random octets for num_addresses IP addresses
        random_octets = np.random.randint(0, 256, size=(num_addresses, 4), dtype=np.uint8)

        # Format the octets as IPv4 addresses
        ip_addresses = [".".join(map(str, octets)) for octets in random_octets]

        return ip_addresses

    # Uses os.urandom
    def generate_random_ipv4_address_os(self, n):
        random_ipv4_addresses = []

        for _ in range(n):
            # Generate 4 random bytes using os.urandom
            random_bytes = os.urandom(4)

            # Convert the random bytes to an IPv4 address string
            ipv4_address = ".".join(map(str, random_bytes))

            random_ipv4_addresses.append(ipv4_address)

        return random_ipv4_addresses

    ### Uses standard library random
    def generate_random_ips(self, num_addresses):
        """
        Function generates random number of IPv4 addresses. Returns them in a list.
        Just how random random.randint() is, is up for further research.
        """


        ip_addresses = []

        for each in range(num_addresses):
            ip_address = ".".join(str(random.randint(0,255)) for each in range(4))

            ip_addresses.append(ip_address)

        return ip_addresses
    
    def live_host(self, host):
        """
        Function takes host (i.e IPv4 address), returns host host if it is online/up.
        Otherwise None is returned.
        """
        if self.host_up(host) == True and host.startswith("127") != True:
            return host
        else:
            return None
        
    def filter_many(self, hosts):
        """
        Function takes a list of hosts and returns list containing IP addresses and 
        filters those that are online/up.
        It uses, threading module to speed things up. 
        
        Breaks when dealing with around 5000 hosts, sijacheck mwanzo. !!!! Make sure to check 
        what the deal is with that. !!!!!
        """
        results = []

        # Function to process each IP address in a separate thread
        def process_ip(ip):
            result = self.live_host(ip)

            if result != None:
                results.append(result)

        # Create a list to store thread objects
        threads = []

        # Start a thread for each IP address in the list
        for ip in hosts:
            thread = threading.Thread(target=process_ip, args=(ip,))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        return results

    def masscan_host(self, host):
        """
        Use masscan to find out number of ports open on host and returns a
        multi sentence string with masscan output.
        """

        command = ["masscan", host, "--top-ports=1500"]
        result = subprocess.check_output(command)

        if result != b'':
            return "{}\n{}".format(host, result.decode("utf-8"))
        else:
            return None
    
    def masscan_many_hosts(self, hosts):

        """
        Function that facilates scanning multiple addresses concurrently.
        Takes a list as variable, and returns a list of strings containing multiple
        line string.
        """

        results = []

        def scan_host(host):
            result = self.masscan_host(host)

            if result != None:
                results.append(result)

        threads = []

        for host in hosts:
            thread = threading.Thread(target=scan_host, args=(host,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        return results
    
    def nmap_scan(self, host):
        """ 
        Function that runs an nmap scan on a host with the arguments
        as -sC -sV --top-ports=1500. Returns a json string object

        should add -O for oses
        """

        nm = nmap.PortScanner()
        results = nm.scan(host, arguments="-sS -sC -sV --top-ports=1500")
    

        return results
    
    def nmap_scan_many(self, hosts):

            """
            Function that takes list of hosts, runs multithreaded nmap scans and returns
            a list of dictionaries with the scan results.
            """

            results = []

            def process_scan(host):
                result = self.nmap_scan(host)

                if result != None:
                    results.append(result)

            threads = []

            for host in hosts:
                thread = threading.Thread(target=process_scan, args=(host,))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            return results

    def geo_location(self, host):
        """
        Function that takes host and returns json string containing Country, City etc
        from geolocation-db.com.

        https://www.ipinfodb.com/free-database
        """
        try:
            request_url = 'https://geolocation-db.com/jsonp/'+ geo_api_key + '/'+ host
            response = requests.get(request_url)
            result = response.content.decode()
            result = result.split("(")[1].strip(")")
            result = json.loads(result)

        except SSLError as err:
            print('Connection error! Problem with ssl: {}'.format(err))
        except ConnectionError as err:
            print("Remote end disconnection.")


        
        
        return result

    def geo_location_many(self, hosts):

            """
            Function taking list of hosts, and using multithreading, returns list of json strings
            with the geographical location data.
            """

            results = []

            def process_geo(host):
                result = self.geo_location(host)

                if result != None:
                    results.append(result)

            threads = []

            for host in hosts:
                thread = threading.Thread(target=process_geo, args=(host,))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            return results


if __name__ == "__main__":
    disc = Discover()
    ips = disc.generate_random_ips(20)

    filt = disc.filter_many(ips)
    
    scan = disc.nmap_scan_many(filt)

    for i in scan:
        print(i)
        print('\n')
    
