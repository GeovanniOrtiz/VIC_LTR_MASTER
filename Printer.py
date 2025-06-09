from PySide6.QtCore import QCoreApplication
import serial

import socket
COM = "COM12"
HOST = "192.168.1.22"
PORT = 4100 # 9100 Para Puebla


class PrinterState:
    def __init__(self):
        self.mState = 0
        self.mText = ""

def check_error(m_string1, m_string2):
    error = ()
    if m_string1[1] == "1":
        error = "     SIN ETIQUETA",1
    elif m_string1[2] == "1" and m_string1[1] == "0" and m_string2[2] == "0":
        error = "     PAUSADA",2
    elif m_string2[2] == "1":
        error = "     ABIERTA",3
    elif m_string2[3] == "1":
        error = "     VERIFICAR RIBBON",4
    else:
        error = "     CONECTADA",0
    return error

def ConsultStatePrint(ui_main, printer_state):
    try:
        # Establecer conexión TCP/IP
        host = HOST # Dirección IP de la impresora
        port = PORT  # Puerto estándar para impresoras Zebra

        with socket.create_connection((host, port), timeout=2) as sock:

            check_command = b"~HS"
            sock.sendall(check_command)

            r = b""
            r += sock.recv(82)  # Leer datos hasta recibir la terminación esperada
            #print(r)

            string_text = r.decode('utf-8')  # Decodificar bytes a texto
            lines = string_text.splitlines()  # Dividir en líneas
            S1 = lines[0].split(",")
            S2 = lines[1].split(",")
            state = check_error(S1, S2)
            printer_state.mState = state[1]
            printer_state.mText = state[0]
    except socket.timeout:
        print("Timeout error while communicating with the printer")
        printer_state.mState = 5
    except socket.error as e:
        print("Network communication error:", e)
        printer_state.mState = 5
    except Exception as e:
        print("fatal error", e)
        printer_state.mState = 5
def Print_MERIDA(fecha, partNo, qty, supplier, serie, ot):
    try:
        # Establecer conexión TCP/IP
        host = HOST  # Dirección IP de la impresora
        port = PORT  # Puerto estándar para impresoras Zebra

        index = partNo[-1:]

        with socket.create_connection((host, port), timeout=10) as sock:
            label = f"""^XA
            ^XFE:Label_Atlas.ZPL^FS
            ^FN1^FD{fecha}^FS	
            ^FN2^FD>:{partNo}^FS
            ^FN3^FD>:{qty}^FS
            ^FN4^FD>;{supplier}^FS
            ^FN5^FD>;{serie}^FS
            ^FN6^FD>;{ot}^FS
            ^PQ1,,,Y
            ^XZ      
            """
            reqPrint = f"""^XA
            ^MMT
            ^PW815
            ^LL1215
            ^LS0
            ^FO196,8^GB0,1191,8^FS
            ^FO396,0^GB0,1191,8^FS
            ^FO595,0^GB0,1191,8^FS
            ^FO8,276^GB192,0,8^FS
            ^FO200,596^GB200,0,8^FS
            ^FO400,412^GB200,0,8^FS
            ^FO599,356^GB168,0,8^FS
            ^FT93,224^A0B,37,38^FH\^CI28^FDRAD ASSY^FS^CI27
            ^FT139,224^A0B,37,38^FH\^CI28^FDLTR {index}^FS^CI27
            ^FT45,1197^A0B,37,38^FH\^CI28^FDPart No^FS^CI27
            ^FT91,1197^A0B,37,38^FH\^CI28^FD(P)^FS^CI27
            ^FT253,1196^A0B,37,38^FH\^CI28^FDQuantity^FS^CI27
            ^FT299,1196^A0B,37,38^FH\^CI28^FD(Q)^FS^CI27
            ^FT453,1191^A0B,37,38^FH\^CI28^FDSupplier^FS^CI27
            ^FT499,1191^A0B,37,38^FH\^CI28^FD(V)^FS^CI27
            ^FT652,1190^A0B,37,38^FH\^CI28^FDSerial^FS^CI27
            ^FT698,1190^A0B,37,38^FH\^CI28^FD(5S)^FS^CI27
            ^FT253,580^A0B,37,38^FH\^CI28^FDNo. Lote^FS^CI27
            ^FT299,580^A0B,37,38^FH\^CI28^FD(1T)^FS^CI27
            ^FT453,396^A0B,37,38^FH\^CI28^FDOT^FS^CI27
            ^FT499,396^A0B,37,38^FH\^CI28^FD(K)^FS^CI27
            ^FT632,348^A0B,25,25^FH\^CI28^FDProduction Date:^FS^CI27
            ^FT692,346^A0B,37,38^FH\^CI28^FD{fecha}^FS^CI27
            ^FT752,339^A0B,25,25^FH\^CI28^FDExpiry Date:^FS^CI27
            ^FT796,1162^A0B,25,25^FH\^CI28^FDAIR TEMP DE MEXICO SA DE C.V. Km. 20 Carretera Merida-Uman Tablaje Rustico No 4193 C.P. 97390 ^FS^CI27
            ^BY3,3,136^FT160,1002^BCB,,Y,N
            ^FH\^FD>:{partNo}^FS
            ^BY3,3,136^FT368,1002^BCB,,Y,N
            ^FH\^FD>:{qty}^FS
            ^BY3,3,136^FT562,1002^BCB,,Y,N
            ^FH\^FD>;{supplier}^FS
            ^BY3,3,99^FT730,1002^BCB,,Y,N
            ^FH\^FD>;{serie}^FS
            ^BY3,3,136^FT560,300^BCB,,Y,N
            ^FH\^FD>;{ot}^FS
            ^PQ1,,,N
            ^XZ
            """
            sock.sendall(reqPrint.encode('UTF-8'))
            print("Print request sent successfully")

    except socket.timeout:
        print("Timeout error while communicating with the printer")
    except socket.error as e:
        print("Network communication error:", e)
    except Exception as e:
        print("Other error:", e)
