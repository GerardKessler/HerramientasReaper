# -*- coding: utf-8 -*-
# Copyright (C) 2021 Gerardo Kessler <ReaperYOtrasYerbas@gmail.com>
# This file is covered by the GNU General Public License.
# Utilización de la librería bs4 basada en el complemento DLEChecker de Antonio Cascales.

import globalPluginHandler
import core
from ui import message
import api
from scriptHandler import script, getLastScriptRepeatCount
from urllib import request, parse
from time import sleep
from threading import Thread
import webbrowser
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
	del sys.modules['html']
except:
	pass

from bs4 import BeautifulSoup
import string

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		self.sections = ["Tutoriales", "Descargas", "AudioTools", "AudioZ", "PluginTorrent", "pro_vst"]
		self.index = [0, 0, 0, 0, 0 ,0]
		self.secciones = None
		self.x = 0
		self.y=0
		self.switch = False
		self.tutoriales = None
		self.descargas = None
		self.audiotools = None
		self.audioz = None
		self.plugintorrent = None
		self.provst = None
		core.postNvdaStartup.register(self.startScrap)

	def startScrap(self):
		Thread(target=self.reaper, daemon= True).start()
		Thread(target=self.vstContent, daemon= True).start()

	def scrap(self, site, tag, pattern= None):
		try:
			contenido = request.Request(site, data=None, headers={"User-Agent": "Mozilla/5.0"})
			html = request.urlopen(contenido)
			datos = html.read().decode('utf-8')
			bs = BeautifulSoup(datos, 'html.parser')
			if pattern == None:
				return bs.find_all(tag)
			else:
				return bs.find_all(tag, pattern)
		except:
			pass

	def reaper(self):
		self.tutoriales = self.scrap("http://ReaperYOtrasYerbas.com/tutoriales.php", "a", {"class": "addon"})
		self.descargas = self.scrap("http://ReaperYOtrasYerbas.com/descargas.php", "a", {"class": "addon"})

	def vstContent(self):
		self.audiotools = self.scrap("https://audiotools.in/", "h2")
		self.audioz = self.scrap("https://audioz.download/", "h2")
		self.plugintorrent = self.scrap("https://plugintorrent.com/", "h2")
		self.provst = self.scrap("http://pro-vst.org/", "h1")
		self.provst.pop(0)
		self.secciones = [self.tutoriales, self.descargas, self.audiotools, self.audioz, self.plugintorrent, self.provst]

	@script(
		category="HerramientasReaper",
		description="Activa y desactiva los comandos del complemento"
	)
	def script_toggle(self, gesture):
		try:
			if len(self.secciones[2]) > 5:
				if self.switch == False:
					self.switch = True
					message("Atajos activados")
					self.bindGestures(
						{"kb:downArrow":"nextItem",
						"kb:upArrow":"previousItem",
						"kb:rightArrow":"nextSection",
						"kb:leftArrow":"previousSection",
						"kb:enter":"open",
						"kb:home":"firstItem",
						"kb:end":"positionAnnounce",
						"kb:f5":"reload",
						"kb:escape":"close"}
					)
				else:
					self.switch = False
					message("Atajos desactivados")
					self.clearGestureBindings()
		except:
			pass

	def script_nextItem(self, gesture):
		self.x = self.x + 1
		if self.x < len(self.secciones[self.y]):
			if self.y == 4:
				item = self.secciones[self.y][self.x]
				message(item.a["title"][12:])
			else:
				message(self.secciones[self.y][self.x].string)
		else:
			self.x = 0
			if self.y == 4:
				item = self.secciones[self.y][self.x]
				message(item.a["title"][12:])
			else:
				message(self.secciones[self.y][self.x].string)

	def script_previousItem(self, gesture):
		self.x = self.x - 1
		if self.x >= 0:
			if self.y == 4:
				item = self.secciones[self.y][self.x]
				message(item.a["title"][12:])
			else:
				message(self.secciones[self.y][self.x].string)
		else:
			self.x = len(self.secciones[self.y]) - 1
			if self.y == 4:
				item = self.secciones[self.y][self.x]
				message(item.a["title"][12:])
			else:
				message(self.secciones[self.y][self.x].string)

	def script_nextSection(self, gesture):
		self.index[self.y] = self.x
		self.x = -1
		self.y = self.y + 1
		if self.y < len(self.sections):
			message(self.sections[self.y])
			self.x = self.index[self.y]
		else:
			self.y = 0
			message(self.sections[self.y])
			self.x = self.index[self.y]

	def script_previousSection(self, gesture):
		self.index[self.y] = self.x
		self.x = -1
		self.y = self.y - 1
		if self.y >= 0:
			message(self.sections[self.y])
			self.x = self.index[self.y]
		else:
			self.y = len(self.sections) - 1
			message(self.sections[self.y])
			self.x = self.index[self.y]

	def script_open(self, gesture):
		item = self.secciones[self.y][self.x]
		if self.y == 0:
			webbrowser.open(f"http://ReaperYOtrasYerbas.com/{item['href']}")
		elif self.y == 1:
			webbrowser.open(item['href'])
		elif self.y == 2:
			webbrowser.open(item.a['href'])
		elif self.y == 3:
			webbrowser.open(item.parent['href'])
		elif self.y == 4:
			webbrowser.open(item.a["href"])
		elif self.y == 5:
			webbrowser.open(item.parent.a["href"])
		self.switch = False
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)

	def script_firstItem(self, gesture):
		self.x = 0
		if self.y == 4:
			item = self.secciones[self.y][self.x]
			message(item.a["title"][12:])
		else:
			message(self.secciones[self.y][self.x].string)

	def script_positionAnnounce(self, gesture):
		if getLastScriptRepeatCount() == 1:
			if self.y == 4:
				item = self.secciones[self.y][self.x]
				message(f'{item.a["title"][12:]}; {self.x+1} de {len(self.secciones[self.y])}')
			else:
				message(f'{self.secciones[self.y][self.x].string}; {self.x+1} de {len(self.secciones[self.y])}')
		else:
			message(f"{self.x+1} de {len(self.secciones[self.y])}")

	def script_reload(self, gesture):
		Thread(target=self.vstContent, daemon= True).start()
		message("Actualizando la base de datos, el proceso puede tardar algunos segundos")

	def script_close(self, gesture):
		self.switch = False
		message("Atajos desactivados")
		self.clearGestureBindings()
