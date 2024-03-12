from .drih_utils import noco
from rdflib import Namespace
from rdflib.namespace import DCAT, DCTERMS, RDF, RDFS

from rdflib import Dataset, Graph


import os
from .person import Person
from .team import Team
from .group import Group
from .access_point import AccessPoint
from .service import Service
from .digital_curating_service import DigitalCuratingService
from .digital_hosting_service import DigitalHostingService
from .volatile_dataset import VolatileDataset
from .persistent_dataset import PersistentDataset
from .digital_machine_event import DigitalMachineEvent
from .project import Project
from .topic import Topic
from .digital_object import DigitalObject
from .overall_graph import OverallGraph
import argparse
from .data_test import ActorTests, ActivitieTests, DigitalObjectTests

noco = noco()

parser = argparse.ArgumentParser(
    description="ingests data from nocodb and load it onto a RS instance at 'remote_url'"
)
parser.add_argument(
    "-url",
    help="url of the remote researchspace instance (default: http://localhost)",
    type=str,
    default="http://localhost",
    required=False,
)

parser.add_argument("-d", action="store_true",
                    help="generate diagram for each entity")

parser.add_argument("-t", action="store_true",
                    help="run tests and generate test reports in output/")

parser.add_argument("-push", action="store_true",
                    help="push to researchspace instance set in -url (you might need to set -u and -p)")


parser.add_argument(
    "-u",
    help="username for the remote researchspace instance (default: admin)",
    type=str,
    default="admin",
    required=False,
)

parser.add_argument(
    "-p",
    help="password for the remote researchspace instance (default: admin)",
    type=str,
    default="admin",
    required=False,
)

args = parser.parse_args()


class DataService:
    def __init__(self):
        print("data_source_started")
        self.types = noco.get_rows("E55_Types")
        self.projects = noco.get_rows("PE45_Research_Projects")
        self.persons = noco.get_rows("E21_Persons")
        self.teams = noco.get_rows("PE34_Teams")
        self.groups = noco.get_rows("E74_Groups")
        self.services = noco.get_rows("PE1_Services")
        self.digital_objects = noco.get_rows("D1_Digital_Objects")
        self.digital_curating_services = noco.get_rows(
            "PE10_Digital_Curating_Services")
        self.digital_hosting_services = noco.get_rows(
            "PE5_Digital_Hosting_Services")
        self.volatile_datasets = noco.get_rows("PE24_Volatile_Datasets")
        self.persistent_datasets = noco.get_rows("PE22_Persistent_Datasets")
        self.access_points = noco.get_rows("PE26_Access_Points")
        self.digital_machine_events = noco.get_rows(
            "D7_Digital_Machine_Events")
        self.namespaces = noco.get_rows("Meta_Namespaces")
        self.topics = noco.get_rows("Topics")


class NameSpacesService:
    def __init__(self, namespaces: dict):
        self.namespaces = noco.get_rows("Meta_Namespaces")

        # default namespaces
        self.DCAT = DCAT
        self.DCTERMS = DCTERMS
        self.RDF = RDF
        self.RDFS = RDFS

        # custom namespaces
        self.CKG = Namespace(
            next(item for item in namespaces if item["short_form"] == "ckg")[
                "long_form"
            ]
        )
        self.CRM = Namespace(
            next(item for item in namespaces if item["short_form"] == "crm")[
                "long_form"
            ]
        )
        self.PDLM = Namespace(
            next(item for item in namespaces if item["short_form"] == "pdlm")[
                "long_form"
            ]
        )
        self.CRM_PEM = Namespace(
            next(item for item in namespaces if item["short_form"] == "crm_pem")[
                "long_form"
            ]
        )
        self.CRM_DIG = Namespace(
            next(item for item in namespaces if item["short_form"] == "crm_dig")[
                "long_form"
            ]
        )


top_store = Dataset()
data_service = DataService()
namespaces_service = NameSpacesService(data_service.namespaces)


def load_persons(create_diagrams=False):
    print("loading persons")
    for person_data in data_service.persons:
        person = Person(person_data, namespaces_service, top_store)

        person.populate_graph()
        if create_diagrams:
            person.visualise()


