// bool CPythonNetworkStream::SendRefinePacket(BYTE byPos, BYTE byType, ...) icinde:
// Bul:
, bool bUseSealOfGod

// Degistir:
#ifdef ENABLE_REFINE_SEAL_RENEWAL
, BYTE bUseSealOfGod
#else
, bool bUseSealOfGod
#endif

