from flask import Flask, render_template, request
import urllib.parse, urllib.request, urllib.error, json
import logging
import random

app = Flask(__name__)

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safe_get(url):
    try:
        mypage = urllib.request.urlopen(url)
        requeststr = mypage.read().decode('utf-8')
        resturantdata = json.loads(requeststr)
    except urllib.error.HTTPError as e:
        print("The server couldn't fulfill the request.")
        print("Error code: ", e.code)
    except urllib.error.URLError as e:
        print("We failed to reach a server")
        print("Reason: ", e.reason)
    else:
        return resturantdata

import yelp_key as yelp_key
def search_resturants(limit= None, offset= None, location= 'New York', latitude= None, longitude= None, radius= None,
                      categories= None, open_now= False, term= None):
    baseurl = 'https://api.yelp.com/v3/businesses/search'

    params = {}
    if limit != None:
        params['limit'] = limit
    if offset != None:
        params['offset'] = offset
    if latitude==None and longitude==None:
        params['location'] = location
    else:
        params['latitude'] = latitude
        params['longitude'] = longitude
    if radius != None:
        if radius < 24:
            params['radius'] = int(radius * 1609.34)
        else:
            params['radius'] = 40000
    params['categories'] = categories
    params['open_now'] = open_now
    params['sort_by'] = 'rating'
    params['term'] = term

    paramstr = urllib.parse.urlencode(params)
    request = baseurl + '?' + paramstr
    header = {'Authorization': 'Bearer %s' % yelp_key.key}
    req = urllib.request.Request(request, headers=header)

    return safe_get(req)

def business_info(id= 'None'):
    baseurl = 'https://api.yelp.com/v3/businesses/'

    request = baseurl + id
    header = {'Authorization': 'Bearer %s' % yelp_key.key}
    req = urllib.request.Request(request, headers=header)

    return safe_get(req)

@app.route("/", methods=['GET', 'POST'])
def start():
    title = "Thirdwheel Prototype"
    data = {'name': 'Macay is cool'}
    return render_template('index.html', title=title, data=data)


@app.route("/go", methods=['GET', 'POST'])
def go():
    app.logger.info("In MainHandler")
    if request.method == 'POST':
        app.logger.info(request.form.get('radius'))
        radius = int(request.form.get('radius'))
        #category = request.form.get('category')
        category = 'restaurants,food'
        term = request.form.get('term')
        if request.form.get('open-now') == 'open':
            open_now = True
        else:
            open_now = False

        if request.form.get('lat') != '0':
            lat = float(request.form.get('lat'))
            lng = float(request.form.get('lng'))
            location = None
        else:
            lat = None
            lng = None
            location = request.form.get('address')

        output = search_resturants(limit= 50, latitude= lat, location= location, longitude= lng, offset= None, radius= radius, categories= category, open_now = open_now, term= term)
        rest_list = []
        for restaurant in output['businesses']:
            rest_list.append(restaurant['id'])

        rest_dict = {}
        for x in range(0, 10):
            rest_id = random.choice(rest_list)
            rest_list.remove(rest_id)

            if rest_id not in rest_dict:
                rest_dict[rest_id] = business_info(id=rest_id)

        title = "Thirdwheel Prototype"
        data = {'radius': radius, 'category': category}
        return render_template('page2.html', title=title, data=data, dict=rest_dict)


@app.route("/select", methods=['GET', 'POST'])
def select():
    app.logger.info("In MainHandler")
    if request.method == 'POST':
        app.logger.info(request.form.get('radius'))
        selected = request.form.getlist('option')

        data = {}
        for rest_id in selected:
            data[rest_id] = business_info(id=rest_id)

        print("here is the data info")
        print(data)

        title = "Thirdwheel Prototype"
        return render_template('page3.html', title=title, data=data)

@app.route("/map", methods=['GET', 'POST'])
def map():
    app.logger.info("In MainHandler")
    if request.method == 'POST':
        selected = request.form.get('option')

        restaurant = business_info(id=selected)

        googlekey = yelp_key.key2
        title = "Thirdwheel Prototype"
        return render_template('page4.html', title=title, data=restaurant, googlekey=googlekey)

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)