def load_teams(create_diagrams=False):
    print("loading teams")
    for team_data in data_service.teams:
        team_data["persons"] = []
        for member_ref in team_data["members"]:
            member = next(
                item for item in data_service.persons if item["Id"] == member_ref["Id"]
            )
            team_data["persons"].append(member)
        team = Team(team_data, namespaces_service, top_store)
        team.populate_graph()
        if create_diagrams:
            team.visualise()


def load_groups(create_diagrams=False):
    print("loading groups")
    for group_data in data_service.groups:
        group_data["persons"] = []
        group_data["groups"] = []
        for member_ref in group_data["members"]:
            member = next(
                item for item in data_service.persons if item["Id"] == member_ref["Id"]
            )
            group_data["persons"].append(member)
        for group_member_ref in group_data["members_groups"]:
            group_member = next(
                item
                for item in data_service.groups
                if item["Id"] == group_member_ref["Id"]
            )
            group_data["groups"].append(group_member)
        group = Group(group_data, namespaces_service, top_store)
        group.populate_graph()
        if create_diagrams:
            group.visualise()


def load_access_points(create_diagrams=False):
    print("loading access_points")
    for access_point_data in data_service.access_points:
        access_point = AccessPoint(
            access_point_data, namespaces_service, top_store)
        access_point.populate_graph()
        if create_diagrams:
            access_point.visualise()


def load_digital_objects(create_diagrams=False):
    print("loading digital objects")
    for do_data in data_service.digital_objects:
        do = DigitalObject(do_data, namespaces_service, top_store)
        do.populate_graph()
        if create_diagrams:
            do.visualise()


def load_services(create_diagrams=False):
    print("loading services")
    for service_data in data_service.services:
        # provided by person, group, team
        service_data["persons"] = []
        service_data["groups"] = []
        service_data["teams"] = []
        service_data["digital_hosting_services"] = []
        service_data["digital_curating_services"] = []
        service_data["digital_objects"] = []
        for person_ref in service_data["provided_by_person"]:
            person = next(
                item for item in data_service.persons if item["Id"] == person_ref["Id"]
            )
            service_data["persons"].append(person)

        for group_ref in service_data["provided_by_group"]:
            group = next(
                item for item in data_service.groups if item["Id"] == group_ref["Id"]
            )
            service_data["groups"].append(group)

        for team_ref in service_data["provided_by_team"]:
            team = next(
                item for item in data_service.teams if item["Id"] == team_ref["Id"]
            )
            service_data["teams"].append(team)

        for dhs_ref in service_data["consists_of_digital_hosting_service"]:
            dhs = next(
                item
                for item in data_service.digital_hosting_services
                if item["Id"] == dhs_ref["Id"]
            )
            service_data["digital_hosting_services"].append(dhs)

        for dcs_ref in service_data["consists_of_digital_curating_service"]:
            dcs = next(
                item
                for item in data_service.digital_curating_services
                if item["Id"] == dcs_ref["Id"]
            )
            service_data["digital_curating_services"].append(dcs)

        for do_ref in service_data["is_referred_to_by"]:
            do = next(
                item
                for item in data_service.digital_objects
                if item["Id"] == do_ref["Id"]
            )
            service_data["digital_objects"].append(do)

        service = Service(service_data, namespaces_service, top_store)
        service.populate_graph()
        if create_diagrams:
            service.visualise()


def load_digital_curating_services(create_diagrams=False):
    print("loading digital curating services")
    for dcs_data in data_service.digital_curating_services:
        dcs_data["curates_volatile_datasets"] = []
        dcs_data["continued_digital_curating_services"] = []

        for vds_ref in dcs_data["curates"]:
            vds = next(
                item
                for item in data_service.volatile_datasets
                if item["Id"] == vds_ref["Id"]
            )
            dcs_data["curates_volatile_datasets"].append(vds)

        for dcs_ref in dcs_data["continued"]:
            dcs = next(
                item
                for item in data_service.digital_curating_services
                if item["Id"] == dcs_ref["Id"]
            )
            dcs_data["continued_digital_curating_services"].append(dcs)

        dcs = DigitalCuratingService(dcs_data, namespaces_service, top_store)
        dcs.populate_graph()
        if create_diagrams:
            dcs.visualise()


