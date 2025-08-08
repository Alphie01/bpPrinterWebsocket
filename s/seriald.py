import serial
import json
import time

def send_zpl_to_printer(port: str, baudrate: int, zpl_command: str):
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            ser.write(zpl_command.encode('utf-8'))
            ser.flush()
            print("ZPL komutu başarıyla gönderildi.")
    except Exception as e:
        print(f"Hata oluştu: {e}")

def generate_zpl_label(
    firma, production_date, lot_code, product_code, product_name, personel_code,
    total_amount, qr_code, bom, hat_kodu, siparis_kodu, firma_kodu, adet_bilgisi,
    uretim_miktari_checked=True, adet_girisi_checked=True,
    firma_bilgileri_checked=True, brut_kg_checked=True
):
    def split_string(text, length=50):
        return text[:length], text[length:] if len(text) > length else ""

    code1, code2 = split_string(product_code)
    name1, name2 = split_string(product_name)
    
    kg_total_amount = (
        "^CF0,25\n"
        "^FO10,385^FB375,1,0,C^FDUretim miktari / Total Amount^FS\n"
        "^A0N,60,60^FO10,415^FB375,1,0,C^FD{}^FS\n"
    ).format(total_amount)
    
    paket_ici_adet = (
        "^CF0,25\n"
        "^FO365,385^FB375,1,0,C^FDParca ic adedi^FS\n"
        "^FO365,410^FB375,1,0,C^FDUnits Per Package^FS\n"
        "^A0N,35,35^FO365,440^FB375,1,0,C^FD{}^FS\n"
    ).format(adet_bilgisi)
    
    firma_bilgileri = (
        "^CF0,25\n"
        "^FO10,490^FB375,1,0,C^FDFirma Kodu / CompanyCode^FS\n"
        "^A0N,30,30^FO10,515^FB375,1,0,C^FD{}^FS\n"
        "^CF0,25\n"
        "^FO10,555^FB375,1,0,C^FDSiparis kodu / Sales Code^FS\n"
        "^A0N,30,30^FO10,585^FB375,1,0,C^FD{}^FS\n"
    ).format(firma_kodu, siparis_kodu)
    
    burut_kg = float(total_amount) + 0.5  # Utils.dara yerine sabit dara eklendi
    formatted_brut_kg = "{:.2f}".format(burut_kg)
    
    brut_kg = (
        "^CF0,25\n"
        "^A0N,20,20^FO390,490^FB375,1,0,C^FDBrut kg / total Weight kg^FS\n"
        "^A0N,50,50^FO390,515^FB375,1,0,C^FD{}^FS\n"
    ).format(formatted_brut_kg)
    
    zpl_label = []
    
    start_main_design = f"""
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
        ^FDFrima Adi /Customer Name^FS

        ^FO25,55
        ^A0N,50,50
        ^FD{firma}^FS

        ^FX black box
        ^FO660,10
        ^GB100,100,80^FS
        ^FR
        ^FO665,30
        ^A0N,80,80
        ^FD {hat_kodu}^FS
        ^FX end of black box

        ^FX border start
        ^FO550,35
        ^GB100,50,4^FS    
        ^FO560,45
        ^A0N,45,45
        ^FD {bom}^FS   
        ^FX border end

        ^FO10,110^GB750,2,2^FS 
        ^FX end of CompanySection

        ^FO18,120
        ^A0N,35,35
        ^FD{code1}  ^FS  ^FS ^FX 30 charecter max

        ^FO18,160
        ^A0N,35,35
        ^FO10,160^GB750,2,2^FS 

        ^FO18,170
        ^A0N,42,42
        ^FD{name1}^FS ^FX 35 charecter max
        ^FO18,220
        ^A0N,42,42
        ^FD${name2}^FS ^FX 35 charecter max
        ^FO10,270^GB750,2,2^FS 
        ^FO10,275^GB750,2,2^FS 
        ^FX start table

        ^FO10,275^GB750,2,2^FS

        ^FO10,275^GB250,50,2^FS
        ^FO260,275^GB250,50,2 ^FS
        ^FO510,275^GB250,50,2 ^FS

        ^CF0,30
        ^A0N,20,20^FO10,290^FB250,1,0,C^FDU. Tarihi / Production Date^FS
        ^A0N,25,25^FO260,290^FB250,1,0,C^FDLot kodu / Lot Code^FS
        ^A0N,25,25^FO510,290^FB250,1,0,C^FDP.kodu / E. Code^FS


        ^FO10,325^GB250,50,2^FS
        ^FO260,325^GB250,50,2 ^FS
        ^FO510,325^GB250,50,2 ^FS

        ^CF0,30
        ^A0N,25,25^FO20,340^FB250,1,0,C^FD{production_date}^FS
        ^A0N,25,25^FO270,340^FB250,1,0,C^FD{lot_code}^FS
        ^A0N,25,25^FO530,340^FB250,1,0,C^FD{personel_code}^FS

        ^FX end of table

        ^FX start bottom table
        
        ^FO10,375^GB375,100,2^FS
        ^FO385,375^GB270,100,2 ^FS
        
  
        ^FO665,375^BQN,2,4
        ^FDQA,{product_code}^FS
        
        ^FX END BOTTOM TABLE
        
        
        ^FX start bottom table
        
        ^FO10,480^GB375,140,2^FS
        ^FO385,480^GB375,140,2^FS

            """
    
    zpl_label.append(start_main_design)
    
    if uretim_miktari_checked:
        zpl_label.append(kg_total_amount)
    if adet_girisi_checked:
        zpl_label.append(paket_ici_adet)
    if firma_bilgileri_checked:
        zpl_label.append(firma_bilgileri)
    if brut_kg_checked:
        zpl_label.append(brut_kg)
    
    zpl_label.append("^XZ")
    
    return "".join(zpl_label).strip()

# Örnek kullanım
serial_port = "COM2"  # Windows için (Linux/Mac için: "/dev/ttyUSB0" gibi)
baudrate = 9600
""" zpl_label = generate_zpl_label("T. İŞ BANKASI A.Ş DESTEL", "2025-03-28", "98649 - 004", "PRD-001", '(LDPE) SEFFAF 12 DELiKLi PARA TORBASI BASKISIZ SEFFAF 100 Mic 38x60', "P123", "100", "QRCodeData", "", "S", "", "NAYLON PARA POSETI BÜYUK", "250", brut_kg_checked=False, uretim_miktari_checked=False, adet_girisi_checked=True, firma_bilgileri_checked=True)
print(zpl_label) """

file_path = "data_IS.json"  # JSON dosyasının yolu

with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
for obj in data:
    zpl_label = generate_zpl_label(
        "T. İŞ BANKASI A.Ş DESTEL",
        obj['tarih'],
        "98649 - 004",
        obj['etiket'],
        "(LDPE) SEFFAF 12 DELiKLi PARA TORBASI BASKISIZ SEFFAF 100 Mic 38x60",
        obj['sicil'],
        obj.get("total_amount", "100"),
        obj['etiket'],
        "",
        "S",
        "",
        "NAYLON PARA POSETI BÜYÜK",
        "250",
        brut_kg_checked=False,
        uretim_miktari_checked=False,
        adet_girisi_checked=True,
        firma_bilgileri_checked=True
    )
    print(zpl_label)
    send_zpl_to_printer(serial_port, baudrate, zpl_label)
    time.sleep(2)