# URL: http://cdec.water.ca.gov/cgi-progs/staSearch?staid=&sensor=&dur=&active=&loc_chk=on&lon1=118&lon2=120&lat1=34&lat2=39&nearby=&basin=&hydro=&county=&operator=&display=staid
import re
import sys
import urllib 

from lxml import etree
from datetime import datetime
from riversim import rivers
from traceback import print_exc


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

def get_station_sensors(station):
    try:
        cdec_datasource = rivers.models.DataSource.objects.get(name='CDEC')
    except rivers.models.DataSource.DoesNotExist:
        cdec_datasource = rivers.models.DataSource.objects.create(name = 'CDEC')

    url = "http://cdec.water.ca.gov/cgi-progs/selectQuery?station_id=%s" % (station.station_id)
    content = urllib.urlopen(url).read()
    tree = etree.HTML(content)
    try:
        rows = tree.xpath("//div[@class='column_inner']/table")[0].xpath('//tr')

        for row in rows:
            try:
                sensor_id = row[0].text
                description_cell = etree.tostring(row[1], method='text')
                source = cdec_datasource
                print "Description: %s" % (description_cell)
                m = re.search('(.*)\s\(\s*(.*?)\s*\).*', description_cell)
                description = m.group(1)
                measurement_unit = m.group(2)
                duration_code = re.search('\((\w+)\)', row[2].text).group(1) 
                try:
                    sensortype = rivers.models.SensorType.objects.get(source = cdec_datasource, sensor_id = sensor_id, duration_code = duration_code)
                except rivers.models.SensorType.DoesNotExist:
                    sensortype = rivers.models.SensorType.objects.create(source = cdec_datasource, sensor_id = sensor_id, name = description, measurement_unit = measurement_unit, duration_code = duration_code)
                
                try:
                   sensor = rivers.models.Sensor.objects.get(station = station, type = sensortype)
                except rivers.models.Sensor.DoesNotExist:
                   sensor = rivers.models.Sensor.objects.create(station = station, type = sensortype)

            except:
                print "Unexpected error:", sys.exc_info()[0]
                print_exc()
       
    except IndexError:
        print "Unable to parse HTML"

def get_sensor_data(station, sensor_type, start_date, end_date):
    if sensor_type.duration_code == 'hourly':
        duration_code = 'H'
    elif sensor_type.duration_code == 'event':
        duration_code = 'E' 

    csv_url_template = "http://cdec.water.ca.gov/cgi-progs/queryCSV?station_id={station_id}&sensor_num={sensor_id}&dur_code={duration_code}&start_date={start_date}&end_date={end_date}&data_wish=View+CSV+Data"
    url = csv_url_template.format(
            station_id = station.station_id, 
            sensor_id = sensor_type.sensor_id, 
            duration_code = duration_code, 
            start_date = start_date.strftime("%Y/%m/%d"), 
            end_date = end_date.strftime("%Y/%m/%d")
          )
    csvdata = urllib.urlopen(url).read()

    try:
        sensor = rivers.models.Sensor.objects.get(station = station, type = sensor_type)
    except rivers.models.Sensor.DoesNotExist:
        sensor = rivers.models.Sensor.objects.create(station = station, type = sensor_type)


    # Remove data from the existing time window since we don't want duplicates
    existing_measurements = sensor.measurement_set.filter(timestamp__gte =
            start_date).filter(timestamp__lte = end_date)
    existing_measurements.delete()

    lines = csvdata.split("\r\n")

    for line in lines[2:-1]:
        (date,time,sample) = line.split(",")
        dtstr = "%s%s" % (date, time)
        dt = datetime.strptime(dtstr, '%Y%m%d%H%M')
        print "Creating measurement: %s // %s @ %s" % (dt, sample, sensor)
        try:
            measurement = rivers.models.Measurement.objects.create(sensor = sensor, value = sample, timestamp = dt)
        except: 
            print "Unable to create measurement..."
    return csvdata 

def get_all_sensor_data(station, start_date, end_date):
    sensors = station.sensor_set.all()
    for sensor in sensors:
        get_sensor_data(station, sensor.type, start_date, end_date)

#if __name__ == "__main__":
#    stations = CDECStation.objects.all()
#    for station in stations:
#    station_ids = fetch_cdec_stations()
#    for station_id in station_ids:
#        try:
#            CDECStation.objects.get(station_id = station_id)
#        except CDECStation.DoesNotExist:
#            metadata = get_station_meta(station_id)
#            if metadata != None:
#                print "Creating a new CDEC Station for %s" % (metadata)
#                station = CDECStation(**metadata)
#                station.save()
