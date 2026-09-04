import base64
from datetime import datetime, timezone

import requests

from rejesha_green.config import settings


def get_base_url():
    return (
        "https://api.safaricom.co.ke"
        if settings.MPESA_ENVIRONMENT == "production"
        else "https://sandbox.safaricom.co.ke"
    )


def format_mpesa_phone(phone: str):
    phone = (
        phone.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("+", "")
    )

    if phone.startswith("0"):
        phone = "254" + phone[1:]

    elif phone.startswith("7"):
        phone = "254" + phone

    if len(phone) != 12 or not phone.startswith("2547"):
        raise ValueError(
            "Invalid Kenyan mobile number"
        )

    return phone


def get_access_token():

    response = requests.get(
        f"{get_base_url()}/oauth/v1/generate?grant_type=client_credentials",
        auth=(
            settings.DARAJA_CONSUMER_KEY,
            settings.DARAJA_CONSUMER_SECRET,
        ),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["access_token"]



def stk_push(
    phone: str,
    amount: int,
    account_reference: str,
    transaction_description: str,
    callback_url: str,
):

    phone = format_mpesa_phone(phone)

    token = get_access_token()

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d%H%M%S")


    password = base64.b64encode(
        (
            f"{settings.DARAJA_SHORTCODE}"
            f"{settings.DARAJA_PASSKEY}"
            f"{timestamp}"
        ).encode()
    ).decode()


    payload = {
        "BusinessShortCode":
            settings.DARAJA_SHORTCODE,

        "Password":
            password,

        "Timestamp":
            timestamp,

        "TransactionType":
            "CustomerPayBillOnline",

        "Amount":
            amount,

        "PartyA":
            phone,

        "PartyB":
            settings.DARAJA_SHORTCODE,

        "PhoneNumber":
            phone,

        "CallBackURL":
            callback_url,

        "AccountReference":
            account_reference,

        "TransactionDesc":
            transaction_description,
    }


    response = requests.post(
        f"{get_base_url()}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )


    if not response.ok:
        raise Exception(
            f"STK Push failed: {response.text}"
        )


    data = response.json()


    if data.get("ResponseCode") != "0":
        raise Exception(
            data.get(
                "errorMessage",
                "STK Push failed"
            )
        )


    return data