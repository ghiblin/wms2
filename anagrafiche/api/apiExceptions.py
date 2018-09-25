#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework.serializers import ValidationError
WMS_ERROR_CODE = 444

### Se estendo la classe APIException non riesco a sovrascrivere la chiave dei messaggi di errore. 
### A me serve mettere nel body della risposta un dizionario con chiave "non_field_errors" e messaggio
### quello che viene passato nel costruttore.

"""
# from rest_framework.exceptions import APIException
class WmsAPIException(APIException):
    status_code = WMS_ERROR_CODE
    default_detail = "Si è verificato un errore durante l'esecuzione delle API"
"""

class WmsValidationError(ValidationError):
	status_code = WMS_ERROR_CODE
