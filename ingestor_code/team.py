from rdflib import URIRef, Literal
from .pattern_builder import PatternBuilder
from rdflib.namespace import RDFS
from .entity import Entity
from .person import Person


class Team(Entity):
    def __init__(self, attributes: dict, namespaces_service, store):

        super().__init__(attributes, namespaces_service, store)

        # attributes
        self.members = []
        self.identifier = Literal(attributes["identifier"])
        self.description = Literal(attributes["description"])
        self.name = Literal(attributes["name"])
        if "persons" in attributes:
            self.members = attributes["persons"]

        # build subject
        self.subject_string = f"actor/project-team/{self.identifier}"
        self.uri = self.namespaces_service.PDLM[self.subject_string]
        self.subject = URIRef(self.uri)

        # build named graph uri & graph proper
        named_graph_string = f"actor/project-teams/{self.identifier}"
        uri_named_graph_string = self.namespaces_service.CKG[named_graph_string]
        self.named_graph_uri = URIRef(uri_named_graph_string)
        self.graph = self.store.get_context(self.named_graph_uri)

    def populate_graph(self):
        pb = PatternBuilder(
            namespaces=self.namespaces_service.namespaces, graph=self.graph
        )

        # team is a team
        self.graph.add(
            (
                self.subject,
                self.namespaces_service.RDF.type,
                self.namespaces_service.CRM_PEM.PE34_Team,
            )
        )

        # team has name team_name
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

        # team has members...
        for member_data in self.members:
            person = Person(member_data, self.namespaces_service, self.store)
            self.graph.add(
                (
                    person.subject,
                    self.namespaces_service.CRM.P107i_is_current_or_former_member_of,
                    self.subject,
                )
            )

            # add label
            # self.graph.add(
            #     (
            #         URIRef(person.subject),
            #         RDFS.label,
            #         Literal(person.name),
            #     )
            # )
