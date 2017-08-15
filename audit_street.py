import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "bengaluru_india.osm"                                                                                                               
#OSMFILE = "bengaluru_sample.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Road", "Cross"]

# UPDATE THIS VARIABLE
mapping = {"Rd.": "Road",
           "Rd'": "Road",
           "Rd": "Road",
           "Roa": "Road",
           "St": "Street",
           "st": "Street",
           "rd": "Road",
           "Naga": "Nagar",
           "crs": "Cross",
           "blk":"Block",
           "cmplx": "Complex",
           "Jct": "Junction"
           
           }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected :
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                    root.clear()
    osm_file.close()
    return street_types



def check_comma(name):
    if name[-1]==',':
        name= name[:-1]
        pass
    if name[0:2]==', ':
        name= name[2:]
        pass
    if name[0]==',':
        name=name[1:]
        pass
    if name[-1]=='.':
        name= name[:-1]
    return name
    

    
    

def update_name(name, mapping):
    
    name= check_comma(name)
    name_list = name.split(" ")
    new_name_list = []
    for word in name_list:
        if len(word)== 0:
            break
        if word not in mapping.keys():
            if word[-1]==',':
                word_new= word[:-1]
                if word_new not in mapping.keys():
                    new_name_list.append(word_new+',')
                else:
                    new_name_list.append(mapping[word_new]+ ',')
            else:
                new_name_list.append(word)
        else:
            new_name_list.append(mapping[word])
    name = " ".join(new_name_list)
    return name

def test():
    st_types = audit(OSMFILE)
    for key in st_types:
        if len(st_types[key])> 3:
        #if len(st_types[key])> 0:  
        # (for bengaluru_sample)    
            
            for name in st_types[key]:
                better_name = update_name(name, mapping)
                print name, "=>", better_name  
        

if __name__ == '__main__':
    test()


#There not much that can be done. As most street name contain full address. But we have removed basic errors like comma etc.    


#EXAMPLE OUTPUT
# , CMH Road, Near ICICI Bank ATM,Indiranagar => CMH Road, Near ICICI Bank ATM,Indiranagar