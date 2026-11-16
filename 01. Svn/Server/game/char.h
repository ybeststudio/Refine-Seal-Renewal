// Bul:
typedef bool TRefineSealArg;

// Degistir:
#ifdef ENABLE_REFINE_SEAL_RENEWAL
typedef BYTE TRefineSealArg;	// seal flags (bit0 +5, bit1 +10)
#else
typedef bool TRefineSealArg;
#endif

