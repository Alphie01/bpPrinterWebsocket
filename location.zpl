^XA
        ^FX set width and height
        ^PW799 ^FX size in points = 100 mm width
        ^LL630   ^FX size in points = 80 mm height
        ^CI28
        ^MMT    ^FX set media type to Tear-off
        ^BY3,3  ^FX set the bar code height and gap between labels (gap in dots, 3 mm = 12 dots at 8 dots/mm)
        ^FX border start
        ^FO10,10^GB750,2,2^FS ^FX TOP
        ^FO10,10^GB2,600,2,B^FS ^FX LEFT
        ^FO759,10^GB2,600,2,B^FS ^FX RIGHT
        ^FO10,618^GB750,2,2^FS ^FX BOTTOM
        ^FX border end
        ^FX companySection
        ^FO18,25
        ^A0N,25,25
        ^FDFrima Adi / Depo^FS

        ^FO25,55
        ^A0N,50,50
        ^FDBil Plastik Ambalaj / Ana Fabrika^FS

        ^FO10,110^GB750,2,2^FS 
        ^FX end of CompanySection

        ^FO18,120
        ^A0N,35,35
        ^FDSevkiyat Ürün Deposu  ^FS  ^FS ^FX 30 charecter max        
        ^FX start bottom table
        ^CF0,40
        ^FO10,200^FB375,1,0,C^FDAlt Raf^FS
        ^A0N,30,30^FO10,250^FB375,1,0,C^FDDP-S-{i}1^FS
        ^FO90,320
        ^BQN,2,10
        ^FDLA,DP-S-{i}1^FS

        ^CF0,40
        ^FO390,200^FB375,1,0,C^FDÜst Raf^FS
        ^A0N,30,30^FO390,250^FB375,1,0,C^FDDP-S-{i}2^FS
        ^FO470,320
        ^BQN,2,10
        ^FDLA,DP-S-{i}2^FS
        ^FO10,170^GB375,450,2^FS
        ^FO385,170^GB375,450,2^FS
        ^XZ