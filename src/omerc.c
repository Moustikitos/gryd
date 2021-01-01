// Copyright (c) 2016, THOORENS Bruno
// All rights reserved.
#include "./geoid.h"

typedef struct{
	double B;
	double A;
	double t0;
	double D;
	double D2;
	double F;
	double H;
	double G;
	double g0;
	double l0;
	double uc;
	double vc;
}Coef;

EXPORT Coef omerc_coef(double a, double e, double lambda0, double phi0, double k0, double azimut){
	Coef result;
	double e2, cphi0, sphi0;

	e2 = e*e;
	cphi0 = cos(phi0); sphi0 = sin(phi0);

	result.B = sqrt(1 + e2*pow(cphi0, 4) / (1 - e2));
	result.A = sqrt(a*result.B*k0*(1 - e2 )) / (1 - e2*pow(sin(lambda0), 2));
	result.t0 = tan(M_PI/4 - phi0/2) / pow((1 - e*sphi0) / (1 + e*sphi0), e/2);
	result.D = result.B * sqrt(1 - e2) / (cphi0 * sqrt(1 - e2*pow(sphi0, 2)));
	result.D2 = (result.D > 1) ? pow(result.D, 2) : 1;
	result.F = result.D + sqrt(result.D2 - 1) * ((phi0 > 0) ? 1 : -1);
	result.H = pow(result.F*result.t0, result.B);
	result.G = (result.F - 1/result.F) / 2;
	result.g0 =	asin(sin(azimut) / result.D);
	result.l0 =	phi0 - (asin(result.G * tan(result.g0))) / result.B;
	result.uc = abs((int)cos(azimut)) < EPS ? result.A * (lambda0 - result.l0) : (result.A/result.B) * atan2(sqrt(result.D2 - 1), cos(azimut)) * ((phi0 > 0) ? 1 : -1);
	result.vc = 0;

	return result;
}


EXPORT Geographic omerc_forward(Crs *crs, Geodesic *lla){
	Geographic xya;
	Coef coef;
	double t, Q, S, T, V, U, v, u, cphi, sphi;

	coef = omerc_coef(crs->datum.ellipsoid.a, crs->datum.ellipsoid.e, crs->lambda0, crs->phi0, crs->k0, crs->azimut);
	cphi = cos(lla->latitude); sphi = sin(lla->latitude);
// t	=	tan(p / 4 - f / 2) / ((1 - e sin (f)) / (1 + e sin (f)))e/2
	t = tan(M_PI/4 - lla->latitude/2) / pow(1-crs->datum.ellipsoid.e*sphi/(1+crs->datum.ellipsoid.e*sphi), crs->datum.ellipsoid.e/2);
// Q	=	H / tB
	Q = coef.H/pow(t, coef.B);
// S	=	(Q - 1 / Q) / 2
	S = (Q - 1 / Q) / 2;
// T	=	(Q + 1 / Q) / 2
	T = (Q + 1 / Q) / 2;
// V	=	sin(B (l - l0))
	V = sin(coef.B * (lla->longitude - coef.l0));
// U	=	(- V cos(g0) + S sin(g0)) / T
	U = (-V * cos(coef.g0) + S * sin(coef.g0));
// v	=	A ln((1 - U) / (1 + U)) / 2 B
	v = coef.A * log((1-U)/(1+U)) / (2*coef.B);
// u	=	A atan((S cos(g0) + V sin(g0)) / cos(B (l - l0 ))) / B
	u = coef.A * atan2((S * cos(coef.g0) + V * sin(coef.g0)), cos(coef.B * (lla->longitude - coef.l0))) / coef.B;
	u -= coef.uc;

// E	= v cos(gc) + u sin(gc) + (FE or Ec)
// N 	= u cos(gc) - v sin(gc) + (FN or Nc)
// gc = 0.
	xya.x = u + crs->x0;
	xya.y = v + crs->y0;
	xya.altitude = lla->altitude;
	return xya;
}

EXPORT Geodesic omerc_inverse(Crs *crs, Geodesic *xya){
	Geodesic lla;
	Coef coef;
	coef = omerc_coef(crs->datum.ellipsoid.a, crs->datum.ellipsoid.e, crs->lambda0, crs->phi0, crs->k0, crs->azimut);
	return lla;
}
