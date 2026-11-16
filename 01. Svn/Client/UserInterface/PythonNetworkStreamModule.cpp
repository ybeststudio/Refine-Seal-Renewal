// PyObject *netSendRefinePacket(PyObject *poSelf, PyObject *poArgs) icinde:
// Bul:
	bool bUseSealOfGod;
	if (!PyTuple_GetBoolean(poArgs, 2, &bUseSealOfGod))
	{
		return Py_BuildException();
	}

// Degistir:
#ifdef ENABLE_REFINE_SEAL_RENEWAL
	int iSealFlags;	// bit0 seal (+5), bit1 seal+ (+10)
	if (!PyTuple_GetInteger(poArgs, 2, &iSealFlags))
		return Py_BuildException();
	BYTE bUseSealOfGod = (BYTE)(iSealFlags & 3);
#else
	bool bUseSealOfGod;
	if (!PyTuple_GetBoolean(poArgs, 2, &bUseSealOfGod))
	{
		return Py_BuildException();
	}
#endif

