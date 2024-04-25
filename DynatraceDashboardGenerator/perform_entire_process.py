# import os
import sys
import create_backup_zip_file
import create_version_json_file
import create_metrics_json_file
# import create_entities_json_file
import create_metrics_table
# import create_entities_table
import create_templates_table
import create_dashboard_generator_yaml_file
import generate_dashboards_from_yaml
import create_index_of_generated_dashboards

# from Reuse import dynatrace_api
from Reuse import environment


def main(arguments):
    if len(arguments) != 4:
        friendly_function_name = 'Dynatrace Automation'
        env_name_supplied = environment.get_env_name(friendly_function_name)
        # For easy control from IDE
        env_name_supplied = 'Upper'
        # env_name_supplied = 'Lower'
        # env_name_supplied = 'Sandbox'
        #
        # env_name_supplied = 'Prod'
        # env_name_supplied = 'PreProd'
        # env_name_supplied = 'Sandbox'
        # env_name_supplied = 'Dev'
        # env_name_supplied = 'Personal'
        # env_name_supplied = 'Demo'
        env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
        arguments = '', env, token
    else:
        print(f'Arguments: {arguments}')
        env_name = arguments[3]

    # Create project backup zip file
    print('creating backup zip file')
    create_backup_zip_file.main(env_name)

    # Create "version.json" file used to generate dashboards
    print('creating version.json file')
    create_version_json_file.main(arguments)

    # Create "metrics.json" file used to generate metrics dashboards
    print('creating metrics.json file')
    create_metrics_json_file.main(arguments)

    # TODO: Entities are not used in the process currently for various reasons...
    # Create "entities.json" file used to generate entities dashboards
    # print('creating entities.json file')
    # create_entities_json_file.main(arguments)

    database = r'DynatraceDashboardGenerator.db'
    conn = create_metrics_table.create_connection(database)

    # Create and load "metrics" table used to generate metrics dashboards
    print('loading metrics table')
    with conn:
        create_metrics_table.drop_metrics_table(conn)
        create_metrics_table.create_metrics_table(conn)
        create_metrics_table.load_metrics_table(conn)

    # TODO: Entities are not used in the process currently for various reasons...
    # Create and load "entities" table used to generate metrics dashboards
    # print('loading entities table')
    # create_entities_table.main()  #  This will query to test it...not needed here
    # with conn:
    #     create_entities_table.drop_entities_table(conn)
    #     create_entities_table.create_entities_table(conn)
    #     create_entities_table.load_entities_table(conn)

    # Create and load "templates" table used to generate metrics dashboards
    print('loading templates table')
    # create_templates_table.main()  #  This will query to test it...not needed here
    with conn:
        create_templates_table.drop_templates_table(conn)
        create_templates_table.create_templates_table(conn)
        create_templates_table.load_templates_table(conn)

    # Create "dashboard_controller.yaml" used to generate metrics dashboards
    print('creating dashboard_controller.yaml file')
    create_dashboard_generator_yaml_file.main()

    # Generate dashboards in JSON format
    print('generating dashboard JSON files format')
    generate_dashboards_from_yaml.main()

    # Create dashboard index text file
    print('creating dashboard index text file')
    create_index_of_generated_dashboards.main()


if __name__ == '__main__':
    # Specify the tenant, token and environment name in arguments or
    # in the "main" method inline
    main(sys.argv)
