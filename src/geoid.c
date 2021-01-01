// Copyright (c) 2015-2016, THOORENS Bruno
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without modification,
// are permitted provided that the following conditions are met:
//
//  * Redistributions of source code must retain the above copyright notice, this
//    list of conditions and the following disclaimer.
//  * Redistributions in binary form must reproduce the above copyright notice,
//    this list of conditions and the following disclaimer in the documentation and/or
//    other materials provided with the distribution.
//  * Neither the name of the *Gryd* nor the names of its contributors may be
//    used to endorse or promote products derived from this software without specific
//    prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
// FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
// CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
// OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#include "./geoid.h"
#include <stdlib.h>

EXPORT double MD(double a, double e, double latitude){return meridian_distance(a,e,latitude);}

EXPORT Dms dms(double value){
	Dms result;
	double degrees, minutes, seconds;

	if (value < 0) result.sign = 0;
	else result.sign = 1;
	value = fmod(fabs(value), 360);

	degrees = floor(value);
	minutes = (value - degrees) * 60;
	seconds = (minutes - floor(minutes)) * 60;
	minutes = floor(minutes);

	if (seconds >= (60. - EPS)){seconds = 0; minutes = minutes+1;}
	if (minutes >= (60. - EPS)){minutes = 0; degrees = degrees+1;}

	result.degree = degrees;
	result.minute = minutes;
	result.second = seconds;

	return result;
}

EXPORT Dmm dmm(double value){
	Dmm result;
	double degrees, minutes;

	if (value < 0) result.sign = 0;
	else result.sign = 1;
	value = fmod(fabs(value), 360);

	degrees = floor(value);
	minutes = (value - degrees) * 60;

	if (minutes >= (60. - EPS)){minutes = 0; degrees = degrees+1;}

	result.degree = degrees;
	result.minute = minutes;

	return result;
}

/*
Source :
The Mercator projections, Peter Osborne, 2008
� Chapter 5. The geometry of the ellipsoid
*/
EXPORT Geocentric geocentric(Ellipsoid *ellps, Geodesic *lla){
	Geocentric result;
	double v;

	v = nhu(ellps->a, ellps->e, lla->latitude);
	result.x = (v+lla->altitude) * cos(lla->latitude) * cos(lla->longitude);
	result.y = (v+lla->altitude) * cos(lla->latitude) * sin(lla->longitude);
	result.z = (v * (1 - pow(ellps->e,2)) + lla->altitude) * sin(lla->latitude);

	return result;
}

EXPORT Geodesic geodesic(Ellipsoid *ellps, Geocentric *xyz){
	Geodesic result;
	double sqrt_xxpyy, phi_i, phi_ip1, e2;
	int i = 0;

	e2 = ellps->e*ellps->e;
	sqrt_xxpyy = sqrt(xyz->x*xyz->x + xyz->y*xyz->y);
	phi_i = atan2(xyz->z, ((1 - e2) * sqrt_xxpyy));
	phi_ip1 = atan2((xyz->z + e2 * nhu(ellps->a, ellps->e, phi_i) * sin(phi_i)), sqrt_xxpyy);

	while ((fabs(phi_i - phi_ip1) > EPS) && (i < MAX_ITER)){
		phi_i = phi_ip1;
		phi_ip1 = atan2((xyz->z + e2 * nhu(ellps->a, ellps->e, phi_i) * sin(phi_i)), sqrt_xxpyy);
		i += 1;
	}

	result.longitude = atan2(xyz->y, xyz->x);
	result.latitude = phi_ip1;
	result.altitude = 1/cos(phi_ip1) * sqrt_xxpyy - nhu(ellps->a, ellps->e, phi_ip1);

	return result;
}

