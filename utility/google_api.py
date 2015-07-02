import json
import logging
import urllib2

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


def get_city_by_code(post_code):
    print '\n\n\n'
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
            error = 'No location with post code %s' % post_code
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
                error = 'No city with post code %s in GB' % post_code
            else:
                """
                finally find city name
                """
                searching_city = ''
                address_components = results_with_required_zip_code_in_GB['address_components']
                for address_component in address_components:
                    types = address_component['types']
                    for t in types:
                        if t == 'postal_town':
                            searching_city = address_component['long_name']
                if not searching_city:
                    print url
                    error = 'No city with post code %s in GB' % post_code
                else:
                    city = searching_city
    elif request_status == 'ZERO_RESULTS':
        error = 'Wrong post code %s' % post_code
    else:
        error = request_status
    return {
        'error': error,
        'data': city
    }

if __name__ == '__main__':
    print get_city_by_code('BFPO')
