from xml.dom.minidom import parseString

import httplib

def usgs_elevation(lon, lat):
	"""
	Fetch the elevation of a given longitude and latitude using the USGS web services provided. 
	Returns the elevation in feet
	"""
	conn = httplib.HTTPConnection("gisdata.usgs.gov")
	url = "/xmlwebservices2/elevation_service.asmx/getElevation?X_Value=%(longitude).8f&Y_Value=%(latitude).8f&Elevation_Units=FEET&Source_Layer=NED.CONUS_NED&Elevation_Only=TRUE" % {"longitude": lon, "latitude": lat}
	conn.request("GET", url)
	xmldata = conn.getresponse().read()
	dom = parseString(xmldata)
	xmltag = dom.getElementsByTagName("double")[0].toxml()
	elevation = float(xmltag.replace("<double>", "").replace("</double>", ""))
	return elevation