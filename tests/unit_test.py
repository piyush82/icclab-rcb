'''
Created on Feb 18, 2014

@author:  Tea Kolevska
@contact: tea.kolevska@zhaw.ch
@organization: ICCLab, Zurich University of Applied Sciences
@summary: Unittesting

'''
import sys
sys.path.append('/home/kolv/workspace/icc-lab-master/os_api')
import ceilometer_api
import compute_api
import keystone_api
import unittest

class ApiTest(unittest.TestCase):
    auth_uri = 'http://160.85.4.10:5000' 
    compute="http://160.85.4.10:8774/v2/323936522894416b903d3528fa971537"
    metering="http://160.85.4.10:8777"
    status, token_data = keystone_api.get_token_v3(auth_uri)
    for key, value in token_data.iteritems():
        if key=="token-id":
            token_id=value
          
    def test_api(self):
        for key, value in self.token_data.iteritems():
            if key==self.compute:
                self.assertEqual(self.compute, value) 
            if key==self.metering:
                self.assertEqual(self.metering,value)


class MeterTest(unittest.TestCase):  
    metering="http://160.85.4.10:8777"      
    pom=ApiTest("test_api")  
    status, meter_list = ceilometer_api.get_meter_list(pom.token_id,metering)             
    def test_sample(self):              
        status,sample_list=ceilometer_api.get_meter_samples("network",self.metering,self.pom.token_id,False,self.meter_list)       
        for i in range(len(sample_list)):
            self.assertEqual(str(sample_list[i]["counter-unit"]),"network")
            self.assertEqual(str(sample_list[i]["counter-type"]),"gauge")
    def test_resource(self):
        status,resources_list=ceilometer_api.get_resources(self.metering,self.pom.token_id,False)       
        for i in range(len(resources_list)):
            self.assertEqual(str(resources_list[i]["project-id"]),"323936522894416b903d3528fa971537")
        
                    
        
if __name__ == "__main__":
    unittest.main()       