/*
Source :
http://www.movable-type.co.uk/scripts/latlong-vincenty-direct.html
*/
EXPORT Vincenty_dist distance(Ellipsoid *ellps, Geodesic *start, Geodesic *stop){ 
	Vincenty_dist result;
	double x, xp1;
	double L, U1, U2, sU1, cU1, sU2, cU2, A, B, C, u2, k1;
	double sx, cx, ssigma, csigma, sigma, salpha, calpha2, c2sigma_m, Dsigma;
	int i = 0;

	result.distance = 0;
	result.initial_bearing = 0;
	result.final_bearing = 0;

	L = stop->longitude - start->longitude; x = L; xp1 = L+1;
	U1 = atan((1-ellps->f) * tan(start->latitude)); U2 = atan((1-ellps->f) * tan(stop->latitude));
	cU1 = cos(U1); sU1 = sin(U1); cU2 = cos(U2); sU2 = sin(U2);

	while ((fabs(x - xp1) > EPS) && (i < MAX_ITER)){
		sx = sin(x); cx = cos(x);
		ssigma = sqrt(pow(cU2*sx, 2) + pow(cU1*sU2 - sU1*cU2*cx, 2));
		if (ssigma < EPS) return result;
		csigma = sU1*sU2 + cU1*cU2*cx;
		sigma = atan2(ssigma, csigma);
		salpha = cU1*cU2*sx / ssigma;
		calpha2 = 1 - pow(salpha, 2);
		if (calpha2 < EPS){
			c2sigma_m = 0.;}else{
			c2sigma_m = csigma - 2*sU1*sU2/calpha2;
		}
		C = ellps->f/16*calpha2 * (4 + ellps->f*(4-3*calpha2));
		xp1 = x;
		x = L + (1-C)*ellps->f*salpha*(sigma + C*ssigma*(c2sigma_m + C*csigma*(-1+2*c2sigma_m*c2sigma_m)));
		i += 1;
	}
	u2 = calpha2 * (ellps->a*ellps->a - ellps->b*ellps->b) / pow(ellps->b, 2);
	k1 = (sqrt(1+u2)-1) / (sqrt(1+u2)+1);
	A = (1 + 0.25*k1*k1) / (1-k1);
	B = k1 * (1 - 0.375*k1*k1);
	Dsigma = B*ssigma * (c2sigma_m + B/4*(csigma*(-1 + 2*c2sigma_m*c2sigma_m) - B/6*c2sigma_m*(-3 + 4*ssigma*ssigma)*(-3 + 4*c2sigma_m*c2sigma_m)));

	result.distance = ellps->b*A*(sigma - Dsigma);
	result.initial_bearing = atan2(cU2*sx, (cU1*sU2 - sU1*cU2*cx));
	result.final_bearing = atan2(cU1*sx, (-sU1*cU2 + cU1*sU2*cx));

	return result;
}