def Print_HBPO(date, partNo, qty, internalPartNo, serialNum, copies=2):
    try:
        # Establecer conexión TCP/IP
        host = HOST  # Dirección IP de la impresora
        port = PORT  # Puerto estándar para impresoras Zebra
        supplier = "43700413"

        with socket.create_connection((host, port), timeout=10) as sock:
            reqPrint = f"""^XA
            ~TA000
            ~JSN
            ^LT0
            ^MNW
            ^MTT
            ^PON
            ^PMN
            ^LH0,0
            ^JMA
            ^PR4
            ~SD17
            ^JUS
            ^LRN
            ^CI27
            ^PA0,1,1,0
            ^XZ
            ^XA
            ^MMT
            ^PW831
            ^LL1223
            ^LS0
            ^FO87,7^GB0,1207,2^FS
            ^FO279,7^GB0,1207,2^FS
            ^FO399,7^GB0,1207,2^FS
            ^FO527,631^GB0,583,2^FS
            ^FO664,7^GB0,1207,2^FS
            ^FO8,629^GB272,0,2^FS
            ^FO401,629^GB423,0,2^FS
            ^FO191,7^GB0,623,2^FS
            ^FO192,397^GB88,0,2^FS
            ^FO192,166^GB88,0,2^FS
            ^FO455,7^GB0,615,2^FS
            ^FO591,7^GB0,615,2^FS
            ^FO592,437^GB72,0,2^FS
            ^FT37,1214^A@B,20,20,TT0003M_^FH\^CI28^FD(1) Receiver^FS^CI27
            ^FT47,1091^A0B,25,20^FH\^CI28^FDHBPO MEXICO S.A. DE C.V.^FS^CI27
            ^FT78,1091^A0B,25,20^FH\^CI28^FDKM 117 AUTOPISTA MEX - PUE^FS^CI27
            ^BY2,3,61^FT382,1123^B3B,N,,N,N
            ^FDP{partNo}^FS
            ^FPH,3^FT314,1047^A0B,39,43^FH\^CI28^FD{partNo}^FS^CI27
            ^FT37,623^A@B,20,20,TT0003M_^FH\^CI28^FD(2) Dock - Gate^FS^CI27
            ^FT78,550^A0B,45,33^FH\^CI28^FDMX-1^FS^CI27
            ^FT114,623^A@B,20,20,TT0003M_^FH\^CI28^FD(4) Supplier adress^FS^CI27
            ^FT310,1214^A@B,20,20,TT0003M_^FH\^CI28^FD(8) Part no. (P)^FS^CI27
            ^FPH,1^FT143,623^A0B,25,18^FH\^CI28^FDAIRTEMP DE MÉXICO AUTOPISTA MEX-PUE 296^FS^CI27
            ^FPH,1^FT172,623^A0B,25,18^FH\^CI28^FDPARQUE INDUSTRIAL RESURRECCIÓN C.P. 72228^FS^CI27
            ^FT213,623^A@B,20,20,TT0003M_^FH\^CI28^FD(5) Net weight ^FS^CI27
            ^FT213,392^A@B,20,20,TT0003M_^FH\^CI28^FD(6) Gross weight^FS^CI27
            ^FT213,160^A@B,20,20,TT0003M_^FH\^CI28^FD(7) No. boxes^FS^CI27
            ^FT260,605^A0B,45,33^FH\^CI28^FD51.216^FS^CI27
            ^FT260,352^A0B,45,33^FH\^CI28^FD56.216^FS^CI27
            ^FT260,103^A0B,45,33^FH\^CI28^FD1^FS^CI27
            ^FT427,1214^A@B,20,20,TT0003M_^FH\^CI28^FD(9) Quantity (Q)^FS^CI27
            ^FT478,623^A@B,20,20,TT0003M_^FH\^CI28^FD(11) Supplier part no. (30S)^FS^CI27
            ^FT421,623^A@B,20,20,TT0003M_^FH\^CI28^FD(10) Description^FS^CI27
            ^BY2,3,61^FT516,1123^B3B,N,,N,N
            ^FDQ{qty}^FS
            ^FT438,1047^A0B,39,48^FH\^CI28^FD{qty}^FS^CI27
            ^FT446,466^A0B,45,30^FH\^CI28^FDRADIADOR DE BAJA TEMPERATURA^FS^CI27
            ^BY2,3,61^FT581,555^B3B,N,,N,N
            ^FD30S{internalPartNo}^FS
            ^FPH,1^FT505,373^A0B,39,43^FH\^CI28^FD{internalPartNo}^FS^CI27
            ^FT551,1214^A@B,20,20,TT0003M_^FH\^CI28^FD(12) Supplier (V)^FS^CI27
            ^BY2,3,61^FT646,1123^B3B,N,,N,N
            ^FDV{supplier}^FS
            ^FPH,1^FT576,1047^A0B,31,30^FH\^CI28^FD{supplier}^FS^CI27
            ^FT614,623^A@B,20,20,TT0003M_^FH\^CI28^FD(13) Date^FS^CI27
            ^FT614,433^A@B,20,20,TT0003M_^FH\^CI28^FD(14) Engr. change^FS^CI27
            ^FT655,587^A0B,39,38^FH\^CI28^FDD^FS^CI27
            ^FT655,550^A0B,39,30^FH\^CI28^FD{date}^FS^CI27
            ^FT689,623^A@B,20,20,TT0003M_^FH\^CI28^FD(16) Batch no. (H)^FS^CI27
            ^BY2,3,61^FT768,555^B3B,N,,N,N
            ^FDH^FS
            ^FT801,592^A@B,17,18,TT0003M_^FH\^CI28^FDWarenanhänger VDA 4902, versión 4^FS^CI27
            ^FT689,1214^A@B,20,20,TT0003M_^FH\^CI28^FD(15) Serial no.(S)^FS^CI27
            ^BY2,3,61^FT778,1123^B3B,N,,N,N
            ^FDS{serialNum}^FS
            ^FPH,1^FT708,1047^A0B,31,30^FH\^CI28^FD{serialNum}^FS^CI27
            ^FT810,1214^A@B,17,13,TT0003M_^FH\^CI28^FD(17) AirTemp de México Autopista Mex-Pue 296, Parque industrial Resurrección C.P. 72228^FS^CI27
            ^PQ{copies},,,N
            ^XZ"""
            sock.sendall(reqPrint.encode('UTF-8'))
            print("Print request HBPO sent successfully")

    except socket.timeout:
        print("Timeout error while communicating with the printer")
    except socket.error as e:
        print("Network communication error:", e)
    except Exception as e:
        print("Other error:", e)
