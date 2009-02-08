import RDF

ns = {
  'dc': RDF.NS('http://purl.org/dc/elements/1.1/'),
  'foaf': RDF.NS('http://xmlns.com/foaf/0.1/'),
  'frbr': RDF.NS('http://purl.org/vocab/frbr/core#'),
  'rdf': RDF.NS('http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
  'nao': RDF.NS('http://www.semanticdesktop.org/ontologies/2007/08/15/nao#'),
  # original URL has been removed (MusicBrainz noooooo :()
  # described at <http://www.schemaweb.info/schema/SchemaInfo.aspx?id=168>
  'mm': RDF.NS('http://musicbrainz.org/mm/mm-2.1#'),
  'mo': RDF.NS('http://purl.org/ontology/mo/'),
  # need this to get xs:int track_numbers working
  'xs': RDF.NS('http://www.w3.org/2001/XMLSchema#'),
}
