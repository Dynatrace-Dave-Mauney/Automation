import os
import sys
import create_backup_zip_file
import create_version_json_file
import create_metrics_json_file
import create_entities_json_file
import create_metrics_table
import create_entities_table
import create_templates_table
import create_dashboard_generator_yaml_file
import generate_dashboards_from_yaml
import create_index_of_generated_dashboards
import put_all_dashboards_util


def main(arguments):
    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'
    arguments = '', env, token

    # Create project backup zip file
    print('creating backup zip file')
    create_backup_zip_file.main(env_name)

    # Create "version.json" file used to generate dashboards
    print('creating version.json file')
    # TODO: Wny is this API call no longer possible for SaaS?
    # TODO: Use the UI to copy the version manually for SaaS...
    # create_version_json_file.main(arguments)

    # Create "metrics.json" file used to generate metrics dashboards
    print('creating metrics.json file')
    create_metrics_json_file.main(arguments)

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

    # Upload all dashboards to Dynatrace tenant or environment
    #print(f'uploading dashboards to {arguments[1]}')
    #put_all_dashboards_util.main(arguments)


if __name__ == '__main__':
    # Specify the tenant and token in arguments
    main(sys.argv)