def load_digital_hosting_services(create_diagrams=False):
    print("loading digital hosting services")
    for dhs_data in data_service.digital_hosting_services:
        dhs_data["provides_access_points"] = []
        dhs_data["hosts_volatile_datasets"] = []
        dhs_data["hosts_persistent_datasets"] = []

        for access_point_ref in dhs_data["provides_access_point"]:
            access_point = next(
                item
                for item in data_service.access_points
                if item["Id"] == access_point_ref["Id"]
            )
            dhs_data["provides_access_points"].append(access_point)

        for dovds_ref in dhs_data["hosts_digital_object_volatile_dataset"]:
            dovds = next(
                item
                for item in data_service.volatile_datasets
                if item["Id"] == dovds_ref["Id"]
            )
            dhs_data["hosts_volatile_datasets"].append(dovds)

        for dopds_ref in dhs_data["hosts_digital_object_persistent_dataset"]:
            dopds = next(
                item
                for item in data_service.persistent_datasets
                if item["Id"] == dopds_ref["Id"]
            )
            dhs_data["hosts_persistent_datasets"].append(dopds)

        dhs = DigitalHostingService(dhs_data, namespaces_service, top_store)
        dhs.populate_graph()
        if create_diagrams:
            dhs.visualise()


def load_volatile_datasets(create_diagrams=False):
    print("loading volatile datasets")
    for volatile_dataset_data in data_service.volatile_datasets:
        volatile_dataset_data["accessible_at_access_points"] = []
        volatile_dataset_data["has_persistent_dataset_snapshots"] = []

        for access_point_ref in volatile_dataset_data["accessible_at"]:
            access_point = next(
                item
                for item in data_service.access_points
                if item["Id"] == access_point_ref["Id"]
            )
            volatile_dataset_data["accessible_at_access_points"].append(
                access_point)

        for persistent_dataset_ref in volatile_dataset_data["has_dataset_snapshot"]:
            persistent_dataset = next(
                item
                for item in data_service.persistent_datasets
                if item["Id"] == persistent_dataset_ref["Id"]
            )
            volatile_dataset_data["has_persistent_dataset_snapshots"].append(
                persistent_dataset
            )

        volatile_dataset = VolatileDataset(
            volatile_dataset_data, namespaces_service, top_store
        )
        volatile_dataset.populate_graph()
        if create_diagrams:
            volatile_dataset.visualise()


def load_persistent_datasets(create_diagrams=False):
    print("loading persistent datasets")
    for persistent_dataset_data in data_service.persistent_datasets:
        persistent_dataset_data["accessible_at_access_points"] = []

        for access_point_ref in persistent_dataset_data["accessible_at"]:
            access_point = next(
                item
                for item in data_service.access_points
                if item["Id"] == access_point_ref["Id"]
            )
            persistent_dataset_data["accessible_at_access_points"].append(
                access_point)

        persistent_dataset = PersistentDataset(
            persistent_dataset_data, namespaces_service, top_store
        )
        persistent_dataset.populate_graph()
        if create_diagrams:
            persistent_dataset.visualise()


