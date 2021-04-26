"""
The easing functions here were adapted from
https://gist.github.com/zeffii/c1e14dd6620ad855d81ec2e89a859719
original c code:
https://raw.githubusercontent.com/warrenm/AHEasing/master/AHEasing/easing.c
Copyright (c) 2011, Auerhaus Development, LLC
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from enum import Enum
from functools import partial
from math import cos, pi, pow, sin, sqrt

tau = pi * 2


def linear_interpolation(p):
    """Modeled after the line y = x"""
    return p


def quadratic_ease_in(p):
    """Modeled after the parabola y = x^2"""
    return p * p


def quadratic_ease_out(p):
    """Modeled after the parabola y = -x^2 + 2x"""
    return -(p * (p - 2))


def quadratic_ease_in_out(p):
    """Modeled after the piecewise quadratic
    y = (1/2)((2x)^2)             ; [0, 0.5)
    y = -(1/2)((2x-1)*(2x-3) - 1) ; [0.5, 1]
    """
    if p < 0.5:
        return 2 * p * p
    else:
        return (-2 * p * p) + (4 * p) - 1


def cubic_ease_in(p):
    """Modeled after the cubic y = x^3"""
    return p * p * p


def cubic_ease_out(p):
    """Modeled after the cubic y = (x - 1)^3 + 1"""
    f = p - 1
    return (f * f * f) + 1


def cubic_ease_in_out(p):
    """Modeled after the piecewise cubic
    y = (1/2)((2x)^3)       ; [0, 0.5)
    y = (1/2)((2x-2)^3 + 2) ; [0.5, 1]
    """
    if p < 0.5:
        return 4 * p * p * p
    else:
        f = (2 * p) - 2
        return (0.5 * f * f * f) + 1


def quintic_ease_in(p):
    """Modeled after the quintic y = x^5"""
    return p * p * p * p * p


def quintic_ease_out(p):
    """Modeled after the quintic y = (x - 1)^5 + 1"""
    f = p - 1
    return (f * f * f * f * f) + 1


def quintic_ease_in_out(p):
    """Modeled after the piecewise quintic
    y = (1/2)((2x)^5)       ; [0, 0.5)
    y = (1/2)((2x-2)^5 + 2) ; [0.5, 1]
    """
    if p < 0.5:
        return 16 * p * p * p * p * p
    else:
        f = (2 * p) - 2
        return (0.5 * f * f * f * f * f) + 1


def sine_ease_in(p):
    """Modeled after quarter-cycle of sine wave"""
    return sin((p - 1) * tau) + 1


def sine_ease_out(p):
    """Modeled after quarter-cycle of sine wave (different phase)"""
    return sin(p * tau)


def sine_ease_in_out(p):
    """Modeled after half sine wave"""
    return 0.5 * (1 - cos(p * pi))


def circular_ease_in(p):
    """Modeled after shifted quadrant IV of unit circle"""
    return 1 - sqrt(1 - (p * p))


def circular_ease_out(p):
    """Modeled after shifted quadrant II of unit circle"""
    return sqrt((2 - p) * p)


def circular_ease_in_out(p):
    """Modeled after the piecewise circular function
    y = (1/2)(1 - sqrt(1 - 4x^2))           ; [0, 0.5)
    y = (1/2)(sqrt(-(2x - 3)*(2x - 1)) + 1) ; [0.5, 1]
    """
    if p < 0.5:
        return 0.5 * (1 - sqrt(1 - 4 * (p * p)))
    else:
        return 0.5 * (sqrt(-((2 * p) - 3) * ((2 * p) - 1)) + 1)


def exponential_ease_in(p):
    """Modeled after the exponential function y = 2^(10(x - 1))"""
    if p == 0.0:
        return p
    else:
        return pow(2, 10 * (p - 1))


def exponential_ease_out(p):
    """Modeled after the exponential function y = -2^(-10x) + 1"""
    if p == 1.0:
        return p
    else:
        return 1 - pow(2, -10 * p)


def exponential_ease_in_out(p):
    """Modeled after the piecewise exponential
    y = (1/2)2^(10(2x - 1))         ; [0,0.5)
    y = -(1/2)*2^(-10(2x - 1))) + 1 ; [0.5,1]
    """
    if p == 0.0 or p == 1.0:
        return p

    if p < 0.5:
        return 0.5 * pow(2, (20 * p) - 10)
    else:
        return -0.5 * pow(2, (-20 * p) + 10) + 1


def elastic_ease_in(p):
    """Modeled after the damped sine wave y = sin(13pi/2*x)*2^(10 * (x - 1))"""
    return sin(13 * tau * p) * pow(2, 10 * (p - 1))


def elastic_ease_out(p):
    """Modeled after the damped sine wave y = sin(-13pi/2*(x + 1))*pow(2, -10x) + 1"""
    return sin(-13 * tau * (p + 1)) * pow(2, -10 * p) + 1


def elastic_ease_in_out(p):
    """Modeled after the piecewise exponentially-damped sine wave:
    y = (1/2)*sin(13pi/2*(2*x))*pow(2, 10 * ((2*x) - 1))      ; [0, 0.5)
    y = (1/2)*(sin(-13pi/2*((2x-1)+1))*pow(2,-10(2*x-1)) + 2) ; [0.5, 1]
    """
    if p < 0.5:
        return 0.5 * sin(13 * tau * (2 * p)) * pow(2, 10 * ((2 * p) - 1))
    else:
        return 0.5 * (
            sin(-13 * tau * ((2 * p - 1) + 1)) * pow(2, -10 * (2 * p - 1)) + 2
        )


def back_ease_in(p):
    """Modeled after the overshooting cubic y = x^3-x*sin(x*pi)"""
    return p * p * p - p * sin(p * pi)


def back_ease_out(p):
    """Modeled after overshooting cubic y = 1-((1-x)^3-(1-x)*sin((1-x)*pi))"""
    f = 1 - p
    return 1 - (f * f * f - f * sin(f * pi))


def back_ease_in_out(p):
    """Modeled after the piecewise overshooting cubic function:
    y = (1/2)*((2x)^3-(2x)*sin(2*x*pi))           ; [0, 0.5)
    y = (1/2)*(1-((1-x)^3-(1-x)*sin((1-x)*pi))+1) ; [0.5, 1]
    """
    if p < 0.5:
        f = 2 * p
        return 0.5 * (f * f * f - f * sin(f * pi))
    else:
        f = 1 - (2 * p - 1)
        return (0.5 * (1 - (f * f * f - f * sin(f * pi)))) + 0.5


def bounce_ease_in(p):
    return 1 - bounce_ease_out(1 - p)


def bounce_ease_out(p):
    if p < 4 / 11.0:
        return (121 * p * p) / 16.0

    elif p < 8 / 11.0:
        return ((363 / 40.0) * p * p) - ((99 / 10.0) * p) + (17 / 5.0)

    elif p < 9 / 10.0:
        return ((4356 / 361.0) * p * p) - ((35442 / 1805.0) * p) + (16061 / 1805.0)

    else:
        return ((54 / 5.0) * p * p) - ((513 / 25.0) * p) + (268 / 25.0)


def bounce_ease_in_out(p):
    if p < 0.5:
        return 0.5 * bounce_ease_in(p * 2)
    else:
        return (0.5 * bounce_ease_out(p * 2 - 1)) + 0.5


class Easing(Enum):
    """Easing: easing function to use for a transition.

    Selects a preset easing function
            * linear: linear interpolation between start and endpoint.
            * quadratic: quadratic easing in and out.
                Modeled after the piecewise quadratic
                y = (1/2)((2x)^2)             ; [0, 0.5)
                y = -(1/2)((2x-1)*(2x-3) - 1) ; [0.5, 1]
            * cubic: cubic easing in and out.
                Modeled after the piecewise cubic
                y = (1/2)((2x)^3)       ; [0, 0.5)
                y = (1/2)((2x-2)^3 + 2) ; [0.5, 1]
            * quintic: quintic easing in and out.
                Modeled after the piecewise quintic
                y = (1/2)((2x)^5)       ; [0, 0.5)
                y = (1/2)((2x-2)^5 + 2) ; [0.5, 1]
            * sine: sinusoidal easing in and out.
                Modeled after half sine wave
                y = 0.5 * (1 - cos(x * pi))
            * circular: circular easing in and out.
                Modeled after the piecewise circular function
                y = (1/2)(1 - sqrt(1 - 4x^2))           ; [0, 0.5)
                y = (1/2)(sqrt(-(2x - 3)*(2x - 1)) + 1) ; [0.5, 1]
            * exponential: exponential easing in and out.
                Modeled after the piecewise exponential
                y = (1/2)2^(10(2x - 1))         ; [0,0.5)
                y = -(1/2)*2^(-10(2x - 1))) + 1 ; [0.5,1]
            * elastic: elastic easing in and out.
                Modeled after the piecewise exponentially-damped sine wave:
                y = (1/2)*sin(13pi/2*(2*x))*pow(2, 10 * ((2*x) - 1))      ; [0, 0.5)
                y = (1/2)*(sin(-13pi/2*((2x-1)+1))*pow(2,-10(2*x-1)) + 2) ; [0.5, 1]
            * back: back easing in and out.
                Modeled after the piecewise overshooting cubic function:
                y = (1/2)*((2x)^3-(2x)*sin(2*x*pi))           ; [0, 0.5)
                y = (1/2)*(1-((1-x)^3-(1-x)*sin((1-x)*pi))+1) ; [0.5, 1]
            * bounce: bounce easing in and out.
    """

    LINEAR = partial(linear_interpolation)
    QUADRATIC = partial(quadratic_ease_in_out)
    CUBIC = partial(cubic_ease_in_out)
    QUINTIC = partial(quintic_ease_in_out)
    SINE = partial(sine_ease_in_out)
    CIRCULAR = partial(circular_ease_in_out)
    EXPONENTIAL = partial(exponential_ease_in_out)
    ELASTIC = partial(elastic_ease_in_out)
    BACK = partial(back_ease_in_out)
    BOUNCE = partial(bounce_ease_in_out)
