import sys

# Support import from "Reuse" package when invoked from command line
sys.path.append("../..")

from Reuse import environment


def test_environment():
    env_name, env, token = environment.get_environment('Dev')
    masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
    print('')
    print(f'Returned values: {env_name}, {env}, {masked_token}')


if __name__ == '__main__':
    test_environment()