def Print_CKD(date, partNo, qty, internalPartNo, serialNum, copies =2):
    try:
        # Establecer conexión TCP/IP
        host = HOST  # Dirección IP de la impresora
        port = PORT  # Puerto estándar para impresoras Zebra
        supplier = "43700413"

        with socket.create_connection((host, port), timeout=10) as sock:
            reqPrint = f"""^XA
            ~TA000
            ~JSN
            ^LT0
            ^MNW
            ^MTT
            ^PON
            ^PMN
            ^LH0,0
            ^JMA
            ^PR4
            ~SD17
            ^JUS
            ^LRN
            ^CI27
            ^PA0,1,1,0
            ^XZ
            ^XA
            ^MMT
            ^PW831
            ^LL1223
            ^LS0
            ^FO191,8^GB0,1207,2^FS
            ^FO367,8^GB0,1207,2^FS
            ^FO515,632^GB0,583,2^FS
            ^FO663,8^GB0,1207,2^FS
            ^FO8,879^GB184,0,2^FS
            ^FO369,631^GB456,0,2^FS
            ^FO443,9^GB0,615,2^FS
            ^FO590,9^GB0,615,2^FS
            ^FO591,439^GB72,0,2^FS
            ^FT37,1215^A@B,20,20,TT0003M_^FH\^CI28^FD(1) Warenempfänger - Kurzadresse^FS^CI27
            ^BY2,3,61^FT333,1124^B3B,N,,N,N
            ^FDP{partNo}^FS
            ^FPH,3^FT265,1048^A0B,39,43^FH\^CI28^FD{partNo}^FS^CI27
            ^FT37,866^A@B,20,20,TT0003M_^FH\^CI28^FD(2) Abiadestelle - Lagerort -^FS^CI27
            ^FT38,522^A@B,20,20,TT0003M_^FH\^CI28^FD(3) Lieferschein-Nr. (N)^FS^CI27
            ^FT219,1215^A@B,20,20,TT0003M_^FH\^CI28^FD(8) Sach -Nr. Kunder (P)^FS^CI27
            ^FT392,1215^A@B,20,20,TT0003M_^FH\^CI28^FD(9) Füllmenge (Q)^FS^CI27
            ^FT467,624^A@B,20,20,TT0003M_^FH\^CI28^FD(11) Sach - Nr. Lieferant (30S)^FS^CI27
            ^FT390,624^A@B,20,20,TT0003M_^FH\^CI28^FD(10) Bezeichnung Lieferung. Leistung^FS^CI27
            ^BY2,3,61^FT503,1124^B3B,N,,N,N
            ^FDQ{qty}^FS
            ^FT433,1048^A0B,39,48^FH\^CI28^FD{qty}^FS^CI27
            ^FT435,548^A0B,45,30^FH\^CI28^FDRADIADOR DE BAJA TEMPERATURA^FS^CI27
            ^BY2,3,61^FT573,556^B3B,N,,N,N
            ^FD30S{internalPartNo}^FS
            ^FPH,1^FT505,374^A0B,39,43^FH\^CI28^FD{internalPartNo}^FS^CI27
            ^FT541,1215^A@B,20,20,TT0003M_^FH\^CI28^FD(12) Lieferanten - Nr. (V)^FS^CI27
            ^BY2,3,61^FT646,1124^B3B,N,,N,N
            ^FDV{supplier}^FS
            ^FPH,1^FT576,1048^A0B,31,30^FH\^CI28^FD{supplier}^FS^CI27
            ^FT613,624^A@B,20,20,TT0003M_^FH\^CI28^FD(13) Datum^FS^CI27
            ^FT613,435^A@B,20,20,TT0003M_^FH\^CI28^FD(14) Änderungsstand Konstruktion^FS^CI27
            ^FT651,589^A0B,39,30^FH\^CI28^FD{date}^FS^CI27
            ^FT689,624^A@B,20,20,TT0003M_^FH\^CI28^FD(16) Chargen - Nr. (H)^FS^CI27
            ^BY2,3,61^FT767,556^B3B,N,,N,N
            ^FDH^FS
            ^FT689,1215^A@B,20,20,TT0003M_^FH\^CI28^FD(15) Serial no.(S)^FS^CI27
            ^BY2,3,61^FT777,1124^B3B,N,,N,N
            ^FDS{serialNum}^FS
            ^FPH,1^FT708,1048^A0B,31,30^FH\^CI28^FD{serialNum}^FS^CI27
            ^FO8,535^GB184,0,2^FS
            ^FT59,830^A@B,20,20,TT0003M_^FH\^CI28^FDVewendungsschlüssel^FS^CI27
            ^FT436,719^A0B,68,68^FH\^CI28^FDST^FS^CI27
            ^PQ{copies},,,N
            ^XZ
               """
            sock.sendall(reqPrint.encode('UTF-8'))
            print("Print request CKD sent successfully")

    except socket.timeout:
        print("Timeout error while communicating with the printer")
    except socket.error as e:
        print("Network communication error:", e)
    except Exception as e:
        print("Other error:", e)

