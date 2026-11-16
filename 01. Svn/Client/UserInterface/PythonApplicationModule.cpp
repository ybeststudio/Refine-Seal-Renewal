// void initapp() icinde:
// Ara:
	PyModule_AddIntConstant(poModule, "ENABLE_TEXTLINE_EMOJI", 0);

// Altina ekle:
#ifdef ENABLE_REFINE_SEAL_RENEWAL
	PyModule_AddIntConstant(poModule, "ENABLE_REFINE_SEAL_RENEWAL", 1);
#else
	PyModule_AddIntConstant(poModule, "ENABLE_REFINE_SEAL_RENEWAL", 0);
#endif

