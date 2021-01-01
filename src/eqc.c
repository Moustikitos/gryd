// Copyright (c) 2015-2016, THOORENS Bruno
// All rights reserved.
#include "./geoid.h"

EXPORT Geographic eqc_forward(Crs *crs, Geodesic *lla){
	Geographic xya;

	xya.x = cos(crs->phi1)*(lla->longitude - crs->lambda0)*crs->datum.ellipsoid.a + crs->x0;
	xya.y = (lla->latitude - crs->phi0)*crs->datum.ellipsoid.a + crs->y0;
	xya.altitude = lla->altitude;

	return xya;
}

EXPORT Geodesic eqc_inverse(Crs *crs, Geographic *xya){
	Geodesic lla;

	lla.longitude = (xya->x - crs->x0)/(cos(crs->phi1)*crs->datum.ellipsoid.a) + crs->lambda0;
	lla.latitude = (xya->y - crs->y0)/crs->datum.ellipsoid.a + crs->phi0;
	lla.altitude = xya->altitude;

	return lla;
}
