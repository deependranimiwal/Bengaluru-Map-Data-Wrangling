import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

#OSM_FILE = "bengaluru_india.osm"
OSM_FILE = "bengaluru_sample.osm"

def update_postcode(postcode):
    if len(postcode)<6:
        return postcode
    if postcode[3]==' ':
        postcode=postcode[0:3]+ postcode[4:7]
        pass
    if postcode[-1]==',':
        postcode=postcode[:-1]
        pass
    if postcode[0:2]=='- ':
        postcode=postcode[2:]
        pass
    if postcode[-1]=='"':
        postcode=postcode[:-1]
        pass

    #if len(postcode)== 7:
        #if postcode[3]== '0':
           #postcode=postcode[0:3]+ postcode[4:7]
        #pass   
         
    if postcode[-1]=='h':
        postcode=postcode[:-1]
        pass
    if postcode[-1]=='p':
        postcode=postcode[:-1]
        pass
    else:
        return postcode
    return postcode
    
        
def audit_postcode(osmfile):
    osm_file = open(osmfile, "r")
    post_types = []
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                    if  tag.attrib['k']=='addr:postcode':
                        if len(tag.attrib['v']) != 6:
                            if tag.attrib['v'] not in post_types:
                                post_types.append(tag.attrib['v'])
                                root.clear()
                                
    osm_file.close()
    for post in post_types:
        newpost= update_postcode(post)
        print post, "=>", newpost

audit_postcode(OSM_FILE)     


#note: We only updated those were error is confirmed and known, Others are ignored and later removed from the database.
#OUTPUT:-
#560003  => 560003
#560 068 => 560068
#560 100 => 560100
#5600091 => 5600091
#560 064 => 560064
#5600041 => 5600041
#560 020 => 560020
#5600011 => 5600011
#560 025 => 560025
#560 037 => 560037