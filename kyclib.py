import pymysql
import traceback
import time
import json

import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config
from hdacpy.transaction import Transaction
from hdacpy import wallet


def getConnection():
    return pymysql.connect(**(config.DBINFO)
            , charset='utf8', cursorclass=pymysql.cursors.DictCursor)

def closeConnection(conn):
    conn.close()

def getKYCInfoFromArgosAPI(last_input_id):
    # Call API, parse response, and return the parsed info
    res = []

    # TODO: parse code here
    # The below for loop is just for example
    for _ in range(1):
        unit_info = {
              "address": "friday193lmkelm57nvsrafm4fewjs3s8nq6eduukev7z4kz2ac3h64elqsn9llrc"
            , "email": "psy2848048@gmail.com"
            , "kyc_level": 1
        }
        res.append(unit_info)

    return res

def insertKYCInfoToDb(kyc_info_list):
    conn = getConnection()
    cursor = conn.cursor()

    query = """
        INSERT INTO KYC_COMPLETE
            (address, email, kyc_level, status)
        VALUES
            (%s, %s, %s, 0)
    """
    try:
        for unit_info in kyc_info_list:
            cursor.execute(query, (unit_info["address"], unit_info["email"], unit_info["kyc_level"],))
        
        conn.commit()
    
    except:
        conn.rollback()
        traceback.print_exc()

    finally:
        closeConnection(conn)


def sendKYCInfoOnContract():
    conn = getConnection()
    cursor = conn.cursor()
    contract_info = config.CONTRACT_INFO
    query_getone = """
        SELECT address, kyc_level FROM KYC_COMPLETE WHERE status = 0 LIMIT 1
    """

    cursor.execute(query_getone)
    ret = cursor.fetchall()
    if len(ret) == 0:
        return
    
    address, kyc_level = ret[0]['address'], ret[0]['kyc_level']

    tx_obj = Transaction(
        chain_id=contract_info['chain_id'],
        host=contract_info['rest_server'],
        privkey=wallet.mnemonic_to_privkey(contract_info['admin_mnemonic'])
    )
    param = json.dumps([
        {
            "name": "method",
            "value":{
                "cl_type":{
                    "simple_type":"STRING"
                },
                "value":{
                    "str_value":"insert_kyc_data"
                }
            }
        },
        {
            "name": "address",
            "value": {
                "cl_type": {
                    "list_type": {
                        "inner": {
                            "simple_type":"U8"
                        }
                    }
                },
                "value":{
                    "bytes_value": address
                }
            }
        },
        {
            "name":"kyc_level",
            "value":{
                "cl_type":{
                    "simple_type":"U512"
                },
                "value":{
                    "u512":{
                        "value": str(kyc_level)
                    }
                }
            }
        }
    ]).replace(" ", "")

    kyc_store_tx_info = tx_obj.execute_contract("hash", contract_info["swap_proxy"], "", param, 0.01)
    kyc_store_tx_hash = kyc_store_tx_info['txhash']

    time.sleep(5)

    try:
        tx_obj.get_tx(kyc_store_tx_hash)
    except:
        raise Exception("Fail to input KYC complete info: {}".format(address))

    query_update = """
        UPDATE KYC_COMPLETE
          SET
               tx_hash = %s
             , status = 1
        WHERE
          address = %s
    """
    try:
        cursor.execute(query_update, (kyc_store_tx_hash, address, ))
        conn.commit()

    except:
        conn.rollback()

        query_update = """
            UPDATE KYC_COMPLETE
            SET
                status = 91
            WHERE
            address = %s
        """
        cursor.execute(query_update, (address, ))
        conn.commit()

        raise Exception("KYC recording contract status update failed {}".format(address))
    
    finally:
        closeConnection(conn)


def sendMail():
    conn = getConnection()
    cursor = conn.cursor()
    query_getone = """
        SELECT email, tx_hash, address
        FROM KYC_COMPLETE
        WHERE status = 1
        LIMIT 1
    """
    cursor.execute(query_getone)
    ret = cursor.fetchall()
    if len(ret) == 0:
        return
    
    requester_email, tx_hash, address = ret[0]['email'], ret[0]['tx_hash'], ret[0]['address']

    ##################
    # SEND MAIL PART #
    ##################

    # TODO: Modify config.MAIL_TEMPLATE
    try:
        content = MIMEText(config.MAIL_TEMPLATE.format(tx_hash=tx_hash, address=address), 'html', _charset='utf-8')
        msg = MIMEMultipart('alternative')

        msg['Subject'] = "Your KYC information has been recorded on chain!"
        msg['From'] = 'test <no-reply@hdac.io>'
        msg['To'] = requester_email
        msg.attach(content)

        a = smtplib.SMTP(config.MAILER_INFO['host'])
        a.ehlo()
        a.starttls()
        a.login(config.MAILER_INFO["sender"], config.MAILER_INFO["password"])
        a.sendmail("no-reply@hdac.io", requester_email, msg.as_string())
        a.quit()

    except:
        query_update = """
            UPDATE KYC_COMPLETE
            SET
                status = 92
            WHERE
            address = %s
        """
        cursor.execute(query_update, (address, ))
        conn.commit()
        raise Exception("Mail alert send failure {}".format(address))

    # Mark as complete
    query_update = """
        UPDATE KYC_COMPLETE
          SET
             status = 2
        WHERE
          address = %s
    """

    try:
        cursor.execute(query_update, (address, ))
        conn.commit()
    except:
        conn.rollback()
        raise Exception("KYC status DB update failure {}".format(address))
