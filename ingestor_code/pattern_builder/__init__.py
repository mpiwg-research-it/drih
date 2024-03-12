from rdflib import Literal, Namespace, RDF, URIRef


class PatternBuilder:
    def __init__(self, graph, namespaces=list):
        self.graph = graph
        self.namespaces = {}
        for namespace in namespaces:
            self.namespaces[namespace["short_form"]] = Namespace(namespace["long_form"])
            self.graph.bind(namespace["short_form"], Namespace(namespace["long_form"]))
        self.a = RDF.type

    # laf.6
    def add_name(self, entity_uri: str, name_uri: str, name_string: str):
        entity_uri_ref = URIRef(entity_uri)
        name_literal = Literal(name_string)
        name_uri_ref = URIRef(name_uri)

        self.graph.add(
            (entity_uri_ref, self.namespaces["crm"].P1_is_identified_by, name_uri_ref)
        )
        self.graph.add(
            (
                name_uri_ref,
                self.a,
                self.namespaces["crm"].E33_E41_Linguistic_Appellation,
            )
        )
        self.graph.add(
            (
                name_uri_ref,
                self.namespaces["crm"].P190_has_symbolic_content,
                name_literal,
            )
        )
        # label
        self.graph.add((entity_uri_ref, self.namespaces["rdfs"].label, name_literal))

    # pdlf.1 and pdlf.2
    def add_description(
        self,
        entity_uri: str,
        description_uri: str,
        description_string: str,
        description_type_uri: str = None,
    ):
        entity_uri_ref = URIRef(entity_uri)
        description_literal = Literal(description_string)
        description_uri_ref = URIRef(description_uri)

        self.graph.add(
            (
                entity_uri_ref,
                self.namespaces["crm"].P129i_is_subject_of,
                description_uri_ref,
            )
        )
        self.graph.add(
            (
                description_uri_ref,
                self.a,
                self.namespaces["crm"].E33_Linguistic_Object,
            )
        )
        self.graph.add(
            (
                description_uri_ref,
                self.namespaces["crm"].P190_has_symbolic_content,
                description_literal,
            )
        )

        # description type
        if description_type_uri != None:
            description_type_uri_ref = URIRef(description_type_uri)
            self.graph.add(
                (
                    description_uri_ref,
                    self.namespaces["crm"].P2_has_type,
                    description_type_uri_ref,
                )
            )

            self.graph.add(
                (
                    description_type_uri_ref,
                    self.a,
                    self.namespaces["crm"].E55_Type,
                )
            )

    # laf.11 and laf.12
    def add_type(self, entity_uri: str, type_uri: str, metatype_uri: str = None):
        entity_uri_ref = URIRef(entity_uri)
        type_uri_ref = URIRef(type_uri)

        self.graph.add(
            (
                entity_uri_ref,
                self.namespaces["crm"].P2_has_type,
                type_uri_ref,
            )
        )

        self.graph.add(
            (
                type_uri_ref,
                self.a,
                self.namespaces["crm"].E55_Type,
            )
        )

        # metatype
        if metatype_uri != None:
            metatype_uri_ref = URIRef(metatype_uri)
            self.graph.add(
                (
                    type_uri_ref,
                    self.namespaces["crm"].P2_has_type,
                    metatype_uri_ref,
                )
            )
            self.graph.add(
                (
                    metatype_uri_ref,
                    self.a,
                    self.namespaces["crm"].E55_Type,
                )
            )

    # laf.10 and laf.9
    def add_identifier(
        self,
        entity_uri: str,
        identifier_uri: str,
        identifier_string: str,
        identifier_type_uri: str = None,
    ):
        entity_uri_ref = URIRef(entity_uri)
        identifier_uri_ref = URIRef(identifier_uri)
        identifier_string_literal = Literal(identifier_string)

        self.graph.add(
            (
                entity_uri_ref,
                self.namespaces["crm"].P1_is_identified_by,
                identifier_uri_ref,
            )
        )

        self.graph.add(
            (
                identifier_uri_ref,
                self.a,
                self.namespaces["crm"].E42_Identifier,
            )
        )

        self.graph.add(
            (
                identifier_uri_ref,
                self.namespaces["crm"].P190_has_symbolic_content,
                identifier_string_literal,
            )
        )

        # identifier type
        if identifier_type_uri != None:
            identifier_type_uri_ref = URIRef(identifier_type_uri)
            self.graph.add(
                (
                    identifier_uri_ref,
                    self.namespaces["crm"].P2_has_type,
                    identifier_type_uri_ref,
                )
            )

            self.graph.add(
                (
                    identifier_type_uri_ref,
                    self.a,
                    self.namespaces["crm"].E55_Type,
                )
            )

    # pdlf.3
    def add_digital_access_point(
        self,
        entity_uri: str,
        digital_access_point_uri: str,
        digital_access_point_string: str,
        digital_access_point_type_uri: str = None,
    ):
        entity_uri_ref = URIRef(entity_uri)
        digital_access_point_uri_ref = URIRef(digital_access_point_uri)
        digital_access_point_string_literal = Literal(digital_access_point_string)

        self.graph.add(
            (
                entity_uri_ref,
                self.namespaces["crm"].PP50_accessible_at,
                digital_access_point_uri_ref,
            )
        )

        self.graph.add(
            (
                digital_access_point_uri_ref,
                self.a,
                self.namespaces["crm"].PE29_access_point,
            )
        )

        self.graph.add(
            (
                digital_access_point_uri_ref,
                self.namespaces["crm"].P190_has_symbolic_content,
                digital_access_point_string_literal,
            )
        )

        # identifier type
        if digital_access_point_type_uri != None:
            digital_access_point_type_uri_ref = URIRef(digital_access_point_type_uri)
            self.graph.add(
                (
                    digital_access_point_uri_ref,
                    self.namespaces["crm"].P2_has_type,
                    digital_access_point_type_uri_ref,
                )
            )

            self.graph.add(
                (
                    digital_access_point_type_uri_ref,
                    self.a,
                    self.namespaces["crm"].E55_Type,
                )
            )
