import sys
sys.path.append('..')

from database.chunk import Vips

from urllib.parse import unquote

def main():
    vips = Vips(unquote("https://newsis.com/view/?id=NISX20230911_0002445882", encoding="utf-8"))
    vips.setRound(10)
    vips.service()
    
main()
