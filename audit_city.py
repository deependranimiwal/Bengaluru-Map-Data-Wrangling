import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSM_FILE = "bengaluru_india.osm"
#OSM_FILE = "bengaluru_sample.osm"


mappingcity = {"Bangaloreroad_leaved","Bidadi","Begur","Begur","Bellary", "Banga"}


def update_city(cityname, mappingcity):
    if cityname not in mappingcity:
        if cityname.find(",") != -1:
            return cityname
        if cityname.find(" ") != -1:
            return cityname
        if cityname[0]=="B":
            return "Bengaluru"
        if cityname[0]== "b":
            return "Bengaluru"
        else:
            return cityname    
    else:
        return cityname
    

        
def audit(osmfile):
    osm_file = open(osmfile, "r")
    city_types = []
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                    if  tag.attrib['k']=='addr:city':
                        if tag.attrib['v'] not in city_types:
                            if tag.attrib['v'] not in mappingcity:
                                city_types.append(tag.attrib['v'])
                        root.clear()
                                
    osm_file.close()
    for city in city_types:
        newcity= update_city(city, mappingcity)
        print city, "=>", newcity
    
audit(OSM_FILE)  


#note: We have ignored many city name and only updated city where error was confirmed. 

#OUTPUT
#Marathahalli, Bangalore => Marathahalli, Bangalore
#Whitefield, Bangalore => Whitefield, Bangalore
#Cottonpet, Bangalore => Cottonpet, Bangalore
#K.R Puram => K.R Puram
#Bangalore => Bengaluru
#Gandhi Nagar, Bangalore => Gandhi Nagar, Bangalore
#Bengaluru => Bengaluru
#bangalore => Bengaluru
#Bangaluru => Bengaluru
#White field,Bangalore => White field,Bangalore
#BTM Layout, Bangalore => BTM Layout, Bangalore
#Koramangala => Koramangala