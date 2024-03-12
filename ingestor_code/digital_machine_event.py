from rdflib import URIRef, Literal
from .pattern_builder import PatternBuilder
from rdflib.namespace import RDFS
from .entity import Entity
from .volatile_dataset import VolatileDataset
from .persistent_dataset import PersistentDataset
from .project import Project
from .person import Person


class DigitalMachineEvent(Entity):
    def __init__(self, attributes: dict, namespaces_service, store):

        super().__init__(attributes, namespaces_service, store)

        # attributes
        self.identifier = Literal(attributes["identifier"])
        self.name = Literal(attributes["name"])

        self.was_motivated_by_projects = []
        self.had_input_volatile_datasets = []
        self.had_output_volatile_datasets = []
        self.had_input_persistent_datasets = []
        self.had_output_persistent_datasets = []
        self.carried_out_by_persons = []

        if "was_motivated_by_projects" in attributes:
            self.was_motivated_by_projects = attributes["was_motivated_by_projects"]
        if "had_input_volatile_datasets" in attributes:
            self.had_input_volatile_datasets = attributes["had_input_volatile_datasets"]
        if "had_output_volatile_datasets" in attributes:
            self.had_output_volatile_datasets = attributes[
                "had_output_volatile_datasets"
            ]
        if "had_input_persistent_datasets" in attributes:
            self.had_input_persistent_datasets = attributes[
                "had_input_persistent_datasets"
            ]
        if "had_output_persistent_datasets" in attributes:
            self.had_output_persistent_datasets = attributes[
                "had_output_persistent_datasets"
            ]
        if "carried_out_by_persons" in attributes:
            self.carried_out_by_persons = attributes["carried_out_by_persons"]

        # build subject
        self.subject_string = f"activity/dme/{self.identifier}"
        self.uri = self.namespaces_service.PDLM[self.subject_string]
        self.subject = URIRef(self.uri)

        # build named graph uri & graph proper
        named_graph_string = f"digital_machine_events/{self.identifier}"
        uri_named_graph_string = self.namespaces_service.CKG[named_graph_string]
        self.named_graph_uri = URIRef(uri_named_graph_string)
        self.graph = self.store.get_context(self.named_graph_uri)

    def populate_graph(self):
        pb = PatternBuilder(
            namespaces=self.namespaces_service.namespaces, graph=self.graph
        )

        # dmo is a digital machine event
        self.graph.add(
            (
                self.subject,
                self.namespaces_service.RDF.type,
                self.namespaces_service.CRM_DIG.D7_Digital_Machine_Event,
            )
        )

        for project_data in self.was_motivated_by_projects:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM.P17_was_motivated_by,
                    Project(project_data, self.namespaces_service, self.store).subject,
                )
            )

        # had input volatile dataset
        for dataset_data in self.had_input_volatile_datasets:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM_DIG.L10_had_input,
                    VolatileDataset(
                        dataset_data, self.namespaces_service, self.store
                    ).subject,
                )
            )

        # had input persistent dataset
        for dataset_data in self.had_input_persistent_datasets:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM_DIG.L10_had_input,
                    PersistentDataset(
                        dataset_data, self.namespaces_service, self.store
                    ).subject,
                )
            )

        # volatile dataset was output of subject
        for dataset_data in self.had_output_volatile_datasets:
            self.graph.add(
                (
                    VolatileDataset(
                        dataset_data, self.namespaces_service, self.store
                    ).subject,
                    self.namespaces_service.CRM_DIG.L11i_was_output_of,
                    self.subject,
                )
            )

        # persistent dataset was output of subject
        for dataset_data in self.had_output_persistent_datasets:
            self.graph.add(
                (
                    PersistentDataset(
                        dataset_data, self.namespaces_service, self.store
                    ).subject,
                    self.namespaces_service.CRM_DIG.L11i_was_output_of,
                    self.subject,
                )
            )

        for person_data in self.carried_out_by_persons:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM.P14_carried_out_by,
                    Person(person_data, self.namespaces_service, self.store).subject,
                )
            )
