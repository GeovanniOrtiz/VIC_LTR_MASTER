import time

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMessageBox

import serial
import serial.tools.list_ports
import datetime

COM = "COM17"

global currSerial

def _CreatCAC_Label(partNo,SerialNum,levelChange, chamber):
    try:
        with serial.Serial(COM, baudrate=9600, bytesize=8, timeout=10, stopbits=serial.STOPBITS_ONE, xonxoff=False, rtscts=False, dsrdtr=False) as ser:
            date = datetime.datetime.now()
            _date = date.strftime("%d/%m/%y")
            date = date.strftime("%d%m%y%H%M%S")
            _serialNumber = str(SerialNum).zfill(5)

            DMC = f"ZAR{date}{chamber}{partNo}_{_serialNumber}"  # ZAR250821141740104E145785L_00009
            label = f"""^XA^MMT^PW407^LL0203^LS0^XA
            ^FO5,12^GFA,612,612,9,M01F8,L07IFE,K03KFC,J01MF,J07M
            FE,I01OF8,I03IFE07IFC,I0IFCI03IF,001IFK0IF8,003FF8K01FFC,007FFM07FE,00FFC00IF003FF
            ,01FFI0IFI0FF8,01FEI0IFI07F8,03FC0207FE0603FC,07F80E07FE0701FE,07F01F07FE0F80FE,0F
            F01F03FC0F80FF,0FE03F03FC0FC07F,1FE0FF83FC1FF03F,1FC1FF81F81FF83F8,1F81FFC1F81FF81
            F8,3F80FFC0F03FF81FC,3F80FFC0F03FF00FC,3F007FE0707FF00FC,7F003FE0607FC00FE,7E003FF
            060FFC007E,7E001FFI0FF8007E,7E101FF801FF8087E,7E180FF801FF8187E,FE180FFC03FF0183E,
            FC1C07FC03FF0383F,FC1C07FC03FE0383F,FC1E07KFE0783F,FC1E03KFC0783F,FC1F03FE07FC0F83
            F,FC1F01FC03F80F83F,FE1F81FC03F81F83E,7E1FC0F801F83F87E,7E1FC0F801F03F87E,7E1FE0F8
            00F07F87E,7E0FE07060E07F07E,7F0FF0606060FF0FE,3F07F0206040FE0FC,3F07F800F001FE0FC,
            3F83F800F001FC1FC,1F83F801F801FC1F8,1FC1FC01F803F83F8,1FC0FC03FC03F03F8,0FE03E03FC
            07C07F,0FF01E03FC0780FF,07F01E03FE0780FE,07F80F07FE0F01FE,03FC0707FE0E01FC,03FE018
            IF1803F8,01FFI0IFI0FF8,00FFC00IF003FF,007FEI0FI07FE,003FF8K01FFC,001FFEK07FF8,I0IF
            8I01IF,I07IF801IFE,I01OF8,J0NFE,J01MF8,K07KFE,L0KF,M07FE,^FS^FO320,15^GFA,576,576,
            8,7TF,UF,7TF,UF,:::PFEI0F,PFCI0F,PF8001F,:PFI01F,:OFEI03F,OFE0203F,OFC0203F,OFC060
            3F,OF80403F,OF80C07F,OF01C07F,FBLFE01C07F,F9LFE03C07F,FC3KFE0380FF,FF03KF8780FF,FF
            8K07CF80FF,FFEK01FF80FF,IFCK07F00FF,FBFFE0FFC3F01FF,FCMF1F01FF,FE3LFDF01FF,FF03MF0
            1FF,FF8K0FFE01FF,IFK03FE03FF,IFCK0FE03FF,JFE07FC7E03FF,OF3C03FF,OFDC03FF,LFE07FC07
            FF,:LFC07F807FF,LF807F807FF,LF80FF80IF,LF00FF80IF,LF01FF00IF,KFE03FF00IF,KFE03FF01
            IF,KFC07FF01IF,:UF,::::,:UF,:JF87OF,JF0PF,JF0DOF,IFE4DF9MF,FF66CDA9C6930FF,FF87991
            1860307F,FFC7993304DB67F,IFB9B733C9B67F,IFB93738C920FF,IF33F79CDB65FF,IF7BLFE7FF,U
            F,:::^FS
            ^FT95,71^A0N,23,24^FH\^FDZAR
            ^FS^FT95,158^A0N,23,24^FH\^FDA:^FS^FT95,187^A0N,18
            ,19^FH\^FDMADE IN MEXICO^FS^FT95,128^A0N,23,24^FH\^FDDATE: {_date}
            ^FS^FT95,99^A0N,23,24^FH\^FDSN: {_serialNumber}
            ^FS^FT95,41^A0N,34,33^FH\^FD04E.145.785.L
            ^FS^FT226,71^A0N,23,24^FH\^FD{levelChange}
            ^FS^FT300,190^BXN,4,200^FH\^FD{DMC}^FS
            ^FT120,158^A0N,23,24^FH\^FD0.37^FS
            ^FT170,158^A0N,23,24^FH\^FDC:^FS
            ^FT194,158^A0N,23,24^FH\^FD0.25^FS
            ^FT33,108^A0N,23,24^FH\^FD{chamber}^FS
            ^FO5,120^GFA,594,594,9,N02,N06,N07,N0F,N0F8,M01F8,M01FC,M03FC,:M07FE,:M0IF,M0IF
            8,L01IF8,L01IFC,L03IFC,L07IFE,:L0KF,:K01KF8,:K03KFC,:K07KF2,K07JF02,K0JF801,K0IF80
            01,J01FF8J08,J01FL08,J03EL04,:J07CL02,J078L02,J0F8L01,I01B80EJ018,I010C1FK08,I0203
            7F8I01C,I0300FF6I03C,I07C03CFI0FE,I07F00FFI0FE,I078C03F001FE,I0F8700E003FF,I0F8780
            6003FF,001F8570180IF8,003F8538071IFC,003F852F01JFC,007FC52FC03IFE,007FC51E301IFE,0
            0FFC49C1807IF,00FFC4980601IF,01FFC2580F807FF8,01FFE2781FE01FF8,03IF1763FF807FC,03I
            FDF47FFE01FC,07KF0JF807E,07KF8JFE01E,0RF807,0RFE01,1SF808,1SFE08,3TF84,3TFE4,7UFA,
            7UFE,WF,^FS
            ^PQ1,,,N
            ^XZ"""
            ser.write(bytes(label.encode('UTF-8')))
            ser.close()
            #print("Print request sent successfully")

    except serial.SerialTimeoutException:
        print("Timeout error while communicating with the serial port")
    except serial.SerialException as e:
        print("Serial communication error:", e)
    except Exception as e:
        print("Other error:", e)
@Slot(int)
def cycle_Print(partNo,SerialNum,levelChange, chamber):
    _CreatCAC_Label(partNo,SerialNum,levelChange,chamber)

def run_routine():
    pzs = 96
    n = pzs  # Número de veces que se ejecutará la rutina de impresion de Etiqueta
    partNo ="04E145785L"
    levelChange = "09S"
    chamber = "2"
    currSerial = 567
    for _ in range(n):
        cycle_Print(partNo, currSerial, levelChange, chamber)
        print(currSerial)
        currSerial = currSerial + 1
        time.sleep(3)
    print("Proceso Completado con Exito!")

run_routine()

#Cabina 1
#461-556

#cabina 2
#557-662