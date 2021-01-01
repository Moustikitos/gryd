// Copyright (c) 2015-2016, THOORENS Bruno
// All rights reserved.
#include "./geoid.h"

// y = a * 5/4 * ln(tan(pi/4 + 2phi/5)) : forward formula
// 4y/5a = ln(tan(pi/4 + 2phi/5))
// exp(4y/5a) = tan(pi/4 + 2phi/5)
// atan(exp(4y/5a)) = pi/4 + 2phi/5
// atan(exp(4y/5a)) - pi/4 = 2phi/5
// 5/2 * (atan(exp(4y/5a)) - pi/4) = phi : reverse formula

EXPORT Geographic miller_forward(Crs *crs, Geodesic *lla){
	Geographic xya;

	xya.x = crs->datum.ellipsoid.a * (lla->longitude - crs->lambda0) + crs->x0;
	xya.y = crs->datum.ellipsoid.a * 1.25 * log(tan(M_PI/4 + 0.4*lla->latitude)) + crs->y0;
	xya.altitude = lla->altitude;

	return xya;
}

EXPORT Geodesic miller_inverse(Crs *crs, Geographic *xya){
	Geodesic lla;

	lla.longitude = (xya->x - crs->x0)/crs->datum.ellipsoid.a + crs->lambda0;
	lla.latitude = 2.5 * (atan(exp(0.8*(xya->y - crs->y0)/crs->datum.ellipsoid.a)) - M_PI/4);
	lla.altitude = xya->altitude;

	return lla;
}
