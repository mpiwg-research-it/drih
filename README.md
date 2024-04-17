<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->

<a name="readme-top"></a>

<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->

<!-- PROJECT SHIELDS -->

<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

<!-- [![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url] -->

<!-- PROJECT LOGO -->

<br />
<div align="center">
  <a href="https://www.mpiwg-berlin.mpg.de/">
    <img src="images/logo.png" alt="Logo" width="200" height="200">
  </a>

<h3 align="center">Digital Research Infrastructure for the Humanities (DRIH)</h3>

<!-- <p align="center">
    An awesome README template to jumpstart your projects!
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template">View Demo</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Report Bug</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Request Feature</a>
  </p>
</div> -->

</div>

<!-- TABLE OF CONTENTS -->

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#ingestor-script">Ingestor Script</a>
    </li>
    <li><a href="#project-description-layer-model">Project Description Layer Model (PDLM) v.0.1</a></li>
    <li><a href="#pdlm-tabular-data">Tabular data of the PDLM v.0.1</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

<!-- We could add a DRIH screenshot here? -->

<!-- [![Product Name Screen Shot][product-screenshot]](https://example.com) -->

In view of the steadily growing volume of digital output from Humanities research projects in recent decades, the question of the long-term and sustainable preservation of this research data is becoming increasingly urgent. To meet this challenge, we are establishing the Central Knowledge Graph (CKG) as a key element of our documentation and publication strategy for research data. In this paper, we present two of the cornerstones of this strategy: The newly developed Project Description Layer Model (PDLM) provides the means to document the required contextual metadata about research projects and their digital outputs; the Zellij Semantic Documentation Protocol systematically documents the modeling patterns used to create CIDOC CRM representations of project data in a transparent and reusable way. We highlight how we developed and documented our models and present a case study to showcase its expressivity, as well as its real-world potential in saving legacy data at the Max Planck Institute for the History of Science.

<!-- GETTING STARTED -->

## Ingestor Script

Our open-source [ingestor](https://github.com/mpiwg-research-it/drih/blob/main/ingestor_code/__main__.py) is responsible for transforming the data stored in NocoDB into PDLM-compliant triples. It features code able to draw [diagrams](https://github.com/mpiwg-research-it/drih/blob/main/ingestor_output_samples/named_graphs_diagrams/actor/project-team/pe34_002.png) and to [test](https://github.com/mpiwg-research-it/drih/blob/main/ingestor_output_samples/test_reports/activities.txt) each of the named graph it generates and populates, in addition to displaying the test results in the [console](https://github.com/mpiwg-research-it/drih/blob/main/ingestor_output_samples/tests_console_output/tests_output_screenshot.png) for quick verification.

### Prerequisites

If you wish to use the ingestor in your own project, and take advantage of its NocoDB connection capabilities, you will need access to an instance of [NocoDB](https://github.com/nocodb/nocodb). You will then need to create an .env file based on the [.env.sample file](https://github.com/mpiwg-research-it/drih/blob/main/ingestor_code/.env.sample) we provide.

### Installation

Please install the dependencies as described in [requirements.txt](https://github.com/mpiwg-research-it/drih/blob/main/ingestor_code/requirements.txt)

### Usage

```
python -m ingestor -url http://remote_url -u rs_username -p rs_password -d -t
```

options:

- **-h**, --help  shows help and exit
- **-url** URL    url of the remote researchspace instance (default: http://localhost)
- **-u**   U      username for the remote researchspace instance (default: admin)
- **-p**   P      password for the remote researchspace instance  (default: admin)
- **-push**       push to researchspace instance set in -url (you might need to set -u and -p)
- **-d**          generate diagram for each entity
- **-t**          run tests and generate test reports in output/

## Project Description Layer Model

The Project Description Layer Model (PDLM) is a semantic model based on CIDOC CRM, designed to describe research projects and their digital outputs within an institutional research data management strategy. Utilizing concepts from the Parthenos Entities Model (PEM), the PDLM emphasizes entities like digital objects (such as datasets and software), activities (including research and service projects), and actors (individuals, groups, and project teams). Digital objects are categorized into datasets and software, with distinctions made between volatile and persistent forms, crucial for archival purposes and data reuse. Activities encompass research and service projects, with detailed documentation of digital machine events for tracking the creation context of digital objects. Actors, comprising project teams, groups, and individuals, are essential for establishing the contextual framework. Developed and documented using the Zellij Semantic Documentation Protocol, the PDLM serves as a core model for contextualizing projects and their digital outputs, forming a vital part of the institution's Central Knowledge Graph (CKG) alongside CIDOC CRM representations of research data, contributing to sustainable research data management.

![PDLM_0 1_Overview](https://github.com/mpiwg-research-it/drih/assets/10489583/79b98408-62fa-454a-ab09-92b70408a6de)

_Overview of the PDLM_

### PDLM Development Version

The current development version of the PDLM is based on the RDFS encoding of the Parthenos Entity Model 3.1.1.

[CRMpe_v3.1.1_pdlm-extension_2024-04-17.rdfs](https://github.com/mpiwg-research-it/drih/blob/main/pdlm/CRMpe_v3.1.1_pdlm-extension_2024-04-17.rdfs)

We plan to publish the PDLM in its own namespace.

## PDLM Model Definitions from Airtable

CSV-Exports from Airtable of the Project Team and Research Project model:

- [Model_Fields-PDLM.1 Project Team (MPIWG).csv](https://github.com/mpiwg-research-it/drih/files/14572058/Model_Fields-PDLM.1.Project.Team.MPIWG.csv)
- [Model_Fields-PDLM.11 Research Project (MPIWG).csv](https://github.com/mpiwg-research-it/drih/files/14572057/Model_Fields-PDLM.11.Research.Project.MPIWG.csv)

The files show the basic structure of a model consisting of individual fields.

- `ID`: unique identifier for the field within the particular model
- `model_specific_name`: model specific label of the field
- `model_specific_description`: model specific description of the field
- `model_ontological_scope`: domain of the field
- `field_crm_path`: principle CRM path of the field
- `field_expected_value_type`: the expected range type of the field which may either be an entity type, another reference model, or a collection of fields
- `model_specific_expected_resource_model`: gives the specific reference model if the expected range type is a reference model
- `model_specific_expected_collection`: gives the specific collection if the expected range type is a collection
- `field_turtle`: example Turtle serialisation of the field

<!-- LICENSE -->

## License

Distributed under the CC0 1.0 Universal. See `LICENSE.txt` for more information.

<!-- CONTACT -->

## Contact

Your Name - [@your_twitter](https://twitter.com/your_username) - email@example.com

Project Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name)

<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

placeholder
