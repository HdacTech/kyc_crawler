import kyclib

if __name__ == "__main__":
    # Registering KYC info to DB
    res = kyclib.getKYCInfoFromArgosAPI(1)
    kyclib.insertKYCInfoToDb(res)