def Print_HBPO_wTemplate(date, partNo, qty, internalPartNo, serialNum):
    try:
        # Establecer conexión TCP/IP
        host = HOST  # Dirección IP de la impresora
        port = PORT  # Puerto estándar para impresoras Zebra
        supplier = "43700413"
        """
        --> FN1  -> P5QM121251R
        --> FN2  -> 5QM121251R
        --> FN3  -> Q16
        --> FN4  -> 16
        --> FN5  -> 30S04003RA12
        --> FN6  -> 04003RA12
        --> FN7  -> V43700413
        --> FN8  -> 43700413
        --> FN9  -> 17/04/25
        --> FN10 -> S170425044300
        --> FN11 -> 170425044300
        """
        with socket.create_connection((host, port), timeout=10) as sock:
            reqPrint = f"""^XA
            ^XFE:CKD.ZPL^FS
            ^FN1^FDP{partNo}^FS	
            ^FN2^FD{partNo}^FS
            ^FN3^FDQ{qty}^FS
            ^FN4^FD{qty}^FS
            ^FN5^FD30S{internalPartNo}^FS
            ^FN6^FD{internalPartNo}^FS
            ^FN7^FDV{supplier}^FS
            ^FN8^FD{supplier}^FS
            ^FN9^FD{date}^FS
            ^FN10^FDS{serialNum}^FS
            ^FN11^FD{serialNum}^FS
            ^PQ1,,,Y
            ^XZ      
            """
            sock.sendall(reqPrint.encode('UTF-8'))
            print("Print request sent successfully")

    except socket.timeout:
        print("Timeout error while communicating with the printer")
    except socket.error as e:
        print("Network communication error:", e)
    except Exception as e:
        print("Other error:", e)
