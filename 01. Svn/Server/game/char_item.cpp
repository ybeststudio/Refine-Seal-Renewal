// Ara:
		m_dwRefineNPCVID = 0;
	}
}

// Altina ekle:
#ifdef ENABLE_REFINE_SEAL_RENEWAL
static int ConsumeRefineSeals(LPCHARACTER ch, LPITEM item, BYTE flags)
{
	int level = 0;
	for (int i = 0; i < ITEM_LIMIT_MAX_NUM; ++i)
		if (item->GetLimitType(i) == LIMIT_LEVEL)
			level = item->GetLimitValue(i);

	DWORD seal = 0, sealPlus = 0;
	if (level >= 0 && level <= 105)
		seal = 25049, sealPlus = 25050;
	else if (level >= 106 && level <= 110)
		seal = 25051, sealPlus = 25052;
	else
		return 0;

	int bonus = 0;
	if ((flags & 1) && ch->CountSpecifyItem(seal) > 0)
	{
		ch->RemoveSpecifyItem(seal, 1);
		bonus += 5;
	}
	if ((flags & 2) && ch->CountSpecifyItem(sealPlus) > 0)
	{
		ch->RemoveSpecifyItem(sealPlus, 1);
		bonus += 10;
	}
	return bonus;
}
#endif


// bool CHARACTER::DoRefine(LPITEM item, bool bMoneyOnly/* = false*/, ...) icinde:
// Bul:
	if (bUseSealOfGod && CountSpecifyItem(ITEM_VNUM_SEAL_OF_GOD) > 0)
	{
		RemoveSpecifyItem(ITEM_VNUM_SEAL_OF_GOD, 1);
		prob -= EXTRA_CHANCE_SEAL_OF_GOD;
		if (prob <= 0)
		{
			prob = 1;
		}
	}

// Degistir:
#ifdef ENABLE_REFINE_SEAL_RENEWAL
	prob -= ConsumeRefineSeals(this, item, bUseSealOfGod);
	if (prob <= 0)
		prob = 1;
#else
	if (bUseSealOfGod && CountSpecifyItem(ITEM_VNUM_SEAL_OF_GOD) > 0)
	{
		RemoveSpecifyItem(ITEM_VNUM_SEAL_OF_GOD, 1);
		prob -= EXTRA_CHANCE_SEAL_OF_GOD;
		if (prob <= 0)
		{
			prob = 1;
		}
	}
#endif


// bool CHARACTER::DoRefineWithScroll(LPITEM item, ...) icinde:
// Bul:
	if (bUseSealOfGod && CountSpecifyItem(ITEM_VNUM_SEAL_OF_GOD) > 0)
	{
		RemoveSpecifyItem(ITEM_VNUM_SEAL_OF_GOD, 1);

		success_prob = success_prob + EXTRA_CHANCE_SEAL_OF_GOD;
		if (success_prob > 100)
		{
			success_prob = 100;
		}
	}

// Degistir:
#ifdef ENABLE_REFINE_SEAL_RENEWAL
	success_prob = MIN(100, success_prob + ConsumeRefineSeals(this, item, bUseSealOfGod));
#else
	if (bUseSealOfGod && CountSpecifyItem(ITEM_VNUM_SEAL_OF_GOD) > 0)
	{
		RemoveSpecifyItem(ITEM_VNUM_SEAL_OF_GOD, 1);

		success_prob = success_prob + EXTRA_CHANCE_SEAL_OF_GOD;
		if (success_prob > 100)
		{
			success_prob = 100;
		}
	}
#endif


// bool CHARACTER::DoRefineSerpent(LPITEM item, ...) icinde:
// Bul:
	if (bUseSealOfGod && CountSpecifyItem(ITEM_VNUM_SEAL_OF_GOD) > 0)
	{
		RemoveSpecifyItem(ITEM_VNUM_SEAL_OF_GOD, 1);
		prob -= EXTRA_CHANCE_SEAL_OF_GOD;
		if (prob <= 0)
			prob = 1;
	}

// Degistir:
#ifdef ENABLE_REFINE_SEAL_RENEWAL
	prob -= ConsumeRefineSeals(this, item, bUseSealOfGod);
	if (prob <= 0)
		prob = 1;
#else
	if (bUseSealOfGod && CountSpecifyItem(ITEM_VNUM_SEAL_OF_GOD) > 0)
	{
		RemoveSpecifyItem(ITEM_VNUM_SEAL_OF_GOD, 1);
		prob -= EXTRA_CHANCE_SEAL_OF_GOD;
		if (prob <= 0)
			prob = 1;
	}
#endif

