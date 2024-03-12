from rdflib import URIRef, Literal
from .pattern_builder import PatternBuilder
from rdflib.namespace import RDFS
from .entity import Entity
from .person import Person
from .team import Team
from .group import Group
from .digital_curating_service import DigitalCuratingService
from .digital_hosting_service import DigitalHostingService
from .digital_object import DigitalObject


class Service(Entity):
    def __init__(self, attributes: dict, namespaces_service, store):

        super().__init__(attributes, namespaces_service, store)

        # attributes
        self.identifier = Literal(attributes["identifier"])
        self.name = Literal(attributes["name"])
        self.type_uri = self.namespaces_service.PDLM["type/"]
        self.provided_by_persons = []
        self.provided_by_groups = []
        self.provided_by_teams = []
        self.digital_hosting_services = []
        self.digital_curating_services = []
        self.digital_objects = []

        if "persons" in attributes:
            self.provided_by_persons = attributes["persons"]
        if "groups" in attributes:
            self.provided_by_groups = attributes["groups"]
        if "teams" in attributes:
            self.provided_by_teams = attributes["teams"]
        if "digital_hosting_services" in attributes:
            self.digital_hosting_services = attributes["digital_hosting_services"]
        if "digital_curating_services" in attributes:
            self.digital_curating_services = attributes["digital_curating_services"]
        if "digital_objects" in attributes:
            self.digital_objects = attributes["digital_objects"]

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

        # service is a service
        self.graph.add(
            (
                self.subject,
                self.namespaces_service.RDF.type,
                self.namespaces_service.CRM_PEM.PE1_Service,
            )
        )

        # service has name service_name
        name_uri = self.subject_string + "/name/"
        pb.add_name(self.uri, name_uri, self.name)

        # group has type
        pb.add_type(
            self.uri,
            self.type_uri,
            metatype_uri=self.namespaces_service.PDLM["type/metatype_placeholder/"],
        )

        # service is provided by person
        for member_data in self.provided_by_persons:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM_PEM.PP2_provided_by,
                    Person(member_data, self.namespaces_service, self.store).subject,
                )
            )

        # service is provided by team
        for team_data in self.provided_by_teams:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM_PEM.PP2_provided_by,
                    Team(team_data, self.namespaces_service, self.store).subject,
                )
            )

        # service is provided by group
        for group_data in self.provided_by_groups:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM_PEM.PP2_provided_by,
                    Group(group_data, self.namespaces_service, self.store).subject,
                )
            )

        # service consists of digital hosting services
        for dhs_data in self.digital_hosting_services:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM.P9_consists_of,
                    DigitalHostingService(
                        dhs_data, self.namespaces_service, self.store
                    ).subject,
                )
            )

        # service consists of digital curating services
        for dcs_data in self.digital_curating_services:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM.P9_consists_of,
                    DigitalCuratingService(
                        dcs_data, self.namespaces_service, self.store
                    ).subject,
                )
            )

        # service is referred to by digital_objects
        for do_data in self.digital_objects:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM.P67i_is_referred_to_By,
                    DigitalObject(do_data, self.namespaces_service, self.store).subject,
                )
            )
