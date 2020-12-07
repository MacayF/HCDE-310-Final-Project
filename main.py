from flask import Flask, render_template, request
import urllib.parse, urllib.request, urllib.error, json
import logging

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
def search_resturants(limit= None, offset= None, location= 'seattle', radius= None, categories= None):
    baseurl = 'https://api.yelp.com/v3/businesses/search'

    params = {}
    if limit != None:
        params['limit'] = limit
    if offset != None:
        params['offset'] = offset
    params['location'] = location
    if radius != None:
        if radius < 24:
            params['radius'] = int(radius * 1609.34)
        else:
            params['radius'] = 40000
    params['categories'] = categories

    paramstr = urllib.parse.urlencode(params)
    request = baseurl + '?' + paramstr
    header = {'Authorization': 'Bearer %s' % yelp_key.key}
    req = urllib.request.Request(request, headers=header)

    return safe_get(req)

def business_info(api_key= None, id= 'None'):
    baseurl = 'https://api.yelp.com/v3/businesses/'

    request = baseurl + id
    header = {'Authorization': 'Bearer %s' % yelp_key.key}
    req = urllib.request.Request(request, headers=header)

    return safe_get(req)


def gen_rest_info(location= 'Seattle', radius=None, categories=None):
    rest_data = search_resturants(limit= 5, offset= None, location= location, radius= radius, categories= categories)
    for resturant in rest_data['businesses']:
        print(resturant['name'])
        rest_details = business_info(id= resturant['id'])
        print('rating: {}'.format(rest_details['rating']))
        print('cuisine:')
        styles = []
        for style in resturant['categories']:
            styles.append(style['title'])
        print(styles)
        print('')

@app.route("/", methods=['GET', 'POST'])
def start():
    app.logger.info("In MainHandler")
    if request.method == 'POST':
        app.logger.info(request.form.get('radius'))
        radius = int(request.form.get('radius'))
        category = request.form.get('category')

        output = search_resturants(limit= 3, offset= None, location='5021 Brooklyn ave NE, Seattle, WA 98105', radius= radius, categories= category)
        rest_list = []
        for restaurant in output['businesses']:
            rest_list.append(restaurant['name'])

        #print(pretty(business_info(api_key= api_key, id = din_id)))

        title = "Thirdwheel Prototype"
        data = {'radius': radius, 'category': category}
        return render_template('index.html', title=title, data=data, list=rest_list)

    #page start without user input
    else:
        title = "Thirdwheel Prototype"
        data = {'name': 'Macay is cool'}
        return render_template('index.html', title=title, data=data)


@app.route("/eagle")
def with_eagle():
    """ Return a greeting """
    title = "Hello!"
    data = {'name': 'Macay', 'image': 'eagle.png'}
    return render_template('index.html', title=title, data=data)


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)