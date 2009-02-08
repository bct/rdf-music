import RDF

storage = RDF.HashStorage('music', options="hash-type='bdb'")
model = RDF.Model(storage)

def state(s, p, o):
  model.append(RDF.Statement(s, p, o))
