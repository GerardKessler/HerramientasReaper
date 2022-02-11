# -*- coding: utf-8 -*-
# Copyright (C) 2021 Gerardo Kessler <ReaperYOtrasYerbas@gmail.com>
# This file is covered by the GNU General Public License.
# Utilización de la librería bs4 basada en el complemento DLEChecker de Antonio Cascales.

import wx
import gui
import globalPluginHandler
import core
import globalVars
from ui import message, browseableMessage
import api
from scriptHandler import script, getLastScriptRepeatCount
from urllib import request, parse
from time import sleep
from threading import Thread
import webbrowser
from keyboardHandler import KeyboardInputGesture
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
		self.sections = ["Reaper y otras yerbas", "Reaper accesible español", "Descargas", "AudioTools", "AudioZ", "LoopTorrent"]
		self.index = [0, 0, 0, 0, 0 ,0]
		self.secciones = None
		self.x = 0
		self.y=0
		self.switch = False
		self.tutoriales = None
		self.rae = None
		self.descargas = None
		self.audiotools = None
		self.audioz = None
		self.looptorrent = None
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
		self.tutoriales = self.scrap("http://gera.ar/sonido", "a", {"class": "addon"})
		self.rae = self.scrap("http://gera.ar/sonido/files/rae.html", "a", {"class": "addon"})
		self.descargas = self.scrap("http://gera.ar/sonido/descargas.php", "a", {"class": "addon"})

	def vstContent(self):
		self.audiotools = self.scrap("https://audiotools.in/", "h2")
		self.audioz = self.scrap("https://audioz.download/", "h2")
		self.looptorrent = self.scrap("https://looptorrent.net", "h3")
		self.secciones = [self.tutoriales, self.rae, self.descargas, self.audiotools, self.audioz, self.looptorrent]

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
						"kb:b":"search",
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
			message(self.secciones[self.y][self.x].string)
		else:
			self.x = 0
			message(self.secciones[self.y][self.x].string)

	def script_previousItem(self, gesture):
		self.x = self.x - 1
		if self.x >= 0:
			message(self.secciones[self.y][self.x].string)
		else:
			self.x = len(self.secciones[self.y]) - 1
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
			webbrowser.open(f"http://gera.ar/sonido/{item['href']}")
		elif self.y == 1 or self.y == 2:
			webbrowser.open(item['href'])
		elif self.y == 3 or self.y == 5:
			webbrowser.open(item.a['href'])
		elif self.y == 4:
			webbrowser.open(item.parent['href'])
		self.switch = False
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)

	def script_firstItem(self, gesture):
		self.x = 0
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

	@script(
		category="Teclas personalizadas",
		description="Pulsa la tecla aplicaciones"
	)
	def script_applications(self, gesture):
		KeyboardInputGesture.fromName("applications").send()

	@script(
		category="Teclas personalizadas",
		description="Pulsa la tecla Avance de página"
	)
	def script_pageUp(self, gesture):
		KeyboardInputGesture.fromName("pageup").send()

	@script(
		category="Teclas personalizadas",
		description="Pulsa la tecla Retroceso de página"
	)
	def script_pageDown(self, gesture):
		KeyboardInputGesture.fromName("pagedown").send()

	@script(
		category="Teclas personalizadas",
		description="Pulsa la tecla inicio"
	)
	def script_home(self, gesture):
		KeyboardInputGesture.fromName("home").send()
		
	@script(
		category="Teclas personalizadas",
		description="Pulsa la tecla fin"
	)
	def script_end(self, gesture):
		KeyboardInputGesture.fromName("end").send()

	@script(
		category="Teclas personalizadas",
		description="Pulsa la tecla volúmen arriba"
	)
	def script_volumeUp(self, gesture):
		KeyboardInputGesture.fromName("volumeup").send()

	@script(
		category="Teclas personalizadas",
		description="Pulsa la tecla volúmen abajo"
	)
	def script_volumeDown(self, gesture):
		KeyboardInputGesture.fromName("volumedown").send()

	def script_search(self, gesture):
		self.switch = False
		self.clearGestureBindings()
		self.dlg = Search(gui.mainFrame, "Cuadro de búsqueda", "Ingrese los términos de búsqueda y pulse intro:", self.tutoriales, self.rae)
		gui.mainFrame.prePopup()
		self.dlg.Show()

class Search(wx.Dialog):
	def __init__(self, parent, titulo, mensaje, tutoriales, rae):
		# Translators: Título de la ventana
		super(Search, self).__init__(parent, -1, title=titulo)
		self.rae = rae
		self.tutoriales = tutoriales
		self.results = """
			<!doctype html>
			<html lang="es">
			<head>
			<meta charset="UTF-8">
			<title>Resultados</title>
			</head>
			<body>
		"""
		self.r = 0
		self.Panel = wx.Panel(self)
		label = wx.StaticText(self.Panel, wx.ID_ANY, mensaje)
		self.search = wx.TextCtrl(self.Panel,wx.ID_ANY,style=wx.TE_PROCESS_ENTER)
		self.buscarBTN = wx.Button(self.Panel, wx.ID_ANY, "&Buscar")
		self.cerrarBTN = wx.Button(self.Panel, wx.ID_CANCEL, "&Cerrar")
		self.search.Bind(wx.EVT_CONTEXT_MENU, self.onPass)
		self.search.Bind(wx.EVT_TEXT_ENTER, self.onBuscar)
		self.buscarBTN.Bind(wx.EVT_BUTTON, self.onBuscar)
		self.Bind(wx.EVT_ACTIVATE, self.onSalir)
		self.Bind(wx.EVT_BUTTON, self.onSalir, id=wx.ID_CANCEL)

	def onPass(self, event):
		pass

	def onBuscar(self, event):
		articles = self.tutoriales + self.rae
		textSearch = self.search.GetValue()
		for article in articles:
			title = article.string
			if textSearch.lower() in title.lower():
				if "novedades.php" in article["href"]:
					self.results += f'<a href="http://gera.ar/sonido/{article["href"]}">{article.string}</a><br>\n'
				else:
					self.results += f'<a href="{article["href"]}">{article.string}</a><br>'
		if "<a href=" in self.results:
			self.results += "</body></html>"
			with open(f"{globalVars.appArgs.configPath}/addons/HerramientasReaper/GlobalPlugins/HerramientasReaper/resultados.html", "w", encoding="utf-8") as file:
				file.write(self.results)
			webbrowser.open(f"file://{globalVars.appArgs.configPath}/addons/HerramientasReaper/GlobalPlugins/HerramientasReaper/resultados.html", new=2)
		else:
			browseableMessage("😟\nNo se han encontrado resultados con los términos de búsqueda ingresados")
		self.Close()

	def onSalir(self, event):
		if event.GetEventType() == 10012:
			self.Destroy()
			gui.mainFrame.postPopup()
		elif event.GetActive() == False:
			self.Destroy()
			gui.mainFrame.postPopup()
		event.Skip()
