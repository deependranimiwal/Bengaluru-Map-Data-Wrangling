#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_PATH = "bengaluru_india.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']



#.................x.................x.................x.................x.................x.................x


#addr:city is audited, I ignored some words which starts from "B" or "b" which are in mappingcity.
#City tags with extra info of area is also ignored by looking for comma "," and space " " .
#I made all other city tags consistent by updatitng them with "Bengaluru"
#Ignored data if needed, can be removed in future. 
mappingcity = {"Bangaloreroad_leaved","Bidadi","Begur","Bellary", "Banga"}


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
    


#.................x.................x.................x.................x.................x.................x


#Street name is Audited. We also found comma at irregular interval, so we also removed them and updated the street name.
#Street name 



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







#.................x.................x.................x.................x.................x.................x

#postcode tag is audited, problems and errors in the postcode are updated.
#Postcodes which cannot be updated and have some errors are removed from database.

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
    
    if postcode[-1]=='h':
        postcode=postcode[:-1]
        pass
    if postcode[-1]=='p':
        postcode=postcode[:-1]
        pass
    else:
        return postcode
    return postcode




#.................x.................x.................x.................x.................x.................x

#Street tag is updated to full address tag if comma appears during street name.



def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
        node_attribs['id']= element.attrib['id']
        node_attribs['user']= element.attrib['user']
        node_attribs['uid']= element.attrib['uid']
        node_attribs['version']= element.attrib['version']
        node_attribs['lat']= element.attrib['lat']
        node_attribs['lon']= element.attrib['lon']
        node_attribs['changeset']= element.attrib['changeset']
        node_attribs['timestamp']= element.attrib['timestamp']
        
        for elem in element:
            node_list={}
            if elem.tag == 'tag':
                node_list['id'] = element.attrib['id']
                if elem.attrib['k']:
                    k= elem.attrib['k']
                    if LOWER_COLON.search(k):
                        s = k.find(':')
                        if k[s+1:]== 'street':
                            value = elem.attrib['v']
                            if value.find(',') != -1 :
                                node_list['key']= 'full' 
                                node_list['type']= k[:s]
                            else:
                                node_list['key']= k[s+1:]
                                node_list['type']= k[:s]
                        else:
                            node_list['key']= k[s+1:]
                            node_list['type']= k[:s]
                        
                    elif PROBLEMCHARS.search(k):
                        break
                    else:
                        node_list['key']= k
                        node_list['type']= 'regular'
                
                if elem.attrib['v']:
                    if elem.attrib['k']== 'addr:street':
                        node_list['value'] = update_name(elem.attrib['v'], mapping ) 
                    
                    elif elem.attrib['k']== 'addr:city':
                        node_list['value'] = update_city(elem.attrib['v'], mappingcity ) 
                    
                    elif elem.attrib['k']== 'as_in:city':
                        node_list['value'] = update_city(elem.attrib['v'], mappingcity )
                    
                    elif elem.attrib['k']== 'addr:postcode':
                        if  len(update_postcode(elem.attrib['v'])) == 6:
                            node_list['value'] = update_postcode(elem.attrib['v'])
                        else:
                            break
                    else:
                        node_list['value']= elem.attrib['v']
            tags.append(node_list)

        return {'node': node_attribs, 'node_tags': tags}
    
#Way tags are updated similarly     
    
    elif element.tag == 'way':
        way_attribs['id']= element.attrib['id']
        way_attribs['user']= element.attrib['user']
        way_attribs['uid']= element.attrib['uid']
        way_attribs['version']= element.attrib['version']
        way_attribs['changeset']= element.attrib['changeset']
        way_attribs['timestamp']= element.attrib['timestamp']
        
        count=0
        for elem in element:
            if elem.tag == 'nd':
                nd={}
                nd['id']= element.attrib['id']
                nd['node_id']=elem.attrib['ref']
                nd['position']= count
                count=count+1
                way_nodes.append(nd)
        
            way_list={}
            if elem.tag == 'tag':
                way_list['id'] = element.attrib['id']
                if elem.attrib['k']:
                    k= elem.attrib['k']
                    if LOWER_COLON.search(k):
                        s = k.find(':')
                        if k[s+1:]== 'street':
                            value = elem.attrib['v']
                            if value.find(',') != -1 :
                                way_list['key']= 'full' 
                                way_list['type']= k[:s]
                            else:
                                way_list['key']= k[s+1:]
                                way_list['type']= k[:s]
                        else:
                            way_list['key']= k[s+1:]
                            way_list['type']= k[:s]
                        
                    elif PROBLEMCHARS.search(k):
                        break
                    else:
                        way_list['key']= k
                        way_list['type']= 'regular'
                        
                if elem.attrib['v']:
                    if elem.attrib['k']== 'addr:street':
                        way_list['value'] = update_name(elem.attrib['v'], mapping ) 
                    elif elem.attrib['k']== 'addr:city':
                        way_list['value'] = update_city(elem.attrib['v'], mappingcity ) 
                    elif elem.attrib['k']== 'addr:postcode':
                        if  len(update_postcode(elem.attrib['v'])) == 6:
                            way_list['value'] = update_postcode(elem.attrib['v'])
                        else:
                            break
                    else:
                        way_list['value']= elem.attrib['v']
                tags.append(way_list)
            
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


    
    
#.................x.................x.................x.................x.................x.................x



# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
