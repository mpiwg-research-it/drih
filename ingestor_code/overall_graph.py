from rdflib import Graph, Namespace
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import json

load_dotenv()

# import data_test


class OverallGraph:
    def __init__(self, store, namespaces: list, credentials: dict, remote_url: str):
        self.store = store
        self.graph = Graph()
        self.credentials = credentials
        if remote_url.endswith("/"):
            remote_url = remote_url[:-1]
        self.remote_url = remote_url
        self.namespaces = {}
        for namespace in namespaces:
            self.graph.bind(namespace["short_form"], Namespace(namespace["long_form"]))

        for g in self.store.graphs():
            for t in g.triples((None, None, None)):
                self.graph.add(t)

    def serialize(self):
        print("serializing the overall graph")
        os.makedirs("output/rdf", exist_ok=True)
        self.store.serialize("output/rdf/overall_nquads.txt", format="nquads")
        self.store.serialize("output/rdf/overall_trig.trig", format="trig")
        self.graph.serialize("output/rdf/overall_flat.ttl", format="ttl")
        #        f = open("output/rdf/overall_flat.ttl", "r")
        #        content = f.read()
        #        ckg_prefixed = content.replace("http://digital.mpiwg-berlin.mpg.de/ns/", "ckg:")
        #        ckg_prefixed = (
        #            "@prefix ckg: <http://digital.mpiwg-berlin.mpg.de/ns/> .\n" + ckg_prefixed
        #        )
        #
        #        with open("output/rdf/overall_flat.ttl", "w") as file:
        #            file.write(ckg_prefixed)
        print("done")

    def purge_remote(self):
        print("purging remote")
        query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    select distinct ?g
                    where {
                      graph ?g {
                        ?s ?p ?o .
                      }
                      filter(strstarts(str(?g), "http://digital.mpiwg-berlin.mpg.de/ns/"))
                      filter(!strstarts(str(?g), "http://digital.mpiwg-berlin.mpg.de/ns/projects/"))
                }"""
        headers = {
            "content-type": "application/sparql-update",
            "Accept-Charset": "UTF-8",
            "Accept": "application/json",
        }

        basic = HTTPBasicAuth(
            self.credentials["username"], self.credentials["password"]
        )
        try:
            r = requests.post(
                self.remote_url + ":10214/sparql",
                data=query,
                headers=headers,
                auth=basic,
            )
            r.raise_for_status()
            ngs_to_delete = json.loads(r.content)["results"]["bindings"]
            queries = []
            print("(" + str(len(ngs_to_delete)) + " remote named graphs to delete)")
            for graph_info in ngs_to_delete:
                graph_name = graph_info["g"]["value"]
                query = f"DROP GRAPH <{graph_name}>"
                queries.append(query)
                # print("remote named graph to be purged: " + graph_name)
            try:
                r = requests.post(
                    self.remote_url + ":10214/sparql",
                    data=(";").join(queries),
                    headers=headers,
                    auth=basic,
                )
                r.raise_for_status()
                print("done")
            except requests.exceptions.HTTPError as err:
                raise SystemExit(err)

        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

    def push_to_remote(self):
        print("pushing overall_trig.trig to remote")
        headers = {"content-type": "application/x-trig", "Accept-Charset": "UTF-8"}
        r = requests.post(
            self.remote_url + ":10215/blazegraph/sparql",
            data=open("output/rdf/overall_trig.trig", "rb"),
            headers=headers,
        )
        print("done")


#    def test(self, noco):
#        test_graph = practicalSPARQL.rdfGRAPH()
#        temp = self.graph.serialize(format="nt")
#        test_graph.parse(data=temp, format="nt")
#
#        print("ALL ACTORS")
#        actors_test = data_test.test_actors(
#            test_graph, self.noco, report_dir="data/test_results"
#        )
#        actors_test.test_all(report_path="actor_report.txt")
#
#        print("ALL ACTIVITIES")
#        activities_test = data_test.test_activities(
#            test_graph, self.noco, report_dir="data/test_results"
#        )
#        activities_test.test_all(report_path="activities_report.txt")
#
#        print("ALL DIGITAL OBJECTS")
#        digital_objects_test = data_test.test_digital_objects(
#            test_graph, self.noco, report_dir="data/test_results"
#        )
#        digital_objects_test.test_all(report_path="do_report.txt")
