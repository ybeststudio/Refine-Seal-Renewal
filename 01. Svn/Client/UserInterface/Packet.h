// Bul:
	bool seal_of_god;

// Degistir:
#ifdef ENABLE_REFINE_SEAL_RENEWAL
	BYTE seal_of_god;	// bit0 = Tanrilarin Muhru (+5), bit1 = Tanrilarin Muhru+ (+10)
#else
	bool seal_of_god;
#endif

