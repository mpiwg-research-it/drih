from rdflib import URIRef, Literal
from .pattern_builder import PatternBuilder
from rdflib.namespace import RDFS
from .entity import Entity
from .team import Team
from .topic import Topic


class Project(Entity):
    def __init__(self, attributes: dict, namespaces_service, store):

        super().__init__(attributes, namespaces_service, store)

        # attributes
        self.identifier = Literal(attributes["identifier"])
        self.canonical_name = Literal(attributes["canonical_name"])
        self.description = Literal(attributes["description"])
        self.name = Literal(attributes["name"])
        self.start_date = Literal(attributes["project_timeline_start"])
        self.end_date = Literal(attributes["project_timeline_end"])
        self.has_maintaining_teams = []
        self.supported_projects = []
        self.has_topics = []

        if "has_topics" in attributes:
            self.has_topics = attributes["has_topics"]

        if "supported_projects" in attributes:
            self.supported_projects = attributes["supported_projects"]

        if "has_maintaining_teams" in attributes:
            self.has_maintaining_teams = attributes["has_maintaining_teams"]

        # build subject
        self.subject_string = f"project/{self.canonical_name}"
        self.uri = self.namespaces_service.PDLM[self.subject_string]
        self.subject = URIRef(self.uri)

        # build named graph uri & graph proper
        named_graph_string = f"project_descriptions/{self.canonical_name}"
        uri_named_graph_string = self.namespaces_service.CKG[named_graph_string]
        self.named_graph_uri = URIRef(uri_named_graph_string)
        self.graph = self.store.get_context(self.named_graph_uri)

    def populate_graph(self):
        pb = PatternBuilder(
            namespaces=self.namespaces_service.namespaces, graph=self.graph
        )

        # project has name project_name
        name_uri = self.subject_string + "/name/"
        pb.add_name(self.uri, name_uri, self.name)

        # project has description description
        description_uri = self.subject_string + "/description/"
        pb.add_description(
            self.uri,
            description_uri,
            self.description,
            description_type_uri=self.namespaces_service.PDLM[
                "type/descriptions/desc_type_placeholder"
            ],
        )

        # project is a project
        self.graph.add(
            (
                self.subject,
                self.namespaces_service.RDF.type,
                self.namespaces_service.CRM_PEM.PE45_Research_Project,
            )
        )

        if self.start_date and self.end_date:
            # project has start and end dates
            time_span_subject = URIRef(self.subject_string + "/time_span/")
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM["P4_has_time-span"],
                    time_span_subject,
                )
            )
            self.graph.add(
                (
                    time_span_subject,
                    self.namespaces_service.CRM.P82a_begin_of_the_begin,
                    self.start_date,
                )
            )
            self.graph.add(
                (
                    time_span_subject,
                    self.namespaces_service.CRM.P82b_end_of_the_end,
                    self.end_date,
                )
            )

        # project has maintaining teams...
        for team_data in self.has_maintaining_teams:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM_PEM.PP44_has_maintaining_team,
                    Team(team_data, self.namespaces_service, self.store).subject,
                )
            )

        # project supported projects
        for project_data in self.supported_projects:
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM_PEM.PP44_has_maintaining_team,
                    Project(project_data, self.namespaces_service, self.store).subject,
                )
            )

        # project has topics
        for topic_data in self.has_topics:
            topic = Topic(topic_data, self.namespaces_service, self.store)
            self.graph.add(
                (
                    self.subject,
                    self.namespaces_service.CRM.P21_had_general_purpose,
                    topic.subject,
                )
            )
            # self.graph.add(
            #     (
            #         URIRef(topic.subject),
            #         RDFS.label,
            #         Literal(topic.name),
            #     )
            # )
