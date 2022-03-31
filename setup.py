import setuptools
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("LICENSE.txt", "r", encoding='utf-8') as fh:
    license_from_file = fh.read()

setup(
    name="queue-vk-bot-mrmarvel",
    version="0.0.1",
    author="Sergey",
    author_email="seregakkk999@yandex.ru",
    license=license_from_file,
    description="VK Bot for organising queues and other interesting things",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SADT-Boting/VkBot",
    project_urls={
        "Bug Tracker": "https://github.com/SADT-Boting/VkBot/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    install_requires=["setuptools~=61.2.0",
                      "vk_api~=11.9.7",
                      "sphinx~=4.5.0"],
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9"
)
