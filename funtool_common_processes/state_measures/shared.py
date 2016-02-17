# Functions used within multiple state_measure functions
# NOT intended to be used independently as state_measures

import math
import numbers

def compute_ratio(a_value,b_value):
    """
    Computes the ratio between two values, handles divide by zero errors

    """
    if b_value == 0:
        if a_value == 0:
            ratio= float('Nan')
        else:
            ratio= math.copysign(float('inf'),a_value)
    else:
        ratio= a_value/b_value
    return ratio