def Print_CKD_wTemplate(date, partNo, qty, internalPartNo, serialNum):
    try:
        # Establecer conexión TCP/IP
        host = HOST  # Dirección IP de la impresora
        port = PORT  # Puerto estándar para impresoras Zebra
        supplier = "43700413"

        """
        --> FN1  -> P5QM121251Q
        --> FN2  -> 5QM121251Q
        --> FN3  -> Q20
        --> FN4  -> 20
        --> FN5  -> 30S04003RA10
        --> FN6  -> 04003RA10
        --> FN7  -> V43700413
        --> FN8  -> 43700413
        --> FN9  -> 17.04.25
        --> FN10 -> S170425044300
        --> FN11 -> 170425044300
        """
        with socket.create_connection((host, port), timeout=10) as sock:
            reqPrint = f"""^XA
            ^XFE:CKD.ZPL^FS
            ^FN1^FDP{partNo}^FS	
            ^FN2^FD{partNo}^FS
            ^FN3^FDQ{qty}^FS
            ^FN4^FD{qty}^FS
            ^FN5^FD30S{internalPartNo}^FS
            ^FN6^FD{internalPartNo}^FS
            ^FN7^FDV{supplier}^FS
            ^FN8^FD{supplier}^FS
            ^FN9^FD{date}^FS
            ^FN10^FDS{serialNum}^FS
            ^FN11^FD{serialNum}^FS
            ^PQ1,,,Y
            ^XZ      
            """
            sock.sendall(reqPrint.encode('UTF-8'))
            print("Print request sent successfully")

    except socket.timeout:
        print("Timeout error while communicating with the printer")
    except socket.error as e:
        print("Network communication error:", e)
    except Exception as e:
        print("Other error:", e)
