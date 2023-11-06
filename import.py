import dotenv
import os
import json
from neo4j import GraphDatabase

NODE_FUNCTION_MAP = {}
REL_FUNCTION_MAP = {}

def create_sqs_queue(driver, resourceType, resource):
  for instance in resource["instances"]:
    name = instance["attributes"]["name"]
    arn = instance["attributes"]["arn"]
    driver.execute_query("CREATE (resource:" + resourceType + "{name: '"+ name + "', arn: '" + arn + "'})")

def create_lambda_function(driver, resourceType, resource):
  for instance in resource["instances"]:
    name = instance["attributes"]["function_name"]
    arn = instance["attributes"]["arn"]
    driver.execute_query("CREATE (resource:" + resourceType + "{name: '"+ name + "', arn: '" + arn + "'})")

def create_lambda_event_source_mapping(driver, resourceType, resource):
  for instance in resource["instances"]:
    queueArn = instance["attributes"]["event_source_arn"]
    lambdaArn = instance["attributes"]["function_arn"]

    query = ("MATCH (q:aws_sqs_queue) " +
            "MATCH (l:aws_lambda_function) " +
            "WHERE q.arn = '" + queueArn + "' " +
            "AND l.arn = '" + lambdaArn + "' " +
            "MERGE (q)-[:EVENT_TRIGGER]->(l)")
    driver.execute_query(query)

def create_sqs_queue_relationships(driver, resourceType, resource):
  for instance in resource["instances"]:
    queueArn = instance["attributes"]["arn"]
    redrivePolicy = instance["attributes"]["redrive_policy"]
    
    if redrivePolicy:
      dlqArn = json.loads(redrivePolicy)["deadLetterTargetArn"]

      query = ("MATCH (q:aws_sqs_queue) " +
              "MATCH (dlq:aws_sqs_queue) " +
              "WHERE q.arn = '" + queueArn + "' " +
              "AND dlq.arn = '" + dlqArn + "' " +
              "MERGE (q)-[:DLQ]->(dlq)")
      driver.execute_query(query)

def create_node(driver, resource):
  resourceType = resource["type"]
  createFunction = NODE_FUNCTION_MAP.get(resourceType)
  if createFunction:
    createFunction(driver, resourceType, resource)

def create_relationship(driver, resource):
  resourceType = resource["type"]
  createFunction = REL_FUNCTION_MAP.get(resourceType)
  if createFunction:
    createFunction(driver, resourceType, resource)


NODE_FUNCTION_MAP["aws_lambda_function"] = create_lambda_function
NODE_FUNCTION_MAP["aws_sqs_queue"] = create_sqs_queue

REL_FUNCTION_MAP["aws_lambda_event_source_mapping"] = create_lambda_event_source_mapping
REL_FUNCTION_MAP["aws_sqs_queue"] = create_sqs_queue_relationships

# Change these lines to use your database and tfstate file
NEO4J_CONNECTION_FILENAME = "Neo4j-250beb06-Created-2023-10-25.txt"
TFSTATE_FILENAME = "env.tfstate"

def main():
  
  dotenv.load_dotenv(NEO4J_CONNECTION_FILENAME)

  with open(TFSTATE_FILENAME) as tfStateFile:
    tfstate = json.load(tfStateFile)

  URI = os.getenv("NEO4J_URI")
  AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

  with GraphDatabase.driver(URI, auth=AUTH) as driver:
      driver.verify_connectivity()

      # Clear down database before import 
      driver.execute_query("MATCH (n) DETACH DELETE n")

      # Import nodes
      for resource in tfstate["resources"]:
        if resource["mode"] == "managed":
          create_node(driver, resource)

      # Import relationships
      for resource in tfstate["resources"]:
        if resource["mode"] == "managed":
          create_relationship(driver, resource)

if __name__ == '__main__':
  main()