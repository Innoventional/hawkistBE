import json
import logging
import urllib2

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


def get_city_by_code(post_code):
    error = ''
    city = ''
    opener = urllib2.build_opener()
    url = 'http://maps.googleapis.com/maps/api/geocode/json?address={0}&sensor=false'.format(post_code)
    response = opener.open(url).read()
    response_dict = json.loads(response)
    request_status = response_dict['status']
    if request_status == 'OK':
        logger.debug('Google response')
        logger.debug(response_dict)
        results = response_dict['results']
        """
        first get  all results
        with required zip code
        """
        results_with_required_zip_code = []
        for result in results:
            address_components = result['address_components']
            for address_component in address_components:
                types = address_component['types']
                for t in types:
                    if t == 'postal_code' and address_component['short_name'].lower() == post_code.lower():
                        results_with_required_zip_code.append(result)
        if not results_with_required_zip_code:
            error = {
                'status': '8',
                'message': 'Unable to match your Post Code with a City or Location. Please check it and try again'
            }
            # error = 'No location with post code %s' % post_code
        else:
            """
            next we need all results in GB
            """
            results_with_required_zip_code_in_GB = ''
            for good_result in results_with_required_zip_code:
                address_components = good_result['address_components']
                for address_component in address_components:
                    types = address_component['types']
                    for t in types:
                        if t == 'country' and address_component['short_name'].lower() == 'GB'.lower():
                            results_with_required_zip_code_in_GB = good_result
            if not results_with_required_zip_code_in_GB:
                error = {
                    'status': '7',
                    'message': 'Please check the Post Code to ensure that it is correctly formatted'
                }
                # error = 'No city with post code %s in GB' % post_code
            else:
                """
                finally find city name
                """
                address_components = results_with_required_zip_code_in_GB['address_components']
                # first try get postal city
                searching_city = get_city_by_key(address_components, 'postal_town')
                if not searching_city:
                    # next by administrative_area_level_2
                    searching_city = get_city_by_key(address_components, 'administrative_area_level_2')
                if not searching_city:
                    print url
                    error = {
                        'status': '7',
                        'message': 'Please check the Post Code to ensure that it is correctly formatted'
                    }
                    # error = 'No city with post code %s in GB' % post_code
                else:
                    city = searching_city
    elif request_status == 'ZERO_RESULTS':
        error = {
            'status': '8',
            'message': 'Unable to match your Post Code with a City or Location. Please check it and try again'
        }
        # error = 'Wrong post code %s' % post_code
    else:
        error = request_status
    return {
        'error': error,
        'data': city
    }


def get_city_by_key(address_components, key):
    result = ''
    for address_component in address_components:
        types = address_component['types']
        for t in types:
            if t == key:
                result = address_component['long_name']
    return result

if __name__ == '__main__':
    print get_city_by_code('NR100')
    # print get_city_by_code('BFPO')
