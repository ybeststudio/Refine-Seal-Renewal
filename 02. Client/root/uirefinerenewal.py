#
# File Name : uirefinerenewal.py
# Author    : BestStudio
# Version   : 1.0
# Date      : 2026-11-15
#
#   material_bg (3,216): 5 slot_32x32 frames at x 24 + 45 i, y 223, unused ones = locked_slot (+2,+2),
#   bottom_bg (4,264), pity_bg (9,268) + pity_icon (16,277), two seal rows: checkbox (13,316 / 361),
#   slot_material (32,302 / 347), texts x 77; bg_green (9,392) failure warning, bg_green (9,419) cost,
#   button_large (28,451) / (138,451).
import app
import net
import player
import item
import chat
import ui
import uiCommon
import uiToolTip
import localeInfo
import uiScriptLocale
import constInfo
import wndMgr

PATH = "d:/ymir work/ui/game/refine2/"
COMMON = "d:/ymir work/ui/game/common/"

# sit at + (3, 5) (header 5,29 / item_bg 7,57 / material_bg 6,221 / bottom 7,269 / slots 27+45i,228)
BASE_WIDTH = 266
X0, Y0 = 3, 5
WIDTH, HEIGHT = 272, 498
MATERIAL_MAX = 5
SEAL_BONUS = (5, 10)

COLOR_LABEL = 0xffcabdab
COLOR_SEAL_CHANCE = 0xffc7c7c7
COLOR_CHANCE = 0xffb0f2b6
COLOR_WARNING = 0xfff08080
COLOR_COST = 0xffc79e65
COLOR_LACK = 0xffe57875
COLOR_TITLE = 0xfff1e6c0
COLOR_LEVEL = 0xffc1c1c1

RESULT_BOX = (67, 54, 190, 130)
RESULT_CENTER_X = 67 + 190 / 2 - 1
RESULT_STAT_ROWS = 7

ENERGY_CRYSTAL_SCROLLS = (51050, 51051)

REFINE_TYPE_NORMAL, REFINE_TYPE_SCROLL, REFINE_TYPE_HYUNIRON, REFINE_TYPE_MONEY_ONLY, REFINE_TYPE_MUSIN, REFINE_TYPE_BDRAGON = range(6)


def GetRefineSealVnums(itemVnum):
	if not itemVnum:
		return (0, 0)
	item.SelectItem(itemVnum)
	level = 0
	for i in xrange(item.LIMIT_MAX_NUM):
		(limitType, limitValue) = item.GetLimit(i)
		if limitType == item.LIMIT_LEVEL:
			level = limitValue
	if 0 <= level <= 105:
		return (25049, 25050)
	if 106 <= level <= 110:
		return (25051, 25052)
	return (0, 0)


class _LineRecorder(uiToolTip.ItemToolTip):
	def __init__(self):
		uiToolTip.ItemToolTip.__init__(self)
		self.lines = []

	def AppendTextLine(self, text, *args, **kwargs):
		color = args[0] if args else kwargs.get("color", self.FONT_COLOR)
		self.lines.append((text, color))
		return uiToolTip.ItemToolTip.AppendTextLine(self, text, *args, **kwargs)


class _ResultPopup(ui.Board):
	WIDTH, HEIGHT = 280, 105

	def __init__(self):
		ui.Board.__init__(self)
		self.AddFlag("float")
		self.SetSize(self.WIDTH, self.HEIGHT)
		self.onAccept = None
		inner = ui.ThinBoardNew()
		inner.SetParent(self)
		inner.SetPosition(8, 8)
		inner.SetSize(self.WIDTH - 17, self.HEIGHT - 17)
		inner.Show()
		self.inner = inner
		self.message = ui.TextLine()
		self.message.SetParent(self)
		self.message.SetHorizontalAlignCenter()
		self.message.SetVerticalAlignCenter()
		self.message.SetPosition(self.WIDTH / 2, 38)
		self.message.SetPackedFontColor(COLOR_LABEL)
		self.message.Show()
		self.acceptButton = ui.Button()
		self.acceptButton.SetParent(self)
		self.acceptButton.SetUpVisual(COMMON + "button_accept_norm.png")
		self.acceptButton.SetOverVisual(COMMON + "button_accept_hover.png")
		self.acceptButton.SetDownVisual(COMMON + "button_accept_down.png")
		self.acceptButton.SetPosition((self.WIDTH - self.acceptButton.GetWidth()) / 2, 63)
		self.acceptButton.SetEvent(ui.__mem_func__(self.__Accept))
		self.acceptButton.Show()
		self.Hide()

	def __del__(self):
		ui.Board.__del__(self)

	def Open(self, text, onAccept):
		self.message.SetText(text)
		width = max(230, self.message.GetTextSize()[0] + 30)
		self.SetSize(width, self.HEIGHT)
		self.inner.SetSize(width - 17, self.HEIGHT - 17)
		self.message.SetPosition(width / 2, 38)
		self.acceptButton.SetPosition((width - self.acceptButton.GetWidth()) / 2, 63)
		self.onAccept = onAccept
		self.Show()
		self.SetTop()

	def __Accept(self):
		onAccept = self.onAccept
		self.Close()
		if onAccept:
			onAccept()

	def Close(self):
		self.onAccept = None
		self.Hide()

	def OnPressEscapeKey(self):
		self.__Accept()
		return True


