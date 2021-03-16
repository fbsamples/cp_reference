# Copyright 2004-present, Facebook. All Rights Reserved.
from django.db import models
from django.utils.translation import gettext_lazy

""" TextChoices classes """
"""
Set of enum-like classes for easy management of DB fields that have a limited
set of potential values.

Where needed it leverages django translation utils for
easier i18n management down the line.
"""

class Currency(models.TextChoices):
    """ Standard 3 char code of supported currencies"""

    DZD = 'DZD', gettext_lazy('Algerian Dinar')
    ARS = 'ARS', gettext_lazy('Argentine Peso')
    AUD = 'AUD', gettext_lazy('Australian Dollar')
    BDT = 'BDT', gettext_lazy('Bangladeshi Taka')
    BOB = 'BOB', gettext_lazy('Bolivian Boliviano')
    BRL = 'BRL', gettext_lazy('Brazilian Real')
    GBP = 'GBP', gettext_lazy('British Pound')
    CAD = 'CAD', gettext_lazy('Canadian Dollar')
    CLP = 'CLP', gettext_lazy('Chilean Peso')
    CNY = 'CNY', gettext_lazy('Chinese Yuan')
    COP = 'COP', gettext_lazy('Colombian Peso')
    CRC = 'CRC', gettext_lazy('Costa Rican Colon')
    CZK = 'CZK', gettext_lazy('Czech Koruna')
    DKK = 'DKK', gettext_lazy('Danish Krone')
    EGP = 'EGP', gettext_lazy('Egyptian Pounds')
    EUR = 'EUR', gettext_lazy('Euro')
    GTQ = 'GTQ', gettext_lazy('Guatemalan Quetza')
    HNL = 'HNL', gettext_lazy('Honduran Lempira')
    HKD = 'HKD', gettext_lazy('Hong Kong Dollar')
    HUF = 'HUF', gettext_lazy('Hungarian Forint')
    ISK = 'ISK', gettext_lazy('Iceland Krona')
    INR = 'INR', gettext_lazy('Indian Rupee')
    IDR = 'IDR', gettext_lazy('Indonesian Rupiah')
    ILS = 'ILS', gettext_lazy('Israeli New Shekel')
    JPY = 'JPY', gettext_lazy('Japanese Yen')
    KES = 'KES', gettext_lazy('Kenyan Shilling')
    KRW = 'KRW', gettext_lazy('Korean Won')
    MOP = 'MOP', gettext_lazy('Macau Patacas')
    MYR = 'MYR', gettext_lazy('Malaysian Ringgit')
    MXN = 'MXN', gettext_lazy('Mexican Peso')
    NZD = 'NZD', gettext_lazy('New Zealand Dollar')
    NIO = 'NIO', gettext_lazy('Nicaraguan Cordoba')
    NGN = 'NGN', gettext_lazy('Nigerian Naira')
    NOK = 'NOK', gettext_lazy('Norwegian Krone')
    PKR = 'PKR', gettext_lazy('Pakistani Rupee')
    PYG = 'PYG', gettext_lazy('Paraguayan Guarani')
    PEN = 'PEN', gettext_lazy('Peruvian Nuevo Sol')
    PHP = 'PHP', gettext_lazy('Philippine Peso')
    PLN = 'PLN', gettext_lazy('Polish Zloty')
    QAR = 'QAR', gettext_lazy('Qatari Rials')
    RON = 'RON', gettext_lazy('Romanian Leu')
    RUB = 'RUB', gettext_lazy('Russian Ruble')
    SAR = 'SAR', gettext_lazy('Saudi Arabian Riyal')
    SGD = 'SGD', gettext_lazy('Singapore Dollar')
    ZAR = 'ZAR', gettext_lazy('South African Rand')
    SEK = 'SEK', gettext_lazy('Swedish Krona')
    CHF = 'CHF', gettext_lazy('Swiss Franc')
    TWD = 'TWD', gettext_lazy('Taiwan Dollar')
    THB = 'THB', gettext_lazy('Thai Baht')
    TRY = 'TRY', gettext_lazy('Turkish Lira')
    AED = 'AED', gettext_lazy('Uae Dirham')
    USD = 'USD', gettext_lazy('United States Dollar')
    UYU = 'UYU', gettext_lazy('Uruguay Peso')
    VEF = 'VEF', gettext_lazy('Venezuelan Bolivar')
    VND = 'VND', gettext_lazy('Vietnamese Dong')
