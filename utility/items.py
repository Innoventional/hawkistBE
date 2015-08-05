__author__ = 'ne_luboff'


def calculate_discount_value(retail_price, selling_price):
    """
    Discount value calculation
    """
    # calculate discount value
    discount = int(round((retail_price - selling_price) / retail_price * 100))
    # if discount less then 1 %
    if discount == 0:
        discount = 1
    # if discount almost equal to 100 %
    if discount == 100:
        discount = 99
    return discount
