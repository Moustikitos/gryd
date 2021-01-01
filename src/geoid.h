// Copyright (c) 2015-2021, THOORENS Bruno
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

#if __linux__ 
    #define EXPORT extern
#elif _WIN32
    #define _USE_MATH_DEFINES // for C
    #define EXPORT __declspec(dllexport)
#endif

#include <math.h>
#include <stdlib.h>

static double HALF_PI = M_PI/2;
static double TWO_PI = M_PI*2;
static double DEGREE2RAD = M_PI/180.0;
static double RADIAN2DEG = 180.0/M_PI;
static double ARCSEC2RAD = M_PI/648000;
static double EPS = 1e-10;
static int MAX_ITER = 100;

typedef struct{
    int epsg;
    double ratio;
}Unit;

typedef struct{
    int epsg;
    double longitude;
}Prime;

typedef struct{
    int epsg;
    double a;
    double b;
    double e;
    double f;
}Ellipsoid;

typedef struct{
    Ellipsoid ellipsoid;
    Prime prime;
    int epsg;
    double ds;
    double dx;
    double dy;
    double dz;
    double rx;
    double ry;
    double rz;
}Datum;

typedef struct{
    Datum datum;
    Unit unit;
    int epsg;
    double lambda0;
    double phi0;
    double phi1;
    double phi2;
    double k0;
    double x0;
    double y0;
    double azimut;
}Crs;

typedef struct{
    double distance;
    double initial_bearing;
    double final_bearing;
}Vincenty_dist;

typedef struct{
    double longitude;
    double latitude;
    double destination_bearing;
}Vincenty_dest;

typedef struct{
    double x;
    double y;
    double z;
}Geocentric;

typedef struct{
    double x;
    double y;
    double altitude;
}Geographic;

typedef struct{
    double longitude;
    double latitude;
    double altitude;
}Geodesic;

typedef struct{
    double px;
    double py;
    Geodesic lla;
    Geographic xya;
}Point;

typedef struct{
    short sign;
    double degree;
    double minute;
    double second;
}Dms;

typedef struct{
    short sign;
    double degree;
    double minute;
}Dmm;

static long factorial(long n){
    long result = 1;
    if (n < 0) return -1;
    while (n > 1) result = result*n--;
    return result;
}

/*
Source :
The Mercator projections, Peter Osborne, 2008
§ Chapter 5. The geometry of the ellipsoid
*/
static double nhu(double a, double e, double latitude) {return a / sqrt(1 - pow(e * sin(latitude),2));}
static double p(double a, double e, double latitude) {return cos(latitude) * nhu(a, e, latitude);}
static double rho(double a, double e, double latitude) {return  a * (1-e*e) / pow(1 - pow(e * sin(latitude), 2), 1.5);}
static double isometric_latitude(double e, double latitude){return log(tan(M_PI/4 + latitude/2) * pow((1-e*sin(latitude))/(1+e*sin(latitude)), e/2));}

static double geodesic_latitude(double e, double iso_phi){
    double phi_i, sinphi_i, phi_ip1;
    int i = 0;
    phi_i = 2 * atan(exp(iso_phi)) - M_PI/2;
    sinphi_i = sin(phi_i);
    phi_ip1 = 2 * atan(pow((1+e*sinphi_i)/(1-e*sinphi_i), e/2) * exp(iso_phi)) - M_PI/2;

    while ((fabs(phi_i - phi_ip1) > EPS) && (i < MAX_ITER)){
        phi_i = phi_ip1;
        sinphi_i = sin(phi_i);
        phi_ip1 = 2 * atan(pow((1+e*sinphi_i)/(1-e*sinphi_i), e/2) * exp(iso_phi)) - M_PI/2;
        i += 1;
    }

    return phi_ip1;
}

static double meridian_distance(double a, double e, double latitude){
    double e2, e4, e6, e8;
    double A0, A2, A4, A6, A8;

    e2 = pow(e, 2); e4 = pow(e, 4); e6 = pow(e, 6); e8 = pow(e, 8);
    A0 = 1 - e2/4 - 3*e4/64 - 5*e6/256 - 175*e8/16384;
    A2 = -3*e2/8 - 3*e4/32 - 45*e6/1024 - 420*e8/16384;
    A4 = 15*e4/256 + 45*e6/1024 + 525*e8/16384;
    A6 = -35*e6/3072 - 175*e8/12288;
    A8 = 315*e8/131072;

    return a * (A0*latitude + A2*sin(2*latitude) + A4*sin(4*latitude) + A6*sin(6*latitude) + A8*sin(8*latitude));
}

static double footpoint_latitude(double a, double e, double distance){
    double phi_ip1, phi_i;
    int i = 0;
    phi_ip1 = distance/a;
    phi_i = -phi_ip1;

    while ((fabs(phi_i - phi_ip1) > EPS) && (i < MAX_ITER)){
        phi_i = phi_ip1;
        phi_ip1 = phi_i - (meridian_distance(a, e, phi_i) - distance)/a;
        i += 1;
    }

    return phi_ip1;
}
