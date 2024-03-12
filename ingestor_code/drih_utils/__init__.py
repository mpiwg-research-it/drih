import rdflib
import networkx as nx
import dotenv
import os
from nocodb.nocodb import NocoDBProject, APIToken, JWTAuthToken
from nocodb.filters import EqFilter, LikeFilter
from nocodb.infra.requests_client import NocoDBRequestsClient
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class noco:
    """
    Class to pull data from nocodb
    """

    def __init__(self):
        self.client = NocoDBRequestsClient(
            # Your API Token retrieved from NocoDB conf
            APIToken(os.getenv("NOCODB_TOKEN")),
            # Your nocodb root path
            "http://nocodb.mpiwg-berlin.mpg.de",
        )
        self.project = NocoDBProject(
            "noco",  # org name. noco by default
            "DRIH_PRODUCTION",  # project name. Case sensitive!!
        )

    def get_rows(self, table_name):
        rows = self.client.table_row_list(
            self.project, table_name, params={"limit": 10000}
        )
        # filter non-empty records (require identifier)
        if "identifier" in rows["list"][0]:
            filtered_list = list(
                filter(lambda row: row["identifier"] != None, rows["list"])
            )
            if 0 != (n := (len(rows["list"])) - len(filtered_list)):
                print(f"removed {n} empty records from table {table_name}")
            return filtered_list
        else:
            # skip if there is no identifier column
            return rows["list"]

    # TODO make sure that the correct nocodb table is referenced here. Still testing phase so table is changing!
    def get_tests(self, test_class: str):
        """Test class is the name of entry corresponding to the
        test_class col in the Meta_Tests table"""
        tests = self.client.table_row_list(
            self.project, "test_dev_v3", LikeFilter("test_class", test_class)
        )
        return tests["list"]

    def from_list(self, list_name, key, value):
        item = next(item for item in list_name if item[key] == value)
        return item

    def namespaces(self):
        namespaces = {}
        namespace_rows = self.get_rows("Meta_Namespaces")
        for namespace_row in namespace_rows:
            namespaces[namespace_row["short_form"]] = namespace_row["long_form"]
        return namespaces


class rdf2nx:
    """
    Class to create cool nx graphs from rdf graphs.
    """

    def __init__(self, g_rdf: rdflib.Graph):
        self.graph = g_rdf
        self.s = list(g_rdf.subjects())
        self.p = list(g_rdf.predicates())
        self.o = list(g_rdf.objects())
        self.graph = self.create_graph()

    def create_graph(self):
        g = nx.DiGraph()
        g.add_nodes_from(self.s)
        g.add_nodes_from(self.o)
        # create edge attribute
        attributed_edges = []
        for e1, e2, rel in zip(self.s, self.o, self.p):
            tup = (e1, e2, {"relation": rel})
            attributed_edges.append(tup)
        g.add_edges_from(attributed_edges)
        return g