def SendTemplate_MERIDA():
    try:
        # Establecer conexión TCP/IP
        host = HOST  # Dirección IP de la impresora
        port = PORT  # Puerto estándar para impresoras Zebra

        with socket.create_connection((host, port), timeout=10) as sock:
            template = f"""^XA
            ^DFE:Label_Atlas.ZPL^FS
            ^MMT
            ^PW815
            ^LL1215
            ^LS0
            ^FO196,8^GB0,1191,8^FS
            ^FO396,0^GB0,1191,8^FS
            ^FO595,0^GB0,1191,8^FS
            ^FO8,276^GB192,0,8^FS
            ^FO200,595^GB200,0,8^FS
            ^FO400,412^GB200,0,8^FS
            ^FO599,356^GB168,0,8^FS
            ^FT93,224^A0B,37,38^FH\^CI28^FDRAD ASSY^FS^CI27
            ^FT139,224^A0B,37,38^FH\^CI28^FDATLAS^FS^CI27
            ^FT45,1197^A0B,37,38^FH\^CI28^FDPart No^FS^CI27
            ^FT91,1197^A0B,37,38^FH\^CI28^FD(P)^FS^CI27
            ^FT253,1196^A0B,37,38^FH\^CI28^FDQuantity^FS^CI27
            ^FT299,1196^A0B,37,38^FH\^CI28^FD(Q)^FS^CI27
            ^FT453,1191^A0B,37,38^FH\^CI28^FDSupplier^FS^CI27
            ^FT499,1191^A0B,37,38^FH\^CI28^FD(V)^FS^CI27
            ^FT652,1190^A0B,37,38^FH\^CI28^FDSerial^FS^CI27
            ^FT698,1190^A0B,37,38^FH\^CI28^FD(4S)^FS^CI27
            ^FT253,580^A0B,37,38^FH\^CI28^FDNo. Lote^FS^CI27
            ^FT299,580^A0B,37,38^FH\^CI28^FD(1T)^FS^CI27
            ^FT453,396^A0B,37,38^FH\^CI28^FDOT^FS^CI27
            ^FT499,396^A0B,37,38^FH\^CI28^FD(K)^FS^CI27
            ^FT632,348^A0B,25,25^FH\^CI28^FDProduction Date:^FS^CI27
            ^FT692,346^A0B,37,38^FH\^CI28^FN1^FS^CI27    
            ^FT752,339^A0B,25,25^FH\^CI28^FDExpiry Date:^FS^CI27
            ^FT796,1162^A0B,25,25^FH\^CI28^FDAIR TEMP DE MEXICO SA DE C.V. Km. 20 Carretera Merida-Uman Tablaje Rustico No 4193 C.P. 97390 ^FS^CI27
            ^BY3,3,136^FT160,1001^BCB,,Y,N
            ^FH\^FN2^FS                                  
            ^BY3,3,136^FT363,1001^BCB,,Y,N
            ^FH\^FN3^FS                                   
            ^BY3,3,136^FT562,1001^BCB,,Y,N
            ^FH\^FN4^FS                                  
            ^BY3,3,99^FT730,1001^BCB,,Y,N
            ^FH\^FN5^FS                                   
            ^BY3,3,136^FT560,300^BCB,,Y,N
            ^FH\^FN6^FS                                   
            ^XZ"""
            sock.sendall(template.encode('UTF-8'))
            print("Set Template sent succesfully")
    except socket.timeout:
        print("Timeout error while communicating with the printer")
    except socket.error as e:
        print("Network communication error:", e)
    except Exception as e:
        print("Other error:", e)
