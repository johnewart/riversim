# URL: http://cdec.water.ca.gov/cgi-progs/staSearch?staid=&sensor=&dur=&active=&loc_chk=on&lon1=118&lon2=120&lat1=34&lat2=39&nearby=&basin=&hydro=&county=&operator=&display=staid
from lxml import etree
import urllib 
from riversim.rivers.models import * 

def fetch_cdec_stations():
    min_long = -124.4
    min_lat = 32.5
    max_long = -114.133333
    max_lat = 42.0
    # CDEC takes longitude in positive values even though it's west...
    urlparams = {
            'max_long': abs(max_long), 
            'min_long': abs(min_long), 
            'max_lat':  max_lat, 
            'min_lat': min_lat,
            }
    url = "http://cdec.water.ca.gov/cgi-progs/staSearch?staid=&sensor=&dur=&active=&loc_chk=on&lon1=%(max_long).5f&lon2=%(min_long).5f&lat1=%(min_lat).5f&lat2=%(max_lat).5f&nearby=&basin=&hydro=&county=&operator=&display=staid" % urlparams
    print "Fetching from %s" % (url)
    content = urllib.urlopen(url).read()
    tree = etree.HTML(content)

    results_table = tree.xpath("//div[@class='column_inner']/table")[0].xpath('//tr')

    station_ids = []

    # Ugh...
    for row in results_table[1:]:
        station_id = row[0].getchildren()[0].text
        station_ids.append(station_id)

    return station_ids

def get_station_meta(station_id):
    url = "http://cdec.water.ca.gov/cgi-progs/staMeta?station_id=%s" % (station_id)
    content = urllib.urlopen(url).read()
    tree = etree.HTML(content)
    try:
        rows = tree.xpath("//div[@class='column_inner']/table")[0].xpath('//tr')

        longitude = rows[3][3].text.replace(u'\xb0','')
        latitude  = rows[3][1].text.replace(u'\xb0','')

        if longitude[-1] == 'W':
            longitude = 0 - float(longitude.replace("W", ""))
        else:
            longitude = float(longitude.replace("E", ""))

        if latitude[-1] == 'S':
            latitude = 0 - float(latitude.replace("S", ""))
        else:
            latitude = float(latitude.replace("N", ""))

        elevation = rows[0][3].text.replace("'", "").replace(" ", "").replace("ft", "")

        if elevation == "":
            elevation = "-1"

        return {
                "station_id":       station_id,
                "elevation":        float(elevation),
                "river_basin":      rows[1][1].text or "",
                "county":           rows[1][3].text or "",
                "hydrologic_area":  rows[2][1].text or "",
                "nearby_city":      rows[2][3].text or "",
                "latitude":         latitude,
                "longitude":        longitude,
                "operator":         rows[4][1].text or "",
               }
    except IndexError:
        print "Couldn't parse HTML"

if __name__ == "__main__":
    from riversim.rivers.models import *
    station_ids = fetch_cdec_stations()
    for station_id in station_ids:
        try:
            CDECStation.objects.get(station_id = station_id)
        except CDECStation.DoesNotExist:
            metadata = get_station_meta(station_id)
            if metadata != None:
                print "Creating a new CDEC Station for %s" % (metadata)
                station = CDECStation(**metadata)
                station.save()
