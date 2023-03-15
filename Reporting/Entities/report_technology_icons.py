import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

icon_list = []


def process(env, token, entity_type):
    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    params = '&entitySelector=' + urllib.parse.quote(entity_selector) + '&fields=' + urllib.parse.quote('icon')
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)

    print('Technologies as identified by  "primaryIcon"')

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            primary_icon_type = inner_entities_json.get('icon').get('primaryIconType', '')
            if primary_icon_type not in icon_list:
                icon_list.append(primary_icon_type)

    for icon in sorted(icon_list):
        print(icon)


def main():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, 'PROCESS_GROUP')


if __name__ == '__main__':
    main()

# Examples from "Prod" (11/23/2022)
# aix
# apache
# apache-solr
# apache-tomcat
# aspnet
# cassandra
# coredns
# docker-logo
# dotnet
# dynatrace
# elastic
# etcd-signet
# golang-signet
# haproxy
# ibm
# iis-microsoft
# java
# jboss
# jetty
# kafka-signet
# kubernetes-signet
# linux
# mongo-db
# mysql
# node-js
# openshift
# oracledatabase
# oracleweblogic
# perl
# process
# python
# ruby
# sap
# sql-microsoft
# was-liberty-profile
# web-sphere
# windows
