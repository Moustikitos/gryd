// Copyright (c) 2015-2021, THOORENS Bruno
// All rights reserved.
#include "./geoid.h"

static void coef(double *result, double a, double e, double lambda0, double phi0, double phi1, double phi2, double x0, double y0, double k0){
	double nhu_phi1, iso_phi1, nhu_phi2, iso_phi2;
	double n, c, xs, ys;
	double iso_phi0, nhu_phi0;

	iso_phi0 = isometric_latitude(e, phi0);

	if (phi1 != phi2){
		nhu_phi1 = nhu(a, e, phi1);
		iso_phi1 = isometric_latitude(e, phi1);
		nhu_phi2 = nhu(a, e, phi2);
		iso_phi2 = isometric_latitude(e, phi2);
		n = log(nhu_phi2 * cos(phi2)/(nhu_phi1 * cos(phi1))) / (iso_phi1 - iso_phi2);
		c = nhu_phi1 * cos(phi1)/n * exp(n*iso_phi1);
		xs = x0;
		if (fabs(phi0 - M_PI/2) < EPS){ys = y0;}
		else {ys = y0 + c*exp(-n*iso_phi0);}
	}else if (phi0 != 0){
		nhu_phi0 = nhu(a, e, phi0);
		n = sin(phi0);
		c = k0 * nhu_phi0 * (1.0/tan(phi0)) * exp(n * iso_phi0);
		xs = x0;
		ys = y0 + k0 * nhu_phi0 * (1.0/tan(phi0));
	}

	result[0] = lambda0;
	result[1] = n;
	result[2] = c;
	result[3] = xs;
	result[4] = ys;
}


EXPORT Geographic lcc_forward(Crs *crs, Geodesic *lla){
	Geographic xya;
	double L, result[5];

	coef(result, crs->datum.ellipsoid.a, crs->datum.ellipsoid.e, crs->lambda0, crs->phi0, crs->phi1, crs->phi2, crs->x0, crs->y0, crs->k0);
	L = isometric_latitude(crs->datum.ellipsoid.e, lla->latitude);

	xya.x = result[3] + result[2]*exp(-result[1]*L) * sin(result[1]*(lla->longitude-result[0]));
	xya.y = result[4] - result[2]*exp(-result[1]*L) * cos(result[1]*(lla->longitude-result[0]));
	xya.altitude = lla->altitude;

	return xya;
}

EXPORT Geodesic lcc_inverse(Crs *crs, Geographic *xya){
	Geodesic lla;
	double R, v, result[5];

	coef(result, crs->datum.ellipsoid.a, crs->datum.ellipsoid.e, crs->lambda0, crs->phi0, crs->phi1, crs->phi2, crs->x0, crs->y0, crs->k0);
	R = sqrt(pow(xya->x-result[3], 2) + pow(xya->y-result[4], 2));
	v = atan2(xya->x-result[3], result[4]-xya->y);

	lla.longitude = result[0] + v/result[1];
	lla.latitude = geodesic_latitude(crs->datum.ellipsoid.e, -1/result[1] * log(fabs(R/result[2])));
	lla.altitude = xya->altitude;

	return lla;
}
