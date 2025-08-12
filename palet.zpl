^XA
^FX Palet Etiketi - Bil Plastik Ambalaj
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
^FDFirma Adı / Depo^FS

^FO25,55
^A0N,50,50
^FD{firma_adi} / {depo_adi}^FS

^FO10,110^GB750,2,2^FS 
^FX end of CompanySection

^FO18,120
^A0N,35,35
^FD{sevkiyat_bilgisi}^FS ^FX 30 character max

^FO10,160^GB750,2,2^FS 

^FO18,170
^A0N,42,42
^FD{hammadde_ismi}^FS ^FX 35 character max
^FO18,220
^A0N,42,42
^FD{urun_adi}^FS ^FX 35 character max

^FO10,270^GB750,2,2^FS 
^FO10,275^GB750,2,2^FS 

^FX start bottom section
^CF0,40
^FO20,300^FDTeslim Alınan Firma - Bölüm: {teslim_firma}^FS
^FO20,350^FDSipariş Tarihi: {siparis_tarihi}^FS
^FO20,400^FDPalet ID: {palet_id}^FS
^FO20,450^FDDurum: {durum}^FS
^FO20,500^FDBrüt KG.: {brut_kg}^FS
^FO20,550^FDNet KG.: {net_kg}^FS

^FX QR Code section
^CF0,40
^FO620,470
^BQN,2,6
^FDLA,{palet_id}-{lot_no}^FS

^FO600,460^GB160,160,2^FS
^XZ