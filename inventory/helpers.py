ROUND_DIGITS = 2

def calc_price(ori_price, markup):
    return round(ori_price * markup, ROUND_DIGITS)
