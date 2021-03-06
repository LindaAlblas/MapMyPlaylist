import rdflib
import re

class DBPediaScanner:
	""" Uses the rdflib wrapper to search DBPedia for an artist's
	location and geoinformation. Returns this information in appropriate
	formats using the methods below.

	"""
	DBONTO = rdflib.Namespace('http://dbpedia.org/ontology/') # Ontology rdflib Namespace
	ONTOLOGIES = (DBONTO.hometown, DBONTO.birthPlace) # Ontologies constant to check for location info

	labelPredicate = rdflib.term.URIRef(u'http://www.w3.org/2000/01/rdf-schema#label')
	latPredicate = rdflib.URIRef("http://www.w3.org/2003/01/geo/wgs84_pos#lat")
	longPredicate = rdflib.URIRef("http://www.w3.org/2003/01/geo/wgs84_pos#long")
	locationGraph = rdflib.Graph() # Graph to parse location object to

	def __init__(self, artist):
		""" Initialiser for the DBPediaScanner class. Takes the artist's
		name as a string.

		"""
		self.artistURI = rdflib.URIRef("http://dbpedia.org/resource/" + re.sub('\s+', '_', artist))
		print "Artist URI is:", self.artistURI
		self.artistGraph = rdflib.Graph()
		self.artistGraph.parse(self.artistURI)
		self.__checkDisambiguates()
		for ontology in self.ONTOLOGIES:
			try: # Checks to see if any objects of type ontology are found
				self.locationURI = self.artistGraph.objects(self.artistURI, ontology).next()
				print "Ontology of type", ontology, "found!"
				return
			except (StopIteration): # If none of this type found.
				print "No ontology of type", ontology, "found!"
		print "No locational info!"


	def artistLocationURI(self):
		""" Returns the artist's location URI as a string

		"""
		try:
			return str(self.locationURI)
		except AttributeError: # If locationURI hasn't been defined
			print "LocationURI not defined!"
			return None

	def artistLocationLabel(self):
		""" Returns the artists location label in English as
		a string

		"""
		try:
			self.locationGraph.parse(self.locationURI)
		except AttributeError: # If locationURI hasn't been defined
			print "LocationURI not defined!"
			return None
		try:
			hometown = self.locationGraph.preferredLabel(self.locationURI, lang=u'en')[0][1]
			print "English label found!"
			print "Hometown is", hometown
			return str(hometown)
		except IndexError: # If no labels in English are found
			print "No English label found!"
			try:
				hometown = self.locationGraph.objects(self.locationURI, self.labelPredicate).next()
				return str(hometown)
			except StopIteration: # If generator is empty
				print "Empty locationGraph!" 

	def artistLocationGeo(self):
		""" Returns artists hometown latitude and longitude as
		floats.

		"""
		try:
			lat = float(self.locationGraph.objects(self.locationURI, self.latPredicate).next())
			lon = float(self.locationGraph.objects(self.locationURI, self.longPredicate).next())
			print "Latitude is", lat
			print "Longitude is", lon
			return lat, lon
		except StopIteration: # If generator is empty
			print "No geodata!"
		except AttributeError: # If locationURI hasn't been defined
			print "LocationURI not defined!"

	def __checkDisambiguates(self):
		for stmt in self.artistGraph.objects(rdflib.URIRef(self.artistURI), self.DBONTO.wikiPageDisambiguates):
			disamb = str(stmt)
			if '(band)' in disamb:
				self.__updateGraph(stmt)
				print "Disambiguated to :", disamb
				break
			elif '(singer)' in disamb:
				self.__updateGraph(stmt)
				print "Disambiguated to :", disamb
				break
			elif '(group)' in disamb:
				self.__updateGraph(stmt)
				print "Disambiguated to :", disamb
				break
			elif '(musician)' in disamb:
				self.__updateGraph(stmt)
				print "Disambiguated to :", disamb
				break

	def __updateGraph(self, newURI):
		self.artistURI = newURI
		self.artistGraph.parse(newURI)





