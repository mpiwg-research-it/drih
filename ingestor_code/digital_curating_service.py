from rdflib import URIRef, Literal
from .pattern_builder import PatternBuilder
from rdflib.namespace import RDFS
from .entity import Entity
from .volatile_dataset import VolatileDataset


class DigitalCuratingService(Entity):
    def __init__(self, attributes: dict, namespaces_service, store):

        super().__init__(attributes, namespaces_service, store)

        # attributes
        self.identifier = Literal(attributes["identifier"])
        self.name = Literal(attributes["name"])
        self.curates_volatile_datasets = []
        self.continued_digital_curating_services = []

        if "curates_volatile_datasets" in attributes:
            self.curates_volatile_datasets = attributes["curates_volatile_datasets"]

        if "continued_digital_curating_services" in attributes:
            self.continued_digital_curating_services = attributes[
                "continued_digital_curating_services"
            ]

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

        # service is a digital curating service
        self.graph.add(
            (
                self.subject,
                self.namespaces_service.RDF.type,
                self.namespaces_service.CRM_PEM.PE10_Digital_Curating_Service,
            )
        )

        # service continued another service
        for cdcs_data in self.continued_digital_curating_services:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM.P134_continued,
                    DigitalCuratingService(
                        cdcs_data, self.namespaces_service, self.store
                    ).subject,
                )
            )

        # service curates a volatile dataset
        for vds_data in self.curates_volatile_datasets:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM_PEM.PP11_curates_volatile_digital_object,
                    VolatileDataset(
                        vds_data, self.namespaces_service, self.store
                    ).subject,
                )
            )
