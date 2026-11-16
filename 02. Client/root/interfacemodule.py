# Ara:
import uiCommon
import uiRefine

# Altina ekle:
if app.ENABLE_REFINE_SEAL_RENEWAL:
	import uiRefineRenewal


# Interface.__init__ icinde ara:
			self.privateShopBuilder = None
			self.wndSafebox = None

# Altina ekle:
			self.dlgRefineNew = None


# Interface icinde ara:
		return TRUE
	if app.ENABLE_AUTO_REFINE:

# Altina ekle:
		def CheckRefineDialog(self, isFail):
			self.dlgRefineNew.CheckRefine(isFail)


# Interface.__MakeDialogs icinde ara:
			self.privateShopBuilder.BindInterface(self)
		self.privateShopBuilder.Hide()

# Altina ekle:
		if app.ENABLE_REFINE_SEAL_RENEWAL:
			self.dlgRefineNew = uiRefineRenewal.RefineDialogRenewal()
			self.dlgRefineNew.SetInven(self.wndInventory)
			self.dlgRefineNew.BindInterface(self)
		else:
			self.dlgRefineNew = uiRefine.RefineDialogNew()
			if app.ENABLE_SLOT_MARKING_SYSTEM:
				self.dlgRefineNew.SetInven(self.wndInventory)

			if constInfo.SHOW_REFINE_ITEM_DESC:
				self.dlgRefineNew.BindInterface(self)

		self.dlgRefineNew.Hide()


# Interface.Close icinde ara:
		if self.privateShopBuilder:
			self.privateShopBuilder.Destroy()

# Altina ekle:
		if self.dlgRefineNew:
			self.dlgRefineNew.Destroy()


# Interface.Close icinde ara:
		del self.wndItemFinder
		del self.wndChatLog

# Altina ekle:
		del self.dlgRefineNew


# Interface icinde ara:
		self.dlgSystem.OnChangePKMode()
	## Refine

# Altina ekle:
	def OpenRefineDialog(self, targetItemPos, nextGradeItemVnum, cost, prob, type):
		self.dlgRefineNew.Open(targetItemPos, nextGradeItemVnum, cost, prob, type)

	def AppendMaterialToRefineDialog(self, vnum, count):
		self.dlgRefineNew.AppendMaterial(vnum, count)


# Interface.AuraWindowOpen icinde ara:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.ACCE_NOT_OPEN_PRIVATE_SHOP)
				return

# Altina ekle:
			if self.dlgRefineNew and self.dlgRefineNew.IsShow():
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.ACCE_NOT_OPEN_REFINE)
				return

