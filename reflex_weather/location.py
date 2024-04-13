zipdata = dict() # {zip: (lat,lon)}

url_cache = dict() # {url: response}

def init():
    # TODO: make this all threaded
    load_ip_data()
    load_zip_data()

def load_ip_data():
    # TODO: default location based on ip address
    pass

def load_zip_data():
    # zip code data from https://download.geonames.org/export/zip/US.zip
    with open('data/zipcodes.txt', 'r') as f:
        for line in f:
            columns = line.strip().split('\t') # tab delimited file
            zip = columns[1]
            if zip:
                lat = columns[9]
                lon = columns[10]
                zipdata[zip] = (lat,lon)

