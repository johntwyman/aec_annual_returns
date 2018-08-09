#scrapers gonna scrape

import csv
import mechanize
import lxml.html
import scraperwiki
import requests

annDonorsurl = "https://periodicdisclosures.aec.gov.au/AnalysisDonor.aspx"

periods = [
{"year":"1998-1999","id":"1"},
{"year":"1999-2000","id":"2"},
{"year":"2000-2001","id":"3"},
{"year":"2001-2002","id":"4"},
{"year":"2002-2003","id":"5"},
{"year":"2003-2004","id":"6"},
{"year":"2004-2005","id":"7"},
{"year":"2005-2006","id":"8"},
{"year":"2006-2007","id":"9"},
{"year":"2007-2008","id":"10"},
{"year":"2008-2009","id":"23"},
{"year":"2009-2010","id":"24"},
{"year":"2010-2011","id":"48"},
{"year":"2011-2012","id":"49"},
{"year":"2012-2013","id":"51"},
{"year":"2013-2014","id":"55"},
{"year":"2014-2015","id":"56"},
{"year":"2015-2016","id":"60"},
{"year":"2016-2017","id":"64"}
]

partyGroups = [{"entityID":4,"group":"alp"},
{"entityID":52,"group":"alp"},
{"entityID":55,"group":"alp"},
{"entityID":50,"group":"alp"},
{"entityID":64,"group":"alp"},
{"entityID":54,"group":"alp"},
{"entityID":27,"group":"alp"},
{"entityID":51,"group":"alp"},
{"entityID":53,"group":"alp"},
{"entityID":132,"group":"alp"},
{"entityID":32,"group":"greens"},
{"entityID":72,"group":"greens"},
{"entityID":138,"group":"greens"},
{"entityID":1100,"group":"greens"},
{"entityID":98,"group":"greens"},
{"entityID":31,"group":"greens"},
{"entityID":97,"group":"greens"},
{"entityID":205,"group":"greens"},
{"entityID":137,"group":"greens"},
{"entityID":4028,"group":"greens"},
{"entityID":158,"group":"greens"},
{"entityID":153,"group":"greens"},
{"entityID":207,"group":"greens"},
{"entityID":186,"group":"greens"},
{"entityID":27964,"group":"greens"},
{"entityID":6,"group":"liberal"},
{"entityID":40,"group":"liberal"},
{"entityID":46,"group":"liberal"},
{"entityID":35,"group":"liberal"},
{"entityID":44,"group":"liberal"},
{"entityID":36,"group":"liberal"},
{"entityID":43,"group":"liberal"},
{"entityID":41,"group":"liberal"},
{"entityID":211,"group":"liberal"},
{"entityID":19,"group":"nationals"},
{"entityID":37,"group":"nationals"},
{"entityID":39,"group":"nationals"},
{"entityID":38,"group":"nationals"},
{"entityID":49,"group":"nationals"},
{"entityID":42,"group":"nationals"},
{"entityID":24,"group":"liberal"}
]

#Check if scraper has been run before, see where it got up to

if scraperwiki.sqlite.get_var('upto'):
    upto = scraperwiki.sqlite.get_var('upto')
    print "Scraper upto:",upto,"period:",periods[upto]['year']
else:
    print "Scraper first run"
    upto = 0

#to run entirely again, just set upto to 0
upto = 0

#unique number for every entry

count = scraperwiki.sqlite.get_var('count')

#Scrape for time periods taking into account previous runs using 'upto'

