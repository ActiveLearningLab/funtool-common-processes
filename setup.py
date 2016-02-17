from setuptools import setup

setup(name='funtool-common-processes',
        version='0.0.25',
        description='Common processes to be used with the FUN Tool ',
        author='Active Learning Lab',
        author_email='pjanisiewicz@gmail.com',
        license='MIT',
        packages=[
            'funtool_common_processes',
            'funtool_common_processes.adaptors',
            'funtool_common_processes.analysis_selectors',
            'funtool_common_processes.group_measures',
            'funtool_common_processes.grouping_selectors',
            'funtool_common_processes.reporters',
            'funtool_common_processes.state_measures'
        ],
        install_requires=['funtool'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4'
        ],
        zip_safe=False)
