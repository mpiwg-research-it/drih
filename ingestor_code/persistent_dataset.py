from rdflib import URIRef, Literal
from .pattern_builder import PatternBuilder
from rdflib.namespace import RDFS
from .entity import Entity
from .access_point import AccessPoint


class PersistentDataset(Entity):
    def __init__(self, attributes: dict, namespaces_service, store):

        super().__init__(attributes, namespaces_service, store)

        # attributes
        self.identifier = Literal(attributes["identifier"])
        self.name = Literal(attributes["name"])
        self.description = Literal(attributes["description"])

        self.accessible_at_access_points = []

        if "accessible_at_access_points" in attributes:
            self.accessible_at_access_points = attributes["accessible_at_access_points"]

        # build subject
        self.subject_string = f"digital-object/dataset/{self.identifier}"
        self.uri = self.namespaces_service.PDLM[self.subject_string]
        self.subject = URIRef(self.uri)

        # build named graph uri & graph proper
        named_graph_string = f"project_datasets/{self.identifier}"
        uri_named_graph_string = self.namespaces_service.CKG[named_graph_string]
        self.named_graph_uri = URIRef(uri_named_graph_string)
        self.graph = self.store.get_context(self.named_graph_uri)

    def populate_graph(self):
        pb = PatternBuilder(
            namespaces=self.namespaces_service.namespaces, graph=self.graph
        )

        # has name and desc
        name_uri = self.subject_string + "/name/"
        pb.add_name(self.uri, name_uri, self.name)

        description_uri = self.subject_string + "/description/"
        pb.add_description(
            self.uri,
            description_uri,
            self.description,
            description_type_uri=self.namespaces_service.PDLM[
                "type/descriptions/desc_type_placeholder"
            ],
        )

        # persistent dataset is a persistent dataset
        self.graph.add(
            (
                self.subject,
                self.namespaces_service.RDF.type,
                self.namespaces_service.CRM_PEM.PE22_Persistent_Dataset,
            )
        )

        # persistent dataset is accessible at access points
        for access_point_data in self.accessible_at_access_points:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM_PEM.PP50_accessible_at,
                    AccessPoint(
                        access_point_data, self.namespaces_service, self.store
                    ).subject,
                )
            )
