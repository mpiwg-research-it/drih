from rdflib import URIRef, Literal
from rdflib.namespace import RDFS
from .entity import Entity


class AccessPoint(Entity):
    def __init__(self, attributes: dict, namespaces_service, store):

        super().__init__(attributes, namespaces_service, store)

        # attributes
        self.identifier = Literal(attributes["identifier"])
        self.url = Literal(attributes["url"])

        # build subject
        self.subject_string = f"access_point/{self.identifier}"
        self.uri = self.namespaces_service.PDLM[self.subject_string]
        self.subject = URIRef(self.uri)

        # build named graph uri & graph proper
        named_graph_string = f"access_point/{self.identifier}"
        uri_named_graph_string = self.namespaces_service.CKG[named_graph_string]
        self.named_graph_uri = URIRef(uri_named_graph_string)
        self.graph = self.store.get_context(self.named_graph_uri)

    def populate_graph(self):

        # access_point is an access point
        self.graph.add(
            (
                self.subject,
                self.namespaces_service.RDF.type,
                self.namespaces_service.CRM_PEM.PE29_Access_Point,
            )
        )

        # add label
        self.graph.add(
            (
                URIRef(self.subject),
                RDFS.label,
                Literal(self.url),
            )
        )

        self.graph.add(
            (
                self.subject,
                self.namespaces_service.CRM.P190_has_symbolic_content,
                self.url,
            )
        )
