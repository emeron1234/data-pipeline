LOG_FORMAT = '%(asctime)s %(levelname)-5s [%(thread)s] %(module)s - %(message)s'

# environment, space, object_type and refresh_type
environments = ['dev', 'test', 'prod']
spaces = ['feature', 'qa', 'synthetic', 'actual', 'release']

# Common CLI options used by the tasks in this module
ENV_OPTION = 'env'
SPACE_OPTION = 'space'
ZONE_OPTION = 'zone'
TEST_TYPE_OPTION = 'test_type'
OBJECT_TYPE_OPTION = 'object_type'
JOB_TYPE_OPTION = 'job_type'