def sendTemplate_HBPO():
    try:
        # Establecer conexión TCP/IP
        host = HOST  # Dirección IP de la impresora
        port = PORT  # Puerto estándar para impresoras Zebra

        with socket.create_connection((host, port), timeout=10) as sock:
            template = f"""^XA
            ^DFE:HBPO.ZPL^FS
            ^MMT
            ^PW1223
            ^LL831
            ^LS0
            ^FO8,87^GB1207,0,2^FS
            ^FO8,279^GB1207,0,2^FS
            ^FO8,399^GB1207,0,2^FS
            ^FO8,526^GB583,0,2^FS
            ^FO8,663^GB1207,0,2^FS
            ^FO590,8^GB0,272,2^FS
            ^FO590,400^GB0,423,2^FS
            ^FO591,191^GB623,0,2^FS
            ^FO822,192^GB0,88,2^FS
            ^FO1054,192^GB0,88,2^FS
            ^FO599,455^GB615,0,2^FS
            ^FO599,590^GB615,0,2^FS
            ^FO782,591^GB0,72,2^FS
            ^FT8,37^AN,20,20,TT0003M_^FH^CI28^FD(1) Receiver^FS^CI27
            ^FT131,47^A0N,25,20^FH^CI28^FDHBPO MEXICO S.A. DE C.V.^FS^CI27
            ^FT131,78^A0N,25,20^FH^CI28^FDKM 117 AUTOPISTA MEX - PUE^FS^CI27
            ^BY2,3,61^FT99,381^B3N,N,,N,N
            ^FD^FN1^FS                                                                                  
            ^FPH,3^FT175,314^A0N,39,43^FH^CI28^FD^FN2^FS^CI27                                           
            ^FT599,37^AN,20,20,TT0003M_^FH^CI28^FD(2) Dock - Gate^FS^CI27
            ^FT671,78^A0N,45,33^FH^CI28^FDMX-1^FS^CI27
            ^FT599,114^AN,20,20,TT0003M_^FH^CI28^FD(4) Supplier adress^FS^CI27
            ^FT8,309^AN,20,20,TT0003M_^FH^CI28^FD(8) Part no. (P)^FS^CI27
            ^FPH,1^FT598,143^A0N,25,18^FH^CI28^FDAIRTEMP DE MÉXICO AUTOPISTA MEX-PUE 296^FS^CI27
            ^FPH,1^FT598,171^A0N,25,18^FH^CI28^FDPARQUE INDUSTRIAL RESURRECCIÓN C.P. 72228^FS^CI27
            ^FT599,212^AN,20,20,TT0003M_^FH^CI28^FD(5) Net weight ^FS^CI27
            ^FT830,212^AN,20,20,TT0003M_^FH^CI28^FD(6) Gross weight^FS^CI27
            ^FT1062,212^AN,20,20,TT0003M_^FH^CI28^FD(7) No. boxes^FS^CI27
            ^FT617,260^A0N,45,33^FH^CI28^FD51.216^FS^CI27
            ^FT870,260^A0N,45,33^FH^CI28^FD56.216^FS^CI27
            ^FT1119,260^A0N,45,33^FH^CI28^FD1^FS^CI27
            ^FT8,427^AN,20,20,TT0003M_^FH^CI28^FD(9) Quantity (Q)^FS^CI27
            ^FT599,477^AN,20,20,TT0003M_^FH^CI28^FD(11) Supplier part no. (30S)^FS^CI27
            ^FT599,421^AN,20,20,TT0003M_^FH^CI28^FD(10) Description^FS^CI27
            ^BY2,3,61^FT99,516^B3N,N,,N,N
            ^FD^FN3^FS                                                                                  
            ^FT175,438^A0N,39,48^FH^CI28^FD^FN4^FS^CI27                                                  
            ^FT755,445^A0N,45,30^FH^CI28^FDRADIADOR DE BAJA TEMPERATURA^FS^CI27
            ^BY2,3,61^FT667,581^B3N,N,,N,N
            ^FD^FN5^FS                                                                                   
            ^FPH,1^FT849,505^A0N,39,43^FH^CI28^FD^FN6^FS^CI27                                            
            ^FT8,551^AN,20,20,TT0003M_^FH^CI28^FD(12) Supplier (V)^FS^CI27
            ^BY2,3,61^FT99,646^B3N,N,,N,N
            ^FD^FN7^FS                                                                                   
            ^FPH,1^FT175,576^A0N,31,30^FH^CI28^FD43700413^FS^CI27
            ^FT599,613^AN,20,20,TT0003M_^FH^CI28^FD(13) Date^FS^CI27
            ^FT788,613^AN,20,20,TT0003M_^FH^CI28^FD(14) Engr. change^FS^CI27
            ^FT634,655^A0N,39,38^FH^CI28^FDD^FS^CI27
            ^FT671,655^A0N,39,30^FH^CI28^FD^FN8^FS^CI27                                                  
            ^FT599,689^AN,20,20,TT0003M_^FH^CI28^FD(16) Batch no. (H)^FS^CI27
            ^BY2,3,61^FT667,767^B3N,N,,N,N
            ^FDH^FS
            ^FT630,801^AN,17,18,TT0003M_^FH^CI28^FDWarenanhänger VDA 4902, versión 4^FS^CI27
            ^FT8,689^AN,20,20,TT0003M_^FH^CI28^FD(15) Serial no.(S)^FS^CI27
            ^BY2,3,61^FT99,777^B3N,N,,N,N
            ^FD^FN9^FS                                                                                   
            ^FPH,1^FT175,708^A0N,31,30^FH^CI28^FD^FN10^FS^CI27                                           
            ^FT8,809^AN,17,13,TT0003M_^FH^CI28^FD(17) AirTemp de México Autopista Mex-Pue 296, Parque industrial Resurrección C.P. 72228^FS^CI27
            ^XZ"""
            sock.sendall(template.encode('UTF-8'))
            print("Set Template sent succesfully")
    except socket.timeout:
        print("Timeout error while communicating with the printer")
    except socket.error as e:
        print("Network communication error:", e)
    except Exception as e:
        print("Other error:", e)
