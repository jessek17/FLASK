import DBscript
import subprocess
import socket
from flask import Flask, request

def GetIP():
    IP_addres = request.remote_addr
#    h_name = socket.gethostname()
#    IP_addres = socket.gethostbyname(h_name)
    return IP_addres
	

def CheckLogin(usr: str, psw: str) -> bool:
    DBscript.cur.execute("""SELECT achternaam FROM Passagier WHERE achternaam = %(usr)s AND ticketnummer = %(psw)s;""", {'usr': usr, 'psw': psw})
    if DBscript.cur.fetchone():
        # accepted
	
        subprocess.call(["sudo", "iptables", "-t", "nat", "-I", "PREROUTING", "1", "-s", GetIP(), "-j", "ACCEPT"])
        subprocess.call(["sudo", "iptables", "-I", "FORWARD", "-s", GetIP(), "-j", "ACCEPT"])
        return True
    else:
        # Refused
        return False
