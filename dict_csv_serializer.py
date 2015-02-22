import csv

class CSVDictList(object):
  class CSVListEntry(object):
    def __init__(self, d, parent):
      self.__dictionary = d
      self.__parent = parent
      
    def __getitem__(self, n):
      if n in self.__dictionary:
        return self.__dictionary[n]
      else:
        return None
        
    def __setitem__(self, n, v):
      parent._makeHeader(n)
      self.__dictionary[n] = v
  
  def __init__(self):
    self.__headers = []
    self.__entries = []
    
  @property
  def headers(self):
    return list(self.__headers)
    
  def _makeHeader(self, name):
    if name not in self.__headers:
      self.__headers.append(name)
    
  def load(self, filename):
    with open(filename, "rb") as f:
      csvreader = csv.reader(f)
      newHeaders = csvreader.next()
      newEntries = []
      
      for lineCounter, csvline in enumerate(csvreader):
        if len(csvline) > len(newHeaders):
          raise ValueError("More columns than headers in line {}".format(lineCounter + 2))
        newEntries.append(self.CSVListEntry(dict(zip(newHeaders, [(None if v == "" else v.decode('utf-8')) for v in csvline] + [None] * (len(newHeaders) - len(csvline)))), self))
    self.__headers = newHeaders
    self.__entries = newEntries
    
  def save(self, filename):
    with open(filename, "wb") as f:
      csvwriter = csv.writer(f)
      csvwriter.writerow(self.__headers)
      for entry in self:
        csvwriter.writerow([('' if entry[h] is None else entry[h].encode('utf-8')) for h in self.__headers])
      
  def __getitem__(self, i):
    return self.__entries[i]

  def __getslice__(self, slice):
    return self.__entries.__getslice__(slice)

  def __iter__(self):
    return iter(self.__entries)

  def __len__(self):
    return len(self.__entries)