EXPORT Vincenty_dest destination(Ellipsoid *ellps, Geodesic *start, Vincenty_dist *dbb){
	Vincenty_dest result;
	double lambda, phi2;
	double tU1, cU1, sU1, sigma, sigma1, sigma_p, salpha, calpha2, u2, A, B;
	double c2sigma_m, Dsigma, ssigma, csigma, C, L, tmp;
	double calpha1, salpha1;
	int i = 0;

	calpha1 = cos(dbb->initial_bearing); salpha1 = sin(dbb->initial_bearing);
	tU1 = (1-ellps->f)*tan(start->latitude);
	cU1 = 1/sqrt(1 + tU1*tU1); sU1 = tU1*cU1;
	sigma1 = atan2(tU1, calpha1);
	salpha = cU1*salpha1;
	calpha2 = 1 - salpha*salpha;
	u2 = calpha2 * (ellps->a*ellps->a - ellps->b*ellps->b) / (ellps->b*ellps->b);
	A = 1 + u2/16384 * (4096 + u2*(-768 + u2*(320-175*u2)));
	B = u2/1024 * (256 + u2*(-128 + u2*(74 - 47*u2)));
	sigma = dbb->distance / (ellps->b*A); sigma_p = 2*M_PI;

	while ((fabs(sigma - sigma_p) > EPS) && (i < MAX_ITER)){
		c2sigma_m = cos(2*sigma1 + sigma);
		ssigma = sin(sigma);
		csigma = cos(sigma);
		Dsigma = B*ssigma*(c2sigma_m + B/4*(csigma*(-1 + 2*c2sigma_m*c2sigma_m) - B/6*c2sigma_m*(-3 +4*ssigma*ssigma)*(-3 +4*c2sigma_m*c2sigma_m)));
		sigma_p = sigma;
		sigma = dbb->distance / (ellps->b*A) + Dsigma;
		i += 1;
	}
	tmp = sU1*ssigma - cU1*csigma*calpha1;
	phi2 = atan2(sU1*csigma + cU1*ssigma*calpha1, (1-ellps->f)*sqrt(salpha*salpha + tmp*tmp));
	lambda = atan2(ssigma*salpha1, cU1*csigma - sU1*ssigma*calpha1);
	C = ellps->f/16 * calpha2*(4 + ellps->f*(4 - 3*calpha2));
	L = lambda - (1-C)*ellps->f*salpha*(sigma + C*ssigma*(c2sigma_m + C*csigma*(-1 + 2*c2sigma_m*c2sigma_m)));

	result.longitude = start->longitude + L;
	result.latitude = phi2;
	result.destination_bearing = atan2(salpha, -tmp);

	return result;
}

// EXPORT Geodesic dat2dat(Datum *src, Ellipsoid *ellps_src, Datum *dst, Ellipsoid *ellps_dst, Geodesic *lla){
EXPORT Geocentric dat2dat(Datum *src, Datum *dst, Geocentric *xyz){
	Geocentric result;
	double rx, ry, rz, ds;

	rx = (src->rx - dst->rx) * ARCSEC2RAD;
	ry = (src->ry - dst->ry) * ARCSEC2RAD;
	rz = (src->rz - dst->rz) * ARCSEC2RAD;
	ds = (src->ds - dst->ds) / 1000000.0;

	result.x = (src->dx - dst->dx) + (1+ds)*(    xyz->x - rz*xyz->y + ry*xyz->z);
	result.y = (src->dy - dst->dy) + (1+ds)*( rz*xyz->x +    xyz->y - rx*xyz->z);
	result.z = (src->dz - dst->dz) + (1+ds)*(-ry*xyz->x + rx*xyz->y +    xyz->z);

	return result;
}

EXPORT Vincenty_dest * npoints(Ellipsoid *ellps, Geodesic *lla0, Geodesic *lla1, int n){
	Vincenty_dist dbb;
	Geodesic lla;
	Vincenty_dest llb, *result;
	double step;
	int i;

	result = malloc((n+2)*sizeof(Vincenty_dest));
	dbb = distance(ellps, lla0, lla1);
	step = dbb.distance/(n+1);

	llb.longitude = lla0->longitude;
	llb.latitude = lla0->latitude;
	llb.destination_bearing = dbb.initial_bearing;

	result[0] = llb;
	dbb.distance = step;
	for (i=1;i<n+2;i++){
		lla.longitude = llb.longitude;
		lla.latitude = llb.latitude;
		dbb.initial_bearing = llb.destination_bearing;
		llb = destination(ellps, &lla, &dbb);
		result[i] = llb;
	}

	return result;
}


EXPORT double lagrange(double x, double *nx, double *ny, int n){
	double result, xi, xj, p;
	int i, j;

	result = 0;
	for(j=0; j<n; j++){
		p = 1;
		for (i=0; i<n; i++){
			if (i != j){
				xi = nx[i];
				xj = nx[j];
				if (xj != xi) p *= (x - xi)/(xj - xi);
			}
		}
		result += ny[j] * p;
	}

	return result;
}
