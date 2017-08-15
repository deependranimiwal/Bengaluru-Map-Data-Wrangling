import xml.etree.cElementTree as ET  # Use cElementTree or lxml if too slow
import pprint
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        k = element.attrib['k']
        if lower_colon.search(k):
            keys['lower_colon'] += 1
        elif lower.match(k):
            keys['lower'] += 1    
        elif problemchars.search(k):
            keys['problemchars'] += 1
        else:
            keys['other'] += 1
        
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    context = ET.iterparse(filename, events=('start', 'end'))
    _, root = next(context)
    for event, element in context:
        keys = key_type(element, keys)
        root.clear()

    return keys



def test():
    # You can use another testfile 'map.osm' to look at your solution
    # Note that the assertion below will be incorrect then.
    # Note as well that the test function here is only used in the Test Run;
    # when you submit, your code will be checked against a different dataset.
    keys = process_map('bengaluru_india.osm')
    pprint.pprint(keys)


if __name__ == "__main__":
    test()



#OUTPUT:-

# {'lower': 1537742, 'lower_colon': 70522, 'other': 2180, 'problemchars': 8}    