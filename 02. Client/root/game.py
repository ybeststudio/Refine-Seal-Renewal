# GameWindow icinde ara:
		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg, 0, localeInfo.UI_OK)

# Altina ekle:
	def OpenRefineDialog(self, targetItemPos, nextGradeItemVnum, cost, prob, type=0):
		self.interface.OpenRefineDialog(targetItemPos, nextGradeItemVnum, cost, prob, type)

	def AppendMaterialToRefineDialog(self, vnum, count):
		self.interface.AppendMaterialToRefineDialog(vnum, count)


# GameWindow.__ServerCommand_Build icinde ara:
			})
		#PITTY_REFINE

# Altina ekle:
		serverCommandList["RefinePitty"] = self.RecvRefinePitty


# GameWindow icinde ara:
		self.interface.AskSafeboxPassword()
	#PITTY_REFINE

# Altina ekle:
	def RecvRefinePitty(self, itemVnum, pittyValue, pittyMax):
		self.interface.dlgRefineNew.SetPittyInfo(int(itemVnum), int(pittyValue), int(pittyMax))


# GameWindow.RefineSuceededMessage icinde ara:
	def RefineSuceededMessage(self):
		snd.PlaySound("sound/ui/make_soket.wav")

# Altina ekle:
		if app.ENABLE_REFINE_SEAL_RENEWAL and self.interface.dlgRefineNew and self.interface.dlgRefineNew.IsShow():
			self.interface.CheckRefineDialog(FALSE)
			return


# GameWindow.RefineSuceededMessage icinde ara:
		if app.ENABLE_AUTO_REFINE:

# Altina ekle:
			self.interface.CheckRefineDialog(FALSE)


# GameWindow.RefineFailedMessage icinde ara:
	def RefineFailedMessage(self):
		snd.PlaySound("sound/ui/jaeryun_fail.wav")

# Altina ekle:
		if app.ENABLE_REFINE_SEAL_RENEWAL and self.interface.dlgRefineNew and self.interface.dlgRefineNew.IsShow():
			self.interface.CheckRefineDialog(TRUE)
			return


# GameWindow.RefineFailedMessage icinde ara:
		if app.ENABLE_AUTO_REFINE:

# Altina ekle:
			self.interface.CheckRefineDialog(TRUE)

