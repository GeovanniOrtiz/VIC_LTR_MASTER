import os
import sys
import time

from PySide6.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, Slot, QCoreApplication, QDate, QTimeZone, \
    QRegularExpression
from PySide6.QtGui import QPixmap, QFont, QPalette, QColor, QIntValidator, QRegularExpressionValidator
from PySide6.QtWidgets import QMainWindow, QApplication, QTableWidget, QVBoxLayout, QHeaderView, QDialog, QMessageBox, \
    QTextEdit, QLineEdit, QLabel
import socket
from Interfaz.Interfaz_gui import Ui_MainWindow as Interfaz
from Alerts import *
from Printer_Rs232 import *
from SQL import managerDataBase
from LAN.LAN_Connection import WifiMonitor
from Interfaz.Dialogo_ConfirmData_gui import Ui_Dialog as ConfirmData
from Interfaz.Loggin_gui import Ui_Dialog as Loggin
from Printer_Rs232 import ConsultStatePrint, PrinterState
from Server.ServerMonitor import *
from API_Functions.request_API import *
from datetime import *
import json

dataBase = managerDataBase(2)

class DialogoError(QDialog):
    def __init__(self, mensaje, parent=None):
        super().__init__(parent)
        self.mensaje = mensaje
        self.setWindowTitle("Aviso")
        self.setFixedSize(400, 200)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)  # Opcional: sin bordes de ventana
        self.setup_ui()

    def setup_ui(self):
        # Estilo con fondo rojo semitransparente y borde rojo
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(255, 0, 0, 100);  /* Rojo con transparencia */
                border: 4px solid red;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 34px;
                font-weight: bold;
            }
        """)

        etiqueta = QLabel(self.mensaje, self)
        etiqueta.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(etiqueta)
        self.setLayout(layout)
class ConfirmData(QDialog, ConfirmData):
    def __init__(self, parent=None):
        super(ConfirmData, self).__init__(parent)
        self.setupUi(self)
        self.state=False

        # Elimina la barra de menú y el botón de cierre
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.btn_Accept.released.connect(lambda:self.GetState(True))
        self.btn_Reject.released.connect(lambda:self.GetState(False))
    def SetData(self, partNo, Qty, Supplier, Serial, Ot, Client):
        self.lbl_PartNo.setText(QCoreApplication.translate("Dialog",
                                                           f"<html><head/><body><p><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">{partNo}</span></p></body></html>",
                                                           None))
        self.lbl_Cantidad.setText(QCoreApplication.translate("Dialog", f"<html><head/><body><p><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">{Qty}</span></p></body></html>", None))
        self.lbl_Proveedor.setText(QCoreApplication.translate("Dialog", f"<html><head/><body><p><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">{Supplier}</span></p></body></html>", None))
        self.lbl_Serial.setText(QCoreApplication.translate("Dialog", f"<html><head/><body><p><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">{Serial}</span></p></body></html>", None))
        self.lbl_OT.setText(QCoreApplication.translate("Dialog", f"<html><head/><body><p><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">{Ot}</span></p></body></html>", None))
        self.lbl_client.setText(QCoreApplication.translate("Dialog",
                                                           f"<html><head/><body><p><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">{Client}</span></p></body></html>",
                                                           None))

    def GetState(self, respuesta):
        result = respuesta
        if result == True:
            self.accept()
            self.state=True
        else:
            self.reject()
            self.state=False
class Loggin(QDialog, Loggin):
    def __init__(self, parent=None):
        super(Loggin, self).__init__(parent)
        self.setupUi(self)
        self.line_contra.setEchoMode(QLineEdit.Password)

        self.state=0

        # Elimina la barra de menú y el botón de cierre
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.box_Admin.addItems(["Usuario", "Administrador"])
        self.btn_iniciarSesion.released.connect(self.tryInit)
        self.btn_cancelar.released.connect(self.Cancel)

    def tryInit(self):
        if self.box_Admin.currentText() == 'Usuario' and len(self.txt_User.toPlainText())>0 and len(self.line_contra.text())>0:
            print("Get data")
            username = self.txt_User.toPlainText()
            password = self.line_contra.text()

            # Aquí puedes realizar la validación del usuario y contraseña
            if username == "LTR" and password == "0300":
                # Ejemplo simple de validación: solo imprimir los valores ingresados
                print(f"Usuario: {username}, Contraseña: {password}")
                # Cerrar el cuadro de diálogo después de iniciar sesión
                self.state=1
                self.accept()
                QMessageBox.information(None, "Bienvenido", "Usuario registrado con exito")

            else:
                QMessageBox.information(None, "Verificar Informacion", "Usuario o Contraseña Incorrectos")

        elif self.box_Admin.currentText() == 'Administrador' and len(self.txt_User.toPlainText())>0 and len(self.line_contra.text())>0:
            print("Get data")
            username = self.txt_User.toPlainText()
            password = self.line_contra.text()

            # Aquí puedes realizar la validación del usuario y contraseña
            if username == "LTR" and password == "0900":
                # Ejemplo simple de validación: solo imprimir los valores ingresados
                print(f"Usuario: {username}, Contraseña: {password}")
                # Cerrar el cuadro de diálogo después de iniciar sesión
                self.state=2
                self.accept()
                QMessageBox.information(None, "Bienvenido", "Administrador registrado con exito")

            else:
                QMessageBox.information(None, "Verificar Informacion", "Usuario o Contraseña Incorrectos")

        else:
            QMessageBox.information(None, "Verificar Informacion", "Usuario o Contraseña Incorrectos")

    def Cancel(self):
        self.state=0
        self.reject()

class LTR(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui_main = Interfaz()
        self.ui_main.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.showFullScreen()

        self.InitAnimations()
        self.initGui()
        self.InitSlots()

        # lee si se configurara algun parametro
        self.GetPrintMode()

    @Slot()
    def InitAnimations(self):
        # Configuración de la animación menu principal
        self.ui_main.animation = QPropertyAnimation(self.ui_main.leftMenuBg, b'minimumWidth')
        self.ui_main.animation.setDuration(500)
        self.ui_main.animation.setEasingCurve(QEasingCurve.OutQuint)  # Cambia la curva de aceleración aquí

        # Configuración de la animación menu secundario
        self.ui_main.animation_secundario = QPropertyAnimation(self.ui_main.extraLeftBox, b'minimumWidth')
        self.ui_main.animation_secundario.setDuration(500)
        self.ui_main.animation_secundario.setEasingCurve(QEasingCurve.OutQuint)  # Cambia la curva de aceleración aquí

        self.ui_main.animation_config = QPropertyAnimation(self.ui_main.extraRightBox, b'minimumWidth')
        self.ui_main.animation_config.setDuration(500)
        self.ui_main.animation_config.setEasingCurve(QEasingCurve.OutQuint)  # Cambia la curva de aceleración aquí

        self.ui_main.animation_Sesion = QPropertyAnimation(self.ui_main.Login_page, b'geometry')
        self.ui_main.animation_Sesion.setDuration(500)
        self.ui_main.animation_Sesion.setEasingCurve(QEasingCurve.OutQuint)  # Cambia la curva de aceleración aquí
    @Slot()
    def InitSlots(self):
        #self.ui_main.toggleButton.released.connect(self.MainMenu_Control)
        #self.ui_main.settingsTopBtn.released.connect(self.ConfigMenu_Control)
        #self.ui_main.btn_logout.released.connect(self.CloseMenuControl)

        self.ui_main.closeAppBtn.released.connect(QApplication.instance().quit)
        self.ui_main.minimizeAppBtn.released.connect(self.showMinimized)
        self.ui_main.btn_Report.released.connect(self.HistorialPressed)
        self.ui_main.btn_home.released.connect(self.HomePressed)
        self.ui_main.btn_DataMatrix.released.connect(self.DataMatrixPressed)
        self.ui_main.btn_Master.released.connect(self.HistorialMasterPressed)
        self.ui_main.btn_printer.released.connect(self.PrintPressed)
        self.ui_main.btn_PrintLabel.released.connect(self.GetData)
        self.ui_main.btn_configData.released.connect(self.ShowLoggin)
        self.ui_main.btn_initSave.released.connect(lambda:self.SetCurrentData())
        self.ui_main.btn_initCancel.released.connect(self.CancelChange)
        self.ui_main.btn_PrintAction.released.connect(self.PrintPressed)
        self.ui_main.btn_deleteRegister.released.connect(self.delete_CurrData)

        # Slot para enviar a la pagina de Historial
        self.ui_main.btn_printer.released.connect(lambda : self.ui_main.MenuPrincipal.setCurrentIndex(8))

        # Slot para la seleccion de fecha
        self.ui_main.calendarWidget.selectionChanged.connect(self.on_date_selected)
        self.ui_main.calendarWidget.clicked.connect(self.on_date_selected)

        # Conectar señal al método
        self.ui_main.initBox_Cliente.currentIndexChanged.connect(self.on_item_selected)

        # Conecta la senal con el text edit
        self.ui_main.txt_input.textChanged.connect(self.on_text_changed)

        # slot de index de tabla
        self.tableMastertaBase.cellClicked.connect(self.print_selected_row)

        # Slot para detectar el cambio en el buscador
        self.ui_main.Box_Search_Mode.currentIndexChanged.connect(self.ChangeSearch)

        # Slot para buscar el numero de Serie de la master en la base de datos
        self.ui_main.Btn_Search_Serie.released.connect(self.Search_DataMaster)

        #Funcion lambda Estructurada
        self.ui_main.btn_EditAction.released.connect(lambda: (
            self.ui_main.MenuPrincipal.setCurrentIndex(3)
            if self.ui_main.lcdNumber_Realizado.value() == 0
            else (self.ui_main.MenuPrincipal.setCurrentIndex(6),
                  QMessageBox.information(None, "Operación Imposible",
                                          "Terminar el Contenedor actual para crear uno nuevo."))
        ))
    @Slot()
    def initGui(self):
        # Esconde el label de Alertas de proceso
        HideAlerts(self.ui_main)

        # Crea la instancia de PrinterState
        self.printer_state = PrinterState()

        # Timer para consultar el estado de la impresora
        self.StatePrinter = QTimer()
        self.StatePrinter.timeout.connect(lambda:ConsultStatePrint(self.ui_main, self.printer_state))
        self.StatePrinter.start(2000)

        # Verifica la impresora
        ConsultStatePrint(self.ui_main, self.printer_state)

        # Esconde el boton de eliminar registros
        self.ui_main.btn_deleteRegister.setVisible(False)

        # Timer para correr el proceso de escaneado
        self.TimeProcess = QTimer()
        self.TimeProcess.timeout.connect(self.Run_process)
        self.TimeProcess.start(200)

        # Timer para la lectura del Codigo de barras
        self.timerRead_text= QTimer()
        self.timerRead_text.timeout.connect(self.Focus_textEdit)
        self.timerRead_text.start(480)

        # Timer para las alertas vizuales
        self.Alerts = QTimer()
        self.AlertsFisrtScan=QTimer()

        # Timer para actualizar los label de la impresora
        self.timeLabelPrinter = QTimer()
        self.timeLabelPrinter.timeout.connect(self.Update_PrinterLabel)
        self.timeLabelPrinter.start(500)

        # obtiene el respaldo de los datos
        data = dataBase.GetDataBackUp()

        # Variables que se inicializan con el backup
        self.PartNo = data[1]
        self.Supplier = data[2]
        self.OT = data[3]
        self.PzsTotales = int(data[4])
        self.PzsRealizadas = int(data[5])
        self.SerialNum = data[6]
        self.CreationDate = data[7]
        self.Cliente = data[8]
        self.timeAlarma=0
        self.cantidadBackUp=0


        # Calcula las piezas faltantes a escanear
        self.PzsFaltantes = int(self.PzsTotales - self.PzsRealizadas)
        self.PrinterMode = 0
        self.state = 0
        self.CodeRadd = ""
        self.DateLabel = ""
        self.Key = False
        self.mStatus_Wifi = 0
        self.mStatus_Server = 0
        self.firstScan=1
        self.retries=0

        # Esconde el boton de Buscador de Master
        self.ui_main.Btn_Search_Serie.hide()

        # Recuperar datos de archivo Json
        try:
            wifi, server, code = self.Read_Json()
            self.wifiControl = wifi == "1"
            self.Servercontrol = server == "1"
            self.codeControl = code == "1"  # si es True es DMC si es False es CODE BAR

        except Exception as e:
            QMessageBox.critical(self, "Alerta de Registro", "No se encontro registro solicitado, ejecuta el setup!")

            # Si el archivo esta roto se procede a eliminarlo
            archivo = "./Data/setup.json"
            if os.path.exists(archivo):
                os.remove(archivo)
                print(f"{archivo} ha sido eliminado")

            else:
                print(f"{archivo} no se encontró")
            sys.exit(0)

        # Actualiza las vistas de  los label de interfaz
        self.initLabels()
        self.init_LabelTittle(self.Cliente, self.codeControl)

        # Crea la tabla para la base de datos
        self.CreateTable()
        self.CreateTableMaster()

        # Actualiza los displays de contenedores
        self.ui_main.lcdNumber_Realizado.display(self.PzsRealizadas)
        self.ui_main.lcdNumber_Faltantes.display(self.PzsFaltantes)

        # Oculta las tablas de Historial
        self.tableMastertaBase.hide()
        self.tableWidgetdataBase.hide()

        # Inicializa en la hoja de home 6
        self.ui_main.MenuPrincipal.setCurrentIndex(6)

        # Esconde el boton de savedata
        self.ui_main.btn_saveDataLabel.hide()

        # Agrega el ultimo valor del numero de Serie
        self.ui_main.box_serial.addItems(dataBase.GetSerialMaster("LTR_Master"))

        # Inicializa los combox de configuracion inicial
        self.ui_main.initBox_PartNo.addItems(["5QM121251P", "5QM121251Q", "5QM121251R"])

        # Inicializa los combo box de cliente para puebla ** En merida Habilitar MERIDA
        self.ui_main.initBox_Cliente.clear()

        # Inicializa los sistemas de Scaneo Disponibles
        self.ui_main.initBox_Cliente.addItems(["HBPO", "CKD","MERIDA"])

        # Ocultar el boton de data matrix
        self.ui_main.btn_DataMatrix.setVisible(False)

        # Cargar los valores desde el JSON
        self.load_items_from_json()

        # Obtiene la cantidad seteada de piezas desde la base de datos
        mData = dataBase.GetDataBackUp()
        PzsTotales = mData[4]

        # Setea el numeor de piezas en el display
        self.ui_main.initBox_Cantidad.setCurrentText(PzsTotales)

        # Agrega el numero de proveedor al combobox
        self.ui_main.initBox_Proveedor.addItems(["43700413", "6001003941"])

        # Elimina todo lo escrito en el txt de orden de trabajo
        self.ui_main.initTxt_OT.clear()

        # Esconde el boton de imprimir
        self.ui_main.btn_printCurrIndex.hide()

        # Inicializa el widget con la tabla master
        self.tableMastertaBase.show()

        #self.ssid = "FAMILIA ORTIZ"  # SSID
        #self.password = "123OrtizFam"  # Password

        # Define variables para conexion de red
        self.ssid = "ADMINISTRATIVOS"  # SSID
        self.password = "M3X1C086"  # Password

        # Instancia de la Clase de Red Wifi
        self.WIFI = WifiMonitor(self.ssid, self.password)
        self.WIFI.connection_status_changed.connect(self.Update_WifiLabel)

        # Crear el monitor de conexión
        self.ServerMonitor = ConnectionMonitor()
        self.ServerMonitor.connection_status_changed.connect(self.Update_ServerLabel)
        self.ServerMonitor.start()

        # Restringe la entrada de caracteres al buscador del historial
        regex = QRegularExpression(r"\d+")
        validator = QRegularExpressionValidator(regex, self)
        self.ui_main.lineEdit.setValidator(validator)
    @Slot()
    def load_items_from_json(self):
        # Leer el archivo JSON
        with open("./Data/data.json", "r", encoding="utf-8") as file:
            data = json.load(file)  # Cargar el JSON en un diccionario

        #print(data)  # Verificar el contenido del JSON
        #print("Claves disponibles:", list(data.keys()))  # Ver claves exactas
        #print("Quantity:", data.get("quantity"))  # Intentar obtener "quantity"

        self.cantidadBackUp= data.get("quantity")
        #print(self.cantidadBackUp)

        # Obtener el valor máximo
        max_value = data.get('quantity', 10)  # 10 es un valor por defecto

        # Llenar el ComboBox con los valores desde 1 hasta max_value
        self.ui_main.initBox_Cantidad.addItems([str(i) for i in range(1, max_value + 1)])
    @Slot()
    def on_date_selected(self):
        try:
            if self.ui_main.Box_Search_Mode.currentText() == "PIEZAS":

                # Evalua si hay registros en el line edit para el numero de serie
                num_serie = int(self.ui_main.lineEdit.text()) if len(self.ui_main.lineEdit.text()) > 0 else 0

                if num_serie > 0 and num_serie <= 46655:
                    # Convierte el numero de Serie en base 36
                    serie_base_36 = self.base10to36(num_serie).upper()

                    # Obtiene el dia seleccionado en el Widget del calendario
                    date = self.ui_main.calendarWidget.selectedDate()  # QDate

                    # Obtener la fecha como string en formato 'ddMMyyyy'
                    date_str = date.toString("ddMMyyyy")

                    # Adquiere el modelo a buscar
                    Search_partNo = self.ui_main.Box_Search_PartNo.currentText()
                    print(Search_partNo)

                    # Solicita informacion a la base de datos
                    data_piece = dataBase.Get_Seial_Piece(serie_base_36, date_str, Search_partNo)

                    if data_piece is not None:
                        print(data_piece)
                        partNo = data_piece[2][1:11]

                        # 1. Extraer los 14 caracteres a partir del índice 41
                        fecha_str = data_piece[2][data_piece[2].find('=') + 1: data_piece[2].find(
                            '=') + 15]  # Alternativa segura usando '=' como referencia

                        # 2. Convertir a objeto datetime
                        fecha_obj = datetime.strptime(fecha_str, "%d%m%Y%H%M%S")

                        # 3. Formatear en formato legible
                        fecha_creacion = fecha_obj.strftime("%d/%m/%Y %H:%M:%S")

                        # Formato legible para la fecha de liberacion
                        fecha_liberacion = data_piece[3].strftime("%d/%m/%Y %H:%M:%S")
                        info = (
                            f"<b>Numero de Parte:   </b> {partNo}<br>"
                            f"<b>Etiqueta Creada:   </b> {fecha_creacion}<br>"
                            f"<b>Etiqueta Liberada: </b> {fecha_liberacion}<br>"
                            f"<b>Rack Serial:</b> {data_piece[1]}<br>"
                            f"<b>Cliente:</b> {data_piece[5]}"
                        )

                        QMessageBox.information(self, f"Numero de Serie: {serie_base_36}", info)
                    else:
                        info = (
                            f"No Existe registro en la base de datos."
                        )
                        QMessageBox.warning(self, f"Num. Serie: {serie_base_36}", info)

                    # Limpia el buscador
                    self.ui_main.lineEdit.clear()
                    self.ui_main.calendarWidget.setSelectedDate(QDate.currentDate())
                else:
                    pass

        except Exception as e:
            print(e)
            pass
    @Slot()
    def Search_DataMaster(self):
        serieSearch = self.ui_main.lineEdit.text()
        if len(serieSearch) == 12:
            data = dataBase.Get_Serial_Master(serieSearch)
            if data:
                cantidad = len(data)
                ancho = len(str(cantidad)) + 2  # número + punto + espacio

                # Generamos líneas con números en negrita, usando <pre> para mantener la alineación
                texto_datos = "\n".join(
                    f"<b>{str(i + 1).rjust(ancho - 2)}.</b> {r}" for i, r in enumerate(data)
                )

                mensaje = (
                    f"<html><body>"
                    f"<p>Se encontraron <b>{cantidad}</b> registro(s):</p>"
                    f"<pre style='font-family: monospace'>{texto_datos}</pre>"
                    f"</body></html>"
                )

                QMessageBox.information(
                    self,
                    "Registros encontrados",
                    mensaje
                )
                self.ui_main.lineEdit.clear()
            else:
                QMessageBox.warning(
                    self,
                    "Sin resultados",
                    f"No se encontraron registros para el número de serie:\n{serieSearch}"
                )
                self.ui_main.lineEdit.clear()
        else:
            QMessageBox.warning(
                self,
                "Longitud inválida",
                "Verifica que el número de serie tenga exactamente 12 dígitos."
            )
    @Slot()
    def ChangeSearch(self, index):
        texto = self.ui_main.Box_Search_Mode.currentText()
        if texto == "PIEZAS":
            self.ui_main.Btn_Search_Serie.hide()
            self.ui_main.calendarWidget.show()
            layout = self.ui_main.horizontalLayout_11
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if widget:
                    widget.show()

        elif texto == "MASTER":
            self.ui_main.calendarWidget.hide()
            self.ui_main.Btn_Search_Serie.show()
            layout = self.ui_main.horizontalLayout_11
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if widget:
                    widget.hide()
    @Slot()
    def base10to36(self, data: int) -> str:
        dato = ''
        chars = '0123456789abcdefghijklmnopqrstuvwxyz'
        if data == 0:
            return '000'
        while data > 0:
            data, rem = divmod(data, 36)
            dato = chars[rem] + dato
        dato = dato.upper().zfill(3)
        print("base_36: ", dato)
        return dato

    def MainMenu_Control(self):
        self.CloseMenuControl()
        if self.ui_main.toggleButton.isChecked():
            self.ui_main.animation.setStartValue(84)
            self.ui_main.animation.setEndValue(250)
        else:
            self.ui_main.animation.setStartValue(250)
            self.ui_main.animation.setEndValue(84)  # Ajusta el ancho según tus necesidades
        self.ui_main.animation.start()
    def CloseMainMenu(self):
        if self.ui_main.toggleButton.isChecked():
            self.ui_main.toggleButton.setChecked(False)
            self.ui_main.animation.setStartValue(250)
            self.ui_main.animation.setEndValue(84)  # Ajusta el ancho según tus necesidades
            self.ui_main.animation.start()
    def CloseSecondMenu(self):
        if self.ui_main.btn_configData.isChecked():
            self.ui_main.btn_configData.setChecked(False)
            self.ui_main.animation_secundario.setStartValue(250)
            self.ui_main.animation_secundario.setEndValue(0)  # Ajusta el ancho según tus necesidades
            self.ui_main.animation_secundario.start()
    def ConfigMenu_Control(self):
        self.CloseMainMenu()
        self.CloseSecondMenu()

        if self.ui_main.settingsTopBtn.isChecked():
            self.ui_main.animation_config.setStartValue(0)
            self.ui_main.animation_config.setEndValue(147)

        else:
            self.ui_main.animation_config.setStartValue(147)
            self.ui_main.animation_config.setEndValue(0)
        self.ui_main.animation_config.start()
    def CloseMenuControl(self):
        if self.ui_main.settingsTopBtn.isChecked():
            self.ui_main.settingsTopBtn.setChecked(False)
            self.ui_main.animation_config.setStartValue(147)
            self.ui_main.animation_config.setEndValue(0)
            self.ui_main.animation_config.start()
    @Slot()
    def Run_process(self):
        """Ejecuta el proceso principal si la GUI está en la ventana correcta y el sistema está listo."""
        if self.ui_main.MenuPrincipal.currentIndex() != 6:
            return

        if not self._is_ready():
            self._handle_errors()
            return

        # Sistema listo, iniciar proceso
        self.retries = 0
        self.DMC_SCAN()
    @Slot()
    def Focus_textEdit(self):
        if self.ui_main.MenuPrincipal.currentIndex() != 6:
            return

        self.ui_main.txt_input.setFocus()
    @Slot()
    def on_text_changed(self):
        self.ui_main.txt_input.setFocus()
        text = self.ui_main.txt_input.toPlainText()

        # Esperar a que el escáner termine de enviar (incluye \n o \r)
        if not text.endswith('\n') and not text.endswith('\r'):
            return

        # Limpiar texto de caracteres invisibles
        text = text.strip()

        # Verifica longitud y parte
        if len(text) == 55:
            if text[1:11] == self.PartNo:
                self.code_Radiador = text
                self.state = 1
            else:
                # Muestra Dialogo de Pieza con error de numero de Parte
                piezaIncorrecta = DialogoError(f"Error Número de Parte:\n {text[1:11]}")
                piezaIncorrecta.setModal(True)
                piezaIncorrecta.exec()
                #QMessageBox.critical(self, "Número de Parte Inválido", f"Verificar Número de Parte: {text[1:11]}")
        else:
            # Muestra label de Aprovado
            Longitud_error(self.ui_main)
            self.Alerts.singleShot(self.timeAlarma, lambda: HideAlerts(self.ui_main))
            print("Longitud incorrecta")

        # Limpia después de procesar
        self.ui_main.txt_input.clear()
    @Slot()
    def DMC_SCAN(self):
        # Centraliza la maquina de estados
        match self.state:
            case 0:
                pass
            case 1:
                # verifica la existencia del codigo actal dentro de la base de datos
                if dataBase.Check_nCode(self.code_Radiador) == False:
                    print(self.state)
                    # Envia al siguiente estado
                    self.state = 2
                else:
                    print("Codigo Repetido")
                    self.state = 3
            case 2:
                # Obtiene el cliente Actual
                current_client = self.Get_Client(self.Cliente) # la variable self.Cliente es el index del combox de cliente

                # Obtiene los valores actuales de la Etiqueta
                partNo, serialNumber, station, year, month, day, format_date, leak_rate = self._extract_label_data(self.code_Radiador)

                # Obtiene la fecha actual
                self.Date = datetime.strptime(format_date, "%d%m%Y%H%M%S")

                # Guardar pieza en la base de datos
                dataBase.addModule(self.SerialNum, self.code_Radiador, self.Date, current_client)

                # Verifica conexion con la API
                if self.mStatus_Server == 1 and self.Servercontrol == True:
                    # Convierte el valor del numero de serie base 36 a base 10
                    _serial = int(serialNumber, 36)

                    # Asigna los varlores obtenidos del DMC actual
                    chamber = station
                    serial_final = _serial
                    leak = leak_rate

                    # Envia los registros al server
                    set_Register(chamber, self.PartNo, serial_final, leak, 2)

                    # lanza el mensaje de aprovado desde el servidor
                    ApproveServer(self.ui_main)
                    self.Alerts.singleShot(1400, lambda: HideAlerts(self.ui_main))

                else:
                    # Muestra label de Aprovado
                    Approve(self.ui_main)
                    self.Alerts.singleShot(self.timeAlarma, lambda: HideAlerts(self.ui_main))


                # Actualiza variables de los contadores
                self.PzsRealizadas = int(self.PzsRealizadas) + 1
                self.PzsFaltantes = int(self.PzsTotales) - int(self.PzsRealizadas)

                # Asegura que los contadores no se desborden
                if int(self.PzsRealizadas) >= int(self.PzsTotales):
                    self.PzsRealizadas = int(self.PzsTotales)

                if int(self.PzsFaltantes) <= 0:
                    self.PzsFaltantes = 0

                # Actualiza los LCD de la GUI
                self.ui_main.lcdNumber_Realizado.display(self.PzsRealizadas)
                self.ui_main.lcdNumber_Faltantes.display(self.PzsFaltantes)

                # Actualiza la informacion del backup
                dataBase.updateData(self.PartNo, self.Supplier, self.OT, self.PzsTotales, self.PzsRealizadas, self.SerialNum, self.CreationDate, self.Cliente)

                # Verifica contenedor:
                if int(self.PzsFaltantes) == 0 and int(self.PzsRealizadas) == int(self.PzsTotales):
                    # Obtiene la fecha Actual
                    currDate = datetime.now()

                    # Formatear la fecha y hora para Merida
                    hora_formateada = currDate.strftime("%d/%m/%Y %H:%M:%S")

                    # Fecha segun formato HBPO
                    currDate_HBPO = currDate.strftime("%d/%m/%y")

                    # Fecha segun formato CKD
                    currDate_CKD = currDate.strftime("%d.%m.%y")

                    fecha = hora_formateada
                    partNo = self.PartNo  # 5QM121251R
                    Qty = str(self.PzsTotales)  # 10
                    supplier = self.Supplier  # "6001003941"
                    serial = self.SerialNum  #
                    OT = self.OT  # "162555

                    # Detiene el timer de consulta de la impresora
                    self.StatePrinter.stop()

                    # Obtiene el cliente actual:
                    current_client = self.Get_Client(self.Cliente)

                    # Obtiene el numero de parte interno
                    internal_PartNo = self.Get_internalPartNo(partNo)

                    # Verifica que etiqueta sera implementada
                    if current_client == "MERIDA":
                        # Envia a Imprimir segun el cliente
                        Print_MERIDA(fecha, partNo, Qty, supplier, serial, OT)

                    # Guarda los datos en la DB master
                    dataBase.addMaster(self.SerialNum, self.PzsTotales, self.OT, self.CreationDate, fecha, "COMPLETADO",
                                       current_client)

                    # Actualiza los datos de los display
                    self.PzsRealizadas = 0
                    self.PzsFaltantes = int(self.PzsTotales)

                    # Actualiza LCD de la GUI
                    self.ui_main.lcdNumber_Realizado.display(self.PzsRealizadas)
                    self.ui_main.lcdNumber_Faltantes.display(self.PzsFaltantes)
                    QApplication.processEvents()

                    # Evalua si el cliente es planta Merida:
                    if current_client == "MERIDA":
                        # Crea un nuevo numero de serie
                        mSerie = str(currDate.strftime("%d%m%Y%H%M%S"))
                        mSerie = f"2106{mSerie}"

                    else:
                        # Crea un nuevo numero de serie para HBPO
                        mSerie = str(currDate.strftime("%d%m%y%H%M%S"))

                    # Agrega la llave al serial
                    serial = mSerie

                    # Actualiza el numero de serie principal
                    self.SerialNum = serial

                    # Obtiene la fecha actual
                    self.CreationDate = fecha

                    # Actualiza la base de datos del backUp
                    dataBase.updateData(self.PartNo, self.Supplier, self.OT, self.PzsTotales, self.PzsRealizadas,
                                        self.SerialNum, self.CreationDate, self.Cliente)

                    # Actializa los label de interfaz
                    self.ui_main.lbl_Serial1.setText(QCoreApplication.translate("MainWindow", f"{self.SerialNum}", None))
                    self.ui_main.lbl_OT.setText(QCoreApplication.translate("MainWindow", f"{self.OT}", None))
                    self.ui_main.lbl_nPiezas.setText(QCoreApplication.translate("MainWindow",
                                                                                f"<html><head/><body><p><span style=\" color:#0055ff;\">{self.PzsTotales}</span></p></body></html>",
                                                                                None))
                    self.ui_main.lbl_Nparte.setText(QCoreApplication.translate("MainWindow",
                                                                               f"<html><head/><body><p>{self.PartNo}</p></body></html>",
                                                                               None))

                    # Muestra Dialogo de Rack Completado
                    QMessageBox.information(self, "COMPLETADO", f"Contenedor Completado con exito!")

                    # Reinicia la consulta del estado de la impresora
                    self.StatePrinter.start(2000)

                    # Elimina el contenido del text edit y reinicia el escaneo
                    self.ui_main.txt_input.clear()
                    self.state = 0
                else:
                    # Limpia el contenedor del text edit y reinicia el escaneo
                    self.ui_main.txt_input.clear()
                    # Envia al estado inicial
                    self.state = 0
            case 3:
                print(self.state)

                # Muestra la Alerte de Codigo Repetido
                Repeat(self.ui_main)
                self.Alerts.singleShot(self.timeAlarma, lambda: HideAlerts(self.ui_main))

                # Muestra Dialogo de Pieza Repetida
                piezaRepetida = DialogoError("Pieza Repetida")
                piezaRepetida.setModal(True)
                piezaRepetida.exec()

                # Elimina el text Edit
                self.ui_main.txt_input.clear()

                # Reinicia la maquina de estados
                self.state = 0
    @Slot()
    def _is_ready(self):
        _wifi = self.wifiControl
        _server = self.Servercontrol

        if _wifi and _server:
            return self.printer_state.mState==0 and self.mStatus_Wifi == 1 and self.mStatus_Server == 1
        elif _wifi:
            return self.printer_state.mState==0 and self.mStatus_Wifi == 1
        elif _server:
            return self.printer_state.mState==0 and self.mStatus_Server == 1

        return self.printer_state.mState==0  # Si ninguno está activado, la app no está lista.
    @Slot()
    def _handle_errors(self):
        """Maneja los mensajes de error dependiendo del estado de la aplicación."""
        if self.firstScan == 1:
            self.AlertsFisrtScan.singleShot(3000, lambda: self._reset_first_scan())

        elif self.printer_state.mState!=0:
            self._show_error("IMPRESORA", "Verificar el estado de la Impresora")

        elif self.mStatus_Wifi == 0:
            self.retries += 1
            self._show_error("CONEXION", f"Verificar la conexión WIFI del equipo.\nIntentos: {self.retries}/5")

        elif self.mStatus_Server == 0:
            self.retries += 1
            self._show_error("SERVIDOR", f"Verificar el SERVIDOR\nIntentos: {self.retries}/5")

        if self.retries > 4:
            self._show_error("CONEXION FALLIDA",
                             "El dispositivo no logra establecer una conexion exitosa.\nEjecute el setup para deshabilitar el monitoreo.")
            sys.exit(0)
    @Slot()
    def _reset_first_scan(self):
        self.firstScan = 0
    @Slot(str, str)
    def _show_error(self, title: str, message: str):
        """Muestra un mensaje de error y limpia la entrada."""
        print(f"Error: {message}")
        QMessageBox.critical(self, title, message)
    @Slot()
    def CreateTable(self):
        # Crear la tabla sin especificar el número de filas y columnas
        self.tableWidgetdataBase = QTableWidget(0, 6, self.ui_main.DatabaseWidget)
        #self.tableWidgetdataBase.setStyleSheet(u"background-color: rgb(18, 118, 118);border: 2px transparent #000000;border-radius: 5px;")

        self.tableWidgetdataBase.setObjectName(u"tableWidget")
        self.tableWidgetdataBase.setHorizontalHeaderLabels(
            ['ID', 'NUMERO DE SERIE', 'CODIGO DE RADIADOR', 'FECHA DE CREACION', 'FECHA DE ETIQUETA', 'CLIENTE'])
        self.tableWidgetdataBase.horizontalHeader().setStyleSheet("background-color: #A9A9A9; color: black")
        self.tableWidgetdataBase.setStyleSheet("color: black")

        # Ajustar el tamaño de las columnas para que se expandan automáticamente
        #self.tableWidgetdataBase.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.tableWidgetdataBase.setAlternatingRowColors(True)
        self.tableWidgetdataBase.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidgetdataBase.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidgetdataBase.setSelectionMode(QTableWidget.SingleSelection)

        if self.ui_main.DatabaseWidget.layout() is not None:
            self.ui_main.DatabaseWidget.layout().addWidget(self.tableWidgetdataBase)
        else:
            # Puedes crear un nuevo QVBoxLayout si aún no hay un layout
            new_layout = QVBoxLayout()
            new_layout.addWidget(self.tableWidgetdataBase)
            self.ui_main.DatabaseWidget.setLayout(new_layout)
    @Slot()
    def CreateTableMaster(self):
        # Crear la tabla sin especificar el número de filas y columnas
        self.tableMastertaBase = QTableWidget(0, 8, self.ui_main.DatabaseWidget)
        #self.tableWidgetdataBase.setStyleSheet(u"background-color: rgb(18, 118, 118);border: 2px transparent #000000;border-radius: 5px;")

        self.tableMastertaBase.setObjectName(u"tableWidget2")
        self.tableMastertaBase.setHorizontalHeaderLabels(
            ['ID', 'SERIAL', 'CANTIDAD', 'O.T.', 'F.CREACION', 'F.PRODUCCION', 'ESTATUS', 'CLIENTE'])
        self.tableMastertaBase.horizontalHeader().setStyleSheet("background-color: #A9A9A9; color: black")
        self.tableMastertaBase.setStyleSheet("color: black")

        # Ajustar el tamaño de las columnas para que se expandan automáticamente
        #self.tableMastertaBase.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.tableMastertaBase.setAlternatingRowColors(True)
        self.tableMastertaBase.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableMastertaBase.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableMastertaBase.setSelectionMode(QTableWidget.SingleSelection)

        if self.ui_main.DatabaseWidget.layout() is not None:
            self.ui_main.DatabaseWidget.layout().addWidget(self.tableMastertaBase)
        else:
            # Puedes crear un nuevo QVBoxLayout si aún no hay un layout
            new_layout = QVBoxLayout()
            new_layout.addWidget(self.tableMastertaBase)
            self.ui_main.DatabaseWidget.setLayout(new_layout)
    @Slot()
    def print_selected_row(self, row, column):
        row_data = []
        for col in range(self.tableMastertaBase.columnCount()):
            item = self.tableMastertaBase.item(row, col)
            if item is not None:
                row_data.append(item.text())
            else:
                row_data.append('')
        print(f"Row {row} data: {row_data}")

        # obtiene el respaldo de los datos
        data = dataBase.GetDataBackUp()


        # Variables que se inicializan con el backup
        #partno = data[1] #Verificar para que no lo uedan modificar ---- modificado
        supplier=data[2]
        serial= row_data[1]
        cantidad = row_data[2]
        ot= row_data[3]
        client = row_data[7]

        # Obtiene el numero de parte referenciando el numero de serie
        partno = dataBase.get_lastPartNo(serial)
        partno = partno[1:11]

        self.ConfirmPrint(partno, cantidad, supplier, serial, ot, client)
    @Slot()
    def HistorialPressed(self):
        self.ui_main.btn_printCurrIndex.hide()
        self.tableMastertaBase.hide()
        self.tableWidgetdataBase.show()
        dataBase.InsertinTable(1, self.tableWidgetdataBase, 30)
        # Después de agregar los datos a la tabla, ajusta el ancho de las columnas al contenido máximo
        self.tableWidgetdataBase.resizeColumnsToContents()
        self.ui_main.MenuPrincipal.setCurrentIndex(4)
        self.Key = False
    @Slot()
    def HistorialMasterPressed(self):
        self.ui_main.btn_printCurrIndex.hide()
        self.tableWidgetdataBase.hide()
        self.tableMastertaBase.show()
        dataBase.InsertinTable(2, self.tableMastertaBase, 30)
        # Después de agregar los datos a la tabla, ajusta el ancho de las columnas al contenido máximo
        self.tableMastertaBase.resizeColumnsToContents()
        self.ui_main.MenuPrincipal.setCurrentIndex(4)
        self.Key=False
    @Slot()
    def PrintPressed(self):
        # Muestra el widget del calendario y envia el slot para configurar la vista
        self.ui_main.calendarWidget.show()
        self.ui_main.Box_Search_Mode.setCurrentIndex(0)
        self.ui_main.btn_printCurrIndex.hide()

        if self.Key == True:
            # Esconde la tabla de piezas realizadas
            self.tableWidgetdataBase.hide()

            # Actualiza la tabla con la informacion de la master
            dataBase.InsertinTable(2, self.tableMastertaBase, 1)

            # Después de agregar los datos a la tabla, ajusta el ancho de las columnas al contenido máximo
            self.tableMastertaBase.resizeColumnsToContents()
            self.tableMastertaBase.show()
            self.ui_main.MenuPrincipal.setCurrentIndex(4)#5
    @Slot()
    def HomePressed(self):
        self.Key = False
        self.ui_main.btn_printCurrIndex.hide()
        self.ui_main.MenuPrincipal.setCurrentIndex(6)
    @Slot()
    def DataMatrixPressed(self):
        self.Key = False
        self.ui_main.btn_printCurrIndex.hide()
        self.ui_main.MenuPrincipal.setCurrentIndex(7)
    @Slot()
    def ShowDialog(self, dialog, enable):
        if enable:
            dialog.setModal(True)
            # Muestra el diálogo
            dialog.show()
        else:
            # Oculta el diálogo si enable es False
            dialog.hide()
    @Slot()
    def GetData(self):
        if len(self.ui_main.box_serial.currentText())>0:
            self.ui_main.btn_PrintLabel.hide()
            serial = self.ui_main.box_serial.currentText()
            print(serial, type(serial))
            result = dataBase.GetDataMaster(serial)
            data = dataBase.GetDataBackUp()
            partno = data[1]
            qty = result[2]
            supplier = data[2]
            ot = result[3]
            client = result[4]

            self.ui_main.lbl_PartNoprint.setText(partno)
            self.ui_main.lbl_QtyPrint.setText(qty)
            self.ui_main.lbl_ProveedorPrint.setText(supplier)
            self.ui_main.lbl_OTPrint.setText(ot)

            #partno = self.ui_main.box_PartNo.currentText()
            #qty = self.ui_main.box_Cantidad.currentText()
            #supplier = self.ui_main.box_proveedor.currentText()
            #ot = self.ui_main.box_OT.currentText()
            self.ConfirmPrint(partno, qty, supplier, serial, ot, client)
        else:
            QMessageBox.warning(None, "Informacion Incompleta", "Verificar que todos los campos esten correctamente especificados")
    @Slot()
    def ConfirmPrint(self, PartNo,Qty,Supplier,Serial,OT, CLIENT):
        ConfirmPrint = ConfirmData()
        ConfirmPrint.setModal(True)
        #_client = self.Get_Client(int(CLIENT))
        ConfirmPrint.SetData(PartNo, Qty, Supplier, Serial, OT,CLIENT)
        ConfirmPrint.exec()

        result = ConfirmPrint.state

        if result == True:
            if self.Key ==True:
                print("Imprime Etiqueta")

                #Detiene el monitor de la impresora
                self.StatePrinter.stop()

                if CLIENT == "MERIDA":
                    currDate = datetime.now()
                    currDate = currDate.strftime("%d/%m/%Y %H:%M:%S")
                    Print_MERIDA(currDate, PartNo, Qty, Supplier, Serial, OT)
                    QMessageBox.information(self, "Etiqueta Interna Impresa", "Se ha enviado la etiqueta correctamente")


                self.ui_main.btn_PrintLabel.show()
                self.ui_main.MenuPrincipal.setCurrentIndex(6)
                self.Key = False
                self.StatePrinter.start(2000)

        else:
            print("Editar informacion")
            self.ui_main.btn_PrintLabel.show()
            self.ui_main.btn_saveDataLabel.hide()
    @Slot()
    def ShowLoggin(self):
        loggin = Loggin()
        loggin.setModal(True)
        loggin.exec()
        self.Key = loggin.state

        if self.Key == 1: # Usuario Registrado
            # Asigna los datos actuales a las combo Box
            self.ui_main.initBox_PartNo.setCurrentText(self.PartNo)
            self.ui_main.initBox_Cantidad.setCurrentText(str(self.PzsTotales))
            self.ui_main.initTxt_OT.setText(self.OT)
            self.ui_main.initBox_Cliente.setCurrentText(self.Get_Client(self.Cliente))

            # Aplica solo para Merida
            self.ui_main.initBox_Cliente.setCurrentText(self.Get_Client(2))
            self.ui_main.initBox_Cliente.setEnabled(False)

            # Bloquea el box de cantidad para HBPO y CKD
            if self.Get_Client(self.Cliente) == "HBPO":
                self.ui_main.initBox_Cantidad.setEnabled(False)

            if self.Get_Client(self.Cliente) == "CKD":
                self.ui_main.initBox_Cantidad.setEnabled(False)

            if self.Get_Client(self.Cliente) == "MERIDA":
                self.ui_main.initBox_Cantidad.setEnabled(False)

            # Muestra los botones de editar e imprimir
            self.ui_main.btn_PrintAction.show()
            self.ui_main.btn_EditAction.show()

            # Esconde el boton de Delete Register
            self.ui_main.btn_deleteRegister.setVisible(False)
            
            # Envia la GUI a la pagina de edicion
            self.ui_main.MenuPrincipal.setCurrentIndex(1)

        elif self.Key ==2: # Administrador Registrado
            # Asigna los datos actuales a las combo Box
            self.ui_main.initBox_PartNo.setCurrentText(self.PartNo)
            self.ui_main.initBox_Cantidad.setCurrentText(str(self.PzsTotales))
            self.ui_main.initTxt_OT.setText(self.OT)
            self.ui_main.initBox_Cliente.setCurrentText(self.Get_Client(self.Cliente))

            # Bloquea el box de cantidad para HBPO y CKD
            if self.Get_Client(self.Cliente) == "HBPO":
                self.ui_main.initBox_Cantidad.setEnabled(False)

            if self.Get_Client(self.Cliente) == "CKD":
                self.ui_main.initBox_Cantidad.setEnabled(False)

            if self.Get_Client(self.Cliente) == "MERIDA":
                self.ui_main.initBox_Cantidad.setEnabled(False)

            # Oculta los botones de editar e imprimir
            self.ui_main.btn_PrintAction.hide()
            self.ui_main.btn_EditAction.hide()

            # Muestra el boton de Delete Register
            self.ui_main.btn_deleteRegister.setVisible(True)

            # Envia la GUI a la pagina de edicion
            self.ui_main.MenuPrincipal.setCurrentIndex(1)

        else:    
            # Esconde el boton de Delete Register
            self.ui_main.btn_deleteRegister.setVisible(False)

            # Envia la GUI a la pagina Principal
            self.ui_main.MenuPrincipal.setCurrentIndex(6)

            # Reset a Key
            self.Key=0
    @Slot()
    def SetCurrentData(self):
        if len(self.ui_main.initBox_PartNo.currentText())>0 and len(self.ui_main.initBox_Cantidad.currentText())>0 and len(self.ui_main.initBox_Proveedor.currentText())>0 and len(self.ui_main.initTxt_OT.toPlainText())>0 and len(self.ui_main.initBox_Cliente.currentText())>0:
            print("Guardar Datos")
            PartNo = self.ui_main.initBox_PartNo.currentText()
            Cantidad = self.ui_main.initBox_Cantidad.currentText()
            Proveedor = self.ui_main.initBox_Proveedor.currentText()
            OT = self.ui_main.initTxt_OT.toPlainText()
            cliente = self.ui_main.initBox_Cliente.currentIndex()

            currDate = datetime.now()
            hora_formateada = currDate.strftime("%d/%m/%Y %H:%M:%S")
            fecha = hora_formateada
            curr_client = self.Get_Client(cliente)

            if curr_client == "MERIDA":
                mSerie = str(currDate.strftime("%d%m%Y%H%M%S"))
                serial = f"2106{mSerie}"

            else:
                mSerie = str(currDate.strftime("%d%m%y%H%M%S"))
                serial = str(mSerie)

            self.SerialNum = serial
            self.CreationDate = fecha

            self.PartNo = PartNo
            self.Supplier = Proveedor
            self.OT = OT
            self.PzsTotales = int(Cantidad)
            self.PzsRealizadas= 0
            self.PzsFaltantes = int(self.PzsTotales)
            self.Cliente = cliente

            # Actualiza la base de datos del backUp
            dataBase.updateData(self.PartNo, self.Supplier, self.OT, self.PzsTotales, self.PzsRealizadas,
                                self.SerialNum,
                                self.CreationDate, self.Cliente)

            self.ui_main.lbl_Serial1.setText(QCoreApplication.translate("MainWindow", f"{self.SerialNum}", None))
            self.ui_main.lbl_OT.setText(QCoreApplication.translate("MainWindow", f"{self.OT}", None))
            self.ui_main.lbl_nPiezas.setText(QCoreApplication.translate("MainWindow",
                                                                        f"<html><head/><body><p><span style=\" color:#0055ff;\">{self.PzsTotales}</span></p></body></html>",
                                                                        None))
            self.ui_main.lbl_Nparte.setText(
                QCoreApplication.translate("MainWindow", f"<html><head/><body><p>{self.PartNo}</p></body></html>",
                                           None))

            self.ui_main.lbl_PrinterState.setText(QCoreApplication.translate("MainWindow",
                                                                             f"<html><head/><body><p><span style=\" font-size:16pt; font-weight:700;\">IMPRESORA: </span><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\"></span></p></body></html>",
                                                                             None))


            self.ui_main.lcdNumber_Realizado.display(self.PzsRealizadas)
            self.ui_main.lcdNumber_Faltantes.display(self.PzsFaltantes)

            self.init_LabelTittle(self.Cliente, self.codeControl)

            self.ui_main.MenuPrincipal.setCurrentIndex(6)
            self.Key = False

            QMessageBox.information(None, "Informacion Actualizada", "Datos Actualizados Correctamente")

        else:
            QMessageBox.warning(None, "Informacion Incompleta", "Verificar que todos los campos esten correctamente especificados")
    @Slot()
    def CancelChange(self):
        self.Key=False
        self.ui_main.MenuPrincipal.setCurrentIndex(6)
    @Slot()
    def GetPrintMode(self):
        # Abre y lee el contenido del archivo JSON
        with open('./Data/data.json', 'r') as file:
            data = json.load(file)

        # Extrae los enteros del JSON
        template = data.get('template')
        calibrate = data.get('calibrate')
        timeAlarm = data.get('time')

        self.timeAlarma=int(timeAlarm)
        #print(self.timeAlarma)

        if template == 1:
            pass
        elif calibrate == 1:
            SendLabelCalibrate()
    @Slot()
    def initLabels(self):
        self.ui_main.lbl_Serial1.setText(QCoreApplication.translate("MainWindow", f"{self.SerialNum}", None))
        self.ui_main.lbl_OT.setText(QCoreApplication.translate("MainWindow", f"{self.OT}", None))
        self.ui_main.lbl_nPiezas.setText(QCoreApplication.translate("MainWindow",
                                                                    f"<html><head/><body><p><span style=\" color:#0055ff;\">{self.PzsTotales}</span></p></body></html>",
                                                                    None))
        self.ui_main.lbl_Nparte.setText(
            QCoreApplication.translate("MainWindow", f"<html><head/><body><p>{self.PartNo}</p></body></html>", None))
        """self.ui_main.lbl_PrinterState.setText(QCoreApplication.translate("MainWindow",
                                                                         f"<html><head/><body><p><span style=\" font-size:16pt; font-weight:700;\">IMPRESORA: </span><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\"></span></p></body></html>",
                                                                         None))"""
        self.ui_main.lbl_PrinterState.setText(QCoreApplication.translate("MainWindow",
                                                                         f"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:700;\">IMPRESORA:<br/></span><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">CONECTANDO...</span></p></body></html>",
                                                                         None))

        self.ui_main.lbl_labelMasterEdit.setPixmap(QPixmap(u"./Label_Master.PNG"))
    @Slot()
    def init_LabelTittle(self, model, code):
        match model:
            case 0:#HBPO
                self.ui_main.titleLeftApp.setText(QCoreApplication.translate("MainWindow",
                                                                     f"<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">LTR - </span><span style=\" font-size:12pt; color:#e5e500;\">HBPO</span></p></body></html>",
                                                                     None))
            case 1:#CKD
                self.ui_main.titleLeftApp.setText(QCoreApplication.translate("MainWindow",
                                                                     f"<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">LTR - </span><span style=\" font-size:12pt; color:#e5e500;\">CKD</span></p></body></html>",
                                                                     None))
            case 2:#MERIDA
                self.ui_main.titleLeftApp.setText(QCoreApplication.translate("MainWindow",
                                                                             f"<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">LTR - </span><span style=\" font-size:12pt; color:#e5e500;\">Merida</span></p></body></html>",
                                                                             None))
        # Evalua el tipo de Barcode
        match code:
            case 0:
                self.ui_main.extraLabel.setText(QCoreApplication.translate("MainWindow",
                                                           u"<html><head/><body><p><span style=\" font-weight:900;\">CODIGO: </span><span style=\" font-weight:900; color:#e5e500;\"> DMC</span></p></body></html>",
                                                           None))
            case 1:
                self.ui_main.extraLabel.setText(QCoreApplication.translate("MainWindow",
                                                                   u"<html><head/><body><p><span style=\" font-weight:800;\">CODIGO: </span><span style=\" font-weight:800; color:#e5e500;\"> DMC</span></p></body></html>",
                                                                   None))
    @Slot()
    def on_item_selected(self, index):
        print(index)
        """Se ejecuta al seleccionar un ítem del ComboBox.
        0 - HBPO
        1 - CKD
        2 - MERIDA
        """

        if index == 0:
            self.ui_main.initBox_PartNo.setEnabled(True)
            self.ui_main.initBox_Cantidad.setEnabled(False)
            self.ui_main.initBox_Cantidad.setCurrentText("16")
            self.ui_main.initBox_Proveedor.setCurrentText("43700413")
            self.ui_main.initBox_Proveedor.setEnabled(False)
        elif index == 1:
            self.ui_main.initBox_Cantidad.setEnabled(False)
            self.ui_main.initBox_Cantidad.setCurrentText("20")
            self.ui_main.initBox_PartNo.setEnabled(False)
            self.ui_main.initBox_PartNo.setCurrentText("5QM121251Q")
            self.ui_main.initBox_Proveedor.setCurrentText("43700413")
            self.ui_main.initBox_Proveedor.setEnabled(False)
        else:
            self.ui_main.initBox_Proveedor.setCurrentText("6001003941")
            self.ui_main.initBox_Proveedor.setEnabled(False)
            self.ui_main.initBox_Cantidad.setCurrentText("16")
            self.ui_main.initBox_Cantidad.setEnabled(False)
            self.ui_main.initBox_PartNo.setEnabled(True)
    @Slot(str)
    def _extract_label_data(self, code: str):
        try:
            numero_parte = code[1:12].strip()
            año = code[26]
            mes = code[27]
            dia = code[28]
            numero_serie = code[29:32]
            cabina = code[32]
            fecha_formateada = code[36:50]
            rate_fuga = float(code[51:].strip())
        except (IndexError, ValueError):
            numero_parte = año = mes = dia = numero_serie = cabina = fecha_formateada = rate_fuga = None

        return numero_parte, numero_serie, cabina, año, mes, dia, fecha_formateada, rate_fuga
    @Slot()
    def Update_PrinterLabel(self):
        mState = self.printer_state.mState
        mText = self.printer_state.mText
        match mState:
            case 0:
                self.ui_main.lbl_PrinterState.setStyleSheet(u"QLabel {\n"
                                                       "    border: 2px solid #00aa00; /* Cambia el color del borde a rojo */\n"
                                                       "	border-color: #00aa00;\n"
                                                       "	border-radius:5px;\n"
                                                       "}")
                """self.ui_main.lbl_PrinterState.setText(QCoreApplication.translate("MainWindow",
                                                                            f"<html><head/><body><p><span style=\" font-size:16pt; font-weight:700;\">Estado de la Impresora: </span><span style=\" font-size:16pt; font-weight:700; color:#7FFF00;\">{mText}</span></p></body></html>",
                                                                            None))"""
                self.ui_main.lbl_PrinterState.setText(QCoreApplication.translate("MainWindow",
                                                                         f"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:700;\">IMPRESORA:<br/></span><span style=\" font-size:16pt; font-weight:700; color:#00aa00;\">{mText}</span></p></body></html>",
                                                                         None))
            case 1:
                self.ui_main.lbl_PrinterState.setStyleSheet(u"QLabel {\n"
                                                       "    border: 2px solid #FF0000; /* Cambia el color del borde a rojo */\n"
                                                       "	border-color: rgb(255, 196, 0);\n"
                                                       "	border-radius:5px;\n"
                                                       "}")
                """self.ui_main.lbl_PrinterState.setText(QCoreApplication.translate("MainWindow",
                                                                            f"<html><head/><body><p><span style=\" font-size:16pt; font-weight:700;\">Estado de la Impresora: </span><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">{mText}</span></p></body></html>",
                                                                            None))"""

                self.ui_main.lbl_PrinterState.setText(QCoreApplication.translate("MainWindow",
                                                                         f"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:700;\">IMPRESORA:<br/></span><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">{mText}</span></p></body></html>",
                                                                         None))
            case 2:
                self.ui_main.lbl_PrinterState.setStyleSheet(u"QLabel {\n"
                                                       "    border: 2px solid #FF0000; /* Cambia el color del borde a rojo */\n"
                                                       "	border-color: rgb(255, 196, 0);\n"
                                                       "	border-radius:5px;\n"
                                                       "}")
                """self.ui_main.lbl_PrinterState.setText(QCoreApplication.translate("MainWindow",
                                                                            f"<html><head/><body><p><span style=\" font-size:16pt; font-weight:700;\">Estado de la Impresora: </span><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">{mText}</span></p></body></html>",
                                                                            None))"""

                self.ui_main.lbl_PrinterState.setText(QCoreApplication.translate("MainWindow",
                                                                                 f"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:700;\">IMPRESORA:<br/></span><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">{mText}</span></p></body></html>",
                                                                                 None))

            case 3:
                self.ui_main.lbl_PrinterState.setStyleSheet(u"QLabel {\n"
                                                       "    border: 2px solid #FF0000; /* Cambia el color del borde a rojo */\n"
                                                       "	border-color: rgb(255, 196, 0);\n"
                                                       "	border-radius:5px;\n"
                                                       "}")
                """self.ui_main.lbl_PrinterState.setText(QCoreApplication.translate("MainWindow",
                                                                            f"<html><head/><body><p><span style=\" font-size:16pt; font-weight:700;\">Estado de la Impresora: </span><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">{mText}</span></p></body></html>",
                                                                            None))"""

                self.ui_main.lbl_PrinterState.setText(QCoreApplication.translate("MainWindow",
                                                                                 f"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:700;\">IMPRESORA:<br/></span><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">{mText}</span></p></body></html>",
                                                                                 None))
            case 4:
                self.ui_main.lbl_PrinterState.setStyleSheet(u"QLabel {\n"
                                                       "    border: 2px solid #FF0000; /* Cambia el color del borde a rojo */\n"
                                                       "	border-color: rgb(255, 196, 0);\n"
                                                       "	border-radius:5px;\n"
                                                       "}")
                """self.ui_main.lbl_PrinterState.setText(QCoreApplication.translate("MainWindow",
                                                                            f"<html><head/><body><p><span style=\" font-size:16pt; font-weight:700;\">Estado de la Impresora: </span><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">{mText}</span></p></body></html>",
                                                                            None))"""

                self.ui_main.lbl_PrinterState.setText(QCoreApplication.translate("MainWindow",
                                                                                 f"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:700;\">IMPRESORA:<br/></span><span style=\" font-size:16pt; font-weight:700; color:#ffc400;\">{mText}</span></p></body></html>",
                                                                                 None))
            case 5:
                self.ui_main.lbl_PrinterState.setStyleSheet(u"QLabel {\n"
                                                       "    border: 2px solid #FF0000; /* Cambia el color del borde a rojo */\n"
                                                       "	border-color: #FF0000;\n"
                                                       "	border-radius:5px;\n"
                                                       "}")


                self.ui_main.lbl_PrinterState.setText(QCoreApplication.translate("MainWindow",
                                                                                 f"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:700;\">IMPRESORA:<br/></span><span style=\" font-size:16pt; font-weight:700; color:#FF0000;\">DESCONECTADA</span></p></body></html>",
                                                                                 None))
    @Slot(bool)
    def Update_WifiLabel(self, status):
        """
        Actualiza la etiqueta de estado con la información más reciente.
        """
        if status == False:
            self.mStatus_Wifi = 0
            self.ui_main.lbl_wifiState.setStyleSheet(u"QLabel {\n"
                                             "    border: 2px solid #FF0000; /* Cambia el color del borde a rojo */\n"
                                             "	border-color: #FF0000;\n"
                                             "	border-radius:5px;\n"
                                             "}")
            self.ui_main.lbl_wifiState.setText(QCoreApplication.translate("MainWindow",
                                                                  u"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:700;\">WIFI: <br/></span><span style=\" font-size:16pt; font-weight:700; color:#FF0000;\">DESCONECTADO</span></p></body></html>",
                                                                  None))
        else:
            self.mStatus_Wifi = 1
            self.ui_main.lbl_wifiState.setStyleSheet(u"QLabel {\n"
                                             "    border: 2px solid #FF0000;\n"
                                             "	border-color: #00aa00;\n"
                                             "	border-radius:5px;\n"
                                             "}")
            self.ui_main.lbl_wifiState.setText(QCoreApplication.translate("MainWindow",
                                                                          u"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:700;\">WIFI: <br/></span><span style=\" font-size:16pt; font-weight:700; color:#00aa00;\">CONECTADO</span></p></body></html>",
                                                                          None))
    @Slot(bool)
    def Update_ServerLabel(self, status):
        if status:
            self.mStatus_Server=1
            self.ui_main.lbl_ServerState.setStyleSheet(u"QLabel {\n"
                                               "    border: 2px solid #00aa00;\n"
                                               "	border-color: #00aa00;\n"
                                               "	border-radius:5px;\n"
                                               "}")
            self.ui_main.lbl_ServerState.setText(QCoreApplication.translate("MainWindow",
                                                                    u"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:700;\">SERVIDOR:<br/></span><span style=\" font-size:16pt; font-weight:700; color:#00aa00;\">EN LINEA</span></p></body></html>",
                                                                    None))

        else:
            self.mStatus_Server=0
            self.ui_main.lbl_ServerState.setStyleSheet(u"QLabel {\n"
                                                       "    border: 2px solid #FF0000;\n"
                                                       "	border-color: #FF0000;\n"
                                                       "	border-radius:5px;\n"
                                                       "}")
            self.ui_main.lbl_ServerState.setText(QCoreApplication.translate("MainWindow",
                                                                            u"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:700;\">SERVIDOR:<br/></span><span style=\" font-size:16pt; font-weight:700; color:#FF0000;\">DESCONECTADO</span></p></body></html>",
                                                                            None))

            """QMessageBox.information(None, "Servidor sin Conexion",
                                "Espera a que el servidor este conectado para comenzar. "
                                "Verificar conexion WIFI")"""
    @Slot()
    def Read_Json(self):
        """
        Metodo que obtiene los valores base de cada estacion. Se define los Puertos COM y direcciones IP.
        :return:
        """
        archivo = "./Data/setup.json"
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Asignar los valores a variables individuales
        WIFI = data["WIFI"]
        SERVER = data["SERVER"]
        CODE = data["CODE"]
        return WIFI, SERVER, CODE
    @Slot()
    def Get_Client(self, cliente):
        estados = {
            0: "HBPO",
            1: "CKD",
            2: "MERIDA"
        }
        return estados.get(cliente, "Desconocido")
    @Slot(str)
    def Get_internalPartNo(self, PartNo: str) -> str:
        """
        Devuelve el número de parte interno correspondiente al número de parte externo proporcionado.

        Args:
            numero_parte_externo (str): El número de parte externo (ej. "5QM121251R")

        Returns:
            str: El número de parte interno correspondiente (ej. "04003RA12")
        """
        mapa_partes = {
            "5QM121251R": "04003RA12",
            "5QM121251P": "04003RA09",
            "5QM121251Q": "04003RA10",
        }

        return mapa_partes.get(PartNo, "DESCONOCIDO")
    @Slot()
    def delete_CurrData(self):
        # obtiene el valor actual del contador de piezas realizadas
        count = int(self.ui_main.lcdNumber_Realizado.value())
        print(count)

        if count > 0:
            #Elimina los registros grabados sin cerrar orden
            dataBase._delete_last_registers(dataBase.db_piece, count)

            # Eliminar los ultimos n registros de la tabla
            dataBase._delete_last_rows(self.tableWidgetdataBase, count)

            # Muestra el aviso de que los registros han sido Eliminados
            QMessageBox.warning(self, "Regitros Eliminados", f"Se han eliminado los ultimos {count} registros con exito")

            # Actualiza el valor de piezas realizadas
            self.PzsRealizadas = 0

            # Actualiza el valor de piezas faltantes
            self.PzsFaltantes = int(self.PzsTotales)

            # Actualiza la informacion del BackUp
            dataBase.updateData(self.PartNo, self.Supplier, self.OT, self.PzsTotales, self.PzsRealizadas,
                                self.SerialNum, self.CreationDate, self.Cliente)

            # Actualiza los LCD de la GUI.
            self.ui_main.lcdNumber_Realizado.display(self.PzsRealizadas)
            self.ui_main.lcdNumber_Faltantes.display(self.PzsTotales)

            # Manda la GUI a la interfaz principal
            self.ui_main.MenuPrincipal.setCurrentIndex(6)
        else:
            # Muestra el aviso de que los registros han sido Eliminados
            QMessageBox.warning(self, "Sin Registros",
                                f"No existen registros a eliminar.")
            # Manda la GUI a la interfaz principal
            self.ui_main.MenuPrincipal.setCurrentIndex(6)


if __name__ == "__main__":
    app = QApplication([])
    window = LTR()
    window.show()
    app.exec()
