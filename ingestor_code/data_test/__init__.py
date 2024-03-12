import pandas as pd
import numpy as np
import rdflib
import os
import practicalSPARQL
import warnings
from nocodb.filters import LikeFilter



class outColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def unit_test(data: pd.DataFrame, required_fields: list, test_type: str):
    # valid_test_type = {"one2many","one2one", "dependant"}
    valid_test_type = {"1.1", "1.*", "reflective"}
    if test_type not in valid_test_type:
        raise ValueError(
            "test_type is Invalid - Accepted values: one2many, one2one, dependant"
        )

    # if test_type == 'one2many':
    if test_type == "1.*":
        if len(required_fields) != 1:
            raise ValueError(
                "required_fields must be a list of a single item if test_type is 1.*"
            )

        required_field = required_fields[0]
        fail = False
        failing = None
        var = list(data[required_field])
        if (None in var) or (
            True in list(data[required_field].isna())
        ):  # second condition is a temp fix. should be fixed in practicalsparql for a more general fix of select_dataframe data types (add dtype object)
            fail = True

        # find failing and return
        if fail is True:
            failing = data.loc[data[required_field].isna()]
        return fail, failing

    # elif test_type == "one2one":
    elif test_type == "1.1":
        if len(required_fields) != 2:
            raise ValueError(
                "required_fields must be a list of a two items if test_type is 1.1"
            )

        required_field = required_fields[1]
        required_index = required_fields[
            0
        ]  # this is usually the URI to check for repeated
        fail = False
        failing = None
        var = list(data[required_field])

        # condition one - items have to be present (i.e. no None values)
        if (None in var) or (
            True in list(data[required_field].isna())
        ):  # second condition is a temp fix. should be fixed in practicalsparql for a more general fix of select_dataframe data types (add dtype object)
            fail = True

        # condition two - each item must exist once.
        count = data[required_index].value_counts()
        if set(list(count)) != {1}:
            fail = True

        # find failing and return
        if fail is True:
            var1 = data.loc[data[required_field].isna()]
            temp1 = count.where(count > 1)
            temp2 = temp1[~temp1.isna()].index.to_list()
            var2 = data.loc[data[required_index].isin(temp2)]
            failing = pd.concat([var1, var2], axis=0)
        return fail, failing

    # elif test_type == 'dependant':
    elif test_type == "reflective":
        if len(required_fields) != 2:
            raise ValueError(
                "required_fields var should be a two item list if the test_type is relflective"
            )

        fail = False
        failing_ind = []
        f1 = required_fields[0]  # if f1 exists
        f2 = required_fields[1]  # then f2 should be mandatory
        for ind, row in data.iterrows():
            if (row[f1] is not None) and (row[f2] is None):
                fail = True
                failing_ind.append(ind)
            else:
                continue
        failing = data.iloc[failing_ind]
        return fail, failing