class RefineDialogRenewal(ui.BoardWithTitleBar):
	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		self.interface = None
		self.inven = None
		self.dlgQuestion = None
		self.targetItemPos = 0
		self.vnum = 0
		self.cost = 0
		self.percentage = 0
		self.type = 0
		self.materials = []
		self.sealVnums = (0, 0)
		self.sealStates = [0, 0]
		self.pittyCurrent = 0
		self.pittyMax = 0
		self.resultPopup = None
		self.autoAsk = False
		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetSize(WIDTH, HEIGHT)
		self.SetTitleName(localeInfo.REFINE_RENEWAL_TITLE)
		self.SetCloseEvent(ui.__mem_func__(self.CancelRefine))
		self.SetPosition(wndMgr.GetScreenWidth() - 700, 70)
		self.__Build()
		self.Hide()

	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	# ----------------------------------------------------------------- widgets
	def __Image(self, x, y, path, pick = False):
		image = ui.ImageBox()
		image.SetParent(self)
		image.LoadImage(path)
		image.SetPosition(x + X0, y + Y0)
		if not pick:
			image.AddFlag("not_pick")
		image.Show()
		return image

	def __Text(self, x, y, color = COLOR_LABEL, center = True):
		text = ui.TextLine()
		text.SetParent(self)
		text.SetPackedFontColor(color)
		if center:
			text.SetHorizontalAlignCenter()
		text.SetVerticalAlignCenter()
		text.SetPosition(x + X0, y + Y0)
		text.AddFlag("not_pick")
		text.Show()
		return text

	def __Bar(self, x, y, w, h, color):
		bar = ui.Bar()
		bar.SetParent(self)
		bar.SetPosition(x + X0, y + Y0)
		bar.SetSize(w, h)
		bar.SetColor(color)
		bar.AddFlag("not_pick")
		bar.Show()
		return bar

	def __Button(self, x, y, text):
		button = ui.Button()
		button.SetParent(self)
		button.SetPosition(x + X0, y + Y0)
		button.SetUpVisual(COMMON + "button_large_normal.png")
		button.SetOverVisual(COMMON + "button_large_hover.png")
		button.SetDownVisual(COMMON + "button_large_down.png")
		button.SetText(text)
		button.Show()
		return button

	def __Build(self):
		self.keep = []
		keep = self.keep.append

		# ---- result
		keep(self.__Image(2, 24, PATH + "title_bg.png"))
		self.resultTitle = self.__Text(BASE_WIDTH / 2, 37)
		self.resultTitle.SetText(localeInfo.REFINE_RENEWAL_RESULT)
		keep(self.__Image(4, 52, PATH + "bg_item.png"))
		keep(self.__Image(16, 66, PATH + "slot_item.png"))

		self.itemIcon = ui.ImageBox()
		self.itemIcon.SetParent(self)
		self.itemIcon.SetPosition(20 + X0, 71 + Y0)
		self.itemIcon.SetEvent(ui.__mem_func__(self.__OverInTarget), "mouse_over_in")
		self.itemIcon.SetEvent(ui.__mem_func__(self.__OverOut), "mouse_over_out")
		self.itemIcon.Show()

		(bx, by, bw, bh) = RESULT_BOX
		for (inset, color) in ((0, 0xff000000), (1, 0xff756556), (2, 0xff2a2827), (3, 0xff222120), (4, 0xff131110), (5, 0xff0c0a08)):
			keep(self.__Bar(bx + inset, by + inset, bw - inset * 2, bh - inset * 2, color))
		self.resultName = self.__Text(RESULT_CENTER_X, 67, COLOR_TITLE)
		self.resultLevel = self.__Text(RESULT_CENTER_X, 83, COLOR_LEVEL)
		self.resultLines = [self.__Text(RESULT_CENTER_X, 100 + 12 * i) for i in xrange(RESULT_STAT_ROWS)]

		# ---- requirements
		keep(self.__Image(2, 188, PATH + "title_bg.png"))
		self.requirementTitle = self.__Text(BASE_WIDTH / 2, 201)
		self.requirementTitle.SetText(localeInfo.REFINE_RENEWAL_REQUIREMENTS)
		keep(self.__Image(3, 216, PATH + "material_bg.png"))
		self.materialFrames, self.materialLocks = [], []
		for i in xrange(MATERIAL_MAX):
			x = 24 + 45 * i
			self.materialFrames.append(self.__Image(x, 223, COMMON + "slots/slot_32x32.png"))
			self.materialLocks.append(self.__Image(x + 2, 225, COMMON + "slots/locked_slot.png"))
		self.materialSlot = ui.SlotWindow()
		self.materialSlot.SetParent(self)
		self.materialSlot.SetPosition(24 + X0, 223 + Y0)
		self.materialSlot.SetSize(45 * (MATERIAL_MAX - 1) + 32, 32)
		for i in xrange(MATERIAL_MAX):
			self.materialSlot.AppendSlot(i, 45 * i, 0, 32, 32)
		self.materialSlot.SetOverInItemEvent(ui.__mem_func__(self.__OverInMaterial))
		self.materialSlot.SetOverOutItemEvent(ui.__mem_func__(self.__OverOut))
		self.materialSlot.Show()

		keep(self.__Image(4, 264, PATH + "bottom_bg.png"))

		# ---- 100 % (pity) line
		keep(self.__Image(9, 268, PATH + "pity_bg.png"))
		keep(self.__Image(16, 277, PATH + "pity_icon.png"))
		self.pityText = self.__Text(147, 281, COLOR_CHANCE)

		# ---- seals
		self.sealChecks, self.sealIcons, self.sealNames, self.sealChances = [], [], [], []
		for i in xrange(2):
			y = 45 * i
			check = ui.Button()
			check.SetParent(self)
			check.SetPosition(13 + X0, 316 + y + Y0)
			check.SetEvent(ui.__mem_func__(self.__ToggleSeal), i)
			check.Show()
			self.sealChecks.append(check)
			keep(self.__Image(32, 302 + y, PATH + "slot_material.png"))
			icon = ui.ImageBox()
			icon.SetParent(self)
			icon.SetPosition(36 + X0, 307 + y + Y0)
			icon.SetEvent(ui.__mem_func__(self.__OverInSeal), "mouse_over_in", i)
			icon.SetEvent(ui.__mem_func__(self.__OverOut), "mouse_over_out")
			icon.SetEvent(ui.__mem_func__(self.__ClickSealIcon), "mouse_click", i)
			icon.Show()
			self.sealIcons.append(icon)
			self.sealNames.append(self.__Text(77, 313 + y, COLOR_LABEL, False))
			chance = self.__Text(77, 327 + y, COLOR_SEAL_CHANCE, False)
			chance.SetText(localeInfo.REFINE_RENEWAL_SEAL_CHANCE.format(SEAL_BONUS[i]))
			self.sealChances.append(chance)

		# ---- failure warning / cost
		self.warningBar = self.__Image(9, 392, PATH + "bg_green.png")
		self.warningText = self.__Text(BASE_WIDTH / 2 + 1, 403, COLOR_WARNING)
		keep(self.__Image(9, 419, PATH + "bg_green.png"))
		self.costText = self.__Text(BASE_WIDTH / 2 - 8, 431, COLOR_LABEL)

		self.acceptButton = self.__Button(28, 451, uiScriptLocale.OK)
		self.acceptButton.SetEvent(ui.__mem_func__(self.OpenQuestionDialog))
		self.cancelButton = self.__Button(138, 451, uiScriptLocale.CANCEL)
		self.cancelButton.SetEvent(ui.__mem_func__(self.CancelRefine))

	def BindInterface(self, interface):
		from _weakref import proxy
		self.interface = proxy(interface)

	def SetInven(self, inven):
		self.inven = inven

	def Destroy(self):
		self.inven = None
		self.Close()
		self.resultPopup = None
		self.interface = None
		self.keep = []

	def Open(self, targetItemPos, nextGradeItemVnum, cost, prob, type):
		self.targetItemPos = targetItemPos
		self.vnum = nextGradeItemVnum
		self.cost = long(cost)
		self.percentage = int(prob)
		self.type = int(type)
		self.materials = []
		self.pittyCurrent = self.pittyMax = 0

		curVnum = player.GetItemIndex(targetItemPos)
		if curVnum:
			item.SelectItem(curVnum)
			try:
				self.itemIcon.LoadImage(item.GetIconImageFileName())
			except:
				pass

		self.__RefreshResult()
		self.__RefreshMaterials()
		self.__RefreshPity()
		self.RefreshSealItems()
		self.__RefreshSuccessText()

		self.costText.SetText(localeInfo.REFINE_RENEWAL_COST.format(localeInfo.DottedNumber(self.cost)))
		self.costText.SetPackedFontColor(COLOR_LABEL if player.GetElk() >= self.cost else COLOR_LACK)

		self.SetCantMouseEventSlot(self.targetItemPos)
		self.Show()
		self.SetTop()
		if self.autoAsk:
			self.autoAsk = False
			self.OpenQuestionDialog()

	def AppendMaterial(self, vnum, count):
		if len(self.materials) >= MATERIAL_MAX:
			return
		self.materials.append((vnum, count))
		self.__RefreshMaterials()

	def SetPittyInfo(self, forVnum, pittyCurrent, pittyMax):
		if player.GetItemIndex(self.targetItemPos) != forVnum:
			return
		self.pittyCurrent, self.pittyMax = pittyCurrent, pittyMax
		if pittyMax and pittyCurrent >= pittyMax:
			self.percentage = 100
		self.__RefreshPity()
		self.__RefreshSuccessText()

	# ----------------------------------------------------------------- refresh
	def __RefreshResult(self):
		metinSlot = [player.GetItemMetinSocket(self.targetItemPos, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
		attrSlot = [player.GetItemAttribute(self.targetItemPos, i) for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM)]

		recorder = _LineRecorder()
		recorder.AddRefineItemData(self.vnum, metinSlot, attrSlot)
		recorder.HideToolTip()
		stats = (recorder.POSITIVE_COLOR, recorder.NEGATIVE_COLOR, recorder.SPECIAL_POSITIVE_COLOR,
			recorder.SPECIAL_POSITIVE_COLOR2, 0xff9fd6a8, 0xffe57875)
		lines = [(text, color) for (text, color) in recorder.lines[1:] if color in stats and text]
		recorder.ClearToolTip()

		item.SelectItem(self.vnum)
		self.resultName.SetText(item.GetItemName())
		level = 0
		for i in xrange(item.LIMIT_MAX_NUM):
			(limitType, limitValue) = item.GetLimit(i)
			if limitType == item.LIMIT_LEVEL:
				level = limitValue
		self.resultLevel.SetText(localeInfo.TOOLTIP_ITEM_LIMIT_LEVEL % level if level else "")

		for i, textLine in enumerate(self.resultLines):
			if i < len(lines):
				textLine.SetText(lines[i][0])
				textLine.SetPackedFontColor(lines[i][1])
			else:
				textLine.SetText("")

	def __RefreshMaterials(self):
		for i in xrange(MATERIAL_MAX):
			if i < len(self.materials):
				(vnum, need) = self.materials[i]
				self.materialSlot.SetItemSlot(i, vnum, need)
				self.materialLocks[i].Hide()
			else:
				self.materialSlot.ClearSlot(i)
				self.materialLocks[i].Show()
		self.materialSlot.RefreshSlot()

	def __RefreshPity(self):
		if self.pittyMax:
			self.pityText.SetText(localeInfo.REFINE_RENEWAL_PITY.format(self.pittyCurrent, self.pittyMax))
		else:
			self.pityText.SetText(localeInfo.REFINE_RENEWAL_NO_PITY)

	def __RefreshSuccessText(self):
		if self.percentage >= 100:
			self.warningBar.LoadImage(PATH + "bg_chance_success.png")
			self.warningText.SetPackedFontColor(COLOR_CHANCE)
			self.warningText.SetText(localeInfo.REFINE_RENEWAL_SURE)
		else:
			self.warningBar.LoadImage(PATH + "bg_green.png")
			self.warningText.SetPackedFontColor(COLOR_WARNING)
			self.warningText.SetText(localeInfo.REFINE_RENEWAL_FAIL_WARNING)

	def GetCurrentSealVnums(self):
		return GetRefineSealVnums(player.GetItemIndex(self.targetItemPos))

	def RefreshSealItems(self):
		self.sealVnums = self.GetCurrentSealVnums()
		for i in xrange(2):
			vnum = self.sealVnums[i]
			if vnum:
				item.SelectItem(vnum)
				try:
					self.sealIcons[i].LoadImage(item.GetIconImageFileName())
				except:
					pass
				self.sealIcons[i].Show()
				count = player.GetItemCountByVnum(vnum)
				self.sealNames[i].SetText(localeInfo.REFINE_RENEWAL_SEAL_NAME.format(item.GetItemName(), count))
				if count <= 0:
					self.sealStates[i] = 0
			else:
				self.sealIcons[i].Hide()
				self.sealNames[i].SetText("")
				self.sealStates[i] = 0
			self.__RefreshSealCheck(i)

	def __RefreshSealCheck(self, i):
		image = COMMON + ("checkbox_new_selected.png" if self.sealStates[i] else "checkbox_new_unselected.png")
		self.sealChecks[i].SetUpVisual(image)
		self.sealChecks[i].SetOverVisual(image)
		self.sealChecks[i].SetDownVisual(image)

	def __ClickSealIcon(self, eventName, i):
		self.__ToggleSeal(i)

	def __ToggleSeal(self, i):
		vnum = self.sealVnums[i]
		if not vnum:
			return
		if not self.sealStates[i] and player.GetItemCountByVnum(vnum) <= 0:
			item.SelectItem(vnum)
			if not self.resultPopup:
				self.resultPopup = _ResultPopup()
			self.resultPopup.Open(localeInfo.REFINE_RENEWAL_NO_SEAL.format(item.GetItemName()), None)
			(x, y) = self.GetGlobalPosition()
			self.resultPopup.SetPosition(x + (WIDTH - self.resultPopup.GetWidth()) / 2, y + (HEIGHT - self.resultPopup.GetHeight()) / 2)
			return
		self.sealStates[i] = 0 if self.sealStates[i] else 1
		self.__RefreshSealCheck(i)

	def __SealFlags(self):
		self.RefreshSealItems()
		return (1 if self.sealStates[0] else 0) | (2 if self.sealStates[1] else 0)

	# ----------------------------------------------------------------- tooltips
	def __ToolTip(self):
		interface = constInfo.GetInterfaceInstance()
		return interface.tooltipItem if interface else None

	def __OverInTarget(self, *args):
		tooltip = self.__ToolTip()
		if tooltip:
			tooltip.SetInventoryItem(self.targetItemPos)

	def __OverInMaterial(self, index):
		tooltip = self.__ToolTip()
		if tooltip and index < len(self.materials):
			tooltip.SetItemToolTip(self.materials[index][0])

	def __OverInSeal(self, eventName, index):
		tooltip = self.__ToolTip()
		if tooltip and self.sealVnums[index]:
			tooltip.SetItemToolTip(self.sealVnums[index])

	def __OverOut(self, *args):
		tooltip = self.__ToolTip()
		if tooltip:
			tooltip.HideToolTip()

	# ----------------------------------------------------------------- accept / cancel
	def __CloseQuestionDialog(self):
		if self.dlgQuestion:
			self.dlgQuestion.Close()
		self.dlgQuestion = None

	def __FailureText(self):
		if self.type == REFINE_TYPE_SCROLL:
			return localeInfo.REFINE_RENEWAL_DOWNGRADE
		if self.type == REFINE_TYPE_HYUNIRON:
			return localeInfo.REFINE_RENEWAL_KEEP
		return localeInfo.REFINE_RENEWAL_DESTROY

	def OpenQuestionDialog(self):
		self.__CloseQuestionDialog()
		dlgQuestion = uiCommon.QuestionDialog2()
		if self.percentage >= 100:
			dlgQuestion.SetText1(localeInfo.REFINE_RENEWAL_SURE)
			dlgQuestion.SetText2(localeInfo.REFINE_RENEWAL_SURE_QUESTION)
		else:
			dlgQuestion.SetText1(self.__FailureText())
			dlgQuestion.SetText2(localeInfo.REFINE_WARNING2)
		dlgQuestion.SetAcceptEvent(ui.__mem_func__(self.Accept))
		dlgQuestion.SetCancelEvent(ui.__mem_func__(self.__CloseQuestionDialog))
		dlgQuestion.Open()
		self.__PlacePopup(dlgQuestion)
		self.dlgQuestion = dlgQuestion

	def __PlacePopup(self, popup):
		(x, y) = self.GetGlobalPosition()
		popup.SetPosition(x + (WIDTH - popup.GetWidth()) / 2, y + Y0 + 188 + 29 - popup.GetHeight())

	def Accept(self):
		self.__CloseQuestionDialog()
		net.SendRefinePacket(self.targetItemPos, self.type, self.__SealFlags())

	def CheckRefine(self, isFail):
		self.__CloseQuestionDialog()
		if not self.resultPopup:
			self.resultPopup = _ResultPopup()
		self.resultPopup.Open(localeInfo.REFINE_FAILURE if isFail else localeInfo.REFINE_SUCCESS, ui.__mem_func__(self.__ContinueRefine))
		self.__PlacePopup(self.resultPopup)

	def __ContinueRefine(self):
		curVnum = player.GetItemIndex(self.targetItemPos)
		if not curVnum:				# destroyed
			self.CancelRefine()
			return
		item.SelectItem(curVnum)
		if not item.GetRefinedVnum():		# last grade reached
			self.CancelRefine()
			return
		data = constInfo.AUTO_REFINE_DATA
		if constInfo.AUTO_REFINE_TYPE == 1:
			(scrollPos, itemPos) = data.get("ITEM", [-1, -1])[:2]
			if scrollPos < 0 or itemPos != self.targetItemPos or not player.GetItemIndex(scrollPos):
				self.CancelRefine()
				return
			self.autoAsk = True
			net.SendItemUseToItemPacket(scrollPos, itemPos)
		elif constInfo.AUTO_REFINE_TYPE == 2:
			(npcVID, invType, itemPos, count) = data.get("NPC", [0, -1, -1, 0])[:4]
			if not npcVID or itemPos != self.targetItemPos:
				self.CancelRefine()
				return
			self.autoAsk = True
			net.SendGiveItemPacket(npcVID, invType, itemPos, count)
		else:
			self.CancelRefine()

	def CancelRefine(self):
		net.SendRefinePacket(255, 255, 0)
		self.Close()
		if app.ENABLE_AUTO_REFINE:
			constInfo.AUTO_REFINE_TYPE = 0
			constInfo.AUTO_REFINE_DATA = {"ITEM" : [-1, -1], "NPC" : [0, -1, -1, 0]}

	def Close(self):
		self.__CloseQuestionDialog()
		self.autoAsk = False
		if self.resultPopup:
			self.resultPopup.Close()
		self.__OverOut()
		self.SetCanMouseEventSlot(self.targetItemPos)
		self.Hide()

	def OnPressEscapeKey(self):
		self.CancelRefine()
		return True

	def OnUpdate(self):
		if self.dlgQuestion and self.dlgQuestion.IsShow():
			self.dlgQuestion.SetTop()
		if self.resultPopup and self.resultPopup.IsShow():
			self.resultPopup.SetTop()

	# ----------------------------------------------------------------- inventory slot lock (ENABLE_SLOT_MARKING_SYSTEM)
	def __InventorySlot(self, idx):
		if not self.inven or not app.ENABLE_SLOT_MARKING_SYSTEM:
			return -1
		pageSize = player.INVENTORY_PAGE_SIZE
		page = self.inven.GetInventoryPageIndex()
		if page * pageSize <= idx < (page + 1) * pageSize:
			return idx - page * pageSize
		return -1

	def SetCanMouseEventSlot(self, idx):
		slot = self.__InventorySlot(idx)
		if slot >= 0:
			self.inven.wndItem.SetCanMouseEventSlot(slot)

	def SetCantMouseEventSlot(self, idx):
		slot = self.__InventorySlot(idx)
		if slot >= 0:
			self.inven.wndItem.SetCantMouseEventSlot(slot)

