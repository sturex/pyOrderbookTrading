
#works only for XBTUSD
#for other symbols see https://www.bitmex.com/app/restAPI
def get_price_from_ID(id):
    return 1000000 - (id % 100000000) / 100   


def get_YYYYMMDD(datetime_UTC):
    return datetime_UTC.year * 10000 + datetime_UTC.month * 100 + datetime_UTC.day

def get_HHMMSSmmm(datetime_UTC):
    return datetime_UTC.hour * 10000000 + datetime_UTC.minute * 100000 + datetime_UTC.second * 1000 + int(datetime_UTC.microsecond / 1000)