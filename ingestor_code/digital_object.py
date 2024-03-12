from rdflib import URIRef, Literal
from .pattern_builder import PatternBuilder
from rdflib.namespace import RDFS
from .entity import Entity


class DigitalObject(Entity):
    def __init__(self, attributes: dict, namespaces_service, store):

        super().__init__(attributes, namespaces_service, store)

        # attributes
        self.identifier = Literal(attributes["identifier"])
        self.name = Literal(attributes["name"])
        self.has_topics = []

        if "has_topics" in attributes:
            self.has_topics = attributes["has_topics"]

        # build subject
        self.subject_string = f"digital-object/{self.identifier}"
        self.uri = self.namespaces_service.PDLM[self.subject_string]
        self.subject = URIRef(self.uri)

        # build named graph uri & graph proper
        named_graph_string = f"digital-objects/{self.identifier}"
        uri_named_graph_string = self.namespaces_service.CKG[named_graph_string]
        self.named_graph_uri = URIRef(uri_named_graph_string)
        self.graph = self.store.get_context(self.named_graph_uri)

    def populate_graph(self):
        pb = PatternBuilder(
            namespaces=self.namespaces_service.namespaces, graph=self.graph
        )

        # digital object has name
        name_uri = self.subject_string + "/name/"
        pb.add_name(self.uri, name_uri, self.name)

        # digital object is a digital object
        self.graph.add(
            (
                self.subject,
                self.namespaces_service.RDF.type,
                self.namespaces_service.CRM.D1_Digital_Object,
            )
        )
