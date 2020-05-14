from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

# prints indexes and data of all undirected networks without missing data with nodes < max_nodes

def k_to_float(string):
    if string == '-':
        return None
    elif string[-1] == 'K':
        return float(string[:-1]) * 1000
    elif string[-1] == 'M':
        return float(string[:-1]) * 1000000
    elif string[-1] == 'B':
        return float(string[:-1]) * 1000000000
    else:
        return float(string)

def format_data(data):
    if len(data) < 12: # not enough attributes
        return None
    for i,element in enumerate(data):
        if element[-1] in ['K','M','B']:
            data[i] = k_to_float(element)
        elif element == '-' or element == 'nan':
            return None
        else:
            data[i] = float(element)
    return data

max_nodes = 100

base_url = 'http://networkrepository.com/'
uClient = uReq(base_url + 'networks.php')
page_html = uClient.read()
uClient.close()

networks_soup = soup(page_html, "html.parser")
networks = networks_soup.findAll("tr", {"class": "success hrefRow tooltips"})

for i,network in enumerate(networks):
    data = format_data([element.string for element in network.find_all("td")][2:-2])
    if data != None and data[0] < max_nodes:
        network_url = base_url + network['data-url']
        network_html = uReq(network_url).read()
        network_soup = soup(network_html, "html.parser")
        metadata = network_soup.find("table", {"summary": "Dataset metadata"})
        if metadata != None: # ni podatkov o grafu
            metadata = [ele.text.strip() for ele in metadata.find_all('td')]
            if 'Undirected' in metadata:
                print(i, data)