def load_digital_machine_events(create_diagrams=False):
    print("loading digital machine events")
    for dme_data in data_service.digital_machine_events:
        dme_data["was_motivated_by_projects"] = []
        dme_data["had_input_volatile_datasets"] = []
        dme_data["had_output_volatile_datasets"] = []
        dme_data["had_input_persistent_datasets"] = []
        dme_data["had_output_persistent_datasets"] = []
        dme_data["carried_out_by_persons"] = []

        # dme was motivated by project...
        for project_ref in dme_data["was_motivated_by"]:
            project = next(
                item
                for item in data_service.projects
                if item["Id"] == project_ref["Id"]
            )
            dme_data["was_motivated_by_projects"].append(project)

        # dme had input volatile dataset
        for dataset_ref in dme_data["had_input"]:
            dataset = next(
                item
                for item in data_service.volatile_datasets
                if item["Id"] == dataset_ref["Id"]
            )
            dme_data["had_input_volatile_datasets"].append(dataset)

        # dme had output persistent dataset
        for dataset_ref in dme_data["had_output"]:
            dataset = next(
                item
                for item in data_service.persistent_datasets
                if item["Id"] == dataset_ref["Id"]
            )
            dme_data["had_output_persistent_datasets"].append(dataset)

        # dme had output volatile dataset
        for dataset_ref in dme_data["PE24_Volatile_Datasets List"]:
            dataset = next(
                item
                for item in data_service.volatile_datasets
                if item["Id"] == dataset_ref["Id"]
            )
            dme_data["had_output_volatile_datasets"].append(dataset)

        # dme carried_out by person
        for person_ref in dme_data["carried_out_by_person"]:
            person = next(
                item for item in data_service.persons if item["Id"] == person_ref["Id"]
            )
            dme_data["carried_out_by_persons"].append(person)

        digital_machine_event = DigitalMachineEvent(
            dme_data, namespaces_service, top_store
        )
        digital_machine_event.populate_graph()
        if create_diagrams:
            digital_machine_event.visualise()


def load_topics(create_diagrams=False):
    print("loading topics")
    for topic_data in data_service.topics:
        topic = Topic(topic_data, namespaces_service, top_store)
        topic.populate_graph()
        if create_diagrams:
            topic.visualise()


def load_projects(create_diagrams=False):
    print("loading projects")
    for project_data in data_service.projects:
        project_data["supported_projects"] = []
        project_data["has_maintaining_teams"] = []
        project_data["has_topics"] = []

        # project has topics (only one atm)
        # name of the relation is some weird nocodb convention
        for topic_ref in project_data["nc_j8_t___nc_m2m__eofowxvl5s"]:
            topic = next(
                item
                for item in data_service.topics
                if item["Id"] == topic_ref["table2_id"]
            )
            project_data["has_topics"].append(topic)

        # project has maintaining teams
        for team_ref in project_data["teams"]:
            team = next(
                item for item in data_service.teams if item["Id"] == team_ref["Id"]
            )
            project_data["has_maintaining_teams"].append(team)

        # project supported project
        for project_ref in project_data["supported_project_activity"]:
            project = next(
                item
                for item in data_service.projects
                if item["Id"] == project_ref["Id"]
            )
            project_data["supported_projects"].append(project)

        project = Project(project_data, namespaces_service, top_store)
        project.populate_graph()
        if create_diagrams:
            project.visualise()


def test_all(graph):

    # test all entities
    TESTREPORT_DIR = "output/test_reports/"
    os.makedirs(
        TESTREPORT_DIR, exist_ok=True
    )

    ActorTests(graph, noco, report_dir=TESTREPORT_DIR).test_all("actors.txt")
    ActivitieTests(graph, noco, report_dir=TESTREPORT_DIR).test_all(
        "activities.txt")
    DigitalObjectTests(graph, noco, report_dir=TESTREPORT_DIR).test_all(
        "digitalObects.txt")


def main():
    load_persons(args.d)
    load_teams(args.d)
    load_groups(args.d)
    load_access_points(args.d)
    load_services(args.d)
    load_digital_objects(args.d)
    load_digital_hosting_services(args.d)
    load_digital_curating_services(args.d)
    load_volatile_datasets(args.d)
    load_persistent_datasets(args.d)
    load_digital_machine_events(args.d)
    load_topics(args.d)
    load_projects(args.d)
    # optional: last param for overall graph constructor is url of remote, defaults to http://localhost
    overall_graph = OverallGraph(
        top_store,
        namespaces_service.namespaces,
        {"username": args.u, "password": args.p},
        args.url,
    )
    if args.t:
        test_all(overall_graph)

    overall_graph.serialize()
    # push to remove and purge should be args?
    # I assume every time one pushes, one would purge as well, but maybe not!
    if args.push:
        overall_graph.purge_remote()
        overall_graph.push_to_remote()


if __name__ == "__main__":
    main()