## ACTOR TESTING
class ActorTests:
    def __init__(self, g_rdf: rdflib.Graph, noco, report_dir: str):
        self.graph = self.load_graph(g_rdf)
        self.noco = noco  # nocodb class object containing all relevant tables.
        self.team_test = self.load_clean("team")
        self.person_test = self.load_clean("person")
        self.group_test = self.load_clean("group")

        self.report_dir = report_dir

    def load_graph(self, g_rdf):
        graph = practicalSPARQL.rdfGRAPH()
        trig = g_rdf.store.serialize(format='trig')
        graph.parse(data=trig, format='trig')
        return graph
    
    # TODO here load from nonodb!
    def load_clean(self, cls: str):
        df = self.noco.get_tests(cls)
        df = pd.DataFrame(df)
        # do not test switched off rows
        df = df.loc[df["test_bool"] == True].reset_index(drop=True)
        no_query = df[df["query"].isnull()]
        if len(no_query) > 0:
            for ind, row in no_query.iterrows():
                n = row["name"]
                n = '! - Query for row: "{}" not found, will be ignored'.format(n)
                print(outColors.WARNING + n + outColors.ENDC)
        df_clean = df.drop(no_query.index).reset_index(drop=True)
        return df_clean

    def runTest(
        self, test_string: str, test_query: str, test_fields: list, test_type: str
    ):
        valid_test_type = {"1.1", "1.*", "reflective"}
        if test_type not in valid_test_type:
            raise ValueError(
                "test_type is Invalid - Accepted values: one2many, one2one, dependant"
            )

        g = self.graph
        q = test_query
        df = g.select_as_dataframe(q)

        if test_type == "1.*":
            if len(test_fields) > 1:
                raise ValueError(
                    'test_type is "1.*" but a len 2 list test_field is given. Expected 1'
                )
            else:
                fail, failing_triple = unit_test(df, test_fields, test_type=test_type)
        elif (test_type == "reflective") or (test_type == "1.1"):
            if len(test_fields) < 2:
                raise ValueError(
                    'test_type is "reflective" or "1.1" but a list of len 1 is given, Expected 2'
                )
            else:
                fail, failing_triple = unit_test(df, test_fields, test_type=test_type)

        if fail is True:
            report = "x - Test Failed for {}".format(test_string)
            print(outColors.FAIL + report + outColors.ENDC)
            report_full = (
                report
                + "\n --- Failing Entities --- \n"
                + failing_triple.to_string()
                + "\n\n"
            )
        else:
            report = "\u2713 - Test Passed for {}".format(test_string)
            print(outColors.OKGREEN + report + outColors.ENDC)
            report_full = report + "\n"

        return report_full

    def persons(self, report_path=None):
        person_tests = self.person_test
        report = []
        for ind, test in person_tests.iterrows():
            car = test["cardinality"]
            if test["reflective"] is True:
                car = "reflective"
            rep = self.runTest(
                test["name"],
                test_query=test["query"],
                test_fields=test["relevant_variables"].split(","),
                test_type=car,
            )
            report.append(rep)

        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)

        return report

    def teams(self, report_path=None):
        team_tests = self.team_test

        report = []

        for ind, test in team_tests.iterrows():
            car = test["cardinality"]
            if test["reflective"] is True:
                car = "reflective"
            rep = self.runTest(
                test["name"],
                test_query=test["query"],
                test_fields=test["relevant_variables"].split(","),
                test_type=car,
            )
            report.append(rep)

        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)
        return report

    def groups(self, report_path=None):
        group_tests = self.group_test
        report = []
        for ind, test in group_tests.iterrows():
            car = test["cardinality"]
            if test["reflective"] is True:
                car = "reflective"
            rep = self.runTest(
                test["name"],
                test_query=test["query"],
                test_fields=test["relevant_variables"].split(","),
                test_type=car,
            )
            report.append(rep)

        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)
        return report

    def test_all(self, report_path=None):
        rep_1 = self.persons()
        rep_2 = self.teams()
        rep_3 = self.groups()
        report = rep_1 + rep_2 + rep_3
        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)
        return report


