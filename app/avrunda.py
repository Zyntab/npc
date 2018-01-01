# -*- coding: utf-8 -*-
from decimal import *

def avrunda(trait, x):
    if trait in ['Normal förflyttning', 'Jogg', 'Sprint']:
        D = Decimal(x).quantize(Decimal('1.0'))
        return str(D)
    else:
        D = Decimal(x).to_integral_value(rounding=ROUND_HALF_UP)
        return str(D)
