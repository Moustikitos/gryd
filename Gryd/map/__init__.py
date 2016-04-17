# -*- encoding:utf-8 -*-
'''
Copyright© 2015, THOORENS Bruno
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are not permitted.

 * Only the name of *THOORENS Bruno* may be used to endorse or promote products
   derived from this software.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

# import json, sqlitemap

# class GrydMap(sqlitemap.SqliteMapFile):
# 	ext = ".gmp"

# 	def __init__(self, *args, **kwargs):
# 		sqlitemap.SqliteMapFile.__init__(self, *args, **kwargs)
# 		self.cursor.execute("CREATE TABLE IF NOT EXISTS metadata(name TEXT, value TEXT);")
		
# 	#  metadata table management
# 	def __setitem__(self, item, value):
# 		self.cursor.execute("INSERT OR REPLACE INTO metadata(name, value) VALUES(?, ?);", (item, json.dumps(value)))

# 	def __getitem__(self, item):
# 		try: return json.loads(self.cursor.execute("SELECT * FROM metadata WHERE name=?;", (item,)).fetchall()[0]["value"])
# 		except: raise KeyError('metadata table does not have "%s" key' % item)

# 	def __delitem__(self, item):
# 		self.cursor.execute("DELETE FROM metadata WHERE name=?", (item,))

# 	def clear_metadata(self):
# 		self.cursor.execute("DELETE FROM metadata;")



# class Raster:

# 	def __init__(self, rst, **kw):
# 		pass

