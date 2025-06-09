import time
from datetime import datetime
import serial
from SQL import managerDataBase
COM = "COM12"

database = managerDataBase()

"""
Para asegurarte de que el template se guarda correctamente en la memoria permanente de la impresora, sigue estos pasos:
Guardar el Template en la Memoria Permanente: Usa ^DF con la ubicación adecuada para guardar el template en la memoria flash permanente.Verificar que el Template se Guarda Correctamente: 
Asegúrate de que el template se ha guardado correctamente y persiste después de reiniciar la impresora.
En el comando ^DFE:Label_Atlas.ZPL^FS, E: indica que el template se guarda en la memoria flash de la impresora, que es permanente.
"""
def SendTemplate():
    try:
        ser = serial.Serial(COM, baudrate=9600, bytesize=8, timeout=10,
                            stopbits=serial.STOPBITS_ONE)  # Open port
        #^DFR:SAMPLE.GRF^FS
        template = f"""
        ^XA
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
        ^PQ1,,,Y                                
        ^XZ
        """
        ser.write(bytes(template.encode('UTF-8')))
        ser.close()
    except Exception as e:
        print("fatal error", e)

def SendReqPrint(fecha,partNo,Qty,supplier,serie,OT):
    try:
        ser = serial.Serial(COM, baudrate=9600, bytesize=8, timeout=10,
                            stopbits=serial.STOPBITS_ONE)  # Open port

        #^XFR:SAMPLE.GRF
        reqPrint = f"""
        ^XA
        ^XFE:Label_Atlas.ZPL^FS
        ^FN1^FD{fecha}^FS	
        ^FN2^FD>:{partNo}^FS
        ^FN3^FD>:{Qty}^FS
        ^FN4^FD>;{supplier}^FS
        ^FN5^FD>;{serie}^FS
        ^FN6^FD>;{OT}^FS
        ^XZ
        """
        ser.write(bytes(reqPrint.encode('UTF-8')))
        ser.close()
    except Exception as e:
        print("fatal error", e)
#SendTemplate()

data = database.GetDataBackUp()
print(data)
PartNo = data[1]
Supplier = data[2]
OT = data[3]
PzsTotales = int(data[4])
PzsRealizadas = int(data[5])
SerialNum = data[6]
CreationDate = data[7]

currDate = datetime.now()
currDate = currDate.strftime("%d/%m/%Y %H:%M:%S")
SendReqPrint(currDate, PartNo, PzsTotales, Supplier, SerialNum, OT)
