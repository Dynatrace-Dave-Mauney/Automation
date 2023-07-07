import sys
import create_metrics_json_file
import create_metrics_table
import create_templates_table
import create_dashboard_generator_yaml_file
import generate_dashboards_from_yaml
import create_index_of_generated_dashboards

# from Reuse import dynatrace_api
from Reuse import environment


def main(arguments):
    env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('NonProd')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    # env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    arguments = '', env, token

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
    # Specify the tenant and token in arguments
    main(sys.argv)