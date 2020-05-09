import re


def test(path):
    pat = re.compile('(/(.|[\r\n])*)|(ns:[0-9]+(/.*)?)|(id:.*)')
    return pat.match(path)
