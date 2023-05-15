import csv
import os


def get_modules(clusterone_results, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(clusterone_results) as results, open(f'{output_dir}/clusterone-module-list.tsv', 'w') as output:
        csv_reader = csv.reader(results, delimiter=',')
        next(csv_reader)            # Skip header
        for line in csv_reader:
            modules = line[-1]
            modules = modules.replace(" ", "\t")
            output.write(modules + "\n")

        print(f'Generated {output_dir}/clusterone-module-list.tsv')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'clusterone_results', help='CSV file corresponding to the results of running ClusterONE')
    parser.add_argument(
        'output_dir', help='output directory for the text file containing only the modules found via ClusterONE'
    )

    args = parser.parse_args()

    get_modules(args.clusterone_results, args.output_dir)
