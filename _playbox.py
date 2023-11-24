from simpletools import csv_to_list_of_dicts, resolve_hostname, generate_md5_hash
from noisy_hosts import NoisyHosts

def add_noisy_hosts_data(self,  csv_file_path):
        '''
        Function to add noisy hosts (iykyk) to noisy_hosts table, check csv format and adjust
        accordingly. Takes csv file path as argument.
        '''
        #REMEMBER TO CHECK FOR CASES WHERE HOST HAS MULTIPLE IPs
        hosts_data = csv_to_list_of_dicts(csv_file_path)

        for host in hosts_data:
            ip_address = resolve_hostname(host['host_name'])
            try:
                            
                noisy = NoisyHosts(ip_address,                      
                        generate_md5_hash(ip_address),              
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


add_noisy_hosts_data('/home/lui/Documents/Testing/Python/Lab/explore/testcsv.csv')