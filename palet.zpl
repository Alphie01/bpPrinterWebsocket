^XA
^FX ================================
^FX PALET ETİKETİ TASARIMI
^FX Boyut: 100mm x 80mm
^FX ================================

^FX Label dimensions and setup
^PW799    ^FX Label width = 100mm 
^LL630    ^FX Label height = 80mm
^CI28     ^FX Character set UTF-8
^MMT      ^FX Media type: Tear-off

^FX ================================
^FX ANA ÇERÇEVE
^FX ================================
^FO5,5^GB790,620,3^FS    ^FX Dış çerçeve

^FX ================================
^FX ÜST BAŞLIK BÖLÜMÜ
^FX ================================
^FO10,10^GB780,80,2^FS   ^FX Başlık kutusu
^FO15,25
^A0N,30,25
^FDBİL PLASTİK AMBALAJ A.Ş.^FS

^FO15,50
^A0N,20,15
^FDPALET ETİKETİ^FS

^FX ================================
^FX ÜRÜN BİLGİ BÖLÜMÜ
^FX ================================
^FO10,95^GB780,2,2^FS    ^FX Ayırıcı çizgi

^FO15,105
^A0N,25,20
^FDÜrün Kodu:^FS
^FO200,105
^A0N,25,20
^FD{product_code}^FS

^FO15,135
^A0N,25,20
^FDÜrün Adı:^FS
^FO200,135
^A0N,22,18
^FD{product_name}^FS

^FO15,165
^A0N,25,20
^FDHammadde:^FS
^FO200,165
^A0N,22,18
^FD{hammadde}^FS

^FX ================================
^FX PALET BİLGİ BÖLÜMÜ
^FX ================================
^FO10,195^GB780,2,2^FS   ^FX Ayırıcı çizgi

^FO15,205
^A0N,25,20
^FDPalet ID:^FS
^FO150,205
^A0N,25,20
^FD{palet_id}^FS

^FO400,205
^A0N,25,20
^FDLot No:^FS
^FO500,205
^A0N,25,20
^FD{lot_no}^FS

^FO15,235
^A0N,25,20
^FDÜretim Tarihi:^FS
^FO180,235
^A0N,25,20
^FD{production_date}^FS

^FO400,235
^A0N,25,20
^FDSon Kullanma:^FS
^FO550,235
^A0N,25,20
^FD{expiry_date}^FS

^FX ================================
^FX AĞIRLIK VE MİKTAR BİLGİSİ
^FX ================================
^FO10,265^GB780,2,2^FS   ^FX Ayırıcı çizgi

^FO15,275
^A0N,25,20
^FDAdet:^FS
^FO100,275
^A0N,30,25
^FD{quantity} AD^FS

^FO250,275
^A0N,25,20
^FDBrüt Ağırlık:^FS
^FO400,275
^A0N,30,25
^FD{gross_weight} KG^FS

^FO15,305
^A0N,25,20
^FDAmbalaj:^FS
^FO150,305
^A0N,25,20
^FD{package_type}^FS

^FO400,305
^A0N,25,20
^FDNet Ağırlık:^FS
^FO550,305
^A0N,30,25
^FD{net_weight} KG^FS

^FX ================================
^FX FİRMA VE DEPARTMAN BİLGİSİ
^FX ================================
^FO10,335^GB780,2,2^FS   ^FX Ayırıcı çizgi

^FO15,345
^A0N,22,18
^FDTeslim Alan Firma:^FS
^FO200,345
^A0N,22,18
^FD{receiving_company}^FS

^FO15,370
^A0N,22,18
^FDBölüm/Depo:^FS
^FO150,370
^A0N,22,18
^FD{department}^FS

^FO400,370
^A0N,22,18
^FDSorumlu:^FS
^FO500,370
^A0N,22,18
^FD{responsible_person}^FS

^FX ================================
^FX ALT BÖLÜM VE QR KOD
^FX ================================
^FO10,400^GB520,2,2^FS   ^FX Sol bölüm ayırıcısı
^FO530,335^GB2,265,2^FS  ^FX Dikey ayırıcı QR kod için

^FO15,410
^A0N,20,15
^FDSipariş No:^FS
^FO150,410
^A0N,20,15
^FD{order_no}^FS

^FO15,435
^A0N,20,15
^FDSipariş Tarihi:^FS
^FO150,435
^A0N,20,15
^FD{order_date}^FS

^FO15,460
^A0N,20,15
^FDDurum:^FS
^FO80,460
^A0N,22,18
^FD{status}^FS

^FO15,485
^A0N,20,15
^FDNot:^FS
^FO60,485
^A0N,18,15
^FD{notes}^FS

^FX QR KOD BÖLÜMÜ
^FO545,345
^BQN,2,8
^FDLA,{palet_id}-{lot_no}-{product_code}^FS

^FO535,520
^A0N,15,12
^FDPALET QR^FS

^FX ================================
^FX ALT ÇERÇEVE
^FX ================================
^FO10,600^GB780,2,2^FS   ^FX Alt çizgi

^FO15,610
^A0N,12,10
^FDBaskı Tarihi: {print_date} | Baskı Saati: {print_time}^FS

^XZ