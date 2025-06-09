import random

from PySide6.QtCore import QCoreApplication
import serial
import serial.tools.list_ports
import datetime
def get_rs232_ports():
    """
    Obtiene la lista de puertos COM disponibles y filtra solo los dispositivos RS232 y conversores USB-Serial.
    :return: Lista de puertos COM RS232 disponibles.
    """
    rs232_ports = []
    ports = serial.tools.list_ports.comports()

    for port in ports:
        # Se agregan dispositivos USB-Serial como CH340, CP210x, FTDI, etc.
        if any(x in port.description.upper() for x in ["RS-232", "SERIAL", "UART", "USB"]):
            rs232_ports.append(port.device)

    return rs232_ports if rs232_ports else None


try:
    current_COM = get_rs232_ports()
    COM = current_COM[0]
except Exception as e:
    print(e)

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
        with serial.Serial(COM, baudrate=9600, bytesize=8, timeout=10, stopbits=serial.STOPBITS_ONE, xonxoff=False,  rtscts=False,  dsrdtr=False) as ser:
            # ser = serial.Serial(COM, baudrate=9600, bytesize=8, timeout=10,stopbits=serial.STOPBITS_ONE)  # Open port
            check_command = b"~HS"
            ser.write(check_command)
            r = ser.read_until('', 82)
            string_text = r.decode('utf-8')  # Decodificar bytes a texto
            lines = string_text.splitlines()  # Dividir en líneas
            S1 = lines[0].split(",")
            S2 = lines[1].split(",")
            state = check_error(S1, S2)
            printer_state.mState = state[1]
            printer_state.mText = state[0]
            ser.close()
    except serial.SerialTimeoutException:
        print("Timeout error while communicating with the serial port")
        printer_state.mState = 5
    except serial.SerialException as e:
        print("Serial communication error:", e)
        printer_state.mState = 5
    except Exception as e:
        print("fatal error", e)
        printer_state.mState = 5
def Print_MERIDA(fecha, partNo, qty, supplier, serie, ot):
    try:
        index = partNo[-1:]
        with serial.Serial(COM, baudrate=9600, bytesize=8, timeout=10, stopbits=serial.STOPBITS_ONE, xonxoff=False,  rtscts=False,  dsrdtr=False) as ser:
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
            ser.write(bytes(reqPrint.encode('UTF-8')))
            ser.close()
            print("Print request sent successfully")

    except serial.SerialTimeoutException:
        print("Timeout error while communicating with the serial port")
    except serial.SerialException as e:
        print("Serial communication error:", e)
    except Exception as e:
        print("Other error:", e)

def SendLabelCalibrate():
    try:
        with serial.Serial(COM, baudrate=9600, bytesize=8, timeout=10, stopbits=serial.STOPBITS_ONE, xonxoff=False,  rtscts=False,  dsrdtr=False) as ser:
            Calibrate = f"~JC"
            ser.write(bytes(Calibrate.encode('UTF-8')))
            ser.close()
            print("Calibrate sent succesfully")

    except serial.SerialTimeoutException:
        print("Timeout error while communicating with the serial port")
    except serial.SerialException as e:
        print("Serial communication error:", e)
    except Exception as e:
        print("Other error:", e)