for x in xrange(upto, len(periods)):
    br = mechanize.Browser()
    response = br.open(annDonorsurl)
    print "Loading data for "+periods[x]['year']
    #for form in br.forms():
    #    print form


    #print "All forms:", [ form.name  for form in br.forms() ]

    br.select_form(nr=0)
    #print br.form
    print periods[x]['id']

    br['ctl00$dropDownListPeriod']=[periods[x]['id']]
    response = br.submit("ctl00$buttonGo")

    response = br.open(annDonorsurl)
    br.select_form(nr=0)
    response = br.submit("ctl00$ContentPlaceHolderBody$analysisControl$buttonAnalyse")


    br.select_form(nr=0)
    br['ctl00$ContentPlaceHolderBody$pagingControl$cboPageSize']=["999999"]
    response = br.submit("ctl00$ContentPlaceHolderBody$pagingControl$buttonGo")

    html = response.read()
    #print html

    root = lxml.html.fromstring(html)
    trs = root.cssselect("#ContentPlaceHolderBody_gridViewAnalysis tr")

    #get last row scraped

    if scraperwiki.sqlite.get_var('uptotrs'):
        uptotrs = scraperwiki.sqlite.get_var('uptors')
        #print "Scraper upto row:", uptotrs
    else:
        print "Scraper first row"
        uptotrs = 1

    uptotrs = 1

    for i in xrange(uptotrs,len(trs)):
        #print i
        tds = trs[i].cssselect("td")

        donType = lxml.html.tostring(tds[0]).split('<a href="')[1].split('.aspx?')[0]
        #print donType
        submissionID = lxml.html.tostring(tds[0]).split('SubmissionId=')[1].split('&amp;ClientId=')[0]
        #print submissionID
        clientID = lxml.html.tostring(tds[0]).split('ClientId=')[1].split('">')[0]
        #print clientID
        donName = lxml.html.tostring(tds[0]).split('">')[2].split('</a')[0]
        print donName
        address = tds[1].text
        #print address
        state = tds[2].text
        #print state
        postcode = tds[3].text
        #print postcode
        value = tds[4].text.replace("$", "").replace(",","")
        #print value
        donUrl = lxml.html.tostring(tds[0]).split('<a href="')[1].split('">')[0]
        #print donUrl
        recipName = lxml.html.tostring(tds[5]).split('">')[2].split('</a')[0]
        #print recipName
        recipUrl = lxml.html.tostring(tds[5]).split('<a href="')[1].split('">')[0]
        #print recipUrl
        recipType = lxml.html.tostring(tds[5]).split('<a href="')[1].split('.aspx?')[0]
        #print "recipType", recipType
        recipID = lxml.html.tostring(tds[5]).split('ClientId=')[1].split('">')[0]
        #print recipID

        fixedUrl = 'http://periodicdisclosures.aec.gov.au/' + donUrl.replace("amp;","")
        html = requests.get(fixedUrl).content
        dom = lxml.html.fromstring(html)
        h2s = dom.cssselect(".rightColfadWideHold h2")
        if donType == "Donor" or donType == "AssociatedEntity":
            cleanDonName = h2s[0].text.strip()
            #print cleanDonName.strip()
        if donType == "Party":
            cleanDonName = h2s[1].text.strip()
            #print cleanDonName.strip()

        fixedUrl = 'http://periodicdisclosures.aec.gov.au/' + recipUrl.replace("amp;","")
        html = requests.get(fixedUrl).content
        #print fixedUrl, donType
        dom = lxml.html.fromstring(html)
        h2s = dom.cssselect(".rightColfadWideHold h2")
        if recipType == "Donor" or recipType == "AssociatedEntity":
            cleanRecipName = h2s[0].text.strip()
            #print cleanRecipName.strip()
        if recipType == "Party":
            cleanRecipName = h2s[1].text.strip()
            #print cleanRecipName.strip()


        data = {}
        data['period'] = periods[x]['year']
        data['submissionID'] = submissionID
        data['clientID'] = clientID
        data['recipID'] = recipID
        data['donType'] = donType
        data['donName'] = donName
        data['cleanDonName'] = cleanDonName
        data['recipName'] = recipName
        data['cleanRecipName'] = cleanRecipName
        data['value'] = value
        data['address'] = address
        data['state'] = state
        data['postcode'] = postcode
        data['donUrl'] = donUrl
        data['recipUrl'] = recipUrl
        data['yearcount'] = i

        for groupID in partyGroups:
            if recipID == groupID['entityID']:
                data['partyGroup'] = groupID['group']

        #print data
        scraperwiki.sqlite.save(unique_keys=["yearcount","donUrl","period"], data=data)
        scraperwiki.sqlite.save_var('uptotrs', i)

    scraperwiki.sqlite.save_var('upto', x)
