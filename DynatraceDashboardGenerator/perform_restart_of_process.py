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


def main():
    from Reuse import environment

    # _, env, token = environment.get_environment('Prod')
    # _, env, token = environment.get_environment('Prep')
    # _, env, token = environment.get_environment('Dev')
    _, env, token = environment.get_environment('Personal')
    # _, env, token = environment.get_environment('FreeTrial1')

    database = r'DynatraceDashboardGenerator.db'
    conn = create_metrics_table.create_connection(database)

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
    main()
