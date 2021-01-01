// Copyright (c) 2015-2021, THOORENS Bruno
// All rights reserved.
#include "./geoid.h"

EXPORT Geographic merc_forward(Crs *crs, Geodesic *lla){
	Geographic xya;
	double ak0;

	ak0 = cos(fabs(crs->phi1)) * nhu(crs->datum.ellipsoid.a, crs->datum.ellipsoid.e, crs->phi1);
	xya.x = crs->x0 + crs->k0 * ak0 * (lla->longitude - crs->lambda0);
	xya.y = crs->k0 * ak0 * isometric_latitude(crs->datum.ellipsoid.e, lla->latitude - crs->phi0) + crs->y0;
	xya.altitude = lla->altitude;

	return xya;
}

EXPORT Geodesic merc_inverse(Crs *crs, Geographic *xya){
	Geodesic lla;
	double ak0;

	ak0 = cos(fabs(crs->phi1)) * nhu(crs->datum.ellipsoid.a, crs->datum.ellipsoid.e, crs->phi1);
	lla.longitude = (xya->x - crs->x0)/(ak0 * crs->k0) + crs->lambda0;
	lla.latitude = geodesic_latitude(crs->datum.ellipsoid.e, (xya->y - crs->y0)/(ak0 * crs->k0)) + crs->phi0;
	lla.altitude = xya->altitude;

	return lla;
}
