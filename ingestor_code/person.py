from rdflib import URIRef, Literal
from .pattern_builder import PatternBuilder
from rdflib.namespace import RDF, RDFS
from .entity import Entity


class Person(Entity):
    def __init__(self, attributes: dict, namespaces_service, store):

        super().__init__(attributes, namespaces_service, store)

        # attributes
        self.name = attributes["name"]
        self.email = Literal(attributes["contact"])
        self.pid = attributes["identifier"]

        # build subject
        self.subject_string = f"actor/person/{self.pid}"
        self.uri = self.namespaces_service.PDLM[self.subject_string]
        self.subject = URIRef(self.uri)

        # build named graph uri & graph proper
        named_graph_string = f"persons/{self.pid}"
        uri_named_graph_string = self.namespaces_service.CKG[named_graph_string]
        self.named_graph_uri = URIRef(uri_named_graph_string)
        self.graph = self.store.get_context(self.named_graph_uri)

    def populate_graph(self):
        pb = PatternBuilder(
            namespaces=self.namespaces_service.namespaces, graph=self.graph
        )
        self.graph.add(
            (
                self.subject,
                self.namespaces_service.RDF.type,
                self.namespaces_service.CRM.E21_Person,
            )
        )

        # person has name person_name
        name_uri = self.subject_string + "/name/"
        pb.add_name(self.uri, name_uri, self.name)

        # person has email person_email
        email_appellation_string = self.subject_string + "/email/"
        email_subject = URIRef(email_appellation_string)

        self.graph.add(
            (
                self.subject,
                self.namespaces_service.CRM.P76_has_contact_point,
                email_subject,
            )
        )
        self.graph.add(
            (email_subject, RDF.type, self.namespaces_service.CRM.E41_Appellation)
        )
        self.graph.add(
            (
                email_subject,
                self.namespaces_service.CRM.P190_has_symbolic_content,
                self.email,
            )
        )

        # person has PID person_pid - noco_identifer is a temporary placeholder
        pid_identifier_uri = self.subject_string + "/pid/"
        pb.add_identifier(
            self.uri,
            pid_identifier_uri,
            self.pid,
            self.namespaces_service.CKG.noco_identifier,
        )
