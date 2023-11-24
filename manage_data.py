#!/usr/bin/env python

from sqlalchemy.exc import IntegrityError, PendingRollbackError
import time
import folium

from base import Base, engine, Session
from ip2locationbase import ip2locationBase, ip2locationengine, ip2locationSession

from hosts import Hosts
from geolocation import Geolocation
from lightscan import Lightscan
from heavyscan import Heavyscan
from noisy_hosts import NoisyHosts

from ip2location import IP2Location

# !!! TO TEST THE FUNCTIONALITY, DELETE LATER
from discover import Discover
from simpletools import generate_md5_hash, ip_to_number, resolve_hostname, csv_to_list_of_dicts, extract_domain

#########
Base.metadata.create_all(engine)
ip2locationBase.metadata.create_all(ip2locationengine) #ip2location is on its own db, edit later for one master db???

session = Session()
ip2locationsession = ip2locationSession()

class Managedata():

    def __init__(self, session):
        self.session = session

    def add_lightscan_data(self, md5_hash,result,recent_change=False):
        '''
        Function takes md5 hash and masscan result and adds it to db
        Exception handling is still minimum 9/9/2023
        '''
        try:
            scan = Lightscan( md5_hash,result,recent_change)

            self.session.add(scan)
            self.session.commit()
        except IntegrityError as err:
            pass
        except PendingRollbackError as err:
            self.session.rollback()
            self.session = session

    def add_heavyscan_data(self, md5_hash,result,recent_change=False):
        '''
        Function takes md5 hash and nmap result and adds it to db
        Exception handling is still minimum 9/9/2023
        '''
        try:
            scan = Heavyscan(md5_hash,result,recent_change)

            self.session.add(scan)
            self.session.commit()
        except IntegrityError as err:
            pass
        except PendingRollbackError as err:
            self.session.rollback()
            self.session = session

    def add_geolocation_data(self, md5_hash,geo_dictionary):
        '''
        Function takes md5 hash and a dictionary containing geolocation info and adds to db.
        '''
        try:
            geo = Geolocation(md5_hash, geo_dictionary)
            self.session.add(geo)
            self.session.commit()
        except IntegrityError as err:
            self.session.rollback()
            self.session = session

        except PendingRollbackError as err:
            self.session.rollback()
            self.session = session
  
    def add_host_data(self, ip, md5_hash):
        '''
        Function to add individual host to hosts table. Arguments are ipv4 address and 
        md5_hash corresponding to ip.
        '''

        try:
            host_data = Hosts( ip, md5_hash)

            self.session.add(host_data)
            self.session.commit()
        except IntegrityError as err:
            pass
        except PendingRollbackError as err:
            self.session.rollback()
            self.session = session

    def add_noisy_hosts_data(self, csv_file_path):
        '''
        Function to add noisy hosts (iykyk) to noisy_hosts table, check csv format and adjust
        accordingly. Takes csv file path as argument.
        '''
        #REMEMBER TO CHECK FOR CASES WHERE HOST HAS MULTIPLE IPs
        hosts_data = csv_to_list_of_dicts(csv_file_path)
        
        for host in hosts_data:
            refined_hostname = extract_domain(host['host_name'])
            ip_address = resolve_hostname(refined_hostname)
            try:
                #zero index is for only first ip incase of multiple, temp fixx!!! 
                if ip_address is not None:         
                    noisy = NoisyHosts(ip_address[0],                      
                            generate_md5_hash(ip_address[0]),              
                            host['host_name'], 
                            host['agency'], 
                            host['organization'],
                            host['type_of_government'],
                            host['state'], 
                            host['securitycontactemail'] 
                                    )

                    self.session.add(noisy)
                    self.session.commit()
                            
            except IntegrityError as err:
                self.session.rollback()
                self.session = session
            except PendingRollbackError as err:
                self.session.rollback()
                self.session = session

    def noisy_ips_to_hosts_db(self, csv_file_path):
        '''
        Function to add noisy hosts to the hosts table. Takes csv file path.
        Important for md5_hash foreign key in noisy_hosts table.
        '''

        ls = csv_to_list_of_dicts(csv_file_path)

        for l in ls:
            ip_list = resolve_hostname(l['host_name'])
            if ip_list is not None:
                if len(ip_list) == 1:
                    ip = ip_list[0]
                    manage.add_host_data(ip, generate_md5_hash(ip))
                elif len(ip_list) > 1:
                    index = 0
                    for addr in ip_list:
                        ip = ip_list[index]
                        manage.add_host_data(ip, generate_md5_hash(ip))
                        index += 1
        
    def get_all_hosts(self):
        '''
        Returns list of a list of all hosts. Hosts.ip
        '''
        results = [res[0] for res in self.session.query(Hosts.ip)]

        return results
    
    def get_all_md5_hashes(self):
        '''
        Returns list of all md5 hashes in db.
        '''
        results = [res[0] for res in self.session.query(Hosts.md5_hash)]
        return results
    
    def get_entire_hosts_table(self):
        '''
        Return list of tuples containing contents of entire hosts table.

        (id,ip,md5_hash,created_on,updated_on,reliable)
        '''
        return self.session.query(Hosts.id, Hosts.ip, Hosts.md5_hash, 
                                  Hosts.created_on, Hosts.updated_on, Hosts.reliable)

    def visualize_hosts_on_map(self, coordinates_list, filename):
            """
            Plots a list of [longitude, latitude] coordinates on an OpenStreetMap.
            For example
            [
                [-73.9857, 40.7488],  # New York City
                [-118.2437, 34.0522],  # Los Angeles
                [-87.6298, 41.8781],  # Chicago
                [-95.3698, 29.7604],  # Houston
            ]


            Parameters:
            - coordinates_list (list): List of [longitude, latitude] coordinates.
            - filename (str): .html file name to save desired plot. Name without extension

            Returns:
            nothing, a html file is written and saved as filename.html.
            """
            # Create a map centered at the first coordinate in the list
            initial_coordinate = coordinates_list[0]
            map_center = [initial_coordinate[1], initial_coordinate[0]]
            my_map = folium.Map(location=map_center, zoom_start=1)  # Adjust the zoom level as needed

            folium.TileLayer("OpenStreetMap").add_to(my_map)
            folium.TileLayer("stamentoner", show=False).add_to(my_map)

            folium.LayerControl().add_to(my_map)

            

            # Plot each coordinate on the map
            for coordinate in coordinates_list:
                lat, lon = coordinate[1], coordinate[0]

                i = folium.CustomIcon(icon_image='/home/lui/Descargas/alien.png', icon_size=(20,20))

                folium.Marker([lat, lon], popup='masine\nlat:{}\nlon:{}'.format(lat, lon), icon=i).add_to(my_map)

            my_map.save("{}.html".format(filename))  # Save the map to an HTML file


