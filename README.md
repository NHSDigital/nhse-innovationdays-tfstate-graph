# nhse-innovationdays-tfstate-graph
## Background
I've been looking for a means of automatically visualising AWS deployments, and have been pretty underwhelmed when I've tried to use existing tooling such as [Terraform graph](https://developer.hashicorp.com/terraform/cli/commands/graph) or [InfraMap](https://github.com/cycloidio/inframap) against complex real-world tfstate files.

In particular I have the following requirements...

- To be able to visualise both hard (those expressed directly in terraform resources) and soft (expressed indirectly e.g. via environment variables) relationships between resources.
- To be able to visualise the actual deployment (post-apply) using tfstate rather than pre-applied artefacts such as a terraform plan or terraform source

This repository contains a fledgling proof-of-concept that imports tfstate into a [Neo4j](https://neo4j.com) graph database and (initially) uses the inbuilt graph visualisation capabilities of the database UI to display the results. In the fullness of time this might lead to automated diagram generation by running [Cypher](https://neo4j.com/docs/cypher-manual/current/introduction/) queries against the graph.

## Current State

The current state of the tool will import AWS Lambda Functions and SQS queues, and determine the relationships between these based upon either event triggers or DLQs define in tfstate.

## Developer Setup
### Pre-Requisites

- [Neo4j AuraDb](https://neo4j.com/cloud/aura-free/) cloud-hosted database created (there is a free tier available to run this PoC).
- Python 3 development environment (e.g. [VSCode](https://code.visualstudio.com/docs/python/python-tutorial) )
- TFState file
