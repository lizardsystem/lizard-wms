from setuptools import setup

version = '1.21.dev0'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('TODO.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'Django',
    'django-staticfiles',
    'django-extensions',
    'django-jsonfield',
    'OWSLib',
    'lizard-ui >= 4.0, < 5.0',
    'lizard-map >= 4.0, < 5.0',
    'lizard-maptree',
    'django-nose',
    'pkginfo',
    'GChartWrapper',
    'requests',
    'unicodecsv',
    ],

tests_require = [
    'nose',
    'coverage',
    'factory_boy',
    'mock',
    ]

setup(name='lizard-wms',
      version=version,
      description="App for (external) wms layers.",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Framework :: Django',
                   ],
      keywords=['wms'],
      author='Jack Ha',
      author_email='jack.ha@nelen-schuurmans.nl',
      url='',
      license='GPL',
      packages=['lizard_wms'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
        'console_scripts': [
            ],
        'lizard_map.adapter_class': [
            'wms = lizard_wms.layers:AdapterWMS',
            ],
        },
      )