class DigitalObjectTests:
    def __init__(self, g_rdf: rdflib.Graph, noco, report_dir: str):
        self.graph = self.load_graph(g_rdf)
        self.report_dir = report_dir
        self.noco = noco
        # added separation between volatile and persistent
        self.dataset_per_test = self.load_clean("dataset_persistent")
        self.software_per_test = self.load_clean("software_persistent")
        self.dataset_vol_test = self.load_clean("dataset_volatile")
        self.software_vol_test = self.load_clean("software_volatile")


    def load_graph(self, g_rdf):
        graph = practicalSPARQL.rdfGRAPH()
        trig = g_rdf.store.serialize(format='trig')
        graph.parse(data=trig, format='trig')
        return graph
    
    def load_clean(self, cls: str):
        df = self.noco.get_tests(cls)
        df = pd.DataFrame(df)
        # do not test switched off rows
        df = df.loc[df["test_bool"] == True].reset_index(drop=True)
        no_query = df[df["query"].isnull()]
        if len(no_query) > 0:
            for ind, row in no_query.iterrows():
                n = row["name"]
                n = '! - Query for row: "{}" not found, will be ignored'.format(n)
                print(outColors.WARNING + n + outColors.ENDC)
        df_clean = df.drop(no_query.index).reset_index(drop=True)
        return df_clean

    def runTest(
        self, test_string: str, test_query: str, test_fields: list, test_type: str
    ):
        valid_test_type = {"1.1", "1.*", "reflective"}
        if test_type not in valid_test_type:
            raise ValueError(
                "test_type is Invalid - Accepted values: one2many, one2one, dependant"
            )

        g = self.graph
        q = test_query
        df = g.select_as_dataframe(q)

        if test_type == "1.*":
            if len(test_fields) > 1:
                raise ValueError(
                    'test_type is "1.*" but a len 2 list test_field is given. Expected 1'
                )
            else:
                fail, failing_triple = unit_test(df, test_fields, test_type=test_type)
        elif (test_type == "reflective") or (test_type == "1.1"):
            if len(test_fields) < 2:
                raise ValueError(
                    'test_type is "reflective" or "1.1" but a list of len 1 is given, Expected 2'
                )
            else:
                fail, failing_triple = unit_test(df, test_fields, test_type=test_type)

        if fail is True:
            report = "x - Test Failed for {}".format(test_string)
            print(outColors.FAIL + report + outColors.ENDC)
            report_full = (
                report
                + "\n --- Failing Entities --- \n"
                + failing_triple.to_string()
                + "\n\n"
            )
        else:
            report = "\u2713 - Test Passed for {}".format(test_string)
            print(outColors.OKGREEN + report + outColors.ENDC)
            report_full = report + "\n"

        return report_full

    def datasets_persistent(self, report_path=None):
        # TODO - Chekck and separate tests for Volatile and Presistent
        dataset_tests = self.dataset_per_test
        report = []
        for ind, test in dataset_tests.iterrows():
            car = test["cardinality"]
            if test["reflective"] is True:
                car = "reflective"
            rep = self.runTest(
                test["name"],
                test_query=test["query"],
                test_fields=test["relevant_variables"].split(","),
                test_type=car,
            )
            report.append(rep)

        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)

        return report

    def datasets_volatile(self, report_path=None):
        # TODO - Chekck and separate tests for Volatile and Presistent
        dataset_tests = self.dataset_vol_test
        report = []
        for ind, test in dataset_tests.iterrows():
            car = test["cardinality"]
            if test["reflective"] is True:
                car = "reflective"
            rep = self.runTest(
                test["name"],
                test_query=test["query"],
                test_fields=test["relevant_variables"].split(","),
                test_type=car,
            )
            report.append(rep)

        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)

        return report

    def software_persistent(self, report_path=None):
        # TODO - Chekck and separate tests for Volatile and Presistent
        software_tests = self.software_per_test
        report = []
        for ind, test in software_tests.iterrows():
            car = test["cardinality"]
            if test["reflective"] is True:
                car = "reflective"
            rep = self.runTest(
                test["name"],
                test_query=test["query"],
                test_fields=test["relevant_variables"].split(","),
                test_type=car,
            )
            report.append(rep)

        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)

        return report

    def software_volatile(self, report_path=None):
        # TODO - Chekck and separate tests for Volatile and Presistent
        software_tests = self.software_vol_test
        report = []
        for ind, test in software_tests.iterrows():
            car = test["cardinality"]
            if test["reflective"] is True:
                car = "reflective"
            rep = self.runTest(
                test["name"],
                test_query=test["query"],
                test_fields=test["relevant_variables"].split(","),
                test_type=car,
            )
            report.append(rep)

        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)

        return report

    def test_all(self, report_path=None):
        rep_1 = self.datasets_persistent()
        rep_2 = self.software_persistent()
        rep_3 = self.datasets_volatile()
        rep_4 = self.software_volatile()

        report = rep_1 + rep_2 + rep_3 + rep_4
        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)
        return report


