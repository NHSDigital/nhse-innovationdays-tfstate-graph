# nhse-innovationdays-tfstate-graph
## Background
I've been looking for a means of automatically visualising AWS deployments, and have been pretty underwhelmed when I've tried to use existing tooling such as [Terraform graph](https://developer.hashicorp.com/terraform/cli/commands/graph) or [InfraMap](https://github.com/cycloidio/inframap) against complex real-world tfstate files.

In particular I have the following requirements...

- To be able to visualise both hard (those expressed directly in terraform resources) and soft (expressed indirectly e.g. via environment variables) relationships between resources.
- To be able to visualise the actual deployment (post-apply) using tfstate rather than pre-apply assets such as a terraform plan or terraform source

This repository contains a fledgling proof-of-concept that imports tfstate into a [Neo4j](https://neo4j.com) graph database and (initially) uses the inbuilt graph visualisation capabilities of the database UI to display the results. In the fullness of time this might lead to automated diagram generation by running [Cypher](https://neo4j.com/docs/cypher-manual/current/introduction/) queries against the graph.

## Current State

The current state of the tool is a proof-of-concept that will import AWS Lambda Functions and SQS queues, and determine the relationships between these based upon either event triggers or DLQs define in tfstate.

## Developer Setup
### Pre-Requisites

- [Neo4j AuraDb](https://neo4j.com/cloud/aura-free/) cloud-hosted database created (there is a free tier available to run this PoC).
- Python 3 development environment (e.g. [VSCode](https://code.visualstudio.com/docs/python/python-tutorial) )
- TFState file (provided separately)

### Python Packages

Install the following packages into your virtual environment:

    pip install neo4j
    pip install python-dotenv

### Local configuration

Change the following lines in `import.py` to point to your AuraDB connection file (provided at DB creation) and tfstate file.

    # Change these lines to use your database and tfstate file
    NEO4J_CONNECTION_FILENAME = "Neo4j-250beb06-Created-2023-10-25.txt"
    TFSTATE_FILENAME = "env.tfstate"
    
### Running the import

Execute `import.py` from within your development environment.

There's currently no error handling so the import will succeed silently, or throw an error on issue.

The import script will clear down the database before importing, so can be run multiple times without issue.

### Checking the results

You can confirm that it has worked through your Neo4j workspace:

The following Cypher [query](https://workspace-preview.neo4j.io/workspace/query) should show AWS Lambda Functions, SQS Queues and Relationships:

`MATCH (n) MATCH (p)-[r]->(q) RETURN *`

Or "Show me a graph" in the [explorer](https://workspace-preview.neo4j.io/workspace/explore)

## Useful Resources

- [Neo4j Cypher](https://neo4j.com/docs/getting-started/cypher-intro/) Graph Query Language
- [Neo4j Workspace Explorer](https://workspace-preview.neo4j.io/workspace/query) to run queries and visualisations
- [Neo4J Python Driver Guide](https://neo4j.com/docs/python-manual/current/)
- [Neo4J Python Driver Reference](https://neo4j.com/docs/api/python-driver/current/)

## Next Steps

This is a **very** early proof-of-concept, so there's lots to do, including:

- Refactoring to eliminate copy-and-paste, magic strings, and other hacky messes
- Some semblance of error handling
- Sensible logging
- Use command-line arguments instead of hardcoded constants for the DB connection and tfstate files
- Expand to other resources beyond lambda functions and queues
- Additional relationships, including soft relationships extracted from environment variables
- Testing with tfstate files from multiple sources
- Generation of diagrms with different views based upon different object graph queries
- etc
