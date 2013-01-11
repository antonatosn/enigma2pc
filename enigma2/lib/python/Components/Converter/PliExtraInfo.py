# shamelessly copied from pliExpertInfo (Vali, Mirakels, Littlesat)

from enigma import iServiceInformation, iPlayableService
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.config import config
from Tools.Transponder import ConvertToHumanReadable
from Tools.GetEcmInfo import GetEcmInfo
from Poll import Poll

def addspace(text):
	if text:
		text += " "
	return text

class PliExtraInfo(Poll, Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.type = type
		self.poll_interval = 1000
		self.poll_enabled = True
		self.caid_data = (
			( "0x100",  "0x1ff", "Seca",    "S" ),
			( "0x500",  "0x5ff", "Via",     "V" ),
			( "0x600",  "0x6ff", "Irdeto",  "I" ),
			( "0x900",  "0x9ff", "NDS",     "Nd"),
			( "0xb00",  "0xbff", "Conax",   "Co"),
			( "0xd00",  "0xdff", "CryptoW", "Cw"),
			("0x1700", "0x17ff", "Beta",    "B" ),
			("0x1800", "0x18ff", "Nagra",   "N" ),
			("0x2600", "0x2600", "Biss",    "Bi"),
			("0x4ae0", "0x4ae1", "Dre",     "D" )
		)
		self.ecmdata = GetEcmInfo()
		self.service = self.info = self.feinfo = self.feinfo = self.feraw = self.fedata = None

	def getCryptoInfo(self):
		if (self.info.getInfo(iServiceInformation.sIsCrypted) == 1):
			data = self.ecmdata.getEcmData()
			self.current_source = data[0]
			self.current_caid = data[1]
			self.current_provid = data[2]
			self.current_ecmpid = data[3]
		else:
			self.current_source = ""
			self.current_caid = "0"
			self.current_provid = "0"
			self.current_ecmpid = "0"

	def createCryptoBar(self):
		res = ""
		available_caids = self.info.getInfoObject(iServiceInformation.sCAIDs)

		for caid_entry in self.caid_data:
			if int(self.current_caid, 16) >= int(caid_entry[0], 16) and int(self.current_caid, 16) <= int(caid_entry[1], 16):
				color="\c0000??00"
			else:
				color = "\c007?7?7?"
				try:
					for caid in available_caids:
						if caid >= int(caid_entry[0], 16) and caid <= int(caid_entry[1], 16):
							color="\c00????00"
				except:
					pass

			if res: res += " "
			res += color + caid_entry[3]

		res += "\c00??????"
		return res

	def createCryptoSpecial(self):
		caid_name = "FTA"
		try:
			for caid_entry in self.caid_data:
				if int(self.current_caid, 16) >= int(caid_entry[0], 16) and int(self.current_caid, 16) <= int(caid_entry[1], 16):
					caid_name = caid_entry[2]
					break
			return caid_name + ":%04x:%04x:%04x:%04x" % (int(self.current_caid,16),int(self.current_provid,16),self.info.getInfo(iServiceInformation.sSID),int(self.current_ecmpid,16))
		except:
			pass
		return ""

	def createResolution(self):
		xres = self.info.getInfo(iServiceInformation.sVideoWidth)
		if xres == -1:
			return ""
		yres = self.info.getInfo(iServiceInformation.sVideoHeight)
		mode = ("i", "p", " ")[self.info.getInfo(iServiceInformation.sProgressive)]
		fps  = str((self.info.getInfo(iServiceInformation.sFrameRate) + 500) / 1000)
		return str(xres) + "x" + str(yres) + mode + fps

	def createVideoCodec(self):
		return ("MPEG2", "MPEG4", "MPEG1", "MPEG4-II", "VC1", "VC1-SM", "")[self.info.getInfo(iServiceInformation.sVideoType)]

	def createFrequency(self):
		frequency = self.fedata.get("frequency")
		if frequency:
			return str(frequency / 1000)
		return ""

	def createSymbolRate(self):
		symbolrate = self.fedata.get("symbol_rate")
		if symbolrate:
			return str(symbolrate / 1000)
		return ""

	def createPolarization(self):
		polarization = self.fedata.get("polarization_abbreviation")
		if polarization:
			return polarization
		return ""

	def createFEC(self):
		fec = self.fedata.get("fec_inner")
		if fec:
			return fec
		return ""

	def createModulation(self):
		modulation = self.fedata.get("modulation")
		if modulation:
			return modulation
		return ""

	def createTunerType(self):
		tunertype = self.feraw.get("tuner_type")
		if tunertype:
			return tunertype
		return ""

	def createTunerSystem(self):
		tunersystem = self.fedata.get("system")
		if tunersystem:
			return tunersystem
		return ""

	def createOrbPos(self):
		orbpos = self.feraw.get("orbital_position")
		if orbpos > 1800:
			return str((float(3600 - orbpos)) / 10.0) + "W"
		elif orbpos > 0:
			return str((float(orbpos)) / 10.0) + "E"
		return ""

	def createProviderName(self):
		return self.info.getInfoString(iServiceInformation.sProvider)

	@cached
	def getText(self):

		if not self.info:
			return ""

		if self.type == "CryptoBar":
			self.getCryptoInfo()
			return self.createCryptoBar()

		if self.type == "CryptoSpecial":
			self.getCryptoInfo()
			return self.createCryptoSpecial()

		if self.type == "ResolutionString":
			return self.createResolution()

		if self.type == "VideoCodec":
			return self.createVideoCodec()

		if self.fedata is None:
			return ""

		if self.type == "TransponderFrequency":
			return self.createFrequency()

		if self.type == "TransponderSymbolRate":
			return self.createSymbolRate()

		if self.type == "TransponderPolarization":
			return self.createPolarization()

		if self.type == "TransponderFEC":
			return self.createFEC()

		if self.type == "TransponderModulation":
			return self.createModulation()

		if self.type == "OrbitalPosition":
			return self.createOrbPos()

		if self.type == "TunerType":
			return self.createTunerType()

		if self.type == "TunerSystem":
			return self.createTunerSystem()

		if self.type == "All":
			self.getCryptoInfo()
			if config.usage.show_cryptoinfo.value:
				return addspace(self.createProviderName()) + addspace(self.createTunerSystem()) + addspace(self.createFrequency()) + addspace(self.createPolarization())\
				+ addspace(self.createSymbolRate()) + addspace(self.createFEC()) + addspace(self.createModulation()) + self.createOrbPos() + "\n"\
				+ addspace(self.createCryptoBar()) + addspace(self.createCryptoSpecial()) + "\n"\
				+ addspace(self.createVideoCodec()) + self.createResolution()

			else:

				return addspace(self.createProviderName()) + addspace(self.createTunerSystem()) + addspace(self.createFrequency()) + addspace(self.createPolarization())\
				+ addspace(self.createSymbolRate()) + addspace(self.createFEC()) + addspace(self.createModulation()) + self.createOrbPos() + "\n"\
				+ addspace(self.createCryptoBar()) + self.current_source + "\n"\
				+ addspace(self.createCryptoSpecial()) + addspace(self.createVideoCodec()) + self.createResolution()

		return _("invalid type")

	text = property(getText)

	@cached
	def getBool(self):

		if not self.info:
			return ""

		if self.type == "CryptoCaidSecaAvailable":
			request_caid = "S"
			request_selected = False
		elif self.type == "CryptoCaidViaAvailable":
			request_caid = "V"
			request_selected = False
		elif self.type == "CryptoCaidIrdetoAvailable":
			request_caid = "I"
			request_selected = False
		elif self.type == "CryptoCaidNDSAvailable":
			request_caid = "Nd"
			request_selected = False
		elif self.type == "CryptoCaidConaxAvailable":
			request_caid = "Co"
			request_selected = False
		elif self.type == "CryptoCaidCryptoWAvailable":
			request_caid = "Cw"
			request_selected = False
		elif self.type == "CryptoCaidBetaAvailable":
			request_caid = "B"
			request_selected = False
		elif self.type == "CryptoCaidNagraAvailable":
			request_caid = "N"
			request_selected = False
		elif self.type == "CryptoCaidBissAvailable":
			request_caid = "Bi"
			request_selected = False
		elif self.type == "CryptoCaidDreAvailable":
			request_caid = "D"
			request_selected = False
		elif self.type == "CryptoCaidSecaSelected":
			request_caid = "S"
			request_selected = True
		elif self.type == "CryptoCaidViaSelected":
			request_caid = "V"
			request_selected = True
		elif self.type == "CryptoCaidIrdetoSelected":
			request_caid = "I"
			request_selected = True
		elif self.type == "CryptoCaidNDSSelected":
			request_caid = "Nd"
			request_selected = True
		elif self.type == "CryptoCaidConaxSelected":
			request_caid = "Co"
			request_selected = True
		elif self.type == "CryptoCaidCryptoWSelected":
			request_caid = "Cw"
			request_selected = True
		elif self.type == "CryptoCaidBetaSelected":
			request_caid = "B"
			request_selected = True
		elif self.type == "CryptoCaidNagraSelected":
			request_caid = "N"
			request_selected = True
		elif self.type == "CryptoCaidBissSelected":
			request_caid = "Bi"
			request_selected = True
		elif self.type == "CryptoCaidDreSelected":
			request_caid = "D"
			request_selected = True
		else:
			return False

		if self.info.getInfo(iServiceInformation.sIsCrypted) != 1:
			return False

		data = self.ecmdata.getEcmData()

		if data is None:
			return False

		current_caid	= data[1]
		available_caids = self.info.getInfoObject(iServiceInformation.sCAIDs)

		for caid_entry in self.caid_data:
			if caid_entry[3] == request_caid:
				if(request_selected):
					if int(current_caid, 16) >= int(caid_entry[0], 16) and int(current_caid, 16) <= int(caid_entry[1], 16):
						return True
				else: # request available
					try:
						for caid in available_caids:
							if caid >= int(caid_entry[0], 16) and caid <= int(caid_entry[1], 16):
								return True
					except:
						pass

		return False

	boolean = property(getBool)

	def changed(self, what):
		if what[0] == self.CHANGED_POLL:
			Converter.changed(self, what)
		if what[0] == self.CHANGED_SPECIFIC:
			if what[1] == iPlayableService.evEnd:
				self.info = self.fedata = None
				Converter.changed(self, what)
			if what[1] in (iPlayableService.evStart, iPlayableService.evUpdatedInfo, iPlayableService.evVideoSizeChanged, iPlayableService.evVideoFramerateChanged, iPlayableService.evVideoProgressiveChanged):	
				self.service = self.source.service
				if self.service:
					self.info = self.service.info()
					if self.info and what[1] not in (iPlayableService.evVideoSizeChanged, iPlayableService.evVideoFramerateChanged, iPlayableService.evVideoProgressiveChanged):
						self.feinfo = self.service.frontendInfo()
						if self.feinfo:
							self.feraw = self.feinfo.getAll(False)
							if self.feraw:
								self.fedata = ConvertToHumanReadable(self.feraw)
					Converter.changed(self, what)			

