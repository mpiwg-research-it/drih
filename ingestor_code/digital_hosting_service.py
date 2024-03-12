from rdflib import URIRef, Literal
from .pattern_builder import PatternBuilder

from .entity import Entity
from .access_point import AccessPoint
from .volatile_dataset import VolatileDataset
from .persistent_dataset import PersistentDataset


class DigitalHostingService(Entity):
    def __init__(self, attributes: dict, namespaces_service, store):

        super().__init__(attributes, namespaces_service, store)

        # attributes
        self.identifier = Literal(attributes["identifier"])
        self.name = Literal(attributes["name"])
        self.provides_access_points = []
        self.hosts_volatile_datasets = []
        self.hosts_persistent_datasets = []

        if "provides_access_points" in attributes:
            self.provides_access_points = attributes["provides_access_points"]

        if "hosts_volatile_datasets" in attributes:
            self.hosts_volatile_datasets = attributes["hosts_volatile_datasets"]

        if "hosts_persistent_datasets" in attributes:
            self.hosts_persistent_datasets = attributes["hosts_persistent_datasets"]

        # build subject
        self.subject_string = f"activity/service/{self.identifier}"
        self.uri = self.namespaces_service.PDLM[self.subject_string]
        self.subject = URIRef(self.uri)

        # build named graph uri & graph proper
        named_graph_string = f"services/{self.identifier}"
        uri_named_graph_string = self.namespaces_service.CKG[named_graph_string]
        self.named_graph_uri = URIRef(uri_named_graph_string)
        self.graph = self.store.get_context(self.named_graph_uri)

    def populate_graph(self):
        pb = PatternBuilder(
            namespaces=self.namespaces_service.namespaces, graph=self.graph
        )

        # service has name service_name
        name_uri = self.subject_string + "/name/"
        pb.add_name(self.uri, name_uri, self.name)

        # service is a digital hosting service
        self.graph.add(
            (
                self.subject,
                self.namespaces_service.RDF.type,
                self.namespaces_service.CRM_PEM.PE5_Digital_Hosting_Service,
            )
        )

        # service provides access points
        for access_point_data in self.provides_access_points:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM_PEM.PP49_provides_access_point,
                    AccessPoint(
                        access_point_data, self.namespaces_service, self.store
                    ).subject,
                )
            )

        # service hosts volatile datasets
        for vds_data in self.hosts_volatile_datasets:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM_PEM.PP6_hosts_digital_object,
                    VolatileDataset(
                        vds_data, self.namespaces_service, self.store
                    ).subject,
                )
            )

        # service hosts persistent datasets
        for pds_data in self.hosts_persistent_datasets:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM_PEM.PP6_hosts_digital_object,
                    PersistentDataset(
                        pds_data, self.namespaces_service, self.store
                    ).subject,
                )
            )
