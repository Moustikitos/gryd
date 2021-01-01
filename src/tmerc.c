// Copyright (c) 2015-2021, THOORENS Bruno
// All rights reserved.
#include "./geoid.h"

static double F3 = 3*2;
static double F4 = 4*3*2;
static double F5 = 5*4*3*2;
static double F6 = 6*5*4*3*2;
static double F7 = 7*6*5*4*3*2;
static double F8 = 8*7*6*5*4*3*2;

EXPORT Geographic tmerc_forward(Crs *crs, Geodesic *lla){
	Geographic xya;
	double m, v, lc, B, t, lc2, B2, B3, B4, t2, t4, t6, W3, W4, W5, W6, W7_, W8_, X, Y;

	m   = meridian_distance(crs->datum.ellipsoid.a, crs->datum.ellipsoid.e, lla->latitude) - meridian_distance(crs->datum.ellipsoid.a, crs->datum.ellipsoid.e, crs->phi0);
	v   = nhu(crs->datum.ellipsoid.a, crs->datum.ellipsoid.e, lla->latitude);
	B   = v/rho(crs->datum.ellipsoid.a, crs->datum.ellipsoid.e, lla->latitude);
	lc  = cos(lla->latitude)*(lla->longitude-crs->lambda0);
	t   = tan(lla->latitude);
	lc2 = lc*lc;

	B2 = B*B;  t2 = t*t;
	B3 = B*B2; t4 = t2*t2;
	B4 = B*B3; t6 = t2*t4;

	W3  = B - t2;
	W4  = 4*B2 + B - t2;
	W5  = 4*B3*(1-6*t2) + B2*(1+8*t2) - 2*B*t2 + t4;
	W6  = 8*B4*(11-24*t2) - 28*B3*(1-6*t2) + B2*(1-32*t2) - 2*B*t2 + t4;
	W7_ = 61 - 479*t2 + 179*t4 - t6;
	W8_ = 1385 - 3111*t2 + 543*t4 - t6;

	X = v*lc * (1. + lc2 * (W3/F3 + lc2 * (W5/F5 + lc2*W7_/F7)));
	Y = m + v*t*lc2 * (0.5 + lc2 * (W4/F4 + lc2 * (W6/F6 + lc2*W8_/F8)));

	xya.x = crs->k0*X + crs->x0;
	xya.y = crs->k0*Y + crs->y0;
	xya.altitude = lla->altitude;

	return xya;
}

EXPORT Geodesic tmerc_inverse(Crs* crs, Geographic *xya){
	Geodesic lla;
	double f, v, x, x2, B, t, c, B2, B3, B4, t2, t4, t6, V3, V5, V7_, U4, U6, U8_, lambda, phi;

	f = footpoint_latitude(crs->datum.ellipsoid.a, crs->datum.ellipsoid.e, meridian_distance(crs->datum.ellipsoid.a, crs->datum.ellipsoid.e, crs->phi0) + (xya->y - crs->y0)/crs->k0);
	v = nhu(crs->datum.ellipsoid.a, crs->datum.ellipsoid.e, f);
	x = (xya->x - crs->x0)/(crs->k0*v);
	x2 = x*x;

	B = v/rho(crs->datum.ellipsoid.a, crs->datum.ellipsoid.e, f);
	t = tan(f);
	c = cos(f);

	B2 = B*B;  t2 = t*t;
	B3 = B*B2; t4 = t2*t2;
	B4 = B*B3; t6 = t2*t4;

	V3  = B + 2*t2;
	V5  = 4*B3*(1-6*t2) - B2*(9-68*t2) - 72*B*t2 - 24*t4;
	V7_ = 61 + 662*t2 + 1320*t4 + 720*t6;
	U4  = 4*B2 - 9*B*(1-t2) - 12*t2;
	U6  = 8*B4*(11-24*t2) - 12*B3*(21-71*t2) + 15*B2*(15-98*t2+15*t4) + 180*B*(5*t2-3*t4) + 360*t4;
	U8_ = -1385 - 3633*t2 - 4095*t4 - 1575*t6;

	lambda = x/c * (1. - x2 * (V3/F3 + x2 * (V5/F5 + x2 * V7_/F7)));
	phi = f - x2*B*t * (0.5 + x2 * (U4/F4 + x2 * (U6/F6 + x2 * U8_/F8)));

	lla.longitude = lambda + crs->lambda0;
	lla.latitude = phi;
	lla.altitude = xya->altitude;

	return lla;
}
