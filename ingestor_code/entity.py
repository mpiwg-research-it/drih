import io
import pydotplus
from rdflib.tools.rdf2dot import rdf2dot
import os


class Entity:

    def __init__(self, attributes: dict, namespace_services, store):
        self.store = store
        self.namespaces_service = namespace_services

    def visualise(self):
        stream = io.StringIO()
        rdf2dot(self.graph, stream)
        dg = pydotplus.graph_from_dot_data(stream.getvalue())
        print("creating diagram of named graph for entity " + self.subject_string)
        os.makedirs(
            "output/pictures/" + os.path.dirname(self.subject_string), exist_ok=True
        )
        png = dg.write_png(
            "output/pictures/" + self.subject_string + ".png",
            prog=["dot", "-Goverlap=false"],
        )
