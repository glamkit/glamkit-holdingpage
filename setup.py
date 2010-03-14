from setuptools import setup, find_packages

setup(
    name='glamkit-holdingpage',
    version='0.0.1',
    description='Holding page app for your Django site.',
    url='http://github.com/glamkit/glamkit-holdingpage',
    packages=find_packages(),
    package_data={
        'holdingpage': [
            'templates/holdingpage/*.html',
        ]
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)