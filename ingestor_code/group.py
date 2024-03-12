from rdflib import URIRef, Literal
from .pattern_builder import PatternBuilder
from rdflib.namespace import RDFS
from .entity import Entity
from .person import Person


class Group(Entity):
    def __init__(self, attributes: dict, namespaces_service, store):

        super().__init__(attributes, namespaces_service, store)

        # attributes
        self.identifier = Literal(attributes["identifier"])
        self.name = Literal(attributes["name"])
        self.type_uri = self.namespaces_service.PDLM["type/"]
        self.members = []
        self.group_members = []
        if "persons" in attributes:
            self.members = attributes["persons"]
        if "groups" in attributes:
            self.group_members = attributes["groups"]

        # build subject
        self.subject_string = f"actor/group/{self.identifier}"
        self.uri = self.namespaces_service.PDLM[self.subject_string]
        self.subject = URIRef(self.uri)

        # build named graph uri & graph proper
        named_graph_string = f"actor/groups/{self.identifier}"
        uri_named_graph_string = self.namespaces_service.CKG[named_graph_string]
        self.named_graph_uri = URIRef(uri_named_graph_string)
        self.graph = self.store.get_context(self.named_graph_uri)

    def populate_graph(self):
        pb = PatternBuilder(
            namespaces=self.namespaces_service.namespaces, graph=self.graph
        )

        # group is a group
        self.graph.add(
            (
                self.subject,
                self.namespaces_service.RDF.type,
                self.namespaces_service.CRM.E74_Group,
            )
        )

        # group has name group_name
        name_uri = self.subject_string + "/name/"
        pb.add_name(self.uri, name_uri, self.name)

        # group has type
        pb.add_type(
            self.uri,
            self.type_uri,
            metatype_uri=self.namespaces_service.PDLM["type/metatype_placeholder/"],
        )

        # group has person members...
        for member_data in self.members:
            person = Person(member_data, self.namespaces_service, self.store)
            self.graph.add(
                (
                    URIRef(person.subject),
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

        # group has group members...
        for group_member_data in self.group_members:
            self.graph.add(
                (
                    URIRef(
                        Group(
                            group_member_data, self.namespaces_service, self.store
                        ).subject
                    ),
                    self.namespaces_service.CRM.P107i_is_current_or_former_member_of,
                    self.subject,
                )
            )
