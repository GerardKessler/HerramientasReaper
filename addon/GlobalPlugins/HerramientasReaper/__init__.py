# -*- coding: utf-8 -*-
# Copyright (C) 2021 Gerardo Kessler <ReaperYOtrasYerbas@gmail.com>
# This file is covered by the GNU General Public License.
# Uso de la librería bs4 basada en el complemento DLEChecker de Antonio Cascales.

import wx
import gui
import globalPluginHandler
import core
import globalVars
from ui import message, browseableMessage
import api
import controlTypes
from keyboardHandler import KeyboardInputGesture as kb
from scriptHandler import script, getLastScriptRepeatCount
from urllib import request, parse
from re import findall
from time import sleep
import winUser
from threading import Thread
import webbrowser
from nvwave import playWaveFile
from keyboardHandler import KeyboardInputGesture
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
	del sys.modules['html']
except:
	pass

from bs4 import BeautifulSoup
import string

SOUNDS= os.path.join(os.path.dirname(__file__), 'sounds')

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		self.sections= ['Reaper y otras yerbas', 'Descargas', 'AudioTools', 'AudioZ', 'Loop Torrent', 'Plugin Crack', 'Reaper en español (YouTube)', 'Reaper en español, tutoriales y utilidades (YouTube)']
		self.index= [0, 0, 0, 0, 0, 0, 0, 0]
		self.secciones= None
		self.x= 0
		self.y=0
		self.switch= False
		self.tutoriales= None
		self.descargas= None
		self.audiotools= None
		self.audioz= None
		self.looptorrent= None
		self.plugincrack= None
		core.postNvdaStartup.register(self.startScrap)

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		try:
			if api.getForegroundObject().windowText == 'Nexus (x64 bridged)':
				clsList.insert(0, Nexus)
		except:
			pass

	def startScrap(self):
		Thread(target=self.reaper, daemon= True).start()
		Thread(target=self.vstContent, daemon= True).start()
		Thread(target=self.channels, daemon= True).start()

	def getContent(self, url):
		try:
			contenido= request.Request(url, data=None, headers={'User-Agent': 'Mozilla/5.0'})
			html= request.urlopen(contenido)
			data= html.read().decode('utf-8')
			return data
		except:
			return None

	def scrap(self, url, tag, pattern= None):
		datos= self.getContent(url)
		bs= BeautifulSoup(datos, 'html.parser')
		if pattern == None:
			return bs.find_all(tag)
		else:
			return bs.find_all(tag, pattern)

	def reaper(self):
		sonido= self.scrap("http://gera.ar/sonido", "a", {"class": "addon"})
		self.tutoriales= [(item.text, f'http://gera.ar/sonido/{item["href"]}') for item in sonido]
		descargas= self.scrap("http://gera.ar/sonido/descargas.php", "a", {"class": "addon"})
		self.descargas= [(item.text, item['href']) for item in descargas]

	def vstContent(self):
		sleep(3)
		try:
			audiotools= self.scrap('https://audiotools.in/', 'h2')
			self.audiotools= [(item.text, item.a['href']) for item in audiotools]
			sleep(2)
		except:
			pass
		try:
			audioz= self.scrap('https://audioz.download/', 'h2')
			self.audioz= [(item.text, item.parent['href']) for item in audioz]
			sleep(2)
		except:
			pass
		try:
			looptorrent= self.scrap('https://looptorrent.net', 'h3')
			self.looptorrent= [(item.text, item.a['href']) for item in looptorrent]
			sleep(2)
		except:
			pass
		try:
			plugincrack= self.scrap('https://plugincrack.com/vst/', 'h2')
			self.plugincrack= [(item.text, item.a['href']) for item in plugincrack]
		except:
			pass

	def channels(self):
		sleep(11)
		regex= r'"accessibilityData":\{"label":"([^"]*)"\}\}\}\,"descriptionSnippet":\{"runs":\[\{"text":"([^"]+)"\}\]\}\,"publishedTimeText":\{"simpleText":"[^"]*"\}\,"lengthText":\{"accessibility":\{"accessibilityData":\{"label":"[^"]*"\}\}\,"simpleText":"[^"]*"\}\,"viewCountText":\{"simpleText":"[^"]*"\}\,"navigationEndpoint":\{"clickTrackingParams":"[^"]*","commandMetadata":\{"webCommandMetadata":\{"url":"(\/watch\?v\=[^"]+)"'
		reaper_es= self.getContent('https://www.youtube.com/@reaperenespanol/videos')
		re_data= findall(regex, reaper_es)
		reaper_es_list= [(item[0], f'https://youtube.com{item[2]}', item[1]) for item in re_data]
		sleep(4)
		javier_robledo= self.getContent('https://www.youtube.com/@Reaper_con_Javier_Robledo/videos')
		jr_data= findall(regex, javier_robledo)
		javier_robledo_list= [(item[0], f'https://youtube.com{item[2]}', item[1]) for item in jr_data]
		self.secciones= [self.tutoriales, self.descargas, self.audiotools, self.audioz, self.looptorrent, self.plugincrack, reaper_es_list, javier_robledo_list]

	@script(
		category="HerramientasReaper",
		description="Activa y desactiva los comandos del complemento"
	)
	def script_toggle(self, gesture):
		if self.switch == False:
			self.switch = True
			if not self.secciones:
				Thread(target=self.reaper, daemon= True).start()
				Thread(target=self.vstContent, daemon= True).start()
				Thread(target=self.channels, daemon= True).start()
			message('Cargando la interfaz, por favor espere...' if not self.secciones else 'Atajos activados')
			self.bindGestures({
				"kb:downArrow":"nextItem",
				"kb:upArrow":"previousItem",
				"kb:rightArrow":"nextSection",
				"kb:leftArrow":"previousSection",
				"kb:enter":"open",
				"kb:home":"firstItem",
				"kb:end":"positionAnnounce",
				"kb:f5":"reload",
				"kb:b":"search",
				"kb:escape":"close"
			})
		else:
			self.finish(True)

	def finish(self, msg= False):
		self.switch = False
		if msg: message("Atajos desactivados")
		self.clearGestureBindings()

	def script_nextItem(self, gesture):
		if not self.secciones or not self.secciones[self.y]:
			message('Sin datos')
			return
		self.x = self.x + 1
		if self.x < len(self.secciones[self.y]):
			message(self.secciones[self.y][self.x][0])
		else:
			self.x = 0
			message(self.secciones[self.y][self.x][0])

	def script_previousItem(self, gesture):
		if not self.secciones or not self.secciones[self.y]:
			message('Sin datos')
			return
		self.x = self.x - 1
		if self.x >= 0:
			message(self.secciones[self.y][self.x][0])
		else:
			self.x = len(self.secciones[self.y]) - 1
			message(self.secciones[self.y][self.x][0])

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
		webbrowser.open_new_tab(self.secciones[self.y][self.x][1])
		self.finish()

	def script_firstItem(self, gesture):
		self.x = 0
		message(self.secciones[self.y][self.x][0])

	def script_positionAnnounce(self, gesture):
		if getLastScriptRepeatCount() == 1:
			message(self.secciones[self.y][self.x][0])
		else:
			message(f"{self.x+1} de {len(self.secciones[self.y])}")

	def script_reload(self, gesture):
		Thread(target=self.vstContent, daemon= True).start()
		Thread(target=self.channels, daemon= True).start()
		message("Actualizando los contenidos, el proceso puede tardar algunos segundos")

	def script_close(self, gesture):
		self.finish(True)

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
		self.finish()
		self.dlg = Search(gui.mainFrame, "Cuadro de búsqueda", "Ingrese los términos de búsqueda y pulse intro:", self.secciones)
		gui.mainFrame.prePopup()
		self.dlg.Show()

