import webbrowser
import globalPluginHandler
from ui import message
import api
from scriptHandler import script
from urllib import request, parse
from time import sleep
from threading import Thread
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
	del sys.modules['html']
except:
	pass

from bs4 import BeautifulSoup
import string

def scrap(site):
	try:
		contenido = request.Request(site, data=None, headers={"User-Agent": "Mozilla/5.0"})
		html = request.urlopen(contenido)
		datos = html.read().decode('utf-8')
		bs = BeautifulSoup(datos, 'html.parser')
		if site == "https://audiotools.in/" or site == "https://audioz.download/":
			return bs.find_all('h2')
		else:
			return bs.find_all('a', {'class': 'addon'})
	except:
		pass

def tutoriales(time):
	global tutoriales
	sleep(time)
	tutoriales = scrap("http://ReaperYOtrasYerbas.com/tutoriales.php")

def descargas(time):
	global descargas
	sleep(time)
	descargas = scrap("http://ReaperYOtrasYerbas.com/descargas.php")

def audiotools(time):
	global audiotools
	sleep(time)
	audiotools = scrap("https://audiotools.in/")

def audioz(time):
	global secciones, audioz
	sleep(time)
	audioz = scrap("https://audioz.download/")
	secciones = [tutoriales, descargas, audiotools, audioz]

Thread(target=tutoriales, args=(5,), daemon= True).start()
Thread(target=descargas, args=(5,), daemon= True).start()
Thread(target=audiotools, args=(5,), daemon= True).start()
Thread(target=audioz, args=(5,), daemon= True).start()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	x = -1
	y=0
	switch = False

	@script(
		category="HerramientasReaper",
		description="Activa y desactiva los comandos del complemento",
		gesture="kb:alt+NVDA+r"
	)
	def script_toggle(self, gesture):
		try:
			if len(secciones[3]) > 5:
				if self.switch == False:
					self.switch = True
					message("activado")
					self.bindGestures({"kb:downArrow":"nextItem", "kb:upArrow":"previousItem", "kb:rightArrow":"nextSection", "kb:leftArrow":"previousSection", "kb:enter":"open", "kb:home":"firstItem", "kb:end":"positionAnnounce", "kb:f5":"reload"})
				else:
					self.switch = False
					message("desactivado")
					self.clearGestureBindings()
					self.bindGestures(self.__gestures)
		except:
			pass

	def script_nextItem(self, gesture):
		self.x = self.x + 1
		if self.x < len(secciones[self.y]):
			message(secciones[self.y][self.x].string)
		else:
			self.x = 0
			message(secciones[self.y][self.x].string)

	def script_previousItem(self, gesture):
		self.x = self.x - 1
		if self.x >= 0:
			message(secciones[self.y][self.x].string)
		else:
			self.x = len(secciones[self.y]) - 1
			message(secciones[self.y][self.x].string)

	def script_nextSection(self, gesture):
		self.x = -1
		if self.y == 0:
			self.y = 1
			message("Descargas")
		elif self.y == 1:
			self.y = 2
			message("AudioTools")
		elif self.y == 2:
			self.y = 3
			message("AudioZ")
		elif self.y == 3:
			self.y = 0
			message("Tutoriales")

	def script_previousSection(self, gesture):
		self.x = -1
		if self.y == 3:
			self.y = 2
			message("AudioTools")
		elif self.y == 2:
			self.y = 1
			message("descargas")
		elif self.y == 1:
			self.y = 0
			message("tutoriales")
		elif self.y == 0:
			self.y = 3
			message("AudioZ")

	def script_open(self, gesture):
		item = secciones[self.y][self.x]
		if self.y == 0:
			webbrowser.open(f"http://ReaperYOtrasYerbas.com/{item['href']}")
		elif self.y == 1:
			webbrowser.open(item['href'])
		elif self.y == 2:
			item = secciones[self.y][self.x]
			webbrowser.open(item.a['href'])
		elif self.y == 3:
			item = secciones[self.y][self.x]
			webbrowser.open(item.parent['href'])
		self.switch = False
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)

	def script_firstItem(self, gesture):
		self.x = 0
		message(secciones[self.y][self.x].string)

	def script_positionAnnounce(self, gesture):
		message(f"{self.x+1} de {len(secciones[self.y])}")

	def script_reload(self, gesture):
		Thread(target=audiotools, args=(0,), daemon= True).start()
		Thread(target=audioz, args=(2,), daemon= True).start()
		message("Actualizando la base de datos, el proceso puede tardar algunos segundos")
