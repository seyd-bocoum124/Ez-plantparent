import logging
import subprocess
import tempfile
import os
import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

CA_CERT = "/ssl/rootCA.pem"
CA_KEY  = "/ssl/rootCA-key.pem"

SHARED_KEY = os.getenv("SHARED_KEY")

class ProvisionRequest(BaseModel):
    station_id: str
    description: str

router = APIRouter()

@router.post("/stations/provisions")
def provision_station(params: ProvisionRequest):
    station_id = params.station_id
    description = params.description

    if description != SHARED_KEY:
        raise HTTPException(
            status_code=401,
            detail=f"Unauthorized"
        )

    # Validation basique (MAC ou alphanumérique)
    if not re.match(r"^[A-Za-z0-9:-]+$", station_id):
        raise HTTPException(status_code=400, detail="station_id invalide")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            key_file  = os.path.join(tmpdir, "client.key")
            csr_file  = os.path.join(tmpdir, "client.csr")
            cert_file = os.path.join(tmpdir, "client.crt")

            # Générer clé + CSR
            subprocess.run([
                "openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes",
                "-keyout", key_file,
                "-subj", f"/CN={station_id}",
                "-out", csr_file
            ], check=True)

            # Signer avec le CA
            subprocess.run([
                "openssl", "x509", "-req", "-in", csr_file,
                "-CA", CA_CERT, "-CAkey", CA_KEY, "-CAcreateserial",
                "-out", cert_file, "-days", "365", "-sha256", "-outform", "PEM"
            ], check=True)

            with open(cert_file) as fcert, open(key_file) as fkey:
                logger.info("Provisioning réussi pour station %s", station_id)
                return {
                    "client_cert": fcert.read(),
                    "client_key": fkey.read()
                }

    except subprocess.CalledProcessError as e:
        logger.error("Erreur OpenSSL pour station %s: %s", station_id, e)
        raise HTTPException(status_code=500, detail="Erreur lors de la génération du certificat")