class Search(wx.Dialog):
	def __init__(self, parent, titulo, mensaje, secciones):
		# Translators: Título de la ventana
		super(Search, self).__init__(parent, -1, title=titulo)
		self.secciones= secciones
		self.results= """
			<!doctype html>
			<html lang="es">
			<head>
			<meta charset="UTF-8">
			<title>Resultados</title>
			</head>
			<body>
		"""
		self.r= 0
		self.Panel= wx.Panel(self)
		wx.StaticText(self.Panel, wx.ID_ANY, mensaje)
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
		textSearch = self.search.GetValue()
		for section in self.secciones:
			# for item in section:
				if textSearch.lower() in item[0].lower():
					self.results += f'<a href="{item[1]}">{item[0]}</a><br>\n'
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

class Nexus():
	def initOverlayClass(self):
		self.folders= None
		self.categories= None
		self.presets= None
		self.f= 0
		self.c= 0
		self.p= 0
		self.reverb= None
		self.delay= None
		self.preset_name= None
		self.preset_name_temp= None
		self.bindGestures({
			"kb:alt+downArrow":"next",
			"kb:alt+upArrow":"previous",
			"kb:alt+leftArrow":"preview",
			"kb:alt+rightArrow":"active",
			"kb:alt+home":"first",
			"kb:alt+end":"last",
			"kb:leftArrow":"presetName",
			"kb:rightArrow":"presetActive",
			"kb:alt+r":"reverbToggle",
			"kb:control+r":"reverbType",
			"kb:alt+d":"delayToggle"
		})

	def assignElements(self):
		message('Escaneando los efectos...')
		fg= api.getForegroundObject()
		for child in fg.firstChild.recursiveDescendants:
			try:
				if self.preset_name and self.reverb and self.delay: break
				elif child.UIAAutomationId == 'preset name.preset.header.<empty>.<empty>.<empty>.<empty>':
					self.preset_name= child
				elif child.UIAAutomationId == 'main reverb.<empty>.<empty>.<empty>.<empty>':
					self.reverb= child
				elif child.UIAAutomationId == 'main delay.<empty>.<empty>.<empty>.<empty>':
					self.delay= child
			except:
				pass

	def getLists(self, focus):
		if focus.name == 'presets':
			self.presets= [preset for preset in focus.children if not preset.name in ('-- Uncategorized', '')]
		elif focus.name == 'categories':
			self.categories= [category for category in focus.children if category.name != '']
		elif focus.name == 'folders':
			self.folders= [folder for folder in focus.children if folder.name != '']

	def script_next(self, gesture):
		try:
			focus= api.getFocusObject()
			if focus.name == 'presets':
				if not self.presets: self.getLists(focus)
				self.p = self.p+1
				try:
					message(self.presets[self.p].name)
				except:
					self.p= 0
					message(self.presets[self.p].name)
			elif focus.name == 'categories':
				if not self.categories: self.getLists(focus)
				self.c = self.c+1
				try:
					message(self.categories[self.c].name)
				except:
					self.c= 0
					message(self.categories[self.c].name)
			elif focus.name == 'folders':
				if not self.folders: self.getLists(focus)
				self.f = self.f+1
				try:
					message(self.folders[self.f].name)
				except:
					self.f= 0
					message(self.folders[self.f].name)
		except:
			pass

	def script_previous(self, gesture):
		try:
			focus= api.getFocusObject()
			if focus.name == 'presets':
				if not self.presets: self.getLists(focus)
				self.p = self.p-1
				try:
					message(self.presets[self.p].name)
				except:
					self.p= len(self.presets)-1
					message(self.presets[self.p].name)
			elif focus.name == 'categories':
				if not self.categories: self.getLists(focus)
				self.c = self.c-1
				try:
					message(self.categories[self.c].name)
				except:
					self.c= len(self.categories)-1
					message(self.categories[self.c].name)
			elif focus.name == 'folders':
				if not self.folders: self.getLists(focus)
				self.f = self.f-1
				try:
					message(self.folders[self.f].name)
				except:
					self.f= len(self.folders)-1
					message(self.folders[self.f].name)
		except:
			pass

	def script_preview(self, gesture):
		focus= api.getFocusObject()
		if focus.name == 'presets':
			obj= self.presets[self.p]
			obj.setFocus()
			api.moveMouseToNVDAObject(obj)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
			focus.setFocus()
		else:
			gesture.send()

	def script_active(self, gesture):
		focus= api.getFocusObject()
		if focus.name == 'presets':
			obj= self.presets[self.p]
		elif focus.name == 'categories':
			obj= self.categories[self.c]
		elif focus.name == 'folders':
			obj= self.folders[self.f]
		obj.setFocus()
		api.moveMouseToNVDAObject(obj)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
		focus.setFocus()
		playWaveFile(os.path.join(SOUNDS, 'click.wav'))

	def script_first(self, gesture):
		focus= api.getFocusObject()
		try:
			if focus.name == 'presets':
				self.p= 0
				message(self.presets[self.p].name)
			elif focus.name == 'categories':
				self.c= 0
				message(self.categories[self.c].name)
			elif focus.name == 'folders':
				self.f= 0
				message(self.folders[self.f].name)
		except:
			pass

	def script_last(self, gesture):
		focus= api.getFocusObject()
		try:
			if focus.name == 'presets':
				self.p= len(self.presets)-1
				message(self.presets[self.p].name)
			elif focus.name == 'categories':
				self.c= len(self.categories)-1
				message(self.categories[self.c].name)
			elif focus.name == 'folders':
				self.f= len(self.presets)-1
				message(self.folders[self.f].name)
		except:
			pass

	def verifyElements(self, gesture):
		if api.getFocusObject().name != 'presets':
			gesture.send()
			return
		if not self.preset_name:
			self.assignElements()

	def script_presetActive(self, gesture):
		gesture.send()
		playWaveFile(os.path.join(SOUNDS, 'click.wav'))
		Thread(target=self.assignPreset, daemon= True).start()

	def assignPreset(self):
		if not self.presets or not self.preset_name:
			self.getLists(api.getFocusObject())
			self.assignElements()
		preset_name= self.preset_name.description.split('\n')[1]
		for i in range(30):
			sleep(0.1)
			if preset_name != self.preset_name.description.split('\n')[1]:
				self.p= next((i for i, obj in enumerate(self.presets) if self.preset_name.description.split('\n')[1] in obj.name), None)
				message(self.preset_name.description.split('\n')[1])
				break

	def script_presetName(self, gesture):
		self.verifyElements(gesture)
		if self.preset_name:
			message(self.preset_name.description.split('\n')[1])

	def script_reverbToggle(self, gesture):
		self.verifyElements(gesture)
		focus= api.getFocusObject()
		if self.reverb:
			self.reverb.children[0].doAction()
			focus.setFocus()
			if controlTypes.State.PRESSED in self.reverb.children[0].states:
				message('Reverb activada')
			else:
				message('Reverb desactivada')

	def script_reverbType(self, gesture):
		self.verifyElements(gesture)
		focus= api.getFocusObject()
		if self.reverb:
			self.reverb.children[2].doAction()

	def script_delayToggle(self, gesture):
		self.verifyElements(gesture)
		focus= api.getFocusObject()
		if self.delay:
			self.delay.children[0].doAction()
			focus.setFocus()
			if controlTypes.State.PRESSED in self.delay.children[0].states:
				message('Delay activado')
			else:
				message('Delay desactivado')
