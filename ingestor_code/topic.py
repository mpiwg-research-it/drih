from rdflib import URIRef
from .pattern_builder import PatternBuilder
from rdflib.namespace import RDFS
from .entity import Entity


class Topic(Entity):
    def __init__(self, attributes: dict, namespaces_service, store):

        super().__init__(attributes, namespaces_service, store)

        # attributes
        self.name = attributes["name"]
        self.identifier = attributes["identifier"]

        # build subject
        self.subject_string = f"topic/{self.identifier}"
        self.uri = self.namespaces_service.PDLM[self.subject_string]
        self.subject = URIRef(self.uri)

        # build named graph uri & graph proper
        named_graph_string = f"topics/{self.identifier}"
        uri_named_graph_string = self.namespaces_service.CKG[named_graph_string]
        self.named_graph_uri = URIRef(uri_named_graph_string)
        self.graph = self.store.get_context(self.named_graph_uri)

    def populate_graph(self):
        pb = PatternBuilder(
            namespaces=self.namespaces_service.namespaces, graph=self.graph
        )

        # topic is a type
        self.graph.add(
            (
                self.subject,
                self.namespaces_service.RDF.type,
                self.namespaces_service.CRM.E55_Type,
            )
        )

        # topic has name name
        name_uri = self.subject_string + "/name/"
        pb.add_name(self.uri, name_uri, self.name)
