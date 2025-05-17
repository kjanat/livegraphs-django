from setuptools import setup

setup(
    name="livegraphsdjango",
    version="0.1.0",
    packages=["dashboard_project"],
    entry_points={
        "console_scripts": [
            "manage=dashboard_project.manage:main",
            "runserver=dashboard_project.__main__:main",
            "migrate=dashboard_project.__main__:main",
            "makemigrations=dashboard_project.__main__:main",
            "collectstatic=dashboard_project.__main__:main",
            "createsuperuser=dashboard_project.__main__:main",
            "shell=dashboard_project.__main__:main",
            "test=dashboard_project.__main__:main",
        ],
    },
)