class ActivitieTests:
    def __init__(self, g_rdf: rdflib.Graph, noco, report_dir: str):
        self.graph = self.load_graph(g_rdf)
        self.report_dir = report_dir
        self.noco = noco
        self.service_test = self.load_clean("service")
        self.digita_machine_event_test = self.load_clean("digital_machine_event")
        self.project_research_test = self.load_clean("project_research")
        self.project_service_test = self.load_clean("project_service")
        self.join_leave_test = self.load_clean("join_leave")

    def load_graph(self, g_rdf):
        graph = practicalSPARQL.rdfGRAPH()
        trig = g_rdf.store.serialize(format='trig')
        graph.parse(data=trig, format='trig')
        return graph
    
    def load_clean(self, cls: str):
        df = self.noco.get_tests(cls)
        df = pd.DataFrame(df)
        # do not test switched off rows
        df = df.loc[df["test_bool"] == True].reset_index(drop=True)
        no_query = df[df["query"].isnull()]
        if len(no_query) > 0:
            for ind, row in no_query.iterrows():
                n = row["name"]
                n = '! - Query for row: "{}" not found, will be ignored'.format(n)
                print(outColors.WARNING + n + outColors.ENDC)
        df_clean = df.drop(no_query.index).reset_index(drop=True)
        return df_clean

    def runTest(
        self, test_string: str, test_query: str, test_fields: list, test_type: str
    ):
        valid_test_type = {"1.1", "1.*", "reflective"}
        if test_type not in valid_test_type:
            raise ValueError(
                "test_type is Invalid - Accepted values: one2many, one2one, dependant"
            )

        g = self.graph
        q = test_query
        df = g.select_as_dataframe(q)

        if test_type == "1.*":
            if len(test_fields) > 1:
                raise ValueError(
                    'test_type is "1.*" but a len 2 list test_field is given. Expected 1'
                )
            else:
                fail, failing_triple = unit_test(df, test_fields, test_type=test_type)
        elif (test_type == "reflective") or (test_type == "1.1"):
            if len(test_fields) < 2:
                raise ValueError(
                    'test_type is "reflective" or "1.1" but a list of len 1 is given, Expected 2'
                )
            else:
                fail, failing_triple = unit_test(df, test_fields, test_type=test_type)

        if fail is True:
            report = "x - Test Failed for {}".format(test_string)
            print(outColors.FAIL + report + outColors.ENDC)
            report_full = (
                report
                + "\n --- Failing Entities --- \n"
                + failing_triple.to_string()
                + "\n\n"
            )
        else:
            report = "\u2713 - Test Passed for {}".format(test_string)
            print(outColors.OKGREEN + report + outColors.ENDC)
            report_full = report + "\n"

        return report_full

    def services(self, report_path=None):
        # TODO - Chekck and separate tests for Volatile and Presistent
        service_tests = self.service_test
        report = []
        for ind, test in service_tests.iterrows():
            car = test["cardinality"]
            if test["reflective"] is True:
                car = "reflective"
            rep = self.runTest(
                test["name"],
                test_query=test["query"],
                test_fields=test["relevant_variables"].split(","),
                test_type=car,
            )
            report.append(rep)

        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)

        return report

    def projects_research(self, report_path=None):
        # TODO - Check and separate tests for Volatile and Presistent
        project_tests = self.project_research_test
        report = []
        for ind, test in project_tests.iterrows():
            car = test["cardinality"]
            if test["reflective"] is True:
                car = "reflective"
            rep = self.runTest(
                test["name"],
                test_query=test["query"],
                test_fields=test["relevant_variables"].split(","),
                test_type=car,
            )
            report.append(rep)

        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)

        return report

    def projects_service(self, report_path=None):
        # TODO - Chekck and separate tests for Volatile and Presistent
        project_tests = self.project_service_test
        report = []
        for ind, test in project_tests.iterrows():
            car = test["cardinality"]
            if test["reflective"] is True:
                car = "reflective"
            rep = self.runTest(
                test["name"],
                test_query=test["query"],
                test_fields=test["relevant_variables"].split(","),
                test_type=car,
            )
            report.append(rep)

        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)

        return report

    def digital_machine_events(self, report_path=None):
        # TODO - Chekck and separate tests for Volatile and Presistent
        digita_machine_event_tests = self.digita_machine_event_test
        report = []
        for ind, test in digita_machine_event_tests.iterrows():
            car = test["cardinality"]
            if test["reflective"] is True:
                car = "reflective"
            rep = self.runTest(
                test["name"],
                test_query=test["query"],
                test_fields=test["relevant_variables"].split(","),
                test_type=car,
            )
            report.append(rep)

        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)

        return report

    def join_leave(self, report_path=None):
        # TODO - Chekck and separate tests for Volatile and Presistent
        join_leave_tests = self.join_leave_test
        report = []
        for ind, test in join_leave_tests.iterrows():
            car = test["cardinality"]
            if test["reflective"] is True:
                car = "reflective"
            rep = self.runTest(
                test["name"],
                test_query=test["query"],
                test_fields=test["relevant_variables"].split(","),
                test_type=car,
            )
            report.append(rep)

        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)

        return report

    def test_all(self, report_path=None):
        rep_1 = self.services()
        rep_2 = self.projects_research()
        rep_3 = self.projects_service()
        rep_4 = self.digital_machine_events()
        rep_5 = self.join_leave()

        report = rep_1 + rep_2 + rep_3 + rep_4 + rep_5
        if report_path is not None:
            writing_path = os.path.join(self.report_dir, report_path)
            with open(writing_path, "w+") as f:
                for l in report:
                    f.write(l)
        return report