def sendTemplate_CKD():
    try:
        # Establecer conexión TCP/IP
        host = HOST  # Dirección IP de la impresora
        port = PORT  # Puerto estándar para impresoras Zebra

        with socket.create_connection((host, port), timeout=10) as sock:
            template = f"""^XA
            ^DFE:CKD.ZPL^FS
            ^MMT
            ^PW1223
            ^LL831
            ^LS0
            ^FO8,191^GB1207,0,2^FS
            ^FO8,367^GB1207,0,2^FS
            ^FO8,515^GB583,0,2^FS
            ^FO8,663^GB1207,0,2^FS
            ^FO342,8^GB0,184,2^FS
            ^FO590,369^GB0,456,2^FS
            ^FO599,443^GB615,0,2^FS
            ^FO599,590^GB615,0,2^FS
            ^FO782,591^GB0,72,2^FS
            ^FT8,37^AN,20,20,TT0003M_^FH^CI28^FD(1) Warenempfänger - Kurzadresse^FS^CI27
            ^BY2,3,61^FT99,333^B3N,N,,N,N
            ^FD^FN1^FS                                                                              
            ^FPH,3^FT175,265^A0N,39,43^FH^CI28^FN2^FS^CI27                                          
            ^FT357,37^A@N,20,20,TT0003M_^FH^CI28^FD(2) Abiadestelle - Lagerort -^FS^CI27
            ^FT701,38^AN,20,20,TT0003M_^FH^CI28^FD(3) Lieferschein-Nr. (N)^FS^CI27
            ^FT8,219^AN,20,20,TT0003M_^FH^CI28^FD(8) Sach -Nr. Kunder (P)^FS^CI27
            ^FT8,392^AN,20,20,TT0003M_^FH^CI28^FD(9) Füllmenge (Q)^FS^CI27
            ^FT599,467^AN,20,20,TT0003M_^FH^CI28^FD(11) Sach - Nr. Lieferant (30S)^FS^CI27
            ^FT599,390^AN,20,20,TT0003M_^FH^CI28^FD(10) Bezeichnung Lieferung. Leistung^FS^CI27
            ^BY2,3,61^FT99,503^B3N,N,,N,N
            ^FD^FN3^FS                                                                              
            ^FT175,433^A0N,39,48^FH^CI28^FN4^FS^CI27                                                
            ^FT675,435^A0N,45,30^FH^CI28^FDRADIADOR DE BAJA TEMPERATURA^FS^CI27                     
            ^BY2,3,61^FT667,573^B3N,N,,N,N
            ^FD^FN5^FS                                                                              
            ^FPH,1^FT849,505^A0N,39,43^FH^CI28^FD^FN6^FS^CI27                                       
            ^FT8,541^AN,20,20,TT0003M_^FH^CI28^FD(12) Lieferanten - Nr. (V)^FS^CI27
            ^BY2,3,61^FT99,646^B3N,N,,N,N
            ^FD^FN7^FS                                                                                     
            ^FPH,1^FT175,576^A0N,31,30^FH^CI28^FD^FN8^FS^CI27                                       
            ^FT599,613^AN,20,20,TT0003M_^FH^CI28^FD(13) Datum^FS^CI27
            ^FT788,613^AN,20,20,TT0003M_^FH^CI28^FD(14) Änderungsstand Konstruktion^FS^CI27
            ^FT634,651^A0N,39,30^FH^CI28^FD^FN9^FS^CI27
            ^FT599,689^AN,20,20,TT0003M_^FH^CI28^FD(16) Chargen - Nr. (H)^FS^CI27
            ^BY2,3,61^FT667,767^B3N,N,,N,N
            ^FDH^FS
            ^FT8,689^AN,20,20,TT0003M_^FH^CI28^FD(15) Serial no.(S)^FS^CI27
            ^BY2,3,61^FT99,777^B3N,N,,N,N
            ^FD^FN10^FS                                                                              
            ^FPH,1^FT175,708^A0N,31,30^FH^CI28^FD^FN11^FS^CI27                                      
            ^FO686,8^GB0,184,2^FS
            ^FT393,59^AN,20,20,TT0003M_^FH^CI28^FDVewendungsschlüssel^FS^CI27
            ^FT504,436^A0N,68,68^FH^CI28^FDST^FS^CI27
            ^XZ"""
            sock.sendall(template.encode('UTF-8'))
            print("Set Template sent succesfully")
    except socket.timeout:
        print("Timeout error while communicating with the printer")
    except socket.error as e:
        print("Network communication error:", e)
    except Exception as e:
        print("Other error:", e)

def SendLabelCalibrate():
    try:
        # Establecer conexión TCP/IP
        host = HOST  # Dirección IP de la impresora
        port = PORT  # Puerto estándar para impresoras Zebra

        with socket.create_connection((host, port), timeout=2) as sock:
            Calibrate = b"~JC"
            sock.sendall(Calibrate)
            print("Calibrate sent succesfully")

    except serial.SerialTimeoutException:
        print("Timeout error while communicating with the serial port")
    except serial.SerialException as e:
        print("Serial communication error:", e)
    except Exception as e:
        print("Other error:", e)

