import os
import requests
import logging
from src.app.exceptions.exceptions import UserNotFoundError, BadRequestError


async def block_user_auth(id: str, to_block: bool):
    prefix = await get_auth_url()
    AUTH_SERVICE_URL = f"{prefix}/block/{id}"
    payload = {"block": to_block}
    return await send_patch_request(id, AUTH_SERVICE_URL, payload)


async def change_rol_auth(id: str, new_rol: str):
    prefix = await get_auth_url()
    AUTH_SERVICE_URL = f"{prefix}/rol/{id}"
    payload = {"rol": new_rol}
    return await send_patch_request(id, AUTH_SERVICE_URL, payload)


async def get_auth_url():
    prefix = os.getenv("URL_AUTH")
    if prefix is None:
        raise RuntimeError("Environment variable 'URL_AUTH' is not set")
    return prefix


async def send_patch_request(id, AUTH_SERVICE_URL, payload):
    logging.info(f"Log: Sending request to {AUTH_SERVICE_URL} with payload: {payload}")
    try:
        response = requests.patch(AUTH_SERVICE_URL, json=payload, timeout=5)
        logging.info(f"Auth service response: {response.status_code}, {response.text}")
        if response.status_code == 200:
            return
        elif response.status_code == 404:
            raise UserNotFoundError(user_id=id)
        elif response.status_code == 400:
            raise BadRequestError()

    except requests.exceptions.RequestException as e:
        logging.error(f"Request to auth service failed: {e}")
        raise Exception("Auth service request failed") from e
