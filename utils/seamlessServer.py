#!/usr/bin/env python

#
# A python library for communicating with seamless data servers such as
# USGS and LANDFIRE.
#

#http://extract.cr.usgs.gov/Website/distreq/RequestOptions.jsp?PR=0&CU=Native&ZX=-1.0&ZY=-1.0&ML=COM&MD=DL
#              &AL=39.74127369858583,38.49736905526963,-106.24611383354475,-107.90622991644965&CS=250&PL=ND302XT
#http://landfire.cr.usgs.gov/Website/distreq/RequestSummary.jsp?AL=39.89679054054048,39.300084459459406,-105.99712837837805,-106.63361486486454&CS=250&UTMDATUM=0&PL=F0J02XT

import cookielib
import os
import tarfile
import sys
import re
from subprocess import call

from beautifulSoup import BeautifulStoneSoup as xmlparser
import mechanize
import zipfile
from zipfile import ZipFile

ned3={\
    'name':'ned3',\
    'servURL':'http://extract.cr.usgs.gov/Website/distreq/RequestSummary.jsp?',\
    'prodCode':'ND302XT',\
    'destVar':'ZSF',\
    'units':'meters',\
    'description':'National Elevation Dataset 1/3 arcsecond resolution.',\
    'tilesize':'1300'}

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 300
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=30.0)

def setHTTPDebug():
    # Want debugging messages?
    br.set_debug_http(True)
    br.set_debug_redirects(True)
    br.set_debug_responses(True)

class LatLonBounds(object):
    def __init__(self,latmax,latmin,lonmax,lonmin):
        self.latmax=latmax
        self.latmin=latmin
        self.lonmax=lonmax
        self.lonmin=lonmin
    
    def URLfmt(self):
        return "%f,%f,%f,%f" % (self.latmax,self.latmin,self.lonmax,self.lonmin)

class ProductCode(object):
    meta_d={'XML':'X','HTML':'H','TXT':'T'}
    comp_d={'tgz':'T','zip':'Z'}
    form_d={'ArcGRID':'01','GeoTIFF':'02'}
    def __init__(self,base,meta='XML',comp='tgz',form='GeoTIFF'):
        self.base=base
        self.meta=meta
        self.comp=comp
        self.form=form
    
    def __str__(self):
        if len(self.base)>=4:
            return self.base
        else:
            return "%s%s%s%s" % (self.base,self.form_d[self.form],self.meta_d[self.meta],self.comp_d[self.comp])

class SeamlessServer(object):
    projs={ \
           'native':'PR=0&CU=Native',\
           'lfnative':'UTMDATUM=0'
    }
    misc='ZX=-1.0&ZY=-1.0&ML=COM&MD=DL'
    boundskwd='AL'
    downloadsizekwd='CS'
    productkwd='PL'
    def __init__(self,baseURL,parent):
        self.baseURL=baseURL
        self.parent=parent
    
    def getURL(self,product,bounds,proj='native',dlsize=250):
        return self.baseURL+\
               "&".join([self.projs[proj], \
                         self.misc,"%s=%s" %(self.boundskwd,bounds.URLfmt()),\
                         "%s=%i" %(self.downloadsizekwd,dlsize),\
                         "%s=%s" %(self.productkwd,product)])
    
    def getBaseURL(self):
        return self.baseURL
    
    def getDataURL(self,URL):
        dURL = ""
        first = True
        # Don't allow the program the stop querying the server, ever.
        while re.search("tgz",dURL) == None:
            if not first:
                print "Extracting the files server-side is taking a while. Please be patient.\n";
            br.open(URL)
            #self.parent.emit("opened!\n")
            br.select_form(nr=0)
            #self.parent.emit("selected!\n")
            try:
                br.submit()
            except:
                pass
            #self.parent.emit("submitted!\n")
            r=br.response()
            #self.parent.emit("responded!\n")
            dURL=r.geturl()
            #self.parent.emit("got r done!\n")
            #print "dURL: "+dURL
            first=False
        return dURL
    
    def getData(self,product,bounds,targetdir='data',proj='native',dlsize=250):
        URL=self.getURL(product,bounds,proj,dlsize)
        dURL=self.getDataURL(URL)
        v=br.retrieve(dURL)
        
        # Found Zipfile
        if zipfile.is_zipfile(v[0]):
            #print("Found a zipfile.")
            filename =v[0].rstrip()
            filenames=self.unzip(filename, targetdir)
        else:
            # Found a tarball
            f=tarfile.open(v[0],'r')
            try:
                os.mkdir(targetdir)
            except OSError:
                pass
            if not os.path.isdir(targetdir):
                raise OSError("Could not create target directory in %s."%targetdir)
            
            # The extractall() method of TarFile will only work in Python 2.6 and up
            try:
                f.extractall(path=targetdir, members=None)
            except:
                # Workaround for old Python versions
                for mem in f.getmembers():
                    f.extract(mem, path=targetdir)
    
            filenames=f.getnames()
        
        description=None
        datafile=None
            
        print("Extracted files:")
        for g in filenames:
            f=os.path.join(targetdir,g)
            print("\t"+f)
            if f.split("/")[-1] == "w001001.adf":
                datafile = f
        name=product
        return (datafile,name)

    # Function to unzipping the contents of the zip file
    #
    def unzip(self, daZip, daTarget):
        realZip=(daZip).replace("\\", "/")    
        zfobj=ZipFile(realZip)
        for name in zfobj.namelist():
            zfobj.extract(name, daTarget)
        return zfobj.namelist()

    def emit(self,message):
        self.parent.emit(message)

#--------------------------------------
# DataDef Classes
#--------------------------------------

class BaseDataDef(object):
    def __init__(self,servURL,prodCode,destVar,name,units,description,\
                      numCats=None,border=3,\
                      wordsize=2,signed=True,tilesize=100,scalefactor=1.,\
                      missingval=0.):
        self.servURL=servURL
        self.name=name
        self.baseprodCode=prodCode
        self.destVar=destVar
        self.units=units
        self.description=description
        self.numCats=numCats
        self.border=border
        self.wordsize=wordsize
        self.signed=signed
        self.tilesize=tilesize
        self.scalefactor=scalefactor
        self.missingval=missingval
        self.iscategorical=numCats != None
        self.product=ProductCode(self.baseprodCode)

    def setParent(self,parent):
        self.serverClass=SeamlessServer(self.servURL,parent)

    def getConvertArgs(self):
        args=['-b %i'%self.border,\
              '-w %i'%self.wordsize,\
              '-t %i'%self.tilesize,\
              '-s %f'%self.scalefactor,\
              '-u "%s"'%self.units,\
              '-d "%s"'%self.description]
        if self.iscategorical:
            args.append('-c %i'%self.numCats)
        else:
            args.append('-m %f'%self.missingval)
        return args

    def getServer(self):
        return self.serverClass
    
    def getNumCats(self):
        return self.numCats
    
    def getUnits(self):
        return self.units

    def getProductCode(self):
        return self.product

    def getTileSize(self):
        return self.tilesize 

    def getDestVariable(self):
        return self.destVar

    def getSourceName(self):
        return self.name

    def getSourceDescription(self):
        return self.description

class AllData(dict):
    
    def __init__(self,parent):
        self.parent=parent
    
    def read(self):
        readFile =open("dataSources.py","r")
        contents = readFile.read()
        readFile.close()
        writeFile =open("dataSources.py","w")
        writeFile.write(contents)
        writeFile.close()
        
        try:
            import dataSources
            reload (dataSources)
        except:
            print >> sys.stderr, "Could not read data source descriptions from dataSources.py"
            raise
        for n,p in dataSources.__dict__.iteritems():
            #print p
            if n[0] != '_' and type(p) == dict:
                self[n]=BaseDataDef(**p)
                self[n].setParent(self.parent)

    def getDataDef(self,name):
        if self.has_key(name):
            return self[name]
        else:
            raise Exception("Could not find data source with name %s"%name)
