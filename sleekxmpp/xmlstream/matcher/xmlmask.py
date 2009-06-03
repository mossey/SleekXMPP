from . import base
from xml.etree import cElementTree
from xml.parsers.expat import ExpatError

class MatchXMLMask(base.MatcherBase):

	def __init__(self, criteria):
		base.MatcherBase.__init__(self, criteria)
		if type(criteria) == type(''):
			self._criteria = cElementTree.fromstring(self._criteria)
		self.default_ns = 'jabber:client'
	
	def setDefaultNS(self, ns):
		self.default_ns = ns

	def match(self, xml):
		return self.maskcmp(xml, self._criteria, True)
	
	def maskcmp(self, source, maskobj, use_ns=False, default_ns='__no_ns__'):
		"""maskcmp(xmlobj, maskobj):
		Compare etree xml object to etree xml object mask"""
		#TODO require namespaces
		if source == None: #if element not found (happens during recursive check below)
			return False
		if type(maskobj) == type(str()): #if the mask is a string, make it an xml obj
			try:
				maskobj = cElementTree.fromstring(maskobj)
			except ExpatError:
				logging.log(logging.WARNING, "Expat error: %s\nIn parsing: %s" % ('', maskobj))
		if not use_ns and source.tag.split('}', 1)[-1] != maskobj.tag.split('}', 1)[-1]: # strip off ns and compare
			return False
		if use_ns and (source.tag != maskobj.tag and "{%s}%s" % (self.default_ns, maskobj.tag) != source.tag ):
			return False
		if maskobj.text and source.text != maskobj.text:
			return False
		for attr_name in maskobj.attrib: #compare attributes
			if source.attrib.get(attr_name, "__None__") != maskobj.attrib[attr_name]:
				return False
		#for subelement in maskobj.getiterator()[1:]: #recursively compare subelements
		for subelement in maskobj: #recursively compare subelements
			if not self.maskcmp(source.find(subelement.tag), subelement, use_ns):
				return False
		return True