class ip2location_data():

    def __init__(self, session):
        self.session = session

    def get_possible_iplocations(self, ip_number):
        '''
        Function that takes ip number (as int) and returns a list of dictionary elements containing all possible
        address geolocation
        '''

        self.ip_number = str(ip_number)
        results = self.session.query(IP2Location.ip_from, IP2Location.ip_to,
                                    IP2Location.country_code,
                                    IP2Location.country_name,
                                    IP2Location.region_name,
                                    IP2Location.latitude,
                                    IP2Location.longitude,
                                    IP2Location.zip_code,
                                    IP2Location.time_zone
                                    ).filter(IP2Location.ip_from.like('{}%'.format(self.ip_number[:2])))
        
        result_list = []
        for result in results:
            result_dict = {
                'ip_from':result.ip_from,
                'ip_to':result.ip_to,
                'country_code':result.country_code,
                'country_name':result.country_name,
                'region_name':result.region_name,
                'latitude':result.latitude,
                'longitude':result.longitude,
                'zip_code':result.zip_code,
                'time_zone':result.time_zone
             }
            result_list.append(result_dict)

        return result_list
  
    def precise_iplocation_details(self, possible_locs_data, ip_number):
        '''
        Function that takes a list of possible location data i.e. from the get_possible_iplocation()
        method and returns precise location, if found, in a dictionary. 
        '''

        best_range = None
        best_accuracy = float('inf')  # Initialize with positive infinity
        
        for loc_data in possible_locs_data:
            ip_from = loc_data['ip_from']
            ip_to = loc_data['ip_to']
            midpoint = (ip_from + ip_to) / 2
            accuracy = abs(midpoint - ip_number)
            
            if accuracy < best_accuracy:
                best_accuracy = accuracy
                best_range = loc_data
        
        return best_range



if __name__ == "__main__":

    manage = Managedata(session)

    #manage.noisy_ips_to_hosts_db('/home/lui/Documents/Testing/Python/Lab/explore/gov_urls.csv')

    #manage.add_noisy_hosts_data('/home/lui/Documents/Testing/Python/Lab/explore/cisagovlist.csv')


