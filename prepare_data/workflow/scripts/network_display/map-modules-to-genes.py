import os


def map_genes_to_modules(module_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(module_file) as modules, open(f'{output_dir}/modules-to-genes.tsv', 'w') as output:
        for idx, module in enumerate(modules):
            module = module.rstrip()
            genes = module.split('\t')

            for gene in genes:
                output.write(f'{idx + 1}\t{gene}\n')

    print(f'Generated {output_dir}/modules-to-genes.tsv')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'module_file', help='text file corresponding to the list of modules')
    parser.add_argument(
        'output_dir', help='output directory for the text file mapping the modules to the genes belonging to them'
    )

    args = parser.parse_args()
    map_genes_to_modules(args.module_file, args.output_dir)
