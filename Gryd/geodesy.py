# -*- encoding:utf-8 -*-
import math
import hashlib
import ctypes

from Gryd import geohash as geoH

_TORAD = math.pi / 180.0
_TODEG = 180.0 / math.pi


def base32(secret):
    """
    Return a 32-length of unique bytes from secret hash.
    """
    secret = secret if isinstance(secret, bytes) else secret.encode("utf-8")
    base = bytearray(b"0123456789bcdefghjkmnpqrstuvwxyz")
    h = bytearray(hashlib.sha256(secret).digest())
    newbase = bytearray([b for b in h if h.count(b) == 1])
    newbase.extend(bytearray(b for b in base if b not in newbase))
    return bytes(newbase[:32])


class Geodesic(ctypes.Structure):
    """
    `ctypes` structure for geodesic coordinates

    Attributes:
        longitude (float): longitude value of geodesic coordinates in degrees
        latitude (float): latitude value of geodesic coordinates in degrees
        altitude (float): elevation of the geodesic coordinates in meters

    ```python
    >>> dublin = Gryd.Geodesic(-6.272877, 53.344606, 105.)
    >>> dublin
    <lon=-006°16'22.357" lat=+053°20'40.582" alt=105.000>
    ```
    """
    _fields_ = [
        ("longitude", ctypes.c_double),
        ("latitude",  ctypes.c_double),
        ("altitude",  ctypes.c_double)
    ]

    def __init__(self, *args, **kwargs):
        args = list(args)
        for i in range(min(2, len(args))):
            args[i] *= _TORAD
        for key in [k for k in kwargs if k in ["longitude", "latitude"]]:
            kwargs[key] *= _TORAD
        ctypes.Structure.__init__(self, *args, **kwargs)

    def __repr__(self):
        return "<lon=%.6f lat=%.6f alt=%.3f>" % (
            self.longitude * _TODEG, self.latitude * _TODEG, self.altitude
        )

    def encrypt(self, digit, secret):
        """
        Encrypt geodesic coordinates. It uses geohash with a custom
        32-length base initialized by `Gryd.geodesy.base32`.

        ```python
        >>> g = Gryd.geodesy.Geodesic(-5.412300, 45.632100)
        >>> g.encrypt(23, "secret")
        b'\xbda\xe0\xa3\xe9\xbd\x1d\x86\xe0_a1\x8bV2\xe0aV\xbd2\xcd\xe0\xe0'
        ```

        Arguments:
            digit (int): result bytes-length
            secret (bytes or str): secret used to encrypt geodesic coordinates
        Returns:
            `bytes` data
        """
        return geoH.to_geohash(
            self.longitude * _TODEG,
            self.latitude * _TODEG,
            digit, base32(secret)
        )

    @staticmethod
    def decrypt(encrypted, secret):
        """
        Decrypt geodesic from encrypted. It uses geohash with a custem
        32-length base initialized by `Gryd.geodesy.base32`.

        ```python
        >>> enc = b'\xbda\xe0\xa3\xe9\xbd\x1d\x86\xe0_a1\x8bV2\xe0aV\xbd2\xcd'\
        ...       b'\xe0\xe0'
        >>> geo.Geodesic.decrypt(enc, "secret")
        <lon=-5.412300 lat=45.632100 alt=0.000>
        ```

        Arguments:
            encrypted (bytes): encrypted geodesic coordinates
            secret (bytes or str): secret used to encrypt geodesic coordinates
        Returns:
            `Gryd.geodesy.Geodesic` coordinates
        """
        lon, lat, precision = geoH.from_geohash(
            encrypted, base32(secret), centered=True
        )
        result = Geodesic(lon, lat)
        setattr(result, "precision", precision)
        return result

    def geohash(self, digit=10):
        """
        Convert coordinates to geohash.

        ```python
        >>> dublin.geohash() # by default on 10 digit for metric precision
        'gc7x3r04z7'
        >>> dublin.geohash(14) # why not on 14 digit for millimetric precision
        'gc7x3r04z77csw'
        ```

        Arguments:
            digit (int): total digit to use in the geohash
        Returns:
            Geohash `str`
        """
        return geoH.to_geohash(
            self.longitude * _TODEG,
            self.latitude * _TODEG,
            digit
        )

    @staticmethod
    def from_geohash(geoh):
        """
        Return Geodesic object geohash.

        ```python
        >>> Gryd.Geodesic.from_geohash('gc7x3r04z7')
        <lon=-006°16'22.347" lat=+053°20'40.590" alt=0.000>
        >>> Gryd.Geodesic.from_geohash('gc7x3r04z77csw')
        <lon=-006°16'22.357" lat=+053°20'40.582" alt=0.000>
        ```

        Arguments:
            geoh (str): georef string
        Returns:
            `Gryd.geodesy.Geodesic` coordinates
        """
        lon, lat, precision = geoH.from_geohash(geoh, centered=True)
        result = Geodesic(lon, lat)
        setattr(result, "precision", precision)
        return result

    def maidenhead(self, level=4):
        """
        Convert coordinates to maidenhead.

        ```python
        >>> dublin.maidenhead()
        'IO63ui72gq'
        >>> dublin.maidenhead(level=6)
        'IO63ui72gq19dh'
        ```

        Arguments:
            level (int): precision level of maidenhead
        Returns:
            Maidenhead `str`
        """
        base = "ABCDEFGHIJKLMNOPQRSTUVWX"
        longitude = (self.longitude * _TODEG + 180) % 360
        latitude = (self.latitude * _TODEG + 90) % 180

        result = ""

        lon_idx = longitude / 20
        lat_idx = latitude / 10
        result += \
            base[int(math.floor(lon_idx))] + \
            base[int(math.floor(lat_idx))]

        coef = 10.
        for i in range(level):
            lon_idx = (lon_idx - math.floor(lon_idx)) * coef
            lat_idx = (lat_idx - math.floor(lat_idx)) * coef
            if coef == 10.:
                result += "%d%d" % (math.floor(lon_idx), math.floor(lat_idx))
            else:
                result += (
                    base[int(math.floor(lon_idx))] +
                    base[int(math.floor(lat_idx))]
                ).lower()
            coef = 24. if coef == 10. else 10.

        return result

    @staticmethod
    def from_maidenhead(maidenhead):
        """
        Return Geodesic object from maidenhead string.

        Arguments:
            maidenhead (str): maidenhead string
        Returns:
            `Gryd.geodesy.Geodesic` coordinates
        """
        base = "ABCDEFGHIJKLMNOPQRSTUVWX"
        longitude = latitude = 0
        eps = 18./2.
        lon_str = list(reversed(maidenhead[0::2].upper()))
        lat_str = list(reversed(maidenhead[1::2].upper()))

        for i, j in zip(lon_str[:-1], lat_str[:-1]):
            if i in "0123456789":
                longitude = (longitude + int(i)) / 10.
                latitude = (latitude + int(j)) / 10.
                eps /= 10.
            else:
                longitude = (longitude + base.index(i)) / 24.
                latitude = (latitude + base.index(j)) / 24.
                eps /= 24.

        longitude = (longitude + base.index(lon_str[-1])) * 20. + eps
        latitude = (latitude + base.index(lat_str[-1])) * 10. + eps

        result = Geodesic(longitude=longitude-180, latitude=latitude-90)
        setattr(result, "precision", (eps, eps))
        return result

    def georef(self, digit=8):
        """
        Convert coordinates to georef.

        ```python
        >>> dublin.georef()
        'MKJJ43322037'
        >>> dublin.georef(digit=6)
        'MKJJ433203'
        ```

        Arguments:
            digit (int): digit number of georef (can be 4, 6 or 8)
        Returns:
            Georef `str`
        """
        base = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        longitude = (self.longitude*_TODEG + 180) % 360
        latitude = (self.latitude*_TODEG + 90) % 180

        result = ""

        lon_idx = longitude / 15.
        lat_idx = latitude / 15.
        result += \
            base[int(math.floor(lon_idx))] + \
            base[int(math.floor(lat_idx))]

        lon_idx = (lon_idx - math.floor(lon_idx)) * 15.
        lat_idx = (lat_idx - math.floor(lat_idx)) * 15.
        result += \
            base[int(math.floor(lon_idx))] + \
            base[int(math.floor(lat_idx))]

        lon_idx = (lon_idx - math.floor(lon_idx)) * 60.
        lat_idx = (lat_idx - math.floor(lat_idx)) * 60.

        lon = "%02d" % lon_idx
        lat = "%02d" % lat_idx

        if digit == 6:
            lon_idx = 10 - (lon_idx - math.floor(lon_idx)) * 10.
            lat_idx = 10 - (lat_idx - math.floor(lat_idx)) * 10.
            lat += "%01d" % math.floor(lon_idx)
            lon += "%01d" % math.floor(lat_idx)
        elif digit == 8:
            lon_idx = 100 - (lon_idx - math.floor(lon_idx)) * 100.
            lat_idx = 100 - (lat_idx - math.floor(lat_idx)) * 100.
            lat += "%02d" % math.floor(lon_idx)
            lon += "%02d" % math.floor(lat_idx)

        return result + lon + lat

    @staticmethod
    def from_georef(georef):
        """
        Return Geodesic object from georef.

        ```python
        >>> Gryd.Geodesic.from_georef('MKJJ43322037')
        <lon=-006°16'21.900" lat=+053°20'41.100" alt=0.000>
        >>> Gryd.Geodesic.from_georef('MKJJ433220')    
        <lon=-006°15'57.000" lat=+053°22'45.000" alt=0.000>
        ```

        Arguments:
            georef (str): georef string
        Returns:
            `Gryd.geodesy.Geodesic` coordinates
        """
        base = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        eps = 1./2./60.

        if len(georef) == 12:
            longitude = (1-int(georef[10:])/100. + int(georef[4:6]))/60.
            latitude = (1-int(georef[6:8])/100. + int(georef[8:10]))/60.
            eps /= 100.
        elif len(georef) == 10:
            longitude = (1-int(georef[9])/10. + int(georef[4:6]))/60.
            latitude = (1-int(georef[6])/10. + int(georef[7:9]))/60.
            eps /= 10.
        else:
            longitude = int(georef[4:6])/60.
            latitude = int(georef[6:])/60.

        longitude = (
            (longitude + base.index(georef[2])) / 15. + base.index(georef[0])
        ) * 15. + eps
        latitude = (
            (latitude + base.index(georef[3])) / 15. + base.index(georef[1])
        ) * 15. + eps

        result = Geodesic(longitude=longitude - 180, latitude=latitude - 90)
        setattr(result, "precision", (eps, eps))
        return result

    def gars(self):
        """
        Get the associated GARS Area (5minx5min tile).

        ```python
        >>> dublin.gars()
        '348MY16'
        ```
        """
        base = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        longitude = (self.longitude*_TODEG+180) % 360
        latitude = (self.latitude*_TODEG+90) % 180

        lon_idx = longitude / 0.5
        lat_idx = latitude / 0.5

        quadrant = \
            "%03d" % (lon_idx+1) + \
            base[int(math.floor(lat_idx // 24))] + \
            base[int(math.floor(lat_idx % 24))]

        lon_num_idx = (lon_idx - math.floor(lon_idx)) * 2.
        lat_num_idx = (lat_idx - math.floor(lat_idx)) * 2.
        j = math.floor(lon_num_idx)
        i = 1-math.floor(lat_num_idx)
        number = i*(j+1)+j+1

        lon_key_idx = (lon_num_idx - math.floor(lon_num_idx)) * 3.
        lat_key_idx = (lat_num_idx - math.floor(lat_num_idx)) * 3.
        j = math.floor(lon_key_idx)
        i = 2-math.floor(lat_key_idx)
        key = i*(j+1)+j+1

        return quadrant + str(number) + str(key)

    @staticmethod
    def from_gars(gars, anchor=""):
        """
        Return Geodesic object from gars. Optional anchor value to define
        where to handle 5minx5min tile.

        ```python
        >>> Gryd.Geodesic.from_gars('348MY16', anchor="nw")
        <lon=-006°20'0.000" lat=+053°25'0.000" alt=0.000>
        >>> Gryd.Geodesic.from_gars('348MY16')
        <lon=-006°17'30.000" lat=+053°22'30.000" alt=0.000>
        ```

        Arguments:
            gars (str): gars string
            anchor (str): tile anchor (nesw)
        Returns:
            `Gryd.geodesy.Geodesic` coordinates
        """
        base = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        longitude = 5. / 60. * (
            0 if "w" in anchor else 1 if "e" in anchor else 0.5
        )
        latitude = 5. / 60. * (
            0 if "s" in anchor else 1 if "n" in anchor else 0.5
        )

        key = gars[6]
        longitude += 5. / 60. * (
            0 if key in "147" else 1 if key in "258" else 2
        )
        latitude += 5. / 60. * (
            0 if key in "789" else 1 if key in "456" else 2
        )

        number = gars[5]
        longitude += 15. / 60. * (0 if number in "13" else 1)
        latitude += 15. / 60. * (0 if number in "34" else 1)

        longitude += (int(gars[:3])-1) * 0.5
        latitude += (base.index(gars[3]) * 24 + base.index(gars[4])) * 0.5

        return Geodesic(longitude=longitude - 180, latitude=latitude - 90)


    # def dump_location(self, tilename, zoom=15, size="256x256", mcolor="0xff00ff", format="png", scale=1):
    #     latitude, longitude = self.latitude, self.longitude
    #     try:
    #         urllib.urlretrieve(
    #             "https://maps.googleapis.com/maps/api/staticmap?center=%s,%s&zoom=%s&size=%s&markers=color:%s%%7C%s,%s&format=%s&scale=%s" % (
    #                 latitude, longitude, zoom, size, mcolor, latitude, longitude, format, scale
    #             ),
    #             os.path.splitext(tilename)[0] + "."+format
    #         )
    #     except:
    